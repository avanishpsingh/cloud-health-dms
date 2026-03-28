# Cloud-Native Healthcare Data Management System

**BITS Pilani | Cloud Computing (CSIZG527) | Group 23**

## Overview

A cloud-native healthcare data management system designed for a mid-size hospital chain in India. Built in two phases: a working local application (Phase 1) migrated to AWS cloud infrastructure (Phase 2).

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
│   └── test_appointments.py # Appointment tests (4)
├── docs/                    # Detailed project documentation
├── uploads/                 # Medical file uploads directory
├── health_dms.db            # SQLite database (pre-seeded for testing)
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
python -m pytest tests/ -v    # 17 tests
```

Tests use an in-memory SQLite database (isolated from production data).

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
