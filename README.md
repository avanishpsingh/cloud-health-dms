# Cloud-Native Healthcare Data Management System

**BITS Pilani | Cloud Computing (CSIZG527) | Group 23**

## Overview

A cloud-native healthcare data management system designed for a mid-size hospital chain in India. Built in two phases: a working local application (Phase 1) and a fully cloud-deployable AWS migration (Phase 2) with Infrastructure-as-Code, an S3 storage backend, an RDS PostgreSQL data layer, an EC2 Auto Scaling Group behind an Application Load Balancer, a serverless Lambda for appointment reminders, KMS-backed encryption, CloudTrail audit logging, and CloudWatch observability.

## Team
- Karan Rawat — System Design & Coordination
- Vikas Kumar — Data & Backend Handling
- Kriti Tripathi — Security & Documentation
- Avanish Pratap Singh — Testing & Monitoring

## Tech Stack
- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0
- **Database**: SQLite (Phase 1) → RDS PostgreSQL (Phase 2)
- **Auth**: JWT (python-jose) + bcrypt password hashing + Role-based access control
- **Storage**: Local filesystem (Phase 1) → S3 (Phase 2)
- **Frontend**: Single-page HTML dashboard (served by FastAPI)
- **Cloud**: AWS (EC2, RDS, S3, Lambda, IAM, KMS, CloudWatch, CloudTrail)

## Quick Start (Phase 1)

```bash
# 1. Clone and setup
git clone https://github.com/avanishpsingh/cloud-health-dms.git
cd cloud-health-dms
python -m venv venv

# 2. Activate virtual environment
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Seed the database (100 patients, 10 doctors, sample appointments)
python scripts/seed.py

# 5. Start the server
uvicorn app.main:app --reload
```

### Accessing the Application

| URL | Description |
|-----|-------------|
| http://localhost:8000/dashboard | **Interactive Dashboard** (main UI) |
| http://localhost:8000/docs | Swagger API Documentation |
| http://localhost:8000/ | Health check endpoint |

### Default Login Credentials

| Username | Password | Role | Permissions |
|----------|----------|------|-------------|
| `admin` | `admin123` | Admin | Full access — manage users, doctors, patients, appointments |
| `dr_sharma` | `doctor123` | Doctor | View patients/doctors, manage appointments, add medical records |
| `reception1` | `recep123` | Receptionist | Manage patients, schedule appointments |

## Dashboard Features

The interactive dashboard at `/dashboard` provides a complete hospital management interface:

### Overview Tab
- **Statistics cards** — Total patients, doctors, appointments, completion rates
- **Charts** — Patients by department (bar chart), appointment status distribution
- **Recent patients** — Quick view of the latest patient entries

### Patients Tab
- **Browse** — Paginated table (15 per page) with search by name, contact, address, blood group
- **Add Patient** — Click "+ Add Patient" button to open the form (Name, Age, Gender, Contact, Address, Blood Group)
- **View Details** — Click any patient name to see full details, medical records, and appointment history
- **Edit Patient** — Edit button on each row or in the detail view
- **Delete Patient** — Soft-delete with confirmation dialog

### Doctors Tab
- **Browse** — Full list with search by name/specialization and department dropdown filter
- **Add Doctor** — Click "+ Add Doctor" (Name, Specialization, Department, Contact)
- **View Details** — Click any doctor name to see details and their appointment list
- **Edit/Delete Doctor** — Edit and delete buttons on each row and detail view

### Appointments Tab
- **Browse** — Paginated list with search and status filter (Scheduled/Completed/Cancelled)
- **Add Appointment** — Select patient and doctor from dropdowns, pick date/time, add reason
- **Change Status** — Click any status badge to change it (Scheduled → Completed → Cancelled)
- **Delete Appointment** — Delete button on each row

### Users Tab (Admin only)
- **Browse** — List all system users with their roles
- **Add User** — Register new admin, doctor, or receptionist accounts

## API Endpoints (22 endpoints)

### Authentication
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/auth/login` | Public | Login with username/password, returns JWT token |
| POST | `/auth/register` | Admin | Register new user (admin/doctor/receptionist) |
| GET | `/auth/me` | All roles | Get current logged-in user info |
| GET | `/auth/users` | Admin | List all registered users |

### Patients
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/patients/` | All roles | List patients (search by name) |
| POST | `/patients/` | Admin, Receptionist | Create new patient |
| GET | `/patients/{id}` | All roles | Get patient details |
| PUT | `/patients/{id}` | Admin, Receptionist | Update patient info |
| DELETE | `/patients/{id}` | Admin | Soft-delete patient |

### Doctors
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/doctors/` | All roles | List doctors (search + department filter) |
| POST | `/doctors/` | Admin | Create new doctor |
| GET | `/doctors/{id}` | All roles | Get doctor details |
| PUT | `/doctors/{id}` | Admin | Update doctor info |
| DELETE | `/doctors/{id}` | Admin | Delete doctor |

### Appointments
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/appointments/` | All roles | List appointments (filter by patient/doctor/status) |
| POST | `/appointments/` | Admin, Receptionist | Create appointment |
| PATCH | `/appointments/{id}` | Admin, Doctor | Update appointment status |
| DELETE | `/appointments/{id}` | Admin | Delete appointment |

