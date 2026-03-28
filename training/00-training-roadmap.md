# 🎓 Cloud-Native Healthcare DMS — Complete Training Roadmap

> **Goal**: After completing this training, you will deeply understand every technology, pattern, and design decision used in this project — from Python basics to AWS cloud deployment.

---

## How to Use This Training

1. **Follow the modules in order** — each one builds on the previous
2. **Read the linked resources** — they are specifically chosen for the concepts used in this project
3. **Try the exercises** — every module has hands-on exercises using this project's actual code
4. **Time estimate**: ~25-30 hours total if you go through all materials

---

## 📋 Training Modules

| # | Module | Time | What You'll Learn |
|---|--------|------|-------------------|
| 01 | [Python Foundations](./01-python-foundations.md) | 3 hrs | Python 3.12, type hints, virtual environments, pip |
| 02 | [FastAPI Deep Dive](./02-fastapi-deep-dive.md) | 4 hrs | Routing, dependency injection, middleware, Swagger docs |
| 03 | [SQLAlchemy & Database](./03-sqlalchemy-database.md) | 3 hrs | ORM, models, sessions, migrations, SQLite → PostgreSQL |
| 04 | [Pydantic & Data Validation](./04-pydantic-validation.md) | 2 hrs | Schemas, request/response models, serialization |
| 05 | [Authentication & Security](./05-authentication-security.md) | 3 hrs | JWT, bcrypt, RBAC, password hashing, HTTPBearer |
| 06 | [REST API Design](./06-rest-api-design.md) | 2 hrs | CRUD patterns, HTTP methods, status codes, query params |
| 07 | [Testing with Pytest](./07-testing-pytest.md) | 2 hrs | Fixtures, TestClient, in-memory DB, test isolation |
| 08 | [Project Architecture](./08-project-architecture.md) | 2 hrs | Layered architecture, separation of concerns, code flow |
| 09 | [AWS Cloud Fundamentals](./09-aws-cloud-fundamentals.md) | 4 hrs | EC2, RDS, S3, IAM, VPC, Lambda, CloudWatch |
| 10 | [Phase 2 Migration Guide](./10-phase2-migration-guide.md) | 3 hrs | SQLite→RDS, local files→S3, localhost→EC2+ALB |

---

## 🗺️ Visual Learning Path

```
Module 01: Python Foundations
    │
    ▼
Module 02: FastAPI ←── Module 04: Pydantic (parallel)
    │
    ▼
Module 03: SQLAlchemy & Database
    │
    ▼
Module 05: Authentication & Security
    │
    ▼
Module 06: REST API Design
    │
    ▼
Module 07: Testing
    │
    ▼
Module 08: Project Architecture (ties everything together)
    │
    ▼
Module 09: AWS Cloud Fundamentals
    │
    ▼
Module 10: Phase 2 Migration
```

---

## 🔑 Quick Reference: How This Project Maps to Concepts

| Project File | Key Concepts |
|--------------|-------------|
| `app/main.py` | FastAPI app creation, CORS middleware, router registration |
| `app/config.py` | Pydantic Settings, environment variables, `.env` files |
| `app/database.py` | SQLAlchemy engine, session management, dependency injection |
| `app/auth.py` | JWT tokens, bcrypt hashing, RBAC middleware pattern |
| `app/models/*.py` | SQLAlchemy ORM models, table definitions, relationships |
| `app/schemas/*.py` | Pydantic models, request/response validation |
| `app/routers/*.py` | REST API endpoints, CRUD operations, query parameters |
| `scripts/seed.py` | Database seeding, bulk inserts, test data |
| `tests/*.py` | Pytest fixtures, TestClient, dependency overrides |
| `requirements.txt` | Python dependency management |

---

## 🎯 After Training Checklist

After completing all modules, you should be able to answer:

- [ ] How does FastAPI handle a request from start to finish?
- [ ] What is dependency injection and how does `Depends()` work?
- [ ] How does SQLAlchemy map Python classes to database tables?
- [ ] What's the difference between a Pydantic schema and an ORM model?
- [ ] How does JWT authentication work in this project?
- [ ] What does RBAC mean and how is `require_roles()` implemented?
- [ ] How are tests isolated using an in-memory database?
- [ ] What changes are needed to migrate from SQLite to PostgreSQL?
- [ ] What AWS services replace each local component?
- [ ] How does Auto Scaling work with EC2 + ALB?
