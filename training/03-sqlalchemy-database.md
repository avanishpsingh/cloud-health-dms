# Module 03: SQLAlchemy & Database

> **Time**: ~3 hours | **Prerequisites**: Module 01, basic SQL knowledge

---

## Why This Module

SQLAlchemy is the **data layer** of this project. Every patient record, doctor profile, appointment, and medical record lives in a database managed through SQLAlchemy's ORM. Understanding this means understanding how data flows in and out.

---

## 3.1 What is an ORM?

**ORM = Object-Relational Mapping**

Instead of writing raw SQL:
```sql
INSERT INTO patients (name, age, gender) VALUES ('Priya', 28, 'Female');
```

You write Python:
```python
patient = Patient(name="Priya", age=28, gender="Female")
db.add(patient)
db.commit()
```

The ORM translates Python objects ↔ SQL queries automatically.

### 📚 Resources
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/) — Official tutorial (SQLAlchemy 2.0)
- [Real Python — SQLAlchemy Guide](https://realpython.com/python-sqlite-sqlalchemy/)

---

## 3.2 Engine, Session, and Base

### How This Project Sets It Up

```python
# app/database.py — 26 lines that set up the entire data layer

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# 1. ENGINE — the connection to the database
engine = create_engine(
    "sqlite:///./health_dms.db",      # SQLite file database
    connect_args={"check_same_thread": False}  # SQLite-specific workaround
)

# 2. SESSION FACTORY — creates database sessions
SessionLocal = sessionmaker(
    autocommit=False,    # we manually call db.commit()
    autoflush=False,     # we control when data syncs
    bind=engine          # attached to our engine
)

# 3. BASE CLASS — all models inherit from this
class Base(DeclarativeBase):
    pass

# 4. DEPENDENCY — provides a session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Mental Model
```
Engine (connection) → SessionLocal (factory) → db session (per request)
                                                    │
                                           Base (model definitions)
                                           ├── User
                                           ├── Patient
                                           ├── Doctor
                                           ├── Appointment
                                           └── MedicalRecord
```

### 📚 Resources
- [Engine Configuration](https://docs.sqlalchemy.org/en/20/core/engines.html)
- [Session Basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)

---

## 3.3 Defining Models (Tables)

Each model = one database table. Let's trace every model in this project:

### User Model
```python
# app/models/user.py
class User(Base):
    __tablename__ = "users"                           # table name in SQL

    id = Column(Integer, primary_key=True, index=True)  # auto-increment PK
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default="receptionist")
    created_at = Column(DateTime, server_default=func.now())
```

**Key column options:**
| Option | Meaning |
|--------|---------|
| `primary_key=True` | This is the unique identifier for each row |
| `unique=True` | No two rows can have the same value |
| `nullable=False` | This field is required (NOT NULL in SQL) |
| `index=True` | Creates a database index for faster lookups |
| `default="receptionist"` | Python-side default value |
| `server_default=func.now()` | Database-side default (SQL `NOW()`) |

### Patient Model — with Soft Delete
```python
# app/models/patient.py
class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)
    contact = Column(String(15), nullable=False)
    address = Column(String(200), default="")
    blood_group = Column(String(5), default="")
    is_active = Column(Boolean, default=True)    # <-- SOFT DELETE flag
    created_at = Column(DateTime, server_default=func.now())
```

**Soft Delete**: Instead of removing a row from the database, we set `is_active = False`. The patient still exists but is "hidden" from queries.

### Doctor Model — with Foreign Key
```python
# app/models/doctor.py
class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # <-- links to User
    name = Column(String(100), nullable=False)
    specialization = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    contact = Column(String(15), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
```

**Foreign Key**: `ForeignKey("users.id")` means this column references the `id` column in the `users` table. A doctor *may* have a linked user account (used for login).

### Appointment Model — Two Foreign Keys
```python
# app/models/appointment.py
class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)  # who
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)    # with whom
    date_time = Column(DateTime, nullable=False)
    reason = Column(String(200), default="")
    status = Column(String(20), default="scheduled")  # scheduled/completed/cancelled
    created_at = Column(DateTime, server_default=func.now())
```

### Medical Record Model
```python
# app/models/medical_record.py
class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    diagnosis = Column(String(200), nullable=False)
    prescription = Column(Text, default="")         # Text = unlimited length
    notes = Column(Text, default="")
    file_path = Column(String(300), default="")     # local path or S3 key
    created_at = Column(DateTime, server_default=func.now())
```

### Entity Relationship Diagram
```
Users ──┐
        │ 1:1 (optional)
        ▼
    Doctors ◄─── Appointments ───► Patients
        │              │              │
        │              │              │
        └──── MedicalRecords ─────────┘
