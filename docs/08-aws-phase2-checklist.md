# Phase 2 AWS Checklist (Restricted University Account)

This checklist is designed for the course rubric and for AWS accounts where services like EC2 may be restricted.

## Recommended Architecture

```
User
  -> API Gateway
  -> Lambda (FastAPI + Mangum)
  -> RDS/Aurora PostgreSQL
  -> S3

Cross-cutting: IAM, CloudWatch, CloudTrail
```

## What to Create in AWS

Create these in order:

1. **S3 bucket**
   - Example name: `health-dms-uploads-group23`
   - Region: `ap-south-1`
   - Block all public access: `Enabled`
   - Default encryption: `Enabled`

2. **IAM role for Lambda**
   - Trusted entity: `Lambda`
   - Attach policies that allow:
     - CloudWatch Logs
     - S3 access to your project bucket
     - VPC networking if Lambda needs to reach RDS/Aurora inside private subnets

3. **Lambda function**
   - Runtime: `Python 3.12`
   - Handler: `lambda_handler.handler`
   - Upload source: use the ZIP created by `scripts/package_lambda.sh`
   - Environment variables: copy from `.env.aws.example`

4. **VPC attachment for Lambda**
   - Only needed if your RDS/Aurora database is not publicly reachable
   - Pick the same VPC/subnets used by the database
   - Security group rule: allow database port `5432` from Lambda's security group

5. **API Gateway HTTP API**
   - Integration target: your Lambda function
   - Routes: `ANY /{proxy+}` and `ANY /`
   - Stage: default is fine for the assignment

6. **CloudWatch Logs**
   - Confirm Lambda log group is created after first invocation
   - Use screenshots in report/recording to prove monitoring

7. **CloudTrail**
   - Confirm trail is enabled in the account or create one if allowed
   - Use this in the report for audit/compliance discussion

## Minimal Security Group Plan

If Lambda and RDS/Aurora are in the same VPC:

- `lambda-sg`
  - outbound: allow all

- `rds-sg`
  - inbound: `5432` from `lambda-sg`
  - no public inbound rule needed

## GitHub Actions Secrets to Add

Add these repository secrets before enabling the deploy workflow:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `LAMBDA_FUNCTION_NAME`
- `DATABASE_URL`
- `SECRET_KEY`
- `S3_BUCKET`
- `API_BASE_URL`

## Local vs AWS Environment

Use `.env.example` for local development and `.env.aws.example` as the Phase 2 template.

- Local demo:
  - `DATABASE_URL=sqlite:///./health_dms.db`
  - `USE_S3_UPLOADS=false`
  - `DEPLOYMENT_TARGET=local`

- AWS deployment:
  - `DATABASE_URL=postgresql+psycopg2://...`
  - `USE_S3_UPLOADS=true`
  - `DEPLOYMENT_TARGET=aws-lambda`

## Suggested Demo Flow for Phase 2 Recording

1. Show the project running locally or via deployed API.
2. Show login and one CRUD action.
3. Show a file upload request.
4. Show the file entry or S3 object.
5. Show CloudWatch logs.
6. Briefly show the Lambda function and API Gateway.
7. Mention RDS/Aurora and how the app connects through `DATABASE_URL`.

## Viva Notes

If asked why EC2 was not used:

> The university account had service restrictions, so we chose a feasible managed architecture using API Gateway, Lambda, RDS/Aurora, and S3. This still satisfies the cloud-integration, scalability, security, and monitoring requirements from the rubric.
