import pytest
from fastapi.testclient import TestClient

from src.app.main import app
from src.domain.models import User, UserRole


@pytest.fixture()
def client():
    test_client = TestClient(app)
    yield test_client


def test_register_success(client):
    r = client.post(
        "/api/v1/auth/register", json={"username": "alice", "password": "12345678"}
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_success(client):
    client.post(
        "/api/v1/auth/register", json={"username": "bob", "password": "password123"}
    )
    r = client.post(
        "/api/v1/auth/login", json={"username": "bob", "password": "password123"}
    )
    assert r.status_code == 200, r.text
    assert "access_token" in r.json()


def test_logout_success(client):
    reg = client.post(
        "/api/v1/auth/register", json={"username": "carol", "password": "password123"}
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = client.post("/api/v1/auth/logout", headers=headers)
    assert r.status_code == 204


def test_admin_promote_user_success(client, session):
    admin = User(username="admin", password_hash="hash", role=UserRole.admin)
    session.add(admin)
    user = User(username="dave", password_hash="hash", role=UserRole.user)
    session.add(user)
    session.commit()

    r = client.post("/api/v1/auth/login", json={"username": "dave", "password": "hash"})
    from src.app.security import create_access_token

    token = create_access_token({"sub": str(admin.id), "role": "admin"})
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post("/api/v1/auth/promote/dave", headers=headers)
    assert r.status_code == 200

    assert "access_token" in r.json()
    refreshed = session.get(User, user.id)
    assert refreshed.role == UserRole.admin


# ---------- Негативные сценарии ----------


@pytest.mark.parametrize(
    "username,password",
    [
        ("ab", "password123"),
        ("a" * 101, "password123"),
        ("validname", "short"),
    ],
)
def test_register_invalid_length(client, username, password):
    r = client.post(
        "/api/v1/auth/register", json={"username": username, "password": password}
    )
    assert r.status_code in (400, 422), r.text
    assert "length" in r.text or "too short" in r.text.lower()


def test_register_duplicate_user(client):
    client.post(
        "/api/v1/auth/register", json={"username": "dupe", "password": "password123"}
    )
    r = client.post(
        "/api/v1/auth/register", json={"username": "dupe", "password": "newpassword456"}
    )
    assert r.status_code == 400
    assert "already exists" in r.text


def test_register_invalid_payload(client):
    r = client.post("/api/v1/auth/register", json={"username": "no_pass"})
    assert r.status_code in (400, 422)


def test_login_invalid_credentials(client):
    client.post(
        "/api/v1/auth/register", json={"username": "eva", "password": "password123"}
    )
    r = client.post(
        "/api/v1/auth/login", json={"username": "eva", "password": "wrongpass"}
    )
    assert r.status_code in (401, 403)


def test_login_user_not_found(client):
    r = client.post(
        "/api/v1/auth/login", json={"username": "ghost", "password": "password123"}
    )
    assert r.status_code in (401, 403)


def test_logout_invalid_token(client):
    headers = {"Authorization": "Bearer invalid_token_123"}
    r = client.post("/api/v1/auth/logout", headers=headers)
    assert r.status_code == 401


def test_promote_by_non_admin(client, session):
    user = User(username="bob", password_hash="hash", role=UserRole.user)
    target = User(username="charlie", password_hash="hash", role=UserRole.user)
    session.add(user)
    session.add(target)
    session.commit()

    from src.app.security import create_access_token

    token = create_access_token({"sub": str(user.id), "role": "user"})
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post("/api/v1/auth/promote/charlie", headers=headers)
    assert r.status_code == 403
    assert "Only admins" in r.text


def test_promote_nonexistent_user(client, session):
    admin = User(username="root", password_hash="hash", role=UserRole.admin)
    session.add(admin)
    session.commit()

    from src.app.security import create_access_token

    token = create_access_token({"sub": str(admin.id), "role": "admin"})
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post("/api/v1/auth/promote/unknown_user", headers=headers)
    assert r.status_code == 401 or r.status_code == 404
    assert "not found" in r.text
