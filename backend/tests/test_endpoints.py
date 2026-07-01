import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def _get_auth_headers(client: AsyncClient, email: str) -> dict:
    await client.post(
        "/api/auth/register",
        json={"email": email, "password": "password123"}
    )
    login_response = await client.post(
        "/api/auth/login",
        json={"email": email, "password": "password123"}
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

async def test_create_and_list_stations(client: AsyncClient):
    headers = await _get_auth_headers(client, "station@example.com")
    
    # Create station
    station_payload = {
        "name": "Workout Mix",
        "mood": "Energetic",
        "music_preferences": {"genres": ["Rock", "Metal"]},
        "voice_config": {"personality": "Funny", "voice_name": "Antigravity DJ"}
    }
    create_response = await client.post(
        "/api/stations",
        json=station_payload,
        headers=headers
    )
    assert create_response.status_code == 201
    created_data = create_response.json()
    assert created_data["name"] == "Workout Mix"
    assert created_data["mood"] == "Energetic"
    assert "id" in created_data
    
    # List stations
    list_response = await client.get("/api/stations", headers=headers)
    assert list_response.status_code == 200
    stations = list_response.json()
    assert len(stations) == 1
    assert stations[0]["name"] == "Workout Mix"

async def test_search_catalog(client: AsyncClient):
    headers = await _get_auth_headers(client, "catalog@example.com")
    
    # Search spotify catalog (uses mock list under the hood when credentials are empty)
    response = await client.get(
        "/api/catalog/search?q=Blinding&provider=spotify",
        headers=headers
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert any(track["title"] == "Blinding Lights" for track in results)

async def test_search_catalog_unauthorized(client: AsyncClient):
    response = await client.get("/api/catalog/search?q=Blinding&provider=spotify")
    assert response.status_code == 401
