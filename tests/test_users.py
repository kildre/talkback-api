import pytest

# Minimal payload matching UserCreate schema (required fields only)
user_create_payload = {
    "first_name": "Test",
    "last_name": "User",
    "email": "testuser1@test.com",
    "password": "testpass123",
}


async def seed_data(client):
    client.post("/users/", json=user_create_payload)


@pytest.mark.asyncio
async def test_create_user(client):
    response = client.post("/users/", json=user_create_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == user_create_payload["first_name"]
    assert data["last_name"] == user_create_payload["last_name"]
    assert data["email"] == user_create_payload["email"]
    assert data["display_name"] == "Test User"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_get_all_users(client):
    await seed_data(client)
    response = client.get("/users")
    assert response.status_code == 200
    assert len(response.json()) > 0


@pytest.mark.asyncio
async def test_get_users_paged(client):
    await seed_data(client)
    response = client.get("/users?page_number=0&page_size=10")
    assert response.status_code == 200
    assert len(response.json()) > 0


@pytest.mark.asyncio
async def test_get_user(client):
    await seed_data(client)
    response = client.get("/users/1")
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == user_create_payload["first_name"]
    assert data["email"] == user_create_payload["email"]


@pytest.mark.asyncio
async def test_update_user(client):
    await seed_data(client)
    response = client.put("/users/1", json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False


@pytest.mark.asyncio
async def test_update_user_invalid_id(client):
    await seed_data(client)
    response = client.put("/users/-1", json={"is_active": False})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_user(client):
    await seed_data(client)
    response = client.delete("/users/1")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_user_invalid_id(client):
    await seed_data(client)
    response = client.delete("/users/-1")
    assert response.status_code == 404
