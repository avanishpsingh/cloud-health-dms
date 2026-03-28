# Project Structure

```
cloud-health-dms/
├── .gitignore
├── README.md
├── WorkFlow.md
├── requirements.txt
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
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration (DB URL, secrets)
│   ├── database.py          # SQLAlchemy engine & session
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── patient.py
│   │   ├── doctor.py
│   │   ├── appointment.py
│   │   └── medical_record.py
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── patient.py
│   │   ├── doctor.py
│   │   ├── appointment.py
│   │   └── medical_record.py
│   ├── routers/             # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── patients.py
│   │   ├── doctors.py
│   │   ├── appointments.py
│   │   ├── records.py
│   │   └── analytics.py
│   ├── services/            # Business logic
│   │   └── auth.py
│   └── middleware/          # Auth middleware
│       └── auth.py
│
├── uploads/                 # Local file storage (Phase 1)
│   └── .gitkeep
│
└── tests/                   # Test suite
    ├── __init__.py
    ├── test_auth.py
    ├── test_patients.py
    └── test_appointments.py
```

## Key Design Decisions

1. **FastAPI over Flask** — Auto-generated Swagger docs (great for demo), async support, Pydantic validation built-in
2. **SQLAlchemy ORM** — Database-agnostic; switching from SQLite to PostgreSQL is a config change (critical for Phase 1 → Phase 2 migration)
3. **Flat module structure** — Minimal nesting; this is a small assignment, not a microservices project
4. **Local file storage** — `uploads/` directory in Phase 1, replaced by S3 boto3 calls in Phase 2
5. **SQLite** — Zero-config database for Phase 1; no server setup needed
