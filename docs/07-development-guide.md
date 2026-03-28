# Development Guide

## Prerequisites
- Python 3.11+
- pip (Python package manager)
- Git

## Phase 1 — Local Setup

### 1. Clone & Setup
```bash
git clone <repository-url>
cd cloud-health-dms
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Run the Application
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Access
- API Docs (Swagger): http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 4. Run Tests
```bash
pytest tests/ -v
```

## Phase 2 — AWS Deployment

### 1. AWS Account Setup
- Create IAM user with programmatic access
- Configure AWS CLI: `aws configure`

### 2. Infrastructure Setup
```bash
# VPC, Subnets, Security Groups — use AWS Console or CLI
# RDS PostgreSQL instance (Multi-AZ for demo)
# S3 bucket for medical file uploads
# EC2 instance(s) with Auto Scaling Group
```

### 3. Application Changes for AWS
- Update `config.py` to use RDS connection string (via environment variables)
- Update file upload service to use boto3 S3 client
- Add CloudWatch logging configuration

### 4. Deployment on EC2
```bash
# SSH into EC2
ssh -i key.pem ec2-user@<public-ip>

# Install dependencies
sudo yum install python3 python3-pip -y
pip3 install -r requirements.txt

# Run with gunicorn for production
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Environment Variables

| Variable | Phase 1 Default | Phase 2 (AWS) |
|----------|----------------|---------------|
| `DATABASE_URL` | `sqlite:///./health_dms.db` | `postgresql://user:pass@rds-endpoint/dbname` |
| `SECRET_KEY` | `dev-secret-key-change-me` | AWS Secrets Manager or env var |
| `UPLOAD_DIR` | `./uploads` | (not used — S3 instead) |
| `S3_BUCKET` | (not used) | `health-dms-uploads-group23` |
| `AWS_REGION` | (not used) | `ap-south-1` |

## Dependencies (requirements.txt)

```
fastapi>=0.100.0
uvicorn>=0.23.0
sqlalchemy>=2.0.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
pydantic>=2.0.0
boto3>=1.28.0
pytest>=7.4.0
httpx>=0.24.0
```
