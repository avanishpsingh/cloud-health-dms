# Module 10: Phase 2 — AWS Cloud Migration Guide

> **Time**: ~3 hours | **Prerequisites**: Module 09 (AWS fundamentals)

---

## Why This Module

This is the **practical playbook** for Phase 2 of your assignment. It walks through exactly what changes are needed to move from local to AWS, step by step.

---

## 10.1 Migration Strategy Overview

```
Phase 1 (Local)                    Phase 2 (AWS)
─────────────────                  ─────────────────
SQLite file DB          ───→       RDS PostgreSQL (Multi-AZ)
uploads/ directory      ───→       S3 Bucket (KMS encrypted)
localhost:8000          ───→       EC2 + ALB (Auto Scaling)
print() logging         ───→       CloudWatch Logs
No monitoring           ───→       CloudWatch Metrics + Alarms
No audit trail          ───→       CloudTrail
Dev JWT secret          ───→       AWS Secrets Manager / env var
```

**Key Insight**: SQLAlchemy and the config system were designed from Day 1 to make this migration smooth. Most changes are configuration, not code.

---

## 10.2 Step 1: VPC & Network Setup

### What to Create
```
VPC: 10.0.0.0/16
├── Public Subnet AZ-a:  10.0.1.0/24  → ALB
├── Public Subnet AZ-b:  10.0.2.0/24  → ALB (multi-AZ)
├── Private Subnet AZ-a: 10.0.3.0/24  → EC2, RDS
└── Private Subnet AZ-b: 10.0.4.0/24  → RDS standby (Multi-AZ)

Security Groups:
├── alb-sg: Inbound 80, 443 from 0.0.0.0/0
├── ec2-sg: Inbound 8000 from alb-sg only
└── rds-sg: Inbound 5432 from ec2-sg only
```

### Why This Architecture
- **ALB** in public subnets: needs internet access
- **EC2** in private subnets: not directly accessible from internet
- **RDS** in private subnets: only EC2 can reach it via security group rules

### 📚 Resources
- [VPC with Public and Private Subnets](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Scenario2.html)

---

## 10.3 Step 2: RDS PostgreSQL Setup

### Create RDS Instance
- **Engine**: PostgreSQL 15+
- **Instance class**: db.t3.micro (free tier)
- **Multi-AZ**: Yes (for the assignment about high availability)
- **Storage**: 20 GB, encrypted with KMS
- **VPC**: Place in private subnets
- **Security group**: Only allow port 5432 from EC2 security group

### Code Change — ONE LINE
```python
# In .env file on EC2 (or as environment variable)
DATABASE_URL=postgresql://admin:YourPassword@mydb.xxxx.ap-south-1.rds.amazonaws.com:5432/health_dms
```

That's it. SQLAlchemy handles the rest because the ORM is database-agnostic.

### One Additional Dependency
```bash
pip install psycopg2-binary  # PostgreSQL driver for Python
```

Add to `requirements.txt`:
```
psycopg2-binary>=2.9.0
```

### Also Remove the SQLite connect_args
```python
# app/database.py — adjust the conditional
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
# For PostgreSQL, connect_args stays empty → works seamlessly
```

This code is **already in the project** — no change needed!

### 📚 Resources
- [Create RDS PostgreSQL Instance](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_GettingStarted.CreatingConnecting.PostgreSQL.html)

---

## 10.4 Step 3: S3 Bucket for File Uploads

### Create S3 Bucket
- **Name**: `health-dms-uploads-group23`
- **Region**: `ap-south-1`
- **Encryption**: SSE-KMS (AES-256)
- **Block public access**: Yes (files accessed only via app)

### Code Change — File Upload Router

```python
# app/routers/records.py — replace local file write with S3

import boto3

# Phase 1 code:
# filepath = Path(settings.UPLOAD_DIR) / filename
# filepath.write_bytes(contents)
# record.file_path = str(filepath)

# Phase 2 code:
s3 = boto3.client('s3', region_name=settings.AWS_REGION)
s3_key = f"medical-records/{filename}"
s3.put_object(
    Bucket=settings.S3_BUCKET,
    Key=s3_key,
    Body=contents,
    ServerSideEncryption='aws:kms'
)
record.file_path = s3_key   # store S3 key instead of local path
```

### Add boto3 to Requirements
```
boto3>=1.28.0
```

### 📚 Resources
- [S3 Upload with boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html)

---

## 10.5 Step 4: EC2 Deployment

### Launch EC2 Instance
- **AMI**: Amazon Linux 2023
- **Instance type**: t2.micro (free tier)
- **VPC**: Private subnet
- **IAM role**: Attach role with RDS + S3 permissions
- **Security group**: Allow port 8000 from ALB security group

### Deploy Application on EC2
```bash
# SSH into EC2 (via bastion or SSM)
ssh -i key.pem ec2-user@<private-ip>

# Install Python
sudo yum install python3 python3-pip -y

# Clone the project
git clone https://github.com/avanishpsingh/cloud-health-dms.git
cd cloud-health-dms

# Install Python dependencies
pip3 install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://admin:pass@mydb.xxxx.rds.amazonaws.com:5432/health_dms"
export SECRET_KEY="production-secret-key-here"
export S3_BUCKET="health-dms-uploads-group23"
export AWS_REGION="ap-south-1"
export DEBUG="false"

# Seed the database (first time only)
python3 scripts/seed.py

# Run with Gunicorn (production WSGI server)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Create a systemd Service (Auto-Start)
```ini
# /etc/systemd/system/health-dms.service
[Unit]
Description=Healthcare DMS FastAPI Application
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/cloud-health-dms
Environment="DATABASE_URL=postgresql://..."
Environment="SECRET_KEY=production-key"
ExecStart=/usr/local/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable health-dms
sudo systemctl start health-dms
```

---

## 10.6 Step 5: ALB + Auto Scaling

### Create Target Group
- **Protocol**: HTTP, Port 8000
- **Health check**: `GET /` (returns `{"status": "healthy"}`)
- **Healthy threshold**: 3 checks
- **Interval**: 30 seconds

### Create ALB
- **Scheme**: Internet-facing
- **Subnets**: Both public subnets
- **Listener**: HTTP 80 → target group (or HTTPS 443 with ACM cert)

### Create Auto Scaling Group
- **Launch template**: Same config as your EC2 instance
- **Min**: 1, **Desired**: 1, **Max**: 3
- **Scaling policy**: Target tracking — CPU average > 70% → scale out

### How It Works Together
```
Internet → ALB (public) → EC2 Instance(s) (private) → RDS (private)
                                                     → S3 (via IAM)
