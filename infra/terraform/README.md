# Cloud-Native Healthcare DMS — Terraform Infrastructure (Phase 2)

This Terraform configuration provisions the entire AWS Phase-2 stack for
Group 23's Cloud Computing project. One `terraform apply` brings up:

| Layer            | AWS Resources                                                                 |
|------------------|-------------------------------------------------------------------------------|
| Networking       | VPC (`10.0.0.0/16`), 2× public subnets, 2× private subnets, IGW, NAT, route tables |
| Security         | KMS CMK (RDS + S3), IAM roles, security groups, S3 SSE-KMS, RDS encryption     |
| Storage          | S3 bucket (versioned, KMS-encrypted, public access blocked, lifecycle rules)  |
| Database         | RDS PostgreSQL 15, Multi-AZ, encrypted, in private subnets                    |
| Compute          | EC2 Launch Template + Auto Scaling Group (min 1, max 3) behind ALB            |
| Load Balancer    | Internet-facing Application Load Balancer with HTTP listener + target group   |
| Auto-scaling     | TargetTracking on average CPU = 60%                                          |
| Serverless       | Lambda (appointment reminder) on a 15-minute EventBridge schedule              |
| Notifications    | SNS topic for appointment reminders                                          |
| Audit            | CloudTrail (all-region, KMS-encrypted, S3 backed)                             |
| Monitoring       | CloudWatch log group + 2 alarms (5xx, high CPU) wired to SNS                  |

## Layout

```
infra/terraform/
├── README.md            ← this file
├── main.tf              ← provider, data sources, locals
├── variables.tf         ← inputs (region, project name, db creds, etc.)
├── outputs.tf           ← ALB DNS, RDS endpoint, S3 bucket
├── network.tf           ← VPC, subnets, IGW, NAT, route tables
├── security.tf          ← KMS, IAM, security groups
├── storage_s3.tf        ← S3 bucket for medical files
├── database_rds.tf      ← RDS PostgreSQL Multi-AZ
├── compute_ec2.tf       ← Launch template, ASG, ALB, target group
├── lambda_reminder.tf   ← Lambda + EventBridge + SNS topic
├── observability.tf     ← CloudTrail, CloudWatch alarms
└── user_data.sh         ← EC2 bootstrap (clones repo, runs uvicorn)
```

## Prerequisites

```bash
# 1. AWS account with admin privileges
# 2. AWS CLI configured (`aws configure`) or env vars set
# 3. Terraform ≥ 1.5
# 4. An existing EC2 key pair name (for SSH if you need to debug nodes)
```

## Usage

```bash
cd infra/terraform

# (One-time) initialise the providers
terraform init

# Inspect the plan
terraform plan -var "db_password=ChangeMe123!" -var "key_pair_name=my-key"

# Apply (~12-15 minutes — RDS is the slowest)
terraform apply -auto-approve \
  -var "db_password=ChangeMe123!" \
  -var "key_pair_name=my-key"

# Outputs include the ALB URL — open it in a browser
terraform output alb_url

# When done — TEAR IT DOWN to avoid AWS charges
terraform destroy -auto-approve -var "db_password=ChangeMe123!" -var "key_pair_name=my-key"
```

## What the EC2 user_data does

`user_data.sh` runs on first boot for every ASG instance:

1. Installs Python 3.11, git, pip, the CloudWatch agent.
2. Clones `https://github.com/avanishpsingh/cloud-health-dms` into `/opt/app`.
3. Writes `/opt/app/.env` from EC2 instance metadata + Terraform-injected
   values (RDS endpoint, S3 bucket, KMS key, SNS topic, JSON_LOGS=True).
4. Installs `requirements.txt` (+ `boto3`).
5. Creates tables and seeds the demo data if the database is empty.
6. Starts `uvicorn` as a `systemd` unit (`healthdms.service`) listening on `:8000`.
7. Starts the CloudWatch agent so logs flow to `/aws/ec2/healthdms`.

If an older stack was deployed before this bootstrap step existed and dashboard login fails with `Invalid credentials`, seed the running environment once:

```bash
curl -X POST http://<alb-dns>/auth/seed
```

Then log in with `admin / admin123`.

## Cost estimate (us-east-1, on-demand)

| Resource                        | ~Monthly cost (USD) |
|---------------------------------|---------------------|
| EC2 t3.micro × 2                | $15                 |
| ALB                              | $18                 |
| RDS db.t3.micro Multi-AZ         | $30                 |
| S3 (1 GB + few thousand requests)| < $1               |
| Lambda + CloudWatch + CloudTrail | < $1               |
| NAT Gateway                      | $32                 |
| **Total**                        | **~$95 / month**    |

> ⚠️ Run `terraform destroy` immediately after the demo / viva.

## Production hardening (out of scope for this assignment)

- Add HTTPS listener with ACM certificate + Route 53 alias.
- Move secrets to AWS Secrets Manager.
- Add WAF on the ALB.
- Enable AWS Config conformance pack for HIPAA.
- Convert state to remote backend (S3 + DynamoDB lock).
