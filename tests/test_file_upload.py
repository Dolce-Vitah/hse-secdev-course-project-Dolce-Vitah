import io

from fastapi.testclient import TestClient

from src.app.main import app

client = TestClient(app)


def test_upload_valid_image(auth_headers):
    file_data = io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"0" * 1024)
    response = client.post(
        "/api/v1/wishes/upload",
        files={"file": ("test.png", file_data, "image/png")},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mime"] == "image/png"


def test_upload_invalid_mime(auth_headers):
    file_data = io.BytesIO(b"notanimage")
    response = client.post(
        "/api/v1/wishes/upload",
        files={"file": ("test.txt", file_data, "text/plain")},
        headers=auth_headers,
    )
    assert response.status_code == 415


def test_upload_large_file(auth_headers):
    file_data = io.BytesIO(b"\xff" * (2 * 1024 * 1024 + 1))
    response = client.post(
        "/api/v1/wishes/upload",
        files={"file": ("big.jpg", file_data, "image/jpeg")},
        headers=auth_headers,
    )
    assert response.status_code == 413


def test_upload_invalid_magic_bytes(client_with_user):
    fake_file = io.BytesIO(b"NOTPNG" + b"0" * 1024)
    response = client_with_user.post(
        "/api/v1/wishes/upload",
        files={"file": ("fake.png", fake_file, "image/png")},
    )

    assert response.status_code == 415

    data = response.json()
    assert "File content does not match" in data["detail"]


def test_upload_file_traversal_attempt(client_with_user):
    content = io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"0" * 1024)
    response = client_with_user.post(
        "/api/v1/wishes/upload",
        files={"file": ("../../evil.png", content, "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert ".." not in data["filename"]
    assert data["mime"] == "image/png"
