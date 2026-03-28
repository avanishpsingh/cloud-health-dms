# Module 09: AWS Cloud Fundamentals

> **Time**: ~4 hours | **Prerequisites**: Module 08 (Architecture)

---

## Why This Module

Phase 2 of your assignment migrates this local application to AWS. You need to understand each AWS service, why it's used, and how it replaces a local component. This module covers the **13 AWS services** used in this project.

---

## 9.1 AWS Services Overview

```
┌─────────────────────────────────────────────────────────┐
│                      YOUR PROJECT                        │
│                                                          │
│   Route 53 (DNS) → ALB (Load Balancer) → EC2 (Compute) │
│                                              │           │
│                                    ┌─────────┼─────────┐│
│                                    ▼         ▼         ▼│
│                                  RDS       S3     Lambda ││
│                              (Database) (Files) (Events)││
│                                                          │
│   Cross-cutting: IAM · KMS · CloudTrail · CloudWatch    │
│                  VPC · SNS · Config                      │
└─────────────────────────────────────────────────────────┘
```

---

## 9.2 Amazon EC2 (Elastic Compute Cloud)

### What It Is
A virtual server in the cloud. You get a Linux/Windows machine that you can SSH into, install software, and run your FastAPI app.

### How This Project Uses It
```bash
# Deploy FastAPI on EC2
ssh -i key.pem ec2-user@<public-ip>
pip3 install -r requirements.txt
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Auto Scaling Group (ASG)
- **Min instances**: 1 (always at least one server running)
- **Max instances**: 3 (scales up during peak hours)
- **Trigger**: CPU > 80% for 5 minutes → launch new instance

### 📚 Resources
- [AWS EC2 Getting Started](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html)
- [EC2 Auto Scaling](https://docs.aws.amazon.com/autoscaling/ec2/userguide/what-is-amazon-ec2-auto-scaling.html)
- [YouTube: EC2 Tutorial for Beginners](https://www.youtube.com/watch?v=iHX-jtKIVNA) — TechWorld with Nana

---

## 9.3 Amazon RDS (Relational Database Service)

### What It Is
A managed database service. AWS handles backups, patching, replication — you just use it.

### How This Project Uses It
Replace SQLite with PostgreSQL on RDS:

```python
# Phase 1 (local)
DATABASE_URL = "sqlite:///./health_dms.db"

# Phase 2 (AWS)
DATABASE_URL = "postgresql://admin:password@mydb.xxxx.ap-south-1.rds.amazonaws.com:5432/health_dms"
```

That's the ONLY code change needed (thanks to SQLAlchemy's DB abstraction).

### Multi-AZ Deployment
- RDS runs in **two availability zones** simultaneously
- If one AZ goes down, it automatically fails over to the other
- This gives **high availability** (a key assignment requirement)

### 📚 Resources
- [AWS RDS Getting Started](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Welcome.html)
- [RDS Multi-AZ](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html)
- [YouTube: RDS Tutorial](https://www.youtube.com/watch?v=vw5EO5Jz8-8) — Stephane Maarek

---

## 9.4 Amazon S3 (Simple Storage Service)

### What It Is
Object storage — stores files (PDFs, images, documents) with virtually unlimited capacity.

### How This Project Uses It
Replace local file uploads with S3:

```python
# Phase 1 — saves to local filesystem
filepath = Path(settings.UPLOAD_DIR) / filename
filepath.write_bytes(contents)

# Phase 2 — saves to S3
import boto3
s3 = boto3.client('s3')
s3.put_object(Bucket=settings.S3_BUCKET, Key=filename, Body=contents)
```

### S3 Features Used
- **Server-Side Encryption (SSE-KMS)**: Files encrypted at rest
- **Bucket policies**: Control who can access files
- **Durability**: 99.999999999% (11 nines)

### 📚 Resources
- [AWS S3 Getting Started](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html)
- [boto3 S3 Guide](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-examples.html)
- [YouTube: S3 Tutorial](https://www.youtube.com/watch?v=e6w9LwZJFIA) — Stephane Maarek

---

## 9.5 AWS IAM (Identity and Access Management)

### What It Is
Controls **who** can do **what** on AWS. Every AWS service interaction requires IAM permissions.

### How This Project Uses It
- **EC2 instance role**: Allows EC2 to access RDS and S3 (without hardcoding credentials)
- **Least-privilege policies**: EC2 can only read/write to the specific S3 bucket and RDS instance
- **IAM users**: Each team member has their own AWS account with appropriate permissions

### Example IAM Policy
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": ["s3:PutObject", "s3:GetObject"],
            "Resource": "arn:aws:s3:::health-dms-uploads-group23/*"
        }
    ]
}
```