### Medical Records & Files
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/patients/{id}/records` | Admin, Doctor | Get patient's medical history |
| POST | `/patients/{id}/records` | Doctor | Add medical record |
| POST | `/upload/{record_id}` | Doctor, Admin | Upload medical file (PDF/JPEG/PNG) |

### Analytics
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/analytics/summary` | Admin | Dashboard stats (counts, distributions) |

## Project Structure

```
cloud-health-dms/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, middleware, router registration
│   ├── config.py            # Settings (DB URL, JWT secret, upload config)
│   ├── database.py          # SQLAlchemy engine, session, base
│   ├── auth.py              # Password hashing, JWT creation/verification, RBAC
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── user.py          # User (id, username, password_hash, role)
│   │   ├── patient.py       # Patient (name, age, gender, contact, blood_group)
│   │   ├── doctor.py        # Doctor (name, specialization, department, contact)
│   │   ├── appointment.py   # Appointment (patient_id, doctor_id, date_time, status)
│   │   └── medical_record.py # MedicalRecord (diagnosis, prescription, file_path)
│   ├── schemas/             # Pydantic request/response models
│   │   ├── user.py, patient.py, doctor.py, appointment.py, medical_record.py
│   └── routers/             # API route handlers
│       ├── auth.py          # Login, register, user listing
│       ├── patients.py      # Patient CRUD
│       ├── doctors.py       # Doctor CRUD
│       ├── appointments.py  # Appointment management
│       ├── records.py       # Medical records & file upload
│       ├── analytics.py     # Summary statistics
│       └── dashboard.py     # HTML dashboard SPA
├── scripts/
│   └── seed.py              # Generate sample data (100 patients, 10 doctors)
├── tests/                   # Pytest test suite (17 tests)
│   ├── conftest.py          # Fixtures (in-memory DB, auth tokens)
│   ├── test_auth.py         # Auth tests (6)
│   ├── test_patients.py     # Patient tests (7)
│   ├── test_appointments.py # Appointment tests (4)
│   ├── test_storage.py      # Phase 2 storage backend tests (4)
│   ├── test_lambda_reminder.py    # Phase 2 Lambda tests (3)
│   ├── test_logging_middleware.py # Phase 2 JSON logging tests (3)
│   └── test_upload_e2e.py   # Phase 2 upload E2E tests (2)
├── infra/
│   └── terraform/           # Phase 2 Infrastructure-as-Code (VPC, EC2, RDS, S3, Lambda, …)
├── docs/                    # Detailed project documentation
├── uploads/                 # Medical file uploads directory (Phase 1 only)
├── health_dms.db            # SQLite database (pre-seeded for testing)
├── Dockerfile               # Container image (alternative to EC2 deployment)
├── requirements.txt         # Python dependencies
└── README.md
```

## Seed Data

The `scripts/seed.py` generates reproducible sample data (`random.seed(42)`):
- **3 users**: admin, dr_sharma, reception1
- **10 doctors** across 10 departments (General Medicine, Cardiology, Dermatology, etc.)
- **100 patients** with realistic Indian names, ages, contacts
- **~259 appointments** (mix of scheduled, completed, cancelled)
- **~104 medical records** linked to completed appointments

To re-seed: delete `health_dms.db` and run `python scripts/seed.py`.

## Tests

```bash
python -m pytest tests/ -v    # 29 tests (17 Phase 1 + 12 Phase 2)
```

