# Module 08: Project Architecture — How Everything Fits Together

> **Time**: ~2 hours | **Prerequisites**: Modules 01-07

---

## Why This Module

This module ties everything together. After learning individual technologies, you need to see **how they interconnect**. This is what your professor will ask about in the viva.

---

## 8.1 Complete Request Lifecycle

Let's trace a single request through the entire system:

### Example: `POST /patients/` (Create a Patient)

```
Client sends:
POST http://localhost:8000/patients/
Headers: Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
Body: {"name": "Priya Sharma", "age": 28, "gender": "Female", "contact": "9876543210"}
```

**Step-by-step execution:**

```
1. UVICORN receives HTTP request
   └── passes to FastAPI app (app/main.py)

2. FASTAPI ROUTER MATCHING
   └── matches POST /patients/ → app/routers/patients.py::create_patient()

3. DEPENDENCY RESOLUTION (before the function runs)
   │
   ├── Depends(require_roles("admin", "receptionist"))
   │   │
   │   └── Depends(get_current_user)
   │       │
   │       ├── Depends(security)          → extracts "eyJhbG..." from header
   │       │
   │       ├── Depends(get_db)            → creates DB session #1
   │       │
   │       ├── jwt.decode(token)          → {"sub": "admin", "role": "admin"}
   │       │
   │       └── db.query(User).filter(username="admin") → User object
   │
   │   └── checks: "admin" in ("admin", "receptionist") → ✅ passes
   │
   ├── body: PatientCreate               → Pydantic validates the JSON body
   │   {"name": "Priya", "age": 28, ...} → ✅ all fields valid
   │
   └── Depends(get_db)                   → creates DB session #2

4. FUNCTION EXECUTION
   │
   ├── Patient(**body.model_dump())       → creates ORM object
   ├── db.add(patient)                    → stages for INSERT
   ├── db.commit()                        → writes to SQLite
   ├── db.refresh(patient)                → gets auto-generated id, created_at
   └── return patient                     → ORM object

5. RESPONSE SERIALIZATION
   │
   ├── response_model=PatientOut          → Pydantic converts ORM → JSON
   └── status_code=201                    → HTTP 201 Created

6. CLEANUP
   │
   └── get_db() finally block             → db.close() (both sessions)

7. RESPONSE SENT
   HTTP 201 Created
   {"id": 101, "name": "Priya Sharma", "age": 28, "gender": "Female",
    "contact": "9876543210", "address": "", "blood_group": "", "is_active": true}
```

---

## 8.2 Layered Architecture

```
┌─────────────────────────────────────────┐
│            PRESENTATION LAYER           │
│      (app/routers/*.py + dashboard.py)  │
│  Handles HTTP requests, calls services  │
├─────────────────────────────────────────┤
│            BUSINESS LOGIC LAYER         │
│             (app/auth.py)               │
│  Authentication, authorization, rules   │
├─────────────────────────────────────────┤
│          DATA VALIDATION LAYER          │
│           (app/schemas/*.py)            │
│   Pydantic models, input/output shapes  │
├─────────────────────────────────────────┤
│            DATA ACCESS LAYER            │
│     (app/models/*.py + database.py)     │
│   SQLAlchemy ORM, database operations   │
├─────────────────────────────────────────┤
│             STORAGE LAYER               │
│      (SQLite file + uploads/ dir)       │
│   Physical data storage                 │
└─────────────────────────────────────────┘
```

### Why this separation matters:
- **Routers** don't know about SQL — they use ORM objects
- **Schemas** don't know about the database — they only define shapes
- **Models** don't know about HTTP — they only define tables
- **Auth** is independent — injected via `Depends()`
- **Config** is centralized — one file, one `settings` object

---

## 8.3 File-by-File Map

### Configuration Layer
| File | Purpose | Key Objects |
|------|---------|------------|
| `app/config.py` | All settings | `Settings` class, `settings` singleton |
| `app/database.py` | DB connection | `engine`, `SessionLocal`, `Base`, `get_db()` |

### Auth Layer
| File | Purpose | Key Functions |
|------|---------|--------------|
| `app/auth.py` | All auth logic | `hash_password()`, `verify_password()`, `create_access_token()`, `get_current_user()`, `require_roles()` |

### Data Layer (Models)
| File | Table | Key Columns |
|------|-------|------------|
| `app/models/user.py` | `users` | id, username, password_hash, role |
| `app/models/patient.py` | `patients` | id, name, age, gender, contact, is_active |
| `app/models/doctor.py` | `doctors` | id, user_id (FK), name, specialization |
| `app/models/appointment.py` | `appointments` | id, patient_id (FK), doctor_id (FK), status |
| `app/models/medical_record.py` | `medical_records` | id, patient_id, doctor_id, diagnosis, file_path |

