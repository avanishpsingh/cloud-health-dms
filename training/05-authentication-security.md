# Module 05: Authentication & Security

> **Time**: ~3 hours | **Prerequisites**: Module 02 (FastAPI), Module 03 (SQLAlchemy)

---

## Why This Module

This project implements a **complete authentication system** from scratch: password hashing, JWT tokens, and role-based access control. Understanding this is essential for the security portion of your assignment and for any production application.

---

## 5.1 The Big Picture — Authentication Flow

```
┌──────────┐                    ┌──────────────────┐
│  Client   │───── POST ────────│  /auth/login     │
│ (Browser) │  {username, pass} │                  │
│           │                   │  1. Find user    │
│           │                   │  2. Verify hash  │
│           │                   │  3. Create JWT   │
│           │◄── {token} ──────│                  │
└──────────┘                    └──────────────────┘
     │
     │  All subsequent requests include:
     │  Header: Authorization: Bearer <token>
     │
     ▼
┌──────────┐                    ┌──────────────────┐
│  Client   │──── GET ──────────│  /patients/      │
│           │  + Bearer token   │                  │
│           │                   │  1. Extract JWT  │
│           │                   │  2. Decode JWT   │
│           │                   │  3. Find user    │
│           │                   │  4. Check role   │
│           │                   │  5. Return data  │
│           │◄── [patients] ───│                  │
└──────────┘                    └──────────────────┘
```

---

## 5.2 Password Hashing (bcrypt)

### What & Why
**NEVER** store passwords in plaintext. If your database is breached, all user passwords would be exposed. Instead, we store a **hash** — a one-way transformation.

```python
# app/auth.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)
    # "admin123" → "$2b$12$LJ3m4ys8Xyq5N.5bKjYfYO3Qp6YHfM8fKjV..."

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
    # verify("admin123", "$2b$12$LJ3...") → True
    # verify("wrong",    "$2b$12$LJ3...") → False
```

**Key properties of bcrypt:**
- **One-way**: You can't reverse the hash to get the password
- **Salted**: Same password produces different hashes each time (prevents rainbow tables)
- **Slow by design**: Makes brute-force attacks impractical (~12 rounds of computation)

### How It's Used in Registration
```python
# app/routers/auth.py → register endpoint
user = User(
    username=body.username,
    password_hash=hash_password(body.password),  # <-- hash before storing!
    full_name=body.full_name,
    role=body.role,
)
```

### How It's Used in Login
```python
# app/routers/auth.py → login endpoint
user = db.query(User).filter(User.username == body.username).first()
if not user or not verify_password(body.password, user.password_hash):
    raise HTTPException(status_code=401, detail="Invalid credentials")
```

### 📚 Resources
- [bcrypt Explained Simply](https://auth0.com/blog/hashing-in-action-understanding-bcrypt/)
- [passlib Documentation](https://passlib.readthedocs.io/en/stable/)
- [Why Hash Passwords?](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

---

## 5.3 JWT (JSON Web Tokens)

### What & Why
JWT is a **stateless** authentication mechanism. After login, the server creates a token containing the user's identity. The client sends this token with every request. The server can verify the token without checking the database (because it's cryptographically signed).

### JWT Structure
A JWT has three parts, separated by dots: `header.payload.signature`

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTcxMjM0NTY3OH0.signature_here
```

**Decoded payload:**
```json
{
  "sub": "admin",           // subject (username)
  "role": "admin",          // user role
  "exp": 1712345678         // expiration timestamp
}
```

### How This Project Creates JWTs

```python
# app/auth.py
from jose import jwt

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})  # add expiration time
    return jwt.encode(
        to_encode,                      # data payload
        settings.SECRET_KEY,            # signing key (keep this SECRET!)
        algorithm=settings.ALGORITHM    # HS256 (HMAC-SHA256)
    )
```

**Called in the login endpoint:**
```python
token = create_access_token(data={"sub": user.username, "role": user.role})
return {"access_token": token}
```

### How This Project Verifies JWTs

```python
# app/auth.py
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")   # extract username from payload
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

### Token Lifecycle
```
1. User logs in →  server creates JWT (valid for 60 minutes)
2. Client stores token (in memory, localStorage, or cookie)
3. Every API request includes: Authorization: Bearer <token>
4. Server decodes token → extracts username → loads user
5. After 60 minutes, token expires → client must re-login
```

