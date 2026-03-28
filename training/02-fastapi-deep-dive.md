# Module 02: FastAPI Deep Dive

> **Time**: ~4 hours | **Prerequisites**: Module 01 (Python Foundations)

---

## Why This Module

FastAPI is the **backbone** of this entire project. It handles HTTP requests, API routing, input validation, authentication, file uploads, and auto-generates API documentation. Understanding FastAPI is understanding 80% of how this project works.

---

## 2.1 What is FastAPI?

FastAPI is a modern Python web framework for building APIs. Key features:
- **Fast** — one of the fastest Python frameworks (async support)
- **Auto-docs** — generates Swagger UI at `/docs` automatically
- **Type-driven** — uses Python type hints for validation
- **Dependency Injection** — powerful `Depends()` system

### How This Project Creates the App

```python
# app/main.py — the entire app setup in 39 lines!

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.APP_NAME,          # Shows in Swagger UI
    description="Cloud-Native Healthcare Data Management System",
    version="1.0.0",
)

# CORS middleware — allows the browser to talk to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # Allow all origins (dev only!)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all route modules
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
app.include_router(records.router)
app.include_router(analytics.router)
app.include_router(dashboard.router)
```

### 📚 Resources
- [FastAPI Official Tutorial](https://fastapi.tiangolo.com/tutorial/) — **START HERE**
- [FastAPI — First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/)
- [FastAPI GitHub Repo](https://github.com/tiangolo/fastapi)

---

## 2.2 Routing (APIRouter)

### What & Why
Routes map HTTP requests (like `GET /patients/`) to Python functions. FastAPI uses `APIRouter` to group related routes.

### How This Project Uses It

Each file in `app/routers/` creates its own router:

```python
# app/routers/patients.py
from fastapi import APIRouter

router = APIRouter(
    prefix="/patients",    # all routes start with /patients
    tags=["Patients"],     # groups endpoints in Swagger UI
)

@router.get("/")                    # GET /patients/
def list_patients(...): ...

@router.post("/", status_code=201)  # POST /patients/
def create_patient(...): ...

@router.get("/{patient_id}")        # GET /patients/42
def get_patient(patient_id: int, ...): ...

@router.put("/{patient_id}")        # PUT /patients/42
def update_patient(patient_id: int, ...): ...

@router.delete("/{patient_id}", status_code=204)  # DELETE /patients/42
def delete_patient(patient_id: int, ...): ...
```

**Key concepts:**
- `prefix="/patients"` — adds `/patients` before every route in this file
- `tags=["Patients"]` — organizes routes in Swagger UI
- `{patient_id}` — path parameter, automatically parsed as `int`
- `status_code=201` — overrides default 200 status code

### Router Registration
All routers are registered in `app/main.py`:
```python
app.include_router(patients.router)
app.include_router(doctors.router)
# ... etc
```

### 📚 Resources
- [FastAPI — Path Parameters](https://fastapi.tiangolo.com/tutorial/path-params/)
- [FastAPI — APIRouter](https://fastapi.tiangolo.com/tutorial/bigger-applications/)

### ✏️ Exercise
1. Open `http://localhost:8000/docs` after starting the server
2. Notice how endpoints are grouped by tags (Patients, Doctors, etc.)
3. Try expanding the `GET /patients/` endpoint and clicking "Try it out"

---

## 2.3 Dependency Injection (Depends)

### What & Why
Dependency injection means: **"before running this endpoint, run these other functions first and give me their results."** FastAPI's `Depends()` is how you share common logic across endpoints.

### How This Project Uses It — 3 Critical Dependencies

#### Dependency 1: Database Session (`get_db`)
```python
# app/database.py
def get_db():
    db = SessionLocal()    # create a database session
    try:
        yield db           # give it to the endpoint
    finally:
        db.close()         # clean up after endpoint finishes

# app/routers/patients.py — used in every endpoint
@router.get("/")
def list_patients(
    db: Session = Depends(get_db),    # <-- inject database session
):
    return db.query(Patient).all()
```

#### Dependency 2: Current User (`get_current_user`)
```python
# app/auth.py
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),  # <-- reads the Bearer token
    db: Session = Depends(get_db),  # <-- also gets a DB session!
) -> User:
    token = credentials.credentials
    payload = jwt.decode(token, ...)    # decode the JWT
    user = db.query(User).filter(User.username == payload["sub"]).first()
    return user  # gives the User object to the endpoint
```

#### Dependency 3: Role Checker (`require_roles`)
```python
# app/auth.py — a "dependency factory" (function that returns a dependency)
def require_roles(*roles: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

# Usage in endpoints:
@router.post("/")
def create_patient(
    _: User = Depends(require_roles("admin", "receptionist")),  # <-- only admin or receptionist
):
    ...
```

### Dependency Chain Visualization
```
Request: POST /patients/
    │
    ├── Depends(require_roles("admin", "receptionist"))
    │       │
    │       ├── Depends(get_current_user)
    │       │       │
    │       │       ├── Depends(security)        → extracts Bearer token from header
    │       │       └── Depends(get_db)           → creates DB session
    │       │       └── returns User object
    │       │
    │       └── checks if user.role in ["admin", "receptionist"]
    │
    ├── Depends(get_db)                           → creates DB session
    │
    └── runs create_patient() with db session and validated user
```

### 📚 Resources
- [FastAPI — Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/) — **ESSENTIAL**
- [FastAPI — Dependencies with yield](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/)
- [FastAPI — Security Dependencies](https://fastapi.tiangolo.com/tutorial/security/)

### ✏️ Exercise
In `app/routers/patients.py`, trace the `create_patient` function:
1. What dependencies does it have?
2. In what order do they execute?
3. What happens if the JWT token is invalid?
4. What happens if the user is a "doctor"?

---

## 2.4 Request & Response Models

### How This Project Uses Them

```python
# Request body — FastAPI automatically validates against this schema
@router.post("/", response_model=PatientOut, status_code=201)
def create_patient(
    body: PatientCreate,    # <-- request body, validated by Pydantic
    ...
):
    patient = Patient(**body.model_dump())  # convert Pydantic → ORM
    ...
    return patient  # FastAPI converts ORM → PatientOut (response)
```

```python
# Response model — controls what gets sent back to the client
@router.get("/", response_model=list[PatientOut])
def list_patients(...):
    return query.all()  # SQLAlchemy objects automatically serialized to PatientOut
```

**The data flow:**
```
Client JSON → Pydantic Schema (validation) → ORM Model (database) → Pydantic Schema (response) → Client JSON
```

### 📚 Resources
- [FastAPI — Request Body](https://fastapi.tiangolo.com/tutorial/body/)
- [FastAPI — Response Model](https://fastapi.tiangolo.com/tutorial/response-model/)

---

## 2.5 Query Parameters

### How This Project Uses Them

```python
# app/routers/patients.py
@router.get("/")
def list_patients(
    search: Optional[str] = Query(None, description="Search by name"),
    ...
):
    if search:
        query = query.filter(Patient.name.ilike(f"%{search}%"))

# Called as: GET /patients/?search=Priya
```

```python
# app/routers/appointments.py — multiple filters
@router.get("/")
def list_appointments(
    patient_id: Optional[int] = Query(None),
    doctor_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    ...
):
# Called as: GET /appointments/?status=completed&doctor_id=5
```

### 📚 Resources
- [FastAPI — Query Parameters](https://fastapi.tiangolo.com/tutorial/query-params/)

---

## 2.6 CORS Middleware

### What & Why
CORS (Cross-Origin Resource Sharing) controls which websites can call your API. Without CORS, a browser page at `http://mydashboard.com` can't call `http://localhost:8000/api`.

```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # Allow ALL origins (fine for dev, restrict in prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 📚 Resources
- [FastAPI — CORS](https://fastapi.tiangolo.com/tutorial/cors/)
- [MDN — CORS Explained](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)

---

## 2.7 File Uploads

### How This Project Does It

```python
# app/routers/records.py
from fastapi import UploadFile, File

@router.post("/upload/{record_id}")
def upload_file(
    record_id: int,
    file: UploadFile = File(...),  # <-- FastAPI handles multipart upload
    ...
):
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:   # validate extension
        raise HTTPException(status_code=400, ...)

    contents = file.file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:  # validate size
        raise HTTPException(status_code=400, ...)

    filename = f"{uuid.uuid4().hex}{ext}"         # random filename
    filepath = Path(settings.UPLOAD_DIR) / filename
    filepath.write_bytes(contents)                # save to disk
```

### 📚 Resources
- [FastAPI — File Upload](https://fastapi.tiangolo.com/tutorial/request-files/)

---

## 2.8 Running FastAPI with Uvicorn

```bash
# Development (auto-reload on code changes)
uvicorn app.main:app --reload

# Production (multiple workers for concurrency)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Or with Gunicorn (used on EC2 in Phase 2)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

- `app.main:app` means "import the `app` object from `app/main.py`"
- `--reload` watches for file changes and restarts automatically
- `--host 0.0.0.0` makes it accessible from other machines (not just localhost)

### 📚 Resources
- [Uvicorn Docs](https://www.uvicorn.org/)

---

## Module Summary

| Concept | Where Used | Key Function/Class |
|---------|-----------|-------------------|
| FastAPI app | `main.py` | `FastAPI()` |
| APIRouter | All `routers/*.py` | `APIRouter(prefix=..., tags=...)` |
| Dependency Injection | Every endpoint | `Depends(get_db)`, `Depends(require_roles(...))` |
| Path Parameters | CRUD endpoints | `/{patient_id}`, `/{doctor_id}` |
| Query Parameters | List endpoints | `Query(None, description=...)` |
| Request Body | Create/update endpoints | `body: PatientCreate` |
| Response Model | All endpoints | `response_model=list[PatientOut]` |
| CORS | `main.py` | `CORSMiddleware` |
| File Upload | `records.py` | `UploadFile`, `File(...)` |
| Uvicorn | CLI | `uvicorn app.main:app --reload` |
