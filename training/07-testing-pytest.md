# Module 07: Testing with Pytest

> **Time**: ~2 hours | **Prerequisites**: Module 02, 03, 05

---

## Why This Module

This project has **17 automated tests** covering authentication, patient CRUD, and appointment management. Your role is "Testing & Monitoring" — understanding how these tests work is essential for explaining your contribution.

---

## 7.1 How Tests Work in This Project

### Test Architecture
```
tests/
├── conftest.py           ← shared fixtures (DB, auth tokens)
├── test_auth.py          ← 6 auth tests
├── test_patients.py      ← 7 patient tests
└── test_appointments.py  ← 4 appointment tests
```

```
Real App                         Test Environment
┌─────────┐                      ┌─────────────────┐
│ SQLite   │                      │ In-Memory SQLite │ ← fresh for each test
│ File DB  │                      │ (no file, RAM)   │
└─────────┘                      └─────────────────┘
     ↑                                   ↑
     │                                   │
app/database.py                   tests/conftest.py
get_db()                          override_get_db()
```

Tests use a **completely separate in-memory database**. Nothing you do in tests affects the real `health_dms.db`.

---

## 7.2 Test Fixtures (conftest.py) — Line by Line

### 1. In-Memory Database Setup
```python
# tests/conftest.py

# Create an in-memory SQLite database (lives in RAM, gone when tests end)
engine = create_engine(
    "sqlite://",                              # empty string = in-memory
    connect_args={"check_same_thread": False},
    poolclass=StaticPool                      # share one connection across threads
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### 2. Override the Database Dependency
```python
def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()

# CRITICAL LINE: tells FastAPI to use test DB instead of real DB
app.dependency_overrides[get_db] = override_get_db
```

This is the magic of FastAPI's dependency injection — you can **swap out** any dependency for tests!

### 3. Auto-Reset Database Before Each Test
```python
@pytest.fixture(autouse=True)   # runs automatically for EVERY test
def setup_db():
    Base.metadata.create_all(bind=engine)   # create all tables
    yield                                    # test runs here
    Base.metadata.drop_all(bind=engine)     # drop all tables (clean slate)
```

Every test starts with empty tables and ends by destroying them. Tests are **completely isolated**.

### 4. Test Client
```python
@pytest.fixture
def client():
    return TestClient(app)   # simulates HTTP requests without starting a real server
```

### 5. Authentication Fixtures
```python
@pytest.fixture
def admin_token(client, db):
    """Create admin user and return JWT token."""
    user = User(username="admin", password_hash=hash_password("admin123"),
                full_name="Admin", role="admin")
    db.add(user)
    db.commit()
    resp = client.post("/auth/login", json={"username": "admin", "password": "admin123"})
    return resp.json()["access_token"]

@pytest.fixture
def doctor_token(client, db):
    """Create doctor user + doctor profile and return JWT token."""
    user = User(username="doc1", password_hash=hash_password("doc123"),
                full_name="Dr. Test", role="doctor")
    db.add(user)
    db.flush()
    doctor = Doctor(user_id=user.id, name="Dr. Test", specialization="General",
                    department="General", contact="1234567890")
    db.add(doctor)
    db.commit()
    resp = client.post("/auth/login", json={"username": "doc1", "password": "doc123"})
    return resp.json()["access_token"]

@pytest.fixture
def receptionist_token(client, db):
    ...
```

### Helper Function
```python
def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}

# Usage: client.get("/patients/", headers=auth_header(admin_token))
```

### 📚 Resources
- [Pytest Documentation](https://docs.pytest.org/en/stable/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

---

## 7.3 Auth Tests — Explained

```python
# tests/test_auth.py

