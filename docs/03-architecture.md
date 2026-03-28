# Architecture Design

## Phase 1 — Local Architecture

```
┌─────────────────────────────────────────────────┐
│                   Client Layer                   │
│         (Browser / Postman / Streamlit)          │
└─────────────────────┬───────────────────────────┘
                      │ HTTP (localhost:8000)
┌─────────────────────▼───────────────────────────┐
│               FastAPI Application                │
│  ┌───────────┬──────────┬──────────┬──────────┐ │
│  │  Auth     │ Patient  │ Doctor   │ Appoint- │ │
│  │  Module   │ Module   │ Module   │ ment Mod │ │
│  ├───────────┼──────────┼──────────┼──────────┤ │
│  │  Medical  │ Analytics│ File     │          │ │
│  │  Records  │ Module   │ Upload   │          │ │
│  └───────────┴──────────┴──────────┴──────────┘ │
│                    │                             │
│           SQLAlchemy ORM Layer                   │
└─────────────────────┬───────────────────────────┘
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
    ┌─────────┐ ┌──────────┐ ┌──────────┐
    │ SQLite  │ │  Local   │ │  Logs    │
    │   DB    │ │  Files   │ │ (stdout) │
    └─────────┘ └──────────┘ └──────────┘
```

## Phase 2 — AWS Cloud Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Internet / Users                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                   ┌────────▼────────┐
                   │   Route 53      │
                   │   (DNS)         │
                   └────────┬────────┘
                            │
                   ┌────────▼────────┐
                   │   ALB (Load     │
                   │   Balancer)     │
                   └────────┬────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  EC2     │ │  EC2     │ │  EC2     │
        │ (App 1)  │ │ (App 2)  │ │ (App N)  │
        └────┬─────┘ └────┬─────┘ └────┬─────┘
             │             │             │
             └──────┬──────┘─────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
  ┌──────────┐ ┌─────────┐ ┌──────────┐
  │ RDS      │ │   S3    │ │ Lambda   │
  │ PostgreSQL│ │ Bucket  │ │ Function │
  │ (Multi-AZ)│ │ (Files) │ │ (Events) │
  └──────────┘ └─────────┘ └──────────┘

Cross-Cutting: IAM | KMS | CloudTrail | CloudWatch | VPC | WAF
```

## Technology Stack

### Phase 1 (Local)
| Component | Technology | Justification |
|-----------|-----------|---------------|
| Language | Python 3.11+ | Team familiarity, rich ecosystem |
| Web Framework | FastAPI | Async, auto-docs (Swagger), fast for APIs |
| ORM | SQLAlchemy | DB-agnostic, easy migration to PostgreSQL |
| Database | SQLite | Zero setup, file-based, perfect for local dev |
| Auth | python-jose (JWT) + passlib (bcrypt) | Standard JWT auth |
| File Storage | Local filesystem (`uploads/`) | Simple, migrates to S3 |
| Testing | pytest | Standard Python testing |
| Frontend (optional) | Streamlit or plain HTML | Quick dashboard for demo |

### Phase 2 (AWS)
| Component | AWS Service | Purpose |
|-----------|------------|---------|
| Compute | EC2 + Auto Scaling Group | Run FastAPI app, auto-scale |
| Database | RDS PostgreSQL (Multi-AZ) | Relational patient data |
| File Storage | S3 | Medical reports, images |
| Serverless | Lambda | Event-driven tasks (e.g., notifications) |
| Load Balancer | Application Load Balancer | Distribute traffic |
| DNS | Route 53 | Domain routing (optional) |
| Auth/IAM | IAM | Role-based cloud access |
| Encryption | KMS | Encrypt data at rest |
| Monitoring | CloudWatch | Metrics, alarms, dashboards |
| Audit | CloudTrail | API call logging |
| Analytics | Athena | Query S3 data (optional) |
| Alerts | SNS | Notifications |

## Database Schema (Minimal)

```
Users
├── id (PK)
├── username (unique)
├── password_hash
├── role (admin/doctor/receptionist)
└── created_at

Patients
├── id (PK)
├── name
├── age
├── gender
├── contact
├── address
├── blood_group
├── created_at
└── is_active (soft delete)

Doctors
├── id (PK)
├── user_id (FK → Users, nullable)
├── name
├── specialization
├── department
├── contact
└── created_at

Appointments
├── id (PK)
├── patient_id (FK → Patients)
├── doctor_id (FK → Doctors)
├── date_time
├── reason
├── status (scheduled/completed/cancelled)
└── created_at

MedicalRecords
├── id (PK)
├── patient_id (FK → Patients)
├── doctor_id (FK → Doctors)
├── diagnosis
├── prescription
├── notes
├── file_path (local path / S3 key)
└── created_at
```

## API Endpoints (Minimal)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/login` | Login, get JWT token | Public |
| POST | `/auth/register` | Register user (admin only) | Admin |
| GET | `/patients` | List patients | All roles |
| POST | `/patients` | Create patient | Admin, Receptionist |
| GET | `/patients/{id}` | Get patient details | All roles |
| PUT | `/patients/{id}` | Update patient | Admin, Receptionist |
| DELETE | `/patients/{id}` | Soft-delete patient | Admin |
| GET | `/doctors` | List doctors | All roles |
| POST | `/doctors` | Create doctor | Admin |
| GET | `/appointments` | List appointments | All roles |
| POST | `/appointments` | Book appointment | Admin, Receptionist |
| PATCH | `/appointments/{id}` | Update status | Doctor, Admin |
| GET | `/patients/{id}/records` | Get medical history | Doctor, Admin |
| POST | `/patients/{id}/records` | Add medical record | Doctor |
| POST | `/upload` | Upload medical file | Doctor |
| GET | `/analytics/summary` | Dashboard stats | Admin |
