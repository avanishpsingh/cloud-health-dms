"""Shared pytest fixtures for all tests."""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["AUTO_CREATE_TABLES"] = "false"

from app.database import Base, get_db
from app.main import app
from app.auth import hash_password
from app.models.user import User
from app.models.doctor import Doctor


# In-memory SQLite for tests — isolated from real DB
engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    db = TestSession()
    yield db
    db.close()


@pytest.fixture
def admin_token(client, db):
    """Create admin user and return JWT token."""
    user = User(username="admin", password_hash=hash_password("admin123"), full_name="Admin", role="admin")
    db.add(user)
    db.commit()
    resp = client.post("/auth/login", json={"username": "admin", "password": "admin123"})
    return resp.json()["access_token"]


@pytest.fixture
def doctor_token(client, db):
    """Create doctor user + doctor profile and return JWT token."""
    user = User(username="doc1", password_hash=hash_password("doc123"), full_name="Dr. Test", role="doctor")
    db.add(user)
    db.flush()
    doctor = Doctor(user_id=user.id, name="Dr. Test", specialization="General", department="General", contact="1234567890")
    db.add(doctor)
    db.commit()
    resp = client.post("/auth/login", json={"username": "doc1", "password": "doc123"})
    return resp.json()["access_token"]


@pytest.fixture
def receptionist_token(client, db):
    """Create receptionist user and return JWT token."""
    user = User(username="recep1", password_hash=hash_password("recep123"), full_name="Receptionist", role="receptionist")
    db.add(user)
    db.commit()
    resp = client.post("/auth/login", json={"username": "recep1", "password": "recep123"})
    return resp.json()["access_token"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