# Test 1: Health check endpoint works
def test_health_check(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

# Test 2: Admin can login successfully
def test_login_success(client, admin_token):
    assert admin_token is not None      # if fixture ran, login worked

# Test 3: Wrong password returns 401
def test_login_wrong_password(client, db):
    db.add(User(username="test", password_hash=hash_password("pass"), ...))
    db.commit()
    resp = client.post("/auth/login", json={"username": "test", "password": "wrong"})
    assert resp.status_code == 401

# Test 4: Receptionist CANNOT register new users
def test_register_requires_admin(client, receptionist_token):
    resp = client.post("/auth/register", json={...}, headers=auth_header(receptionist_token))
    assert resp.status_code == 403      # Forbidden!

# Test 5: Admin CAN register new users
def test_register_by_admin(client, admin_token):
    resp = client.post("/auth/register", json={...}, headers=auth_header(admin_token))
    assert resp.status_code == 201      # Created!

# Test 6: /auth/me returns current user info
def test_me(client, admin_token):
    resp = client.get("/auth/me", headers=auth_header(admin_token))
    assert resp.json()["role"] == "admin"
```

---

## 7.4 Patient Tests — Explained

```python
# tests/test_patients.py
PATIENT = {"name": "Test Patient", "age": 30, "gender": "Male",
           "contact": "9999999999", "address": "Test City", "blood_group": "O+"}

# Test 1: Create a patient
def test_create_patient(client, admin_token):
    resp = client.post("/patients/", json=PATIENT, headers=auth_header(admin_token))
    assert resp.status_code == 201
    assert resp.json()["name"] == "Test Patient"

# Test 2: List patients
def test_list_patients(client, admin_token):
    client.post("/patients/", json=PATIENT, headers=auth_header(admin_token))
    resp = client.get("/patients/", headers=auth_header(admin_token))
    assert len(resp.json()) == 1

# Test 3: Get single patient
def test_get_patient(client, admin_token):
    create = client.post("/patients/", json=PATIENT, headers=auth_header(admin_token))
    pid = create.json()["id"]
    resp = client.get(f"/patients/{pid}", headers=auth_header(admin_token))
    assert resp.json()["id"] == pid

# Test 4: Update patient
def test_update_patient(client, admin_token):
    create = client.post("/patients/", json=PATIENT, headers=auth_header(admin_token))
    pid = create.json()["id"]
    resp = client.put(f"/patients/{pid}", json={"name": "Updated"}, headers=auth_header(admin_token))
    assert resp.json()["name"] == "Updated"

# Test 5: Soft delete (patient disappears from list but still exists in DB)
def test_delete_patient_soft(client, admin_token):
    create = client.post("/patients/", json=PATIENT, headers=auth_header(admin_token))
    pid = create.json()["id"]
    resp = client.delete(f"/patients/{pid}", headers=auth_header(admin_token))
    assert resp.status_code == 204
    resp = client.get("/patients/", headers=auth_header(admin_token))
    assert len(resp.json()) == 0      # gone from list!

# Test 6: Search works
def test_search_patients(client, admin_token):
    client.post("/patients/", json=PATIENT, headers=auth_header(admin_token))
    client.post("/patients/", json={**PATIENT, "name": "Another Person"}, headers=auth_header(admin_token))
    resp = client.get("/patients/?search=Test", headers=auth_header(admin_token))
    assert len(resp.json()) == 1      # only "Test Patient" matches

# Test 7: Doctor CANNOT create patients (RBAC test)
def test_doctor_cannot_create_patient(client, doctor_token):
    resp = client.post("/patients/", json=PATIENT, headers=auth_header(doctor_token))
    assert resp.status_code == 403
```

---

## 7.5 Appointment Tests — Explained

```python
# tests/test_appointments.py

def _create_patient_and_doctor(db):
    """Helper: creates test patient + doctor in the test DB."""
    p = Patient(name="P1", age=30, gender="Male", contact="111")
    d = Doctor(name="D1", specialization="General", department="General", contact="222")
    db.add_all([p, d])
    db.commit()
    return p.id, d.id

# Test 1: Create appointment
def test_create_appointment(client, admin_token, db):
    pid, did = _create_patient_and_doctor(db)
    resp = client.post("/appointments/", json={
        "patient_id": pid, "doctor_id": did,
        "date_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "reason": "Checkup"
    }, headers=auth_header(admin_token))
    assert resp.status_code == 201
    assert resp.json()["status"] == "scheduled"     # default status

# Test 2: Filter by patient_id
def test_list_appointments_filter(client, admin_token, db):
    pid, did = _create_patient_and_doctor(db)
    client.post("/appointments/", json={...}, headers=auth_header(admin_token))
    resp = client.get(f"/appointments/?patient_id={pid}", headers=auth_header(admin_token))
    assert len(resp.json()) == 1

# Test 3: Update status
def test_update_appointment_status(client, admin_token, db):
    ...
    resp = client.patch(f"/appointments/{aid}", json={"status": "completed"}, ...)
    assert resp.json()["status"] == "completed"

# Test 4: Reject invalid status
def test_invalid_appointment_status(client, admin_token, db):
    ...
    resp = client.patch(f"/appointments/{aid}", json={"status": "invalid"}, ...)
    assert resp.status_code == 400
```

---

## 7.6 Running Tests

```bash
# Run all tests with verbose output
python -m pytest tests/ -v

# Run only auth tests
python -m pytest tests/test_auth.py -v

# Run a specific test
python -m pytest tests/test_patients.py::test_create_patient -v

# Run with print output visible
python -m pytest tests/ -v -s
```

Expected output:
```
tests/test_auth.py::test_health_check PASSED
tests/test_auth.py::test_login_success PASSED
tests/test_auth.py::test_login_wrong_password PASSED
tests/test_auth.py::test_register_requires_admin PASSED
tests/test_auth.py::test_register_by_admin PASSED
tests/test_auth.py::test_me PASSED
tests/test_patients.py::test_create_patient PASSED
... (17 tests total)
```

### 📚 Resources
- [Pytest Getting Started](https://docs.pytest.org/en/stable/getting-started.html)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [TestClient (Starlette)](https://www.starlette.io/testclient/)

### ✏️ Exercise
1. Run `python -m pytest tests/ -v` and verify all 17 pass
2. Break a test on purpose: in `app/routers/patients.py`, change `status_code=201` to `status_code=200`
3. Run tests again — `test_create_patient` should fail
4. Fix it back

---

## Module Summary

| Concept | Where Used | What It Does |
|---------|-----------|-------------|
| `conftest.py` | Shared fixtures | Provides DB, client, tokens to all tests |
| `dependency_overrides` | `conftest.py` | Swaps real DB for test DB |
| `@pytest.fixture(autouse=True)` | `setup_db` | Creates/drops tables per test |
| `TestClient` | Every test | Simulates HTTP requests |
| `auth_header()` | Every authenticated test | Creates Bearer token header |
| `assert` | Every test | Validates expected outcomes |