```

---

## 10.7 Step 6: Monitoring & Logging

### CloudWatch Logs
```bash
# Install CloudWatch agent on EC2
sudo yum install amazon-cloudwatch-agent -y

# Configure to send application logs
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

### CloudWatch Alarms
| Alarm | Metric | Threshold | Action |
|-------|--------|-----------|--------|
| High CPU | CPUUtilization | > 80% for 5 min | SNS notification + Auto Scale |
| Unhealthy Host | UnHealthyHostCount | > 0 | SNS notification |
| High Latency | TargetResponseTime | > 2 seconds | SNS notification |

### SNS Topic
- Create topic: `health-dms-alerts`
- Subscribe: each team member's email
- Alarms trigger → SNS → email notifications

---

## 10.8 Step 7: Security & Compliance

### IAM Roles
```json
// EC2 Instance Role — allows access to RDS and S3
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
            "Resource": "arn:aws:s3:::health-dms-uploads-group23/*"
        },
        {
            "Effect": "Allow",
            "Action": ["rds-db:connect"],
            "Resource": "arn:aws:rds-db:ap-south-1:*:dbuser:*/admin"
        }
    ]
}
```

### CloudTrail
- Enable for all regions
- Log to S3 bucket: `health-dms-audit-logs`
- Records: who accessed what, when, from where

### KMS Encryption
- RDS: Enable encryption at creation time (can't add later)
- S3: Enable SSE-KMS on the bucket
- Every medical file and patient record is encrypted at rest

---

## 10.9 Step 8: Lambda Function (Bonus)

### Appointment Notification Lambda
```python
# lambda/appointment_notification.py
import json
import boto3

sns = boto3.client('sns')

def handler(event, context):
    """Triggered when an appointment is created/updated."""
    appointment = event['appointment']
    message = f"Appointment {appointment['status']}: Patient #{appointment['patient_id']} with Doctor #{appointment['doctor_id']}"

    sns.publish(
        TopicArn='arn:aws:sns:ap-south-1:123456789:appointment-notifications',
        Message=message,
        Subject='Appointment Update'
    )

    return {'statusCode': 200, 'body': json.dumps('Notification sent')}
```

---

## 10.10 Migration Checklist

```
[ ] VPC with public + private subnets
[ ] Security groups (ALB, EC2, RDS)
[ ] RDS PostgreSQL (Multi-AZ, KMS encrypted)
[ ] S3 bucket (KMS encrypted, block public access)
[ ] EC2 instance with IAM role
[ ] Deploy application code on EC2
[ ] Set environment variables (DATABASE_URL, SECRET_KEY, S3_BUCKET)
[ ] Install psycopg2-binary
[ ] Seed database: python3 scripts/seed.py
[ ] ALB in public subnets
[ ] Target group with health check on GET /
[ ] Auto Scaling Group (min 1, max 3)
[ ] CloudWatch alarms (CPU, latency, unhealthy hosts)
[ ] SNS topic + email subscriptions
[ ] CloudTrail enabled
[ ] CloudWatch Logs agent on EC2
[ ] Lambda function for notifications (optional)
[ ] Verify all endpoints work via ALB URL
[ ] Run tests against AWS deployment
[ ] Demo auto-scaling with load test
```

---

## 📚 Complete AWS Learning Path

| Order | Resource | Time | Coverage |
|-------|---------|------|----------|
| 1 | [AWS Cloud Practitioner Essentials](https://explore.skillbuilder.aws/learn/course/134) | 6 hrs | All AWS basics |
| 2 | [Stephane Maarek — EC2 Tutorial](https://www.youtube.com/watch?v=iHX-jtKIVNA) | 30 min | EC2 hands-on |
| 3 | [Stephane Maarek — RDS Tutorial](https://www.youtube.com/watch?v=vw5EO5Jz8-8) | 30 min | RDS hands-on |
| 4 | [Stephane Maarek — S3 Tutorial](https://www.youtube.com/watch?v=e6w9LwZJFIA) | 30 min | S3 hands-on |
| 5 | [Stephane Maarek — VPC Tutorial](https://www.youtube.com/watch?v=bGDMeD6kOz0) | 30 min | VPC networking |
| 6 | [Stephane Maarek — ALB Tutorial](https://www.youtube.com/watch?v=qpBo95MJ1gI) | 30 min | Load balancing |
| 7 | [AWS Well-Architected Labs](https://wellarchitectedlabs.com/) | 2 hrs | Best practices |

---

## Module Summary

This module is the most important for your Phase 2 assignment. The key takeaway:
**The application was designed from Day 1 for cloud migration.**

- SQLAlchemy → database-agnostic (SQLite → PostgreSQL)
- Pydantic Settings → environment variables (no code changes)
- Stateless JWT → works across multiple EC2 instances
- File upload isolation → easy swap from local to S3