### 📚 Resources
- [AWS IAM Getting Started](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [YouTube: IAM Tutorial](https://www.youtube.com/watch?v=iF9fs8Rdasigg) — Be a Better Dev

---

## 9.6 AWS KMS (Key Management Service)

### What It Is
Manages encryption keys. Used to encrypt data at rest in RDS and S3.

### How This Project Uses It
- **RDS encryption**: All patient data encrypted on disk (AES-256)
- **S3 SSE-KMS**: Medical files encrypted in S3
- **Compliance requirement**: Healthcare data must be encrypted

### 📚 Resources
- [AWS KMS Overview](https://docs.aws.amazon.com/kms/latest/developerguide/overview.html)

---

## 9.7 Elastic Load Balancer (ALB)

### What It Is
Distributes incoming traffic across multiple EC2 instances. If one instance goes down, ALB routes traffic to healthy ones.

### How This Project Uses It
```
User → ALB → EC2 Instance 1 (healthy ✅)
              EC2 Instance 2 (healthy ✅)
              EC2 Instance 3 (down ❌ — ALB stops sending traffic here)
```

- **Health checks**: ALB calls `GET /` every 30 seconds
- **TLS termination**: ALB handles HTTPS (via ACM certificate)

### 📚 Resources
- [ALB Overview](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html)
- [YouTube: ELB Tutorial](https://www.youtube.com/watch?v=qpBo95MJ1gI) — Stephane Maarek

---

## 9.8 Amazon VPC (Virtual Private Cloud)

### What It Is
Your own isolated network in AWS. You control IP ranges, subnets, and network access.

### How This Project Uses It
```
VPC (10.0.0.0/16)
├── Public Subnet (10.0.1.0/24)
│   └── ALB (internet-facing)
├── Private Subnet A (10.0.2.0/24)
│   └── EC2 instances
└── Private Subnet B (10.0.3.0/24)
    └── RDS (not accessible from internet!)
```

RDS is in a **private subnet** — it can only be accessed by EC2 instances, not directly from the internet.

### 📚 Resources
- [VPC Overview](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html)
- [YouTube: VPC Explained](https://www.youtube.com/watch?v=bGDMeD6kOz0) — Stephane Maarek

---

## 9.9 AWS Lambda

### What It Is
Serverless compute — runs code without managing servers. You pay only when the code executes.

### How This Project Uses It
- **Appointment notifications**: Lambda triggered when appointment status changes → sends email via SES/SNS
- **Event-driven**: No always-running server needed for occasional tasks

### 📚 Resources
- [Lambda Getting Started](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
- [YouTube: Lambda Tutorial](https://www.youtube.com/watch?v=eOBq__h4OJ4) — Stephane Maarek

---

## 9.10 Amazon CloudWatch

### What It Is
Monitoring and observability service. Collects metrics, logs, and sets alarms.

### How This Project Uses It
- **Metrics**: CPU utilization, request count, error rate
- **Alarms**: Alert when CPU > 80% (triggers auto-scaling)
- **Logs**: Application logs from EC2 instances
- **Dashboards**: Visual display of system health

### 📚 Resources
- [CloudWatch Overview](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html)

---

## 9.11 AWS CloudTrail

### What It Is
Records every API call made in your AWS account — who did what, when, from where.

### How This Project Uses It
- **Compliance**: Logs all access to patient data
- **Audit trail**: Who created/deleted/modified resources
- **Security**: Detect unauthorized access attempts

### 📚 Resources
- [CloudTrail Overview](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html)

---

## 9.12 Amazon SNS (Simple Notification Service)

### What It Is
Sends notifications via email, SMS, or push notifications.

### How This Project Uses It
- **CloudWatch alarms** → SNS → email to admin when CPU is high
- **Lambda function** → SNS → appointment reminders

### 📚 Resources
- [SNS Overview](https://docs.aws.amazon.com/sns/latest/dg/welcome.html)

---

## 9.13 Route 53

### What It Is
DNS service — maps domain names to IP addresses.

### How This Project Uses It (Optional)
- Maps `healthcare.group23.com` → ALB endpoint
- Not strictly required for the assignment if you use the ALB URL directly

### 📚 Resources
- [Route 53 Overview](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html)

---

## 9.14 Complete Phase 1 → Phase 2 Service Map

| Phase 1 (Local) | Phase 2 (AWS) | What Changes |
|-----------------|---------------|-------------|
| SQLite file | RDS PostgreSQL | Change `DATABASE_URL` config |
| `uploads/` folder | S3 bucket | Replace file I/O with boto3 |
| `localhost:8000` | EC2 + ALB | Deploy app on EC2, load balance |
| Manual running | Gunicorn + systemd | Production process manager |
| No encryption | KMS + TLS | Enable at-rest and in-transit encryption |
| `print()` logs | CloudWatch Logs | Structured logging |
| No scaling | Auto Scaling Group | CPU-based auto-scaling |
| No monitoring | CloudWatch + SNS | Metrics, alarms, notifications |
| No audit | CloudTrail | All API calls logged |
| No network isolation | VPC | Private subnets for data |

---

## 📚 Best Overall AWS Learning Resources

1. **[AWS Cloud Practitioner Essentials (Free Course)](https://explore.skillbuilder.aws/learn/course/external/view/elearning/134/aws-cloud-practitioner-essentials)** — Official AWS training, covers all basics
2. **[Stephane Maarek YouTube Channel](https://www.youtube.com/c/StephaneMaarek)** — Best free AWS tutorials
3. **[AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)** — Design principles
4. **[AWS Free Tier](https://aws.amazon.com/free/)** — Practice without paying

### ✏️ Exercise
1. Sign up for AWS Free Tier
2. Launch an EC2 instance (t2.micro)
3. SSH into it and install Python
4. Clone this project and run it on EC2
5. Access it via the public IP
