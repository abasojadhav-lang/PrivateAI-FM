import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_register_user(client: AsyncClient):
    response = await client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "hashed_password" not in data

async def test_register_duplicate_email(client: AsyncClient):
    # First registration
    await client.post(
        "/api/auth/register",
        json={"email": "duplicate@example.com", "password": "password123"}
    )
    # Duplicate registration
    response = await client.post(
        "/api/auth/register",
        json={"email": "duplicate@example.com", "password": "password999"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "A user with this email already exists."

async def test_login_user(client: AsyncClient):
    # Register first
    await client.post(
        "/api/auth/register",
        json={"email": "login@example.com", "password": "password123"}
    )
    # Login
    response = await client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

async def test_login_invalid_password(client: AsyncClient):
    # Register first
    await client.post(
        "/api/auth/register",
        json={"email": "wrongpass@example.com", "password": "password123"}
    )
    # Login with wrong password
    response = await client.post(
        "/api/auth/login",
        json={"email": "wrongpass@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password."

async def test_get_current_user(client: AsyncClient):
    # Register and Login
    await client.post(
        "/api/auth/register",
        json={"email": "me@example.com", "password": "password123"}
    )
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "me@example.com", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    
    # Get profile
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"

async def test_get_current_user_unauthorized(client: AsyncClient):
    # Try fetching profile with invalid token
    headers = {"Authorization": "Bearer invalidtoken"}
    response = await client.get("/api/auth/me", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"
