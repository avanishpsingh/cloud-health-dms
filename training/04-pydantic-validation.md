# Module 04: Pydantic & Data Validation

> **Time**: ~2 hours | **Prerequisites**: Module 01

---

## Why This Module

Pydantic is the **gatekeeper** of this project. Every piece of data coming in from the client (JSON request body) and going out to the client (JSON response) passes through Pydantic. It validates data types, enforces constraints, and serializes/deserializes automatically.

---

## 4.1 Pydantic vs SQLAlchemy Models — Key Distinction

This is the **most confusing** part for beginners. This project has TWO types of "models":

| Type | Location | Purpose | Example |
|------|----------|---------|---------|
| **SQLAlchemy Model** | `app/models/*.py` | Defines database tables, talks to DB | `Patient` (ORM) |
| **Pydantic Schema** | `app/schemas/*.py` | Validates API input/output, serializes JSON | `PatientCreate`, `PatientOut` |

**Data Flow:**
```
Client JSON → [Pydantic Schema validates] → [SQLAlchemy Model saves to DB]
                                            ↓
Client JSON ← [Pydantic Schema formats]  ← [SQLAlchemy Model reads from DB]
```

---

## 4.2 Request Schemas (Input Validation)

### PatientCreate — What the Client Sends
```python
# app/schemas/patient.py
from pydantic import BaseModel

class PatientCreate(BaseModel):
    name: str           # REQUIRED — must be a string
    age: int            # REQUIRED — must be an integer
    gender: str         # REQUIRED
    contact: str        # REQUIRED
    address: str = ""   # OPTIONAL — defaults to empty string
    blood_group: str = ""  # OPTIONAL
```

If a client sends:
```json
{"name": "Priya", "age": "twenty", "gender": "Female", "contact": "999"}
```
Pydantic will **reject** it because `age` is `"twenty"` (string, not int), returning:
```json
{
  "detail": [{"msg": "Input should be a valid integer", "type": "int_parsing"}]
}
```

### PatientUpdate — Partial Updates with Optional
```python
class PatientUpdate(BaseModel):
    name: Optional[str] = None      # ALL fields optional
    age: Optional[int] = None
    gender: Optional[str] = None
    contact: Optional[str] = None
    address: Optional[str] = None
    blood_group: Optional[str] = None
```

This lets the client update just one field:
```json
{"name": "Updated Name"}
```
All other fields stay `None` and are excluded by `body.model_dump(exclude_unset=True)`.

### AppointmentCreate — Datetime Handling
```python
class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    date_time: datetime    # Pydantic auto-parses ISO datetime strings
    reason: str = ""
```

The client sends: `"date_time": "2026-04-15T10:30:00"` and Pydantic converts it to a Python `datetime` object automatically.

### LoginRequest — Simple Validation
```python
class LoginRequest(BaseModel):
    username: str
    password: str
```

