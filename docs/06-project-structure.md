# Project Structure

```
cloud-health-dms/
├── .gitignore
├── README.md
├── WorkFlow.md
├── requirements.txt
├── health_dms.db            # SQLite database (pre-seeded, tracked in git)
│
├── assignmentQuestion/
│   └── CloudComputing-Assignment_Rubrics.pdf
│
├── Cloud_Phase1_PPTs/
│   └── Cloud Phase_1_260320_172940.pdf
│
├── tasks/
│   ├── todo.md              # Task tracking
│   └── lessons.md           # Lessons learned
│
├── docs/
│   ├── 01-project-overview.md
│   ├── 02-requirements.md
│   ├── 03-architecture.md
│   ├── 04-aws-service-mapping.md
│   ├── 05-security-compliance.md
│   ├── 06-project-structure.md    (this file)
│   └── 07-development-guide.md
│
├── app/                     # Main application
│   ├── __init__.py
│   ├── main.py              # FastAPI app, CORS, router registration
│   ├── config.py            # Settings (DB URL, JWT secret, upload config)
│   ├── database.py          # SQLAlchemy engine, session, base
│   ├── auth.py              # Password hashing, JWT, RBAC decorators
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py          # User (username, password_hash, full_name, role)
│   │   ├── patient.py       # Patient (name, age, gender, contact, blood_group, is_active)
│   │   ├── doctor.py        # Doctor (name, specialization, department, contact, user_id)
│   │   ├── appointment.py   # Appointment (patient_id, doctor_id, date_time, reason, status)
│   │   └── medical_record.py # MedicalRecord (patient_id, doctor_id, diagnosis, prescription, notes, file_path)
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── user.py          # UserCreate, UserOut, Token, LoginRequest
│   │   ├── patient.py       # PatientCreate, PatientUpdate, PatientOut
│   │   ├── doctor.py        # DoctorCreate, DoctorUpdate, DoctorOut
│   │   ├── appointment.py   # AppointmentCreate, AppointmentUpdate, AppointmentOut
│   │   └── medical_record.py # MedicalRecordCreate, MedicalRecordOut
│   └── routers/             # API route handlers (22 endpoints total)
│       ├── __init__.py
│       ├── auth.py          # Login, register, list users, current user
│       ├── patients.py      # Patient CRUD (create, read, update, soft-delete)
│       ├── doctors.py       # Doctor CRUD (create, read, update, delete)
│       ├── appointments.py  # Appointment CRUD (create, list, update status, delete)
│       ├── records.py       # Medical records & file upload
│       ├── analytics.py     # Summary statistics (admin only)
│       └── dashboard.py     # Interactive HTML dashboard SPA
│
├── scripts/
│   └── seed.py              # Generate sample data (100 patients, 10 doctors, ~259 appointments)
│
├── uploads/                 # Local file storage for medical reports (Phase 1)
│   └── .gitkeep
│
└── tests/                   # Pytest test suite (17 tests)
    ├── __init__.py
    ├── conftest.py          # Test fixtures (in-memory DB, auth tokens)
    ├── test_auth.py         # 6 auth tests
    ├── test_patients.py     # 7 patient tests
    └── test_appointments.py # 4 appointment tests
```

## Key Design Decisions

1. **FastAPI over Flask** — Auto-generated Swagger docs (great for demo), async support, Pydantic validation built-in
2. **SQLAlchemy ORM** — Database-agnostic; switching from SQLite to PostgreSQL is a config change (critical for Phase 1 → Phase 2 migration)
3. **Flat module structure** — Minimal nesting; this is a small assignment, not a microservices project
4. **Single-page dashboard** — Entire HTML/CSS/JS served as one response from FastAPI (no frontend build tools needed)
5. **Local file storage** — `uploads/` directory in Phase 1, replaced by S3 boto3 calls in Phase 2
6. **SQLite** — Zero-config database for Phase 1; no server setup needed
7. **Pre-seeded DB in git** — `health_dms.db` is tracked so anyone cloning the repo can immediately test
