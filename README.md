# Cloud-Native Healthcare Data Management System

**BITS Pilani | Cloud Computing (CSIZG527) | Group 23**

## Repository

- **GitHub**: https://github.com/avanishpsingh/cloud-health-dms
- **Clone**:

  ```bash
  git clone https://github.com/avanishpsingh/cloud-health-dms.git
  ```

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
| POST | `/patients/{id}/records` | Doctor | Add medical record (legacy) |
| POST | `/appointments/{appointment_id}/records` | Admin, Doctor (own) | **GUI-driven**: create medical record with optional file upload, directly from the appointments view |
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
├── tests/                   # Pytest test suite (30 tests)
│   ├── conftest.py          # Fixtures (in-memory DB, auth tokens)
│   ├── test_auth.py         # Auth tests (6)
│   ├── test_patients.py     # Patient tests (7)
│   ├── test_appointments.py # Appointment tests (4)
│   ├── test_storage.py      # Phase 2 storage backend tests (4, skipped without moto)
│   ├── test_lambda_reminder.py    # Phase 2 Lambda tests (3)
│   ├── test_logging_middleware.py # Phase 2 JSON logging tests (3)
│   ├── test_upload_e2e.py   # Phase 2 upload E2E tests (4)
│   └── test_medical_records_gui_flow.py # Phase 2 GUI Add Record tests (2)
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
python -m pytest tests/ -v    # 30 tests (28 pass + 2 skipped without moto)
```

Tests use an in-memory SQLite database (isolated from production data).
Phase 2 storage tests use [`moto`](https://github.com/getmoto/moto) to mock S3,
so no AWS credentials are required to run them. If `moto` is not installed,
those 2 tests are auto-skipped (the rest still pass).

| Suite                                | Tests | Covers                                                        |
|--------------------------------------|------:|---------------------------------------------------------------|
| `test_auth.py`                       | 6     | Login, JWT, RBAC                                              |
| `test_patients.py`                   | 7     | Patient CRUD                                                  |
| `test_appointments.py`               | 4     | Appointment lifecycle                                         |
| `test_storage.py`                    | 4     | LocalStorage + S3Storage round trips (skipped w/o moto)       |
| `test_lambda_reminder.py`            | 3     | Window filter, dry-run, SNS publish                           |
| `test_logging_middleware.py`         | 3     | JSON formatter, request ID, idempotent configure              |
| `test_upload_e2e.py`                 | 4     | End-to-end medical-file upload via the storage abstraction    |
| `test_medical_records_gui_flow.py`   | 2     | New Phase 2 GUI flow — add medical record from appointment row, role-based guard |

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

### Step-by-step AWS deployment

The entire stack is provisioned by Terraform under `infra/terraform/` (~600 LOC, 10 `.tf` files). Follow the steps below to host the app on AWS and launch it.

#### 1. Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| AWS CLI | 2.x | https://aws.amazon.com/cli/ |
| Terraform | ≥ 1.5 | https://developer.hashicorp.com/terraform/downloads |
| AWS account | — | Free-tier eligible; needs permissions for VPC, EC2, RDS, S3, IAM, KMS, Lambda, CloudWatch, CloudTrail, SNS |
| EC2 key pair | — | Create in **EC2 → Key Pairs** in the chosen region (default: `ap-south-1`) — used for SSH into instances |

#### 2. Configure AWS credentials

```bash
aws configure
# AWS Access Key ID:     <your key>
# AWS Secret Access Key: <your secret>
# Default region name:   ap-south-1
# Default output format: json

aws sts get-caller-identity     # verify credentials work
```

#### 3. Initialise Terraform

```bash
cd cloud-health-dms/infra/terraform
terraform init                  # downloads AWS + random providers
terraform validate              # syntax check
terraform plan \
  -var "db_password=ChangeMe_Strong#2026" \
  -var "key_pair_name=my-ec2-key" \
  -var "alarm_email=you@example.com"
```

Required variables:

| Variable | Example | Notes |
|----------|---------|-------|
| `db_password` | `ChangeMe_Strong#2026` | RDS master password (≥ 8 chars, no `/`, `@`, `"`, spaces) |
| `key_pair_name` | `my-ec2-key` | Existing EC2 key pair name in the target region |
| `alarm_email` | `you@example.com` | Receives CloudWatch alarms via SNS (confirm subscription email) |

Optional overrides (defaults in `variables.tf`): `aws_region` (`ap-south-1`), `project_name` (`healthdms`), `environment` (`dev`), `instance_type` (`t3.micro`), `db_instance_class` (`db.t3.micro`).

#### 4. Apply (provision the stack)

```bash
terraform apply -auto-approve \
  -var "db_password=ChangeMe_Strong#2026" \
  -var "key_pair_name=my-ec2-key" \
  -var "alarm_email=you@example.com"
```