### 📚 Resources
- [JWT.io](https://jwt.io/) — **Paste a token here to decode it!**
- [How JWT Works](https://auth0.com/learn/json-web-tokens/)
- [python-jose Library](https://python-jose.readthedocs.io/)
- [FastAPI Security Tutorial](https://fastapi.tiangolo.com/tutorial/security/)

### ✏️ Exercise
1. Start the server: `uvicorn app.main:app --reload`
2. Login via Swagger (`/docs`) and copy the token
3. Go to [jwt.io](https://jwt.io/) and paste the token
4. See your decoded payload (username, role, expiration)

---

## 5.4 Role-Based Access Control (RBAC)

### What & Why
Different users should have different permissions:

| Role | Can Do |
|------|--------|
| **Admin** | Everything — manage users, doctors, patients, appointments, view analytics |
| **Doctor** | View patients & doctors, manage appointment status, create medical records |
| **Receptionist** | Manage patients, schedule appointments |

### How This Project Implements RBAC

```python
# app/auth.py
def require_roles(*roles: str):
    """Dependency factory: ensures current user has one of the allowed roles."""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker
```

#### Usage in Endpoints
```python
# Only admin can delete
@router.delete("/{patient_id}")
def delete_patient(
    _: User = Depends(require_roles("admin")),           # admin ONLY
): ...

# Admin or receptionist can create
@router.post("/")
def create_patient(
    _: User = Depends(require_roles("admin", "receptionist")),  # either role
): ...

# Any authenticated user can view
@router.get("/")
def list_patients(
    _: User = Depends(require_roles("admin", "doctor", "receptionist")),  # all roles
): ...
```

### Complete RBAC Matrix

| Endpoint | Admin | Doctor | Receptionist |
|----------|:-----:|:------:|:------------:|
| POST /auth/login | ✅ | ✅ | ✅ |
| POST /auth/register | ✅ | ❌ | ❌ |
| GET /patients/ | ✅ | ✅ | ✅ |
| POST /patients/ | ✅ | ❌ | ✅ |
| PUT /patients/{id} | ✅ | ❌ | ✅ |
| DELETE /patients/{id} | ✅ | ❌ | ❌ |
| POST /doctors/ | ✅ | ❌ | ❌ |
| PATCH /appointments/{id} | ✅ | ✅ | ❌ |
| POST /patients/{id}/records | ❌ | ✅ | ❌ |
| GET /analytics/summary | ✅ | ❌ | ❌ |

### 📚 Resources
- [RBAC Explained](https://auth0.com/docs/manage-users/access-control/rbac)
- [FastAPI — OAuth2 with Password](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)

### ✏️ Exercise
1. Login as `reception1` / `recep123`
2. Try to access `DELETE /patients/1` — you should get a 403 Forbidden
3. Login as `admin` / `admin123` — now the same request succeeds

---

## 5.5 HTTPBearer Security Scheme

```python
# app/auth.py
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()   # tells FastAPI to expect "Authorization: Bearer <token>" header
```

This:
1. Makes Swagger UI show an "Authorize" button
2. Automatically extracts the token from `Authorization: Bearer <token>` header
3. Returns `HTTPAuthorizationCredentials` with `.credentials` = the token string

---

## 5.6 Security Summary for This Project

| Security Control | Implementation |
|-----------------|----------------|
| Password hashing | bcrypt via passlib (12 rounds) |
| Authentication | JWT tokens (HS256, 60-min expiry) |
| Authorization | RBAC with `require_roles()` dependency |
| Input validation | Pydantic schemas on all endpoints |
| SQL injection prevention | SQLAlchemy ORM (parameterized queries) |
| File upload safety | Extension whitelist + 10MB size limit |
| XSS protection | HTML escaping in dashboard |
| Soft delete | Patients deactivated, never permanently removed |

---

## Module Summary

| Concept | File | Key Function |
|---------|------|-------------|
| Password hashing | `auth.py` | `hash_password()`, `verify_password()` |
| JWT creation | `auth.py` | `create_access_token()` |
| JWT verification | `auth.py` | `get_current_user()` |
| RBAC | `auth.py` | `require_roles()` |
| Login flow | `routers/auth.py` | `login()` |
| Registration | `routers/auth.py` | `register()` |
| Token extraction | `auth.py` | `HTTPBearer()`, `security` |
