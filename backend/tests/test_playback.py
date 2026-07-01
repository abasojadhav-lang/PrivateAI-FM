import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock

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

async def test_upload_invalid_file_type(client: AsyncClient):
    headers = await _get_auth_headers(client, "uploader1@example.com")
    
    # Attempt to upload a text file
    files = {"file": ("test.txt", b"dummy content", "text/plain")}
    response = await client.post(
        "/api/music/upload",
        files=files,
        headers=headers
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Only MP3 audio files are supported."

async def test_upload_valid_mp3_fallback(client: AsyncClient):
    headers = await _get_auth_headers(client, "uploader2@example.com")
    
    # Tiny dummy MP3 byte sequence (mutagen will fail to read ID3 tags but fallback is tested)
    dummy_mp3_bytes = b"ID3\x03\x00\x00\x00\x00\x00\x00" + b"\x00" * 100
    files = {"file": ("my_favorite_track.mp3", dummy_mp3_bytes, "audio/mpeg")}
    
    response = await client.post(
        "/api/music/upload",
        files=files,
        headers=headers
    )
    assert response.status_code == 201
    song_data = response.json()
    assert song_data["title"] == "my_favorite_track"  # extracted from filename
    assert song_data["artist"] == "Unknown Artist"     # metadata fallback
    assert song_data["duration"] == 180                # metadata default
    assert "storage_url" in song_data

async def test_get_songs_list(client: AsyncClient):
    headers = await _get_auth_headers(client, "songslist@example.com")
    
    # Upload song first
    dummy_mp3 = b"ID3\x03" + b"\x00" * 50
    await client.post(
        "/api/music/upload",
        files={"file": ("test_list.mp3", dummy_mp3, "audio/mpeg")},
        headers=headers
    )
    
    response = await client.get("/api/music/songs", headers=headers)
    assert response.status_code == 200
    songs = response.json()
    assert len(songs) >= 1
    assert songs[0]["title"] == "test_list"
    assert "stream_url" in songs[0]
    assert songs[0]["stream_url"].startswith("/api/music/file/")

async def test_get_radio_queue_structure(client: AsyncClient):
    headers = await _get_auth_headers(client, "queue@example.com")
    
    # Fetch radio queue (should generate mock songs under the hood if DB is empty, or mix from db)
    response = await client.get("/api/playback/queue", headers=headers)
    assert response.status_code == 200
    queue = response.json()
    
    assert len(queue) == 10  # 5 songs + 5 speech slots
    
    # Alternating types check: song -> speech (dj/weather/news) -> song
    for i, item in enumerate(queue):
        assert "queue_id" in item
        assert "stream_url" in item
        assert "duration" in item
        
        if i % 2 == 0:
            assert item["type"] == "song"
            assert item["transcript"] == ""
        else:
            assert item["type"] in ["dj", "weather", "news", "traffic"]
            assert item["transcript"] != ""
            assert item["artist"] == "AI Radio Service"

async def test_telemetry_history(client: AsyncClient):
    headers = await _get_auth_headers(client, "telemetry@example.com")
    
    response = await client.post(
        "/api/playback/history?song_id=1005&skipped=true&duration_played=45",
        headers=headers
    )
    assert response.status_code == 201
    assert response.json()["status"] == "success"