Tests use an in-memory SQLite database (isolated from production data).
Phase 2 tests use [`moto`](https://github.com/getmoto/moto) to mock S3 and SNS,
so no AWS credentials are required to run them.

| Suite                            | Tests | Covers                                                        |
|----------------------------------|------:|---------------------------------------------------------------|
| `test_auth.py`                   | 6     | Login, JWT, RBAC                                              |
| `test_patients.py`               | 7     | Patient CRUD                                                  |
| `test_appointments.py`           | 4     | Appointment lifecycle                                         |
| `test_storage.py`                | 4     | LocalStorage + S3Storage round trips, factory selection       |
| `test_lambda_reminder.py`        | 3     | Window filter, dry-run, SNS publish                           |
| `test_logging_middleware.py`     | 3     | JSON formatter, request ID, idempotent configure              |
| `test_upload_e2e.py`             | 2     | End-to-end medical-file upload via the storage abstraction    |

## Security Features
- **JWT Authentication** — All API endpoints (except login) require a valid token
- **Role-Based Access Control (RBAC)** — Admin, Doctor, Receptionist with different permissions
- **Password Hashing** — bcrypt via passlib (never stored in plain text)
- **XSS Protection** — All user data escaped in dashboard HTML rendering
- **Input Validation** — Pydantic schemas enforce types and constraints
- **File Upload Validation** — Extension whitelist + size limit
- **Soft Delete** — Patients are deactivated, not permanently removed

## Documentation

See [docs/](docs/) for detailed documentation:
- [Project Overview](docs/01-project-overview.md)
- [Requirements](docs/02-requirements.md)
- [Architecture](docs/03-architecture.md)
- [AWS Service Mapping](docs/04-aws-service-mapping.md)
- [Security & Compliance](docs/05-security-compliance.md)
- [Project Structure](docs/06-project-structure.md)
- [Development Guide](docs/07-development-guide.md)

---

## Phase 2 — AWS Cloud Deployment

Phase 2 ships the same FastAPI codebase to AWS with **zero code changes** required at the call sites — the storage and database layers are pluggable via environment variables.

### Cloud Architecture

```
                          Route 53 (DNS, optional)
                                  │
                                  ▼
                  ┌──────── Application Load Balancer ────────┐
                  │           (public subnets)                │
                  ▼                                           ▼
         EC2 Auto Scaling Group (private subnets, min=1, max=3)
         │                                                    │
         ▼                                                    ▼
   RDS PostgreSQL 15                              S3 (medical files)
   (Multi-AZ, encrypted)                          (SSE-KMS, versioned)
         │
         ▼
   AWS Lambda (appointment_reminder) ── EventBridge cron (15 min) ── SNS topic
                                                                       │
                                                                       ▼
                                                                 Email / SMS

Cross-cutting: VPC · IAM · KMS · CloudTrail · CloudWatch Logs + Alarms
```

### What changed between Phase 1 and Phase 2

| Concern         | Phase 1 (local)                    | Phase 2 (AWS)                                                |
|-----------------|------------------------------------|--------------------------------------------------------------|
| Compute         | `uvicorn` on localhost             | EC2 ASG (min 1, max 3) behind ALB, CPU target tracking 60%   |
| Database        | SQLite file                        | RDS PostgreSQL 15 Multi-AZ, KMS-encrypted, in private subnet |
| File storage    | `./uploads/` on disk               | S3 bucket, SSE-KMS, versioned, 7-year HIPAA lifecycle        |
| Notifications   | (none)                             | Lambda (every 15 min) → SNS → email/SMS                      |
| Logging         | Plain text → stdout                | JSON → CloudWatch Logs (`/aws/ec2/healthdms`)               |
| Auth            | JWT (app-level)                    | JWT + IAM (cloud-level), IMDSv2-only EC2                    |
| Audit           | (none)                             | CloudTrail (multi-region, KMS-encrypted, log file validation)|
| Alerts          | (none)                             | CloudWatch alarms for ALB 5xx and ASG CPU > 80%             |

### Pluggable storage — switch backends with one env var

```bash
# Local (Phase 1 default)
export STORAGE_BACKEND=local

# S3 (Phase 2)
export STORAGE_BACKEND=s3
export S3_BUCKET=healthdms-dev-files-abc123
export S3_KMS_KEY_ID=arn:aws:kms:ap-south-1:123456789012:key/...
export AWS_REGION=ap-south-1
```

The same goes for the database — set `DATABASE_URL=postgresql+psycopg2://...` to switch from SQLite to RDS.

### One-command AWS deployment

```bash
cd infra/terraform
terraform init
terraform apply -auto-approve \
  -var "db_password=<strong password>" \
  -var "key_pair_name=<your EC2 key>" \
  -var "alarm_email=you@example.com"

# After ~12 minutes:
terraform output alb_url    # → http://healthdms-dev-alb-xxx.elb.amazonaws.com/dashboard

# Tear down to stop AWS billing
terraform destroy -auto-approve -var "db_password=<same>" -var "key_pair_name=<same>"
```

See [infra/terraform/README.md](infra/terraform/README.md) for the full IaC walk-through, cost estimate, and production-hardening notes.

### Container deployment (alternative)

```bash
docker build -t healthdms .
docker run --rm -p 8000:8000 \
  -e STORAGE_BACKEND=local \
  -e DATABASE_URL=sqlite:///./health_dms.db \
  healthdms
```

The same image runs on AWS App Runner, ECS Fargate, or any Kubernetes cluster.

### Mapping to Phase 1 Objectives

| Objective | Implementation in Phase 2                                                    |
|-----------|------------------------------------------------------------------------------|
| O1 — Auto-scale to 3× peak     | EC2 ASG min=1/max=3 + TargetTracking on 60% CPU             |
| O2 — Unified data, < 200ms     | Single RDS PostgreSQL Multi-AZ, indexed primary keys        |
| O3 — Security & compliance     | IAM least-privilege, KMS CMK, SSE-KMS S3, CloudTrail, IMDSv2|
| O4 — Serverless analytics      | Lambda + SNS for reminders; structured JSON → CloudWatch    |
| O5 — Cost reduction            | t3.micro instances, single NAT, lifecycle to Glacier        |
| O6 — 99.9% availability        | Multi-AZ RDS, 2-AZ ALB + ASG, ELB health checks             |
