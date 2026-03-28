# Development Guide

## Prerequisites
- Python 3.11+ (tested with 3.12)
- pip (Python package manager)
- Git

## Phase 1 — Local Setup

### 1. Clone & Setup
```bash
git clone https://github.com/avanishpsingh/cloud-health-dms.git
cd cloud-health-dms
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Seed Sample Data
```bash
python scripts/seed.py
```
This creates 3 users, 10 doctors, 100 patients, ~259 appointments, and ~104 medical records.

### 3. Run the Application
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access the Application

| URL | What it provides |
|-----|-----------------|
| http://localhost:8000/dashboard | **Interactive Dashboard** — the main UI for managing the hospital |
| http://localhost:8000/docs | Swagger UI — interactive API documentation with "Try it out" |
| http://localhost:8000/redoc | ReDoc — alternative API docs (read-only) |

### 5. Login to the Dashboard

Open http://localhost:8000/dashboard and sign in:

| Username | Password | Role | What you can do |
|----------|----------|------|-----------------|
| `admin` | `admin123` | Admin | Everything — manage users, doctors, patients, appointments, view analytics |
| `dr_sharma` | `doctor123` | Doctor | View patients & doctors, manage appointments, add medical records |
| `reception1` | `recep123` | Receptionist | Register patients, schedule appointments |

### 6. Using the Dashboard

**Overview tab**: See hospital statistics, department charts, and recent patients.

**Patients tab**:
- Click **"+ Add Patient"** to register a new patient (fill in name, age, gender, contact, etc.)
- Use the **search box** to find patients by name, contact number, or address
- Click a **patient name** to view full details, medical records, and appointments
- Use **Edit** / **Del** buttons to modify or remove patients

**Doctors tab**:
- Click **"+ Add Doctor"** to add a new doctor (name, specialization, department, contact)
- Filter by **department** using the dropdown, or search by name/specialization
- Click a **doctor name** to view details and their appointment list
- Use **Edit** / **Del** buttons to modify or remove doctors

**Appointments tab**:
- Click **"+ Add Appointment"** to schedule a new appointment (select patient, doctor, date/time)
- Filter by **status** (Scheduled, Completed, Cancelled) or search by patient/doctor name
- Click the **status badge** on any appointment to change its status
- Use the **Del** button to remove appointments

**Users tab** (Admin only):
- Click **"+ Add User"** to register a new system user (admin, doctor, or receptionist)
- View all registered users and their roles

### 7. Using the Swagger API

Open http://localhost:8000/docs for interactive API testing:

1. Click the **"Authorize"** button (top right)
2. Go to `/auth/login`, click "Try it out", enter `{"username":"admin","password":"admin123"}`
3. Copy the `access_token` from the response
4. Click **"Authorize"** again, paste the token as `Bearer <token>`
5. Now you can test any endpoint

### 8. Run Tests
```bash
python -m pytest tests/ -v    # 17 tests passing
```

Tests use an in-memory SQLite database (completely isolated from your data).

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
