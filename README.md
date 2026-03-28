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
- **Backend**: Python, FastAPI, SQLAlchemy
- **Database**: SQLite (Phase 1) → RDS PostgreSQL (Phase 2)
- **Storage**: Local filesystem (Phase 1) → S3 (Phase 2)
- **Cloud**: AWS (EC2, RDS, S3, Lambda, IAM, KMS, CloudWatch, CloudTrail)

## Quick Start (Phase 1)
```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python scripts/seed.py       # Seed sample data
uvicorn app.main:app --reload
```
API docs at: http://localhost:8000/docs

### Default Logins (after seeding)
| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin |
| dr_sharma | doctor123 | Doctor |
| reception1 | recep123 | Receptionist |

## API Endpoints (16 endpoints)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/auth/login` | Login (returns JWT) |
| POST | `/auth/register` | Register user (admin only) |
| GET | `/auth/me` | Current user info |
| GET/POST | `/patients/` | List / Create patients |
| GET/PUT/DELETE | `/patients/{id}` | Get / Update / Delete patient |
| GET/POST | `/doctors/` | List / Create doctors |
| GET | `/doctors/{id}` | Get doctor |
| GET/POST | `/appointments/` | List / Create appointments |
| PATCH | `/appointments/{id}` | Update appointment status |
| GET | `/patients/{id}/records` | Get medical history |
| POST | `/patients/{id}/records` | Add medical record |
| POST | `/upload/{record_id}` | Upload medical file |
| GET | `/analytics/summary` | Dashboard stats |

## Tests
```bash
python -m pytest tests/ -v    # 17 tests
```

## Documentation
See [docs/](docs/) for detailed documentation:
- [Project Overview](docs/01-project-overview.md)
- [Requirements](docs/02-requirements.md)
- [Architecture](docs/03-architecture.md)
- [AWS Service Mapping](docs/04-aws-service-mapping.md)
- [Security & Compliance](docs/05-security-compliance.md)
- [Project Structure](docs/06-project-structure.md)
- [Development Guide](docs/07-development-guide.md)
