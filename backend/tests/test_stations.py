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

async def test_stations_crud_ops(client: AsyncClient):
    headers = await _get_auth_headers(client, "stationcrud@example.com")
    
    # 1. Create Station
    create_payload = {
        "name": "Morning Chill",
        "mood": "Calm",
        "music_preferences": {"genres": ["Jazz", "Classical"]},
        "voice_config": {"personality": "Calm", "voice": "Female", "news_frequency": "Medium", "weather_frequency": "Low"}
    }
    create_res = await client.post("/api/stations", json=create_payload, headers=headers)
    assert create_res.status_code == 201
    station_data = create_res.json()
    station_id = station_data["id"]
    assert station_data["name"] == "Morning Chill"
    assert station_data["mood"] == "Calm"
    assert station_data["voice_config"]["personality"] == "Calm"
    
    # 2. Update Station
    update_payload = {
        "name": "Evening Jazz",
        "mood": "Relaxing",
        "music_preferences": {"genres": ["Jazz"]},
        "voice_config": {"personality": "Calm", "voice": "Female", "news_frequency": "High", "weather_frequency": "Off"}
    }
    update_res = await client.put(f"/api/stations/{station_id}", json=update_payload, headers=headers)
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["name"] == "Evening Jazz"
    assert updated_data["mood"] == "Relaxing"
    
    # 3. Dynamic Script queue check for "Calm" personality
    queue_res = await client.get(f"/api/playback/queue?station_id={station_id}", headers=headers)
    assert queue_res.status_code == 200
    queue = queue_res.json()
    
    # Look for DJ or Speech items in the queue and verify they match "Calm" scripts
    speech_items = [item for item in queue if item["type"] in ["dj", "weather", "news"]]
    assert len(speech_items) > 0
    # Calm scripts have words like "glide", "gentle", "quiet", "relax", "peaceful"
    calm_vocabulary = ["glide", "gentle", "quiet", "relax", "peaceful", "soft", "breath"]
    has_calm_speech = False
    for item in speech_items:
        transcript = item["transcript"].lower()
        if any(word in transcript for word in calm_vocabulary):
            has_calm_speech = True
            break
    assert has_calm_speech, "Speech script did not match the Calm personality vocabulary presets."

    # 4. Delete Station
    delete_res = await client.delete(f"/api/stations/{station_id}", headers=headers)
    assert delete_res.status_code == 204
    
    # Verify deletion by listing
    list_res = await client.get("/api/stations", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 0
