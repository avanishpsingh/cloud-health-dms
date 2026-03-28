# AWS Service Mapping

This document maps all services used in the project to their AWS equivalents, as required by the course guidelines.

## Service Mapping Table

| Purpose | AWS Service | Phase Used | Description |
|---------|------------|------------|-------------|
| Virtual Servers | **Amazon EC2** | Phase 2 | Run FastAPI application in Auto Scaling Group |
| Serverless Compute | **AWS Lambda** | Phase 2 | Event-driven processing (e.g., appointment notifications) |
| Load Balancing | **Elastic Load Balancer (ALB)** | Phase 2 | Distribute traffic across EC2 instances |
| Relational Database | **Amazon RDS (PostgreSQL)** | Phase 2 | Patient records, doctor info (Multi-AZ) |
| Object Storage | **Amazon S3** | Phase 2 | Medical files, reports, images |
| DNS | **Amazon Route 53** | Phase 2 | Domain name routing (optional) |
| Identity & Access | **AWS IAM** | Phase 2 | Role-based access, least-privilege policies |
| Encryption | **AWS KMS** | Phase 2 | AES-256 encryption at rest for RDS & S3 |
| Audit Logging | **AWS CloudTrail** | Phase 2 | API call logging for compliance |
| Monitoring | **Amazon CloudWatch** | Phase 2 | Metrics, dashboards, alarms |
| Alerts | **Amazon SNS** | Phase 2 | Email/SMS notifications for critical events |
| Network Isolation | **Amazon VPC** | Phase 2 | Private subnets for data layer |
| Analytics | **Amazon Athena** | Phase 2 | SQL queries on S3 data (optional) |
| Compliance | **AWS Config** | Phase 2 | Automated compliance rule checks |

## Phase 1 → Phase 2 Migration Map

| Phase 1 (Local) | Phase 2 (AWS) | Migration Notes |
|-----------------|---------------|-----------------|
| SQLite | RDS PostgreSQL | SQLAlchemy makes this a config change |
| Local filesystem (`uploads/`) | S3 Bucket | Replace file I/O with boto3 S3 calls |
| `localhost:8000` | EC2 behind ALB | Deploy same FastAPI app on EC2 |
| No auth infra | IAM + JWT | Add IAM for AWS-level access; JWT stays for app-level |
| No encryption | KMS + TLS | Enable RDS encryption, S3 SSE, HTTPS via ALB |
| Print/log statements | CloudWatch Logs | Configure CloudWatch agent on EC2 |
| No scaling | EC2 Auto Scaling Group | Min 1, Max 3 instances, CPU-based scaling |
| Manual testing | CloudWatch Alarms + SNS | Automated health checks & alerts |