### 📚 Resources
- [Pydantic V2 Docs](https://docs.pydantic.dev/latest/) — **Official docs**
- [Pydantic Models](https://docs.pydantic.dev/latest/concepts/models/)
- [FastAPI — Body with Pydantic](https://fastapi.tiangolo.com/tutorial/body/)

---

## 4.3 Response Schemas (Output Formatting)

### PatientOut — What the Client Receives
```python
class PatientOut(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    contact: str
    address: str
    blood_group: str
    is_active: bool

    model_config = {"from_attributes": True}  # <-- KEY: allows reading from ORM objects
```

**`model_config = {"from_attributes": True}`** is critical. Without it, Pydantic can't read data from SQLAlchemy objects (which use `patient.name` attribute access, not `patient["name"]` dictionary access).

### UserOut — Hides Sensitive Data
```python
class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    # NOTE: password_hash is NOT here — it's never exposed in the API!

    model_config = {"from_attributes": True}
```

### Token — Authentication Response
```python
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

### 📚 Resources
- [Pydantic — Model Config](https://docs.pydantic.dev/latest/concepts/config/)
- [FastAPI — Response Model](https://fastapi.tiangolo.com/tutorial/response-model/)

---

## 4.4 model_dump() — Converting Between Pydantic and ORM

### Pydantic → Dictionary → ORM
```python
# In create_patient endpoint
body = PatientCreate(name="Priya", age=28, ...)   # Pydantic object

body.model_dump()
# Returns: {"name": "Priya", "age": 28, "gender": "Female", "contact": "999", "address": "", "blood_group": ""}

patient = Patient(**body.model_dump())  # Unpack dict into ORM constructor
```

### model_dump(exclude_unset=True) — For Updates
```python
body = PatientUpdate(name="New Name")   # Only name was sent

body.model_dump()
# Returns: {"name": "New Name", "age": None, "gender": None, ...}  ← WRONG! Would set everything to None

body.model_dump(exclude_unset=True)
# Returns: {"name": "New Name"}  ← CORRECT! Only includes what the client sent
```

---

## 4.5 Pydantic Settings — Configuration Management

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Healthcare DMS"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./health_dms.db"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: set = {".pdf", ".jpg", ".jpeg", ".png"}
    S3_BUCKET: str = ""
    AWS_REGION: str = "ap-south-1"

    model_config = {"env_file": ".env"}  # <-- reads from .env file

settings = Settings()
```

**How settings are resolved (priority order):**
1. Environment variables (highest priority)
2. `.env` file values
3. Default values in the class (lowest priority)

This means for Phase 2, you just set:
```bash
export DATABASE_URL="postgresql://user:pass@rds-endpoint/dbname"
export S3_BUCKET="health-dms-uploads"
```
And the app automatically uses AWS without changing any code!

### 📚 Resources
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [FastAPI — Settings and Environment Variables](https://fastapi.tiangolo.com/advanced/settings/)

---

## 4.6 Complete Schema Map

| Schema | File | Used For |
|--------|------|----------|
| `UserCreate` | `schemas/user.py` | Register new user (POST /auth/register) |
| `UserOut` | `schemas/user.py` | Return user data (hides password) |
| `Token` | `schemas/user.py` | Return JWT after login |
| `LoginRequest` | `schemas/user.py` | Login credentials |
| `PatientCreate` | `schemas/patient.py` | Create patient (POST /patients/) |
| `PatientUpdate` | `schemas/patient.py` | Update patient (PUT /patients/{id}) |
| `PatientOut` | `schemas/patient.py` | Return patient data |
| `DoctorCreate` | `schemas/doctor.py` | Create doctor (POST /doctors/) |
| `DoctorUpdate` | `schemas/doctor.py` | Update doctor (PUT /doctors/{id}) |
| `DoctorOut` | `schemas/doctor.py` | Return doctor data |
| `AppointmentCreate` | `schemas/appointment.py` | Create appointment |
| `AppointmentUpdate` | `schemas/appointment.py` | Update status (PATCH) |
| `AppointmentOut` | `schemas/appointment.py` | Return appointment data |
| `MedicalRecordCreate` | `schemas/medical_record.py` | Create medical record |
| `MedicalRecordOut` | `schemas/medical_record.py` | Return medical record data |

### ✏️ Exercise
1. Open `app/schemas/patient.py`
2. Add a new field `email: Optional[str] = None` to `PatientCreate`, `PatientUpdate`, and `PatientOut`
3. Now you'd also need to add `email = Column(String(100), default="")` to `app/models/patient.py`
4. This demonstrates how Pydantic and SQLAlchemy work together

---

## Module Summary

| Concept | Where Used | Why It Matters |
|---------|-----------|----------------|
| `BaseModel` | All `schemas/*.py` | Automatic JSON validation |
| `Optional[type]` | Update schemas | Allows partial updates |
| `model_config = {"from_attributes": True}` | Response schemas | Reads from ORM objects |
| `model_dump()` | Create endpoints | Converts Pydantic → dict → ORM |
| `model_dump(exclude_unset=True)` | Update endpoints | Only updates sent fields |
| `BaseSettings` | `config.py` | Environment variable management |
| Response model | `@router.get(response_model=...)` | Controls API output shape |
