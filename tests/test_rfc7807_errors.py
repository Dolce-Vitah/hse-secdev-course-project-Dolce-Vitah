import pytest
from fastapi.testclient import TestClient

from src.app.main import app


@pytest.fixture()
def client():
    return TestClient(app)


def assert_problem_response(resp, expected_status: int, expected_title: str = None):
    assert resp.status_code == expected_status, resp.text
    data = resp.json()
    assert data["type"] == "about:blank"
    assert "title" in data
    assert "status" in data
    assert "detail" in data
    assert "correlation_id" in data
    if expected_title:
        assert expected_title.lower() in data["title"].lower()
    return data


def test_register_duplicate_user_returns_problem_details(client):
    client.post(
        "/api/v1/auth/register", json={"username": "alice", "password": "Password123_"}
    )
    resp = client.post(
        "/api/v1/auth/register", json={"username": "alice", "password": "Password123_"}
    )
    problem = assert_problem_response(resp, 400, "user_already_exists")
    assert "Username" in problem["detail"]


def test_login_invalid_credentials_problem_details(client):
    client.post(
        "/api/v1/auth/register", json={"username": "bob", "password": "Password123_"}
    )
    resp = client.post(
        "/api/v1/auth/login", json={"username": "bob", "password": "WrongPassword123_"}
    )
    problem = assert_problem_response(resp, 401)
    assert "Invalid credentials" in problem["detail"]


def test_unauthorized_access_problem_details(client):
    resp = client.post(
        "/api/v1/auth/logout", headers={"Authorization": "Bearer invalid_token"}
    )
    problem = assert_problem_response(resp, 401)
    assert "Invalid" in problem["detail"] or "token" in problem["detail"]
