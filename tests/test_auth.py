from tests.conftest import auth_header


def test_health_check(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_login_success(client, admin_token):
    assert admin_token is not None


def test_login_wrong_password(client, db):
    from app.models.user import User
    from app.auth import hash_password
    db.add(User(username="test", password_hash=hash_password("pass"), full_name="T", role="admin"))
    db.commit()
    resp = client.post("/auth/login", json={"username": "test", "password": "wrong"})
    assert resp.status_code == 401


def test_register_requires_admin(client, receptionist_token):
    resp = client.post(
        "/auth/register",
        json={"username": "new", "password": "pass", "full_name": "New", "role": "receptionist"},
        headers=auth_header(receptionist_token),
    )
    assert resp.status_code == 403


def test_register_by_admin(client, admin_token):
    resp = client.post(
        "/auth/register",
        json={"username": "new_user", "password": "pass123", "full_name": "New User", "role": "receptionist"},
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 201
    assert resp.json()["username"] == "new_user"


def test_me(client, admin_token):
    resp = client.get("/auth/me", headers=auth_header(admin_token))
    assert resp.status_code == 200
    assert resp.json()["role"] == "admin"
