# Module 01: Python Foundations

> **Time**: ~3 hours | **Prerequisites**: Basic programming knowledge

---

## Why This Module

This project uses Python 3.12 with modern features: **type hints**, **dataclasses**, **f-strings**, **generators** (`yield`), and **virtual environments**. Before touching FastAPI or SQLAlchemy, you need these fundamentals solid.

---

## 1.1 Python Type Hints

### What & Why
Type hints tell Python (and your IDE) what type of data a variable/parameter/return should be. They **don't enforce** types at runtime but make code self-documenting and catch bugs early.

### How This Project Uses Them

```python
# From app/auth.py — every function signature uses type hints
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    ...
```

**Key patterns in this project:**
- `str`, `int`, `bool` — basic types
- `Optional[str]` — means the value can be `str` or `None`
- `list[PatientOut]` — a list containing `PatientOut` objects
- `-> str` — function returns a string
- `dict` — a dictionary

### 📚 Resources
- [Python Type Hints — Official Docs](https://docs.python.org/3/library/typing.html)
- [Real Python — Type Checking Guide](https://realpython.com/python-type-checking/)

### ✏️ Exercise
Open `app/auth.py` and trace every type hint. For `create_access_token`, what does `Optional[timedelta] = None` mean? Answer: the parameter is either a `timedelta` object or `None`, defaulting to `None`.

---

## 1.2 Virtual Environments & pip

### What & Why
A virtual environment (`venv`) is an isolated Python installation. Each project gets its own packages so they don't conflict with other projects on your system.

### How This Project Uses Them

```bash
# Create virtual environment
python -m venv venv

# Activate it (Mac/Linux)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

The `requirements.txt` file pins all the packages:
```
fastapi>=0.100.0      # Web framework
uvicorn>=0.23.0       # ASGI server to run FastAPI
sqlalchemy>=2.0.0     # ORM (database layer)
python-jose>=3.3.0    # JWT token creation/verification
passlib>=1.7.4        # Password hashing
bcrypt==4.1.3         # Bcrypt algorithm for passlib
python-multipart>=0.0.6 # File uploads in FastAPI
pydantic>=2.0.0       # Data validation
pydantic-settings>=2.0.0 # Settings from env vars
pytest>=7.4.0         # Testing framework
httpx>=0.24.0         # HTTP client (used by TestClient)
```

### 📚 Resources
- [Python venv Tutorial](https://docs.python.org/3/tutorial/venv.html)
- [pip User Guide](https://pip.pypa.io/en/stable/user_guide/)

### ✏️ Exercise
1. Delete the `venv` folder
2. Create a fresh virtual environment
3. Activate it
4. Run `pip install -r requirements.txt`
5. Run `pip list` to see all installed packages
6. Compare with `requirements.txt` — notice how many *transitive* dependencies were installed

---

## 1.3 Python Generators (yield)

### What & Why
A generator is a function that **produces values one at a time** instead of returning them all at once. The `yield` keyword pauses the function and resumes it next time you call it.

### How This Project Uses Them

```python
# From app/database.py — this is a critical pattern
def get_db():
    """Dependency that provides a DB session per request."""
    db = SessionLocal()
    try:
        yield db      # <-- gives the session to the caller
    finally:
        db.close()    # <-- runs AFTER the caller is done (cleanup)
```

**Why `yield` and not `return`?**
- `yield db` sends the database session to the FastAPI endpoint
- After the endpoint finishes, the `finally` block runs and closes the session
- This is FastAPI's "dependency injection" pattern — it automatically handles the lifecycle

### Mental Model
```
1. Request comes in
2. get_db() is called → creates session
3. yield db → session sent to endpoint function
4. endpoint runs, uses session (queries, commits, etc.)
5. endpoint finishes
6. finally block runs → session closed
7. Response sent back
```

### 📚 Resources
- [Real Python — Generators](https://realpython.com/introduction-to-python-generators/)
- [FastAPI Dependencies with yield](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/)

### ✏️ Exercise
Write a simple generator:
```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1

for num in countdown(5):
    print(num)  # prints 5, 4, 3, 2, 1
```

---

## 1.4 Decorators

### What & Why
A decorator wraps a function with extra behavior. The `@` syntax is syntactic sugar for passing a function to another function.

### How This Project Uses Them

```python
# FastAPI uses decorators to register routes
@router.get("/", response_model=list[PatientOut])
def list_patients(...):
    ...

# @router.get("/") means: "when someone sends a GET request to /, run this function"
```

```python
# Pytest uses decorators for test fixtures
@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
```

### 📚 Resources
- [Real Python — Decorators](https://realpython.com/primer-on-python-decorators/)
- [Python Decorators 101](https://realpython.com/primer-on-python-decorators/)

---

## 1.5 f-Strings and Dictionary Unpacking

### How This Project Uses Them

```python
# f-strings (string interpolation)
contact = f"98{random.randint(10000000, 99999999)}"  # "9812345678"
filepath = f"{uuid.uuid4().hex}{ext}"                 # "a1b2c3d4.pdf"

# Dictionary unpacking (**) — creates an object from a dict
patient = Patient(**body.model_dump())
# Equivalent to:
# patient = Patient(name=body.name, age=body.age, gender=body.gender, ...)
```

### 📚 Resources
- [Python f-strings](https://realpython.com/python-f-strings/)
- [Dictionary Unpacking](https://realpython.com/python-kwargs-and-args/)

---

## 1.6 Context Managers and `pathlib`

### How This Project Uses Them

```python
# From app/config.py — pathlib for cross-platform file paths
from pathlib import Path
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

# From app/routers/records.py — writing files
filepath = Path(settings.UPLOAD_DIR) / filename
filepath.write_bytes(contents)
```

`pathlib.Path` is the modern way to handle file paths in Python. The `/` operator joins paths.

### 📚 Resources
- [pathlib Guide](https://realpython.com/python-pathlib/)

---

## Module Summary

| Concept | Where Used in Project | Why It Matters |
|---------|----------------------|----------------|
| Type hints | Every function signature | Self-documenting code, IDE support |
| Virtual environments | `venv/`, `requirements.txt` | Isolated dependencies |
| Generators (`yield`) | `get_db()` in `database.py` | FastAPI dependency lifecycle |
| Decorators (`@`) | `@router.get()`, `@pytest.fixture` | Route registration, test setup |
| f-strings | `seed.py`, `auth.py`, `records.py` | String formatting |
| Dict unpacking (`**`) | `Patient(**body.model_dump())` | Creating ORM objects from Pydantic data |
| pathlib | `config.py`, `records.py` | Cross-platform file paths |
