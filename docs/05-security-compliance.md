# Security & Compliance Plan

## Data Sensitivity Classification

| Data Type | Sensitivity | Protection Required |
|-----------|------------|-------------------|
| Patient PII (name, contact, address) | High | Encryption at rest + transit, RBAC |
| Medical records (diagnosis, prescription) | Critical | Encryption, audit logging, strict access |
| Medical files (reports, images) | Critical | Encrypted storage, access-controlled |
| Doctor profiles | Medium | Standard access control |
| Appointment data | Medium | Access control by role |
| Login credentials | Critical | Hashed (bcrypt), never stored in plaintext |

## Phase 1 — Local Security Measures

| Control | Implementation |
|---------|---------------|
| Authentication | JWT tokens with expiry (30 min) |
| Password Storage | bcrypt hashing (12 rounds) |
| Authorization | Role-based middleware (admin/doctor/receptionist) |
| Input Validation | Pydantic models for all request bodies |
| SQL Injection | SQLAlchemy ORM (parameterized queries) |
| File Upload Safety | Whitelist allowed extensions (.pdf, .jpg, .png), size limit (10MB) |
| CORS | Restrict origins in FastAPI CORS middleware |

## Phase 2 — AWS Security Measures

| Control | AWS Service | Configuration |
|---------|------------|---------------|
| Network Isolation | VPC | Public subnet (ALB), private subnet (EC2, RDS) |
| Access Control | IAM | Least-privilege roles per service |
| Encryption at Rest | KMS | RDS encryption, S3 SSE-KMS |
| Encryption in Transit | ALB + ACM | TLS 1.2+ via ACM certificate |
| Audit Trail | CloudTrail | Log all API calls to S3 |
| Compliance Checks | AWS Config | Rules for encryption, public access |
| Admin Access | MFA | Multi-factor auth for AWS console |
| Monitoring | CloudWatch | Failed login alerts, unusual API patterns |

## Compliance Standards Referenced
- **HIPAA** — US health data protection (referenced for best practices)
- **DISHA** — India's Digital Information Security in Healthcare Act
- **ABDM** — Ayushman Bharat Digital Mission guidelines

> **Note**: Full compliance is out of scope for this assignment. We implement key security controls to demonstrate awareness and capability.
