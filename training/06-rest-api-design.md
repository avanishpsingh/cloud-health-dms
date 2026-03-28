# Module 06: REST API Design

> **Time**: ~2 hours | **Prerequisites**: Module 02 (FastAPI)

---

## Why This Module

This project exposes **22 REST API endpoints**. Understanding REST conventions means you can explain *why* each endpoint uses a specific HTTP method, URL structure, and status code — critical for your assignment presentation and viva.

---

## 6.1 What is REST?

**REST** (Representational State Transfer) is an architectural style for APIs. Key principles:

1. **Resources** — Everything is a "resource" (patient, doctor, appointment)
2. **URLs** — Each resource has a unique URL (`/patients/5`)
3. **HTTP Methods** — The method tells the server what to do
4. **Stateless** — Each request is independent (JWT carries auth state)

---

## 6.2 HTTP Methods in This Project

| Method | Purpose | Example | Analogous To |
|--------|---------|---------|-------------|
| **GET** | Read data | `GET /patients/` | SELECT |
| **POST** | Create new data | `POST /patients/` | INSERT |
| **PUT** | Replace/update data | `PUT /patients/5` | UPDATE (full) |
| **PATCH** | Partial update | `PATCH /appointments/3` | UPDATE (partial) |
| **DELETE** | Remove data | `DELETE /patients/5` | DELETE |

### How This Project Uses Them

```python
# GET — List all patients
@router.get("/", response_model=list[PatientOut])
def list_patients(...): ...

# GET — Get one patient by ID
@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: int, ...): ...

# POST — Create a new patient
@router.post("/", response_model=PatientOut, status_code=201)
def create_patient(body: PatientCreate, ...): ...

# PUT — Full update of a patient
@router.put("/{patient_id}", response_model=PatientOut)
def update_patient(patient_id: int, body: PatientUpdate, ...): ...

# DELETE — Remove a patient (soft delete)
@router.delete("/{patient_id}", status_code=204)
def delete_patient(patient_id: int, ...): ...

# PATCH — Partial update (only status field)
@router.patch("/{appointment_id}", response_model=AppointmentOut)
def update_appointment_status(appointment_id: int, body: AppointmentUpdate, ...): ...
```

### PUT vs PATCH in This Project
- **PUT** `/patients/5` — Updates the whole patient (could change name, age, contact, etc.)
- **PATCH** `/appointments/3` — Updates only the status field (`scheduled → completed`)

---

## 6.3 HTTP Status Codes

| Code | Meaning | Where Used |
|------|---------|-----------|
| **200** | OK (success) | Default for GET, PUT, PATCH |
| **201** | Created | POST /patients/, POST /doctors/, etc. |
| **204** | No Content | DELETE /patients/{id} (nothing to return) |
| **400** | Bad Request | Invalid role, invalid status, bad file type |
| **401** | Unauthorized | Invalid/missing JWT token |
| **403** | Forbidden | Valid token but wrong role |
| **404** | Not Found | Patient/doctor/appointment doesn't exist |
| **422** | Validation Error | Pydantic validation failed (wrong data types) |

### How This Project Returns Errors

```python
# 404 Not Found
patient = db.query(Patient).filter(Patient.id == patient_id).first()
if not patient:
    raise HTTPException(status_code=404, detail="Patient not found")

# 401 Unauthorized
if not user or not verify_password(body.password, user.password_hash):
    raise HTTPException(status_code=401, detail="Invalid credentials")

# 403 Forbidden
if current_user.role not in roles:
    raise HTTPException(status_code=403, detail="Insufficient permissions")

# 400 Bad Request
if body.status not in ("scheduled", "completed", "cancelled"):
    raise HTTPException(status_code=400, detail="Invalid status")
```

---

## 6.4 URL Design Patterns

### Resource Collections vs Individual Resources
```
/patients/      → collection (list of patients)
/patients/5     → individual resource (patient #5)
```

### Nested Resources
```
/patients/5/records    → medical records belonging to patient #5
```

### Query Parameters for Filtering
```
/patients/?search=Priya                    → search patients by name
/appointments/?status=completed            → filter by status
/appointments/?patient_id=5&doctor_id=3    → filter by both
/doctors/?department=Cardiology            → filter by department
```

### Complete URL Map of This Project

```
Authentication:
  POST   /auth/login           → login, get token
  POST   /auth/register        → register new user (admin only)
  GET    /auth/me              → get current user info
  GET    /auth/users           → list all users (admin only)

Patients:
  GET    /patients/            → list patients (with search)
  POST   /patients/            → create patient
  GET    /patients/{id}        → get patient details
  PUT    /patients/{id}        → update patient
  DELETE /patients/{id}        → soft-delete patient

Doctors:
  GET    /doctors/             → list doctors (with search + department filter)
  POST   /doctors/             → create doctor
  GET    /doctors/{id}         → get doctor details
  PUT    /doctors/{id}         → update doctor
  DELETE /doctors/{id}         → delete doctor

Appointments:
  GET    /appointments/        → list appointments (with filters)
  POST   /appointments/       → create appointment
  PATCH  /appointments/{id}   → update appointment status
  DELETE /appointments/{id}   → delete appointment

Medical Records:
  GET    /patients/{id}/records    → get patient's medical history
  POST   /patients/{id}/records    → add medical record (doctor only)
  POST   /upload/{record_id}       → upload medical file

Analytics:
  GET    /analytics/summary        → dashboard statistics (admin only)
```

---

## 6.5 CRUD Pattern Applied Consistently

Every resource follows the same pattern:

```python
# 1. LIST — GET /resource/
@router.get("/")
def list_resources(search, filters, db, auth): ...

# 2. CREATE — POST /resource/
@router.post("/", status_code=201)
def create_resource(body, db, auth): ...

# 3. READ — GET /resource/{id}
@router.get("/{id}")
def get_resource(id, db, auth): ...

# 4. UPDATE — PUT /resource/{id}
@router.put("/{id}")
def update_resource(id, body, db, auth): ...

# 5. DELETE — DELETE /resource/{id}
@router.delete("/{id}", status_code=204)
def delete_resource(id, db, auth): ...
```

Each endpoint follows the same internal pattern:
1. Authenticate (via `Depends`)
2. Validate input (via Pydantic)
3. Query/modify database (via SQLAlchemy)
4. Return response (via response_model)

### 📚 Resources
- [REST API Tutorial](https://restfulapi.net/)
- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [RESTful API Design Best Practices](https://blog.stoplight.io/crud-api-design)
- [FastAPI — Status Codes](https://fastapi.tiangolo.com/tutorial/response-status-code/)

### ✏️ Exercise
1. Open `http://localhost:8000/docs`
2. For each endpoint, verify: Does the HTTP method match the action? Does the status code make sense?
3. Try calling endpoints with the wrong method (e.g., PUT /patients/ instead of POST) — what happens?

---

## Module Summary

| Concept | This Project's Usage |
|---------|---------------------|
| GET | Read single or list of resources |
| POST | Create resources, login, upload files |
| PUT | Full update of a resource |
| PATCH | Partial update (appointment status only) |
| DELETE | Remove (soft or hard) |
| 201 Created | Returned after POST creates something |
| 204 No Content | Returned after DELETE |
| 400/401/403/404 | Error responses with descriptive messages |
| Path params `{id}` | Identify specific resources |
| Query params `?search=` | Filter/search collections |
| Nested URLs | `/patients/{id}/records` |
