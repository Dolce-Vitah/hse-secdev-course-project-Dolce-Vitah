import pytest

API_PREFIX = "/api/v1/wishes/"


def test_create_wish_success(client_with_user):
    payload = {
        "title": "New Wish",
        "notes": "Test description",
        "price_estimate": 100.0,
        "link": "https://example.com",
    }
    response = client_with_user.post(API_PREFIX, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["notes"] == payload["notes"]
    assert data["price_estimate"] == payload["price_estimate"]
    assert data["link"].rstrip("/") == payload["link"].rstrip("/")


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"notes": "Missing title"},
        {"title": "", "notes": "Empty title"},
    ],
)
def test_create_wish_invalid(client_with_user, payload):
    response = client_with_user.post(API_PREFIX, json=payload)
    assert response.status_code == 422


def test_create_wish_negative_price(client_with_user):
    payload = {"title": "Invalid Wish", "price_estimate": -10}
    response = client_with_user.post(API_PREFIX, json=payload)
    assert response.status_code == 422


def test_create_wish_invalid_link(client_with_user):
    payload = {"title": "Wish", "link": "not-a-url"}
    response = client_with_user.post(API_PREFIX, json=payload)
    assert response.status_code == 422


def test_create_wish_unauthorized(client):
    payload = {"title": "Wish"}
    response = client.post(API_PREFIX, json=payload)
    assert response.status_code == 403


def test_list_wishes_empty(client_with_user):
    response = client_with_user.get(API_PREFIX)
    assert response.status_code == 200
    assert response.json() == []


def test_list_wishes_with_data(client_with_user):
    client_with_user.post(API_PREFIX, json={"title": "Wish 1"})
    client_with_user.post(API_PREFIX, json={"title": "Wish 2"})

    response = client_with_user.get(API_PREFIX)
    data = response.json()
    assert len(data) >= 2
    titles = [w["title"] for w in data]
    assert "Wish 1" in titles
    assert "Wish 2" in titles


def test_list_wishes_filter_price(client_with_user):
    client_with_user.post(API_PREFIX, json={"title": "Cheap", "price_estimate": 50})
    client_with_user.post(
        API_PREFIX, json={"title": "Expensive", "price_estimate": 200}
    )

    response = client_with_user.get(API_PREFIX, params={"price": 100})
    data = response.json()
    assert all(w["price_estimate"] <= 100 for w in data)


def test_list_wishes_unauthorized(client):
    response = client.get(API_PREFIX)
    assert response.status_code == 403


def test_get_wish_success(client_with_user):
    r = client_with_user.post(API_PREFIX, json={"title": "Single Wish"})
    wish_id = r.json()["id"]

    response = client_with_user.get(f"{API_PREFIX}{wish_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Single Wish"


def test_get_wish_not_found(client_with_user):
    response = client_with_user.get(f"{API_PREFIX}9999")
    assert response.status_code == 404


def test_get_wish_forbidden(client_with_user, client, another_user):
    payload = {"title": "Private Wish", "notes": "Secret wish"}
    response = client_with_user.post(API_PREFIX, json=payload)
    assert response.status_code == 200, f"Unexpected: {response.text}"
    wish_id = response.json()["id"]

    from src.app.main import app
    from src.app.security import get_current_user

    app.dependency_overrides[get_current_user] = lambda: another_user["user"]

    forbidden_response = client.get(f"{API_PREFIX}{wish_id}")

    assert forbidden_response.status_code == 404, (
        f"Expected 404, got {forbidden_response.status_code}. "
        f"Response: {forbidden_response.text}"
    )

    app.dependency_overrides.clear()


def test_update_wish_success(client_with_user):
    r = client_with_user.post(API_PREFIX, json={"title": "Old Title"})
    wish_id = r.json()["id"]

    payload = {"title": "Updated Title", "notes": "Updated notes"}
    response = client_with_user.patch(f"{API_PREFIX}{wish_id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["notes"] == "Updated notes"


def test_update_wish_forbidden(client_with_user, another_user, client):
    create_response = client_with_user.post(
        API_PREFIX, json={"title": "Original Title"}
    )
    assert (
        create_response.status_code == 200
    ), f"Create response: {create_response.json()}"
    wish_id = create_response.json()["id"]

    from src.app.main import app
    from src.app.security import get_current_user

    app.dependency_overrides[get_current_user] = lambda: another_user["user"]

    update_data = {"title": "Hacked Title"}
    update_response = client.patch(f"{API_PREFIX}{wish_id}", json=update_data)

    assert (
        update_response.status_code == 404
    ), f"Update response: {update_response.json()}"

    app.dependency_overrides.clear()


def test_update_wish_invalid_data(client_with_user):
    r = client_with_user.post(API_PREFIX, json={"title": "Title"})
    wish_id = r.json()["id"]

    payload = {"title": ""}
    response = client_with_user.patch(f"{API_PREFIX}{wish_id}", json=payload)
    assert response.status_code == 422


def test_delete_wish_success(client_with_user):
    r = client_with_user.post(API_PREFIX, json={"title": "To Delete"})
    wish_id = r.json()["id"]

    response = client_with_user.delete(f"{API_PREFIX}{wish_id}")
    assert response.status_code == 200
    # Проверяем, что wish больше не существует
    r2 = client_with_user.get(f"{API_PREFIX}{wish_id}")
    assert r2.status_code == 404


def test_delete_wish_forbidden(client_with_user, another_user, client):
    r = client_with_user.post(API_PREFIX, json={"title": "Private"})
    assert r.status_code == 200, f"Response JSON: {r.json()}"
    wish_id = r.json()["id"]

    from src.app.main import app
    from src.app.security import get_current_user

    app.dependency_overrides[get_current_user] = lambda: another_user["user"]

    response = client.delete(f"{API_PREFIX}{wish_id}")

    assert response.status_code == 404, f"Response JSON: {response.json()}"

    app.dependency_overrides.clear()


def test_delete_wish_not_found(client_with_user):
    response = client_with_user.delete(f"{API_PREFIX}9999")
    assert response.status_code == 404