Provisioning takes **~12–15 minutes** (RDS Multi-AZ is the long pole). Resources created:

- VPC (10.0.0.0/16) with 2 public + 2 private subnets across 2 AZs, IGW, single NAT
- Application Load Balancer (public) + target group + HTTP listener on :80
- EC2 launch template (Amazon Linux 2023, IMDSv2-only) + Auto Scaling Group (min 1, max 3, desired 1) with CPU target tracking @ 60 %
- RDS PostgreSQL 15 Multi-AZ, KMS-encrypted, in private subnet, security group allows only the EC2 SG
- S3 bucket for medical files: SSE-KMS, versioning on, public access blocked, 7-year HIPAA lifecycle (→ Glacier after 90 days)
- KMS Customer Managed Key with rotation enabled (used by RDS, S3, CloudTrail)
- Lambda function `appointment_reminder` (Python 3.11) + EventBridge cron (every 15 min) + SNS topic
- CloudTrail (multi-region, KMS-encrypted, log-file validation) → dedicated S3 bucket
- CloudWatch log groups (`/aws/ec2/healthdms`, `/aws/lambda/...`) and alarms (ALB 5xx > 5/min, ASG CPU > 80 %)

#### 5. Launch & verify the app

```bash
terraform output                         # full output map
terraform output -raw alb_dns_name       # e.g. healthdms-dev-alb-12345.ap-south-1.elb.amazonaws.com
terraform output -raw alb_url            # full URL

# Wait ~2 minutes after apply finishes for the EC2 user-data script to:
#   1. install Python + dependencies
#   2. fetch the app code
#   3. run database migrations
#   4. start uvicorn under systemd (port 8000, behind ALB on :80)

# Health check
curl http://$(terraform output -raw alb_dns_name)/

# Open the dashboard in a browser:
#   http://<alb_dns_name>/dashboard
#   default login: admin / admin123
```

The EC2 user-data script (`infra/terraform/user_data.sh`) wires the app to AWS by exporting:

```
STORAGE_BACKEND=s3
S3_BUCKET=<from terraform output>
S3_KMS_KEY_ID=<from terraform output>
DATABASE_URL=postgresql+psycopg2://<user>:<pwd>@<rds-endpoint>:5432/healthdms
AWS_REGION=ap-south-1
```

These are read by `app/config.py`, so the same FastAPI code that ran on SQLite/local in Phase 1 now reads/writes to RDS and S3 with no source changes.

#### 6. Post-deploy checks

```bash
# Confirm ASG instance is healthy in the target group
aws elbv2 describe-target-health \
  --target-group-arn $(terraform output -raw target_group_arn) --region ap-south-1

# Tail application logs
aws logs tail /aws/ec2/healthdms --since 10m --follow --region ap-south-1

# Trigger reminder Lambda manually (instead of waiting for the 15-min cron)
aws lambda invoke --function-name healthdms-dev-appointment-reminder \
  --region ap-south-1 /tmp/out.json && cat /tmp/out.json

# Confirm the SNS subscription email — open the link in the message AWS sent
#   you on apply (otherwise alarms won't email you)
```

#### 7. Common troubleshooting

| Symptom | Likely cause / fix |
|---------|--------------------|
| ALB returns `502 Bad Gateway` for 2–3 min | EC2 user-data still installing — wait, then retry |
| ALB returns `502` after 5+ min | SSH into instance (`ec2-user@<private-ip>` via bastion or SSM Session Manager), check `journalctl -u healthdms -n 100` |
| `terraform apply` fails on RDS | Password contains forbidden chars (`/ @ " space`) or is too short |
| Lambda `AccessDenied` to SNS | KMS key policy not yet replicated — re-run `terraform apply` |
| No alarm emails | SNS subscription not confirmed — check inbox / spam for AWS confirmation link |

#### 8. Tear down (stop AWS billing)

```bash
cd cloud-health-dms/infra/terraform
terraform destroy -auto-approve \
  -var "db_password=ChangeMe_Strong#2026" \
  -var "key_pair_name=my-ec2-key" \
  -var "alarm_email=you@example.com"
```

Destroy takes ~8–10 minutes (RDS deletion is the long pole). After it completes, verify in the AWS Console that VPC, RDS, ALB, ASG, S3 buckets, and KMS keys are gone (KMS keys enter a 7-day pending-deletion window — that's expected).

> **Cost note**: with the defaults (t3.micro EC2, db.t3.micro RDS Multi-AZ, single NAT, ap-south-1) the stack costs roughly **₹250–350 / day** if left running. Always `terraform destroy` after demos.

See [infra/terraform/README.md](infra/terraform/README.md) for the full IaC walk-through, module reference, cost breakdown, and production-hardening notes.

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