```

### 📚 Resources
- [SQLAlchemy Column Types](https://docs.sqlalchemy.org/en/20/core/type_basics.html)
- [Foreign Keys](https://docs.sqlalchemy.org/en/20/core/constraints.html#foreign-key-constraint)

### ✏️ Exercise
1. Look at `app/models/appointment.py`
2. What happens if you try to create an appointment with `patient_id=999` (non-existent)?
3. Check `app/routers/appointments.py` — does it validate this? (Yes! Lines 40-43)

---

## 3.4 CRUD Operations (Create, Read, Update, Delete)

### CREATE
```python
# From app/routers/patients.py
patient = Patient(**body.model_dump())  # create Python object
db.add(patient)                          # stage for insertion
db.commit()                              # write to database
db.refresh(patient)                      # reload with server-generated values (id, created_at)
return patient
```

### READ (Single)
```python
patient = db.query(Patient).filter(
    Patient.id == patient_id,
    Patient.is_active == True     # soft delete filter
).first()                         # returns None if not found
```

### READ (List with Search)
```python
query = db.query(Patient).filter(Patient.is_active == True)
if search:
    query = query.filter(Patient.name.ilike(f"%{search}%"))  # case-insensitive LIKE
return query.order_by(Patient.id.desc()).all()                # newest first
```

### UPDATE
```python
for field, value in body.model_dump(exclude_unset=True).items():
    setattr(patient, field, value)   # only update fields that were sent
db.commit()
db.refresh(patient)
```

**`exclude_unset=True`** is key — it means "only include fields the client actually sent." If they only send `{"name": "New Name"}`, we don't overwrite age, gender, etc.

### DELETE (Soft)
```python
# Patients use soft delete
patient.is_active = False
db.commit()
```

### DELETE (Hard)
```python
# Doctors use hard delete
db.delete(doctor)
db.commit()
```

### 📚 Resources
- [SQLAlchemy Querying Guide](https://docs.sqlalchemy.org/en/20/orm/queryguide/)

---

## 3.5 Table Creation

```python
# app/main.py — creates all tables when the app starts
Base.metadata.create_all(bind=engine)
```

This looks at all classes that inherit from `Base` and creates their tables if they don't exist. It's safe to call multiple times — it won't overwrite existing tables.

---

## 3.6 SQLite → PostgreSQL Migration (Phase 2)

The **entire reason** we use SQLAlchemy is this migration. Change ONE line:

```python
# Phase 1 (local)
DATABASE_URL = "sqlite:///./health_dms.db"

# Phase 2 (AWS RDS)
DATABASE_URL = "postgresql://user:password@rds-endpoint.amazonaws.com/health_dms"
```

SQLAlchemy abstracts the database. Your Python code doesn't change — only the connection string.

### 📚 Resources
- [SQLAlchemy Dialects](https://docs.sqlalchemy.org/en/20/dialects/)

---

## 3.7 Database Seeding

```python
# scripts/seed.py — populates the database with test data
random.seed(42)  # deterministic randomness (same data every time)

# Create users
admin = User(username="admin", password_hash=hash_password("admin123"), ...)
db.add(admin)
db.flush()  # <-- flush sends to DB but doesn't commit (gets the auto-generated ID)

# Create 100 patients in a loop
for i in range(100):
    patient = Patient(name=f"{first} {last}", age=random.randint(5, 85), ...)
    db.add(patient)

db.commit()  # <-- commit saves everything permanently
```

**`flush()` vs `commit()`:**
- `flush()` — sends changes to the DB *temporarily* (you can read auto-generated IDs)
- `commit()` — makes changes permanent

### ✏️ Exercise
1. Delete `health_dms.db`
2. Run `python scripts/seed.py`
3. Verify it created: 3 users, 10 doctors, 100 patients, ~259 appointments, ~104 records

---

## Module Summary

| Concept | Where Used | What It Does |
|---------|-----------|-------------|
| `create_engine()` | `database.py` | Connects to the database |
| `sessionmaker()` | `database.py` | Factory for creating sessions |
| `DeclarativeBase` | `database.py` | Base class for all models |
| `Column()` | All `models/*.py` | Defines table columns |
| `ForeignKey()` | Doctor, Appointment, MedicalRecord | Creates relationships between tables |
| `db.add()` | All routers | Stages an object for insertion |
| `db.commit()` | All routers | Saves changes permanently |
| `db.query().filter()` | All routers | Queries with conditions |
| `db.refresh()` | Create/update endpoints | Reloads server-generated values |
| Soft delete (`is_active`) | Patient model | Deactivates without removing |