### Validation Layer (Schemas)
| File | Schemas | Purpose |
|------|---------|---------|
| `app/schemas/user.py` | UserCreate, UserOut, Token, LoginRequest | Auth I/O |
| `app/schemas/patient.py` | PatientCreate, PatientUpdate, PatientOut | Patient CRUD I/O |
| `app/schemas/doctor.py` | DoctorCreate, DoctorUpdate, DoctorOut | Doctor CRUD I/O |
| `app/schemas/appointment.py` | AppointmentCreate, AppointmentUpdate, AppointmentOut | Appointment I/O |
| `app/schemas/medical_record.py` | MedicalRecordCreate, MedicalRecordOut | Medical record I/O |

### Presentation Layer (Routers)
| File | Prefix | Endpoints | Auth Required |
|------|--------|-----------|---------------|
| `app/routers/auth.py` | `/auth` | login, register, users, me | Mixed |
| `app/routers/patients.py` | `/patients` | CRUD (5 endpoints) | All roles |
| `app/routers/doctors.py` | `/doctors` | CRUD (5 endpoints) | All roles |
| `app/routers/appointments.py` | `/appointments` | CRUD (4 endpoints) | All roles |
| `app/routers/records.py` | (multiple) | records + upload (3 endpoints) | Doctor/Admin |
| `app/routers/analytics.py` | `/analytics` | summary (1 endpoint) | Admin only |
| `app/routers/dashboard.py` | `/dashboard` | HTML SPA (1 endpoint) | None (client-side auth) |

### App Entry Point
| File | Purpose |
|------|---------|
| `app/main.py` | Creates FastAPI app, registers middleware and routers |
| `app/__init__.py` | Makes `app/` a Python package |

---

## 8.4 Data Flow Diagram

```
                    ┌──────────────┐
                    │   Browser    │
                    │  /dashboard  │
                    └──────┬───────┘
                           │ JSON API calls
                           ▼
                    ┌──────────────┐
                    │   FastAPI    │
                    │   main.py    │
                    └──────┬───────┘
                           │ routes to...
          ┌────────┬───────┼────────┬──────────┐
          ▼        ▼       ▼        ▼          ▼
      ┌────────┐┌───────┐┌────────┐┌──────┐┌─────────┐
      │  auth  ││patient││ doctor ││appt  ││ records │
      │ router ││router ││ router ││router││ router  │
      └───┬────┘└──┬────┘└──┬─────┘└──┬───┘└──┬──────┘
          │        │        │         │        │
          │   ┌────┴────────┴─────────┴────┐   │
          │   │    Pydantic Validation    │   │
          │   └────┬────────┬─────────┬────┘   │
          │        │        │         │        │
          ▼        ▼        ▼         ▼        ▼
      ┌────────────────────────────────────────────┐
      │          SQLAlchemy ORM Layer              │
      │  User | Patient | Doctor | Appt | Record   │
      └──────────────────┬─────────────────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │   SQLite DB  │
                  │ health_dms.db│
                  └──────────────┘
```

---

## 8.5 Key Design Decisions Explained

### 1. Why FastAPI over Flask?
- Auto-generates Swagger docs (great for academic demo)
- Built-in Pydantic validation (less boilerplate)
- Async support (better performance)
- Type hints throughout (self-documenting)

### 2. Why SQLAlchemy ORM?
- **Database-agnostic**: SQLite → PostgreSQL is a ONE-LINE config change
- This is the entire Phase 1 → Phase 2 migration strategy

### 3. Why separate schemas and models?
- **Security**: `UserOut` hides `password_hash` from the API
- **Flexibility**: `PatientCreate` has different fields than `PatientOut`
- **Validation**: Pydantic enforces types; SQLAlchemy handles DB constraints

### 4. Why soft delete for patients?
- Medical records are linked to patients via foreign keys
- Hard-deleting a patient would break those references
- Soft delete keeps data integrity while hiding the patient from the UI

### 5. Why a single-page HTML dashboard?
- No frontend build tools needed (no React, no npm)
- Entire UI served as one FastAPI response
- Perfect for academic demo

### 6. Why JWT for authentication?
- **Stateless**: server doesn't need to store sessions
- **Scalable**: works across multiple EC2 instances (Phase 2)
- **Standard**: widely used, well-documented

---

## 8.6 Viva-Ready Q&A

**Q: How does a request flow through the system?**
A: Client → Uvicorn → FastAPI → Router → Dependencies (auth + DB) → Function → Pydantic serialization → Response

**Q: How do you ensure data security?**
A: Passwords are bcrypt-hashed, API uses JWT tokens, RBAC on all endpoints, Pydantic validates input, ORM prevents SQL injection, file uploads are validated.

**Q: How does the Phase 1 → Phase 2 migration work?**
A: SQLAlchemy abstracts the DB, so we change the connection string from SQLite to PostgreSQL. File uploads change from local filesystem to S3 via boto3. The app deploys on EC2 behind ALB.

**Q: What makes this "cloud-native"?**
A: Stateless design (no server sessions), 12-factor app config (env vars), DB-agnostic ORM, horizontally scalable (multiple EC2 instances), designed for managed services (RDS, S3).

---

## ✏️ Exercise

Trace the complete lifecycle for `DELETE /patients/5`:
1. What router handles it?
2. What dependencies run?
3. What query is executed?
4. Is it a hard or soft delete?
5. What status code is returned?
6. What happens to appointments linked to this patient?
