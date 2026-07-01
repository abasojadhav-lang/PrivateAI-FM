import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock
from app.services.weather_service import weather_service
from app.services.news_service import news_service
from app.services.traffic_service import traffic_service

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

# Test 1: Weather Service parsing and mapping
async def test_weather_service_success():
    mock_response_data = {
        "current_weather": {
            "temperature": 27.5,
            "weathercode": 3,
            "windspeed": 12.0
        }
    }
    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_response_data
        mock_get.return_value = mock_resp
        
        weather = await weather_service.get_weather(18.5204, 73.8567)
        assert weather is not None
        assert weather["temperature"] == 27.5
        assert weather["condition"] == "overcast"

async def test_weather_service_failure():
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = Exception("Connection error")
        weather = await weather_service.get_weather(18.5204, 73.8567)
        assert weather is None

# Test 2: RSS News Service parsing
async def test_news_service_success():
    mock_rss_xml = b"""<rss version="2.0">
        <channel>
            <item><title>Google announces Gemini 1.5 - TechCrunch</title></item>
            <item><title>SpaceX launches new satellite constellation - Reuters</title></item>
        </channel>
    </rss>"""
    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = mock_rss_xml
        mock_get.return_value = mock_resp
        
        headlines = await news_service.get_headlines()
        assert len(headlines) == 2
        assert headlines[0] == "Google announces Gemini 1.5"
        assert headlines[1] == "SpaceX launches new satellite constellation"

async def test_news_service_failure():
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = Exception("RSS feed offline")
        headlines = await news_service.get_headlines()
        # Should return fallback headlines
        assert len(headlines) > 0
        assert headlines == news_service.fallback_headlines

# Test 3: Traffic Service routing mapping
async def test_traffic_service():
    # Test close match to Pune
    pune_traffic = traffic_service.get_traffic_report(18.53, 73.86)
    assert pune_traffic["city"] == "Pune"
    assert "pune" in pune_traffic["summary"].lower()
    
    # Test close match to London
    london_traffic = traffic_service.get_traffic_report(51.51, -0.13)
    assert london_traffic["city"] == "London"
    assert "london" in london_traffic["summary"].lower()
    
    # Test default fallback
    unknown_traffic = traffic_service.get_traffic_report(0.0, 0.0)
    assert unknown_traffic["city"] == "your area"

# Test 4: Queue endpoint with coordinates arguments
async def test_queue_with_coordinates(client: AsyncClient):
    headers = await _get_auth_headers(client, "coordtest@example.com")
    
    # Request queue passing London GPS coordinates
    response = await client.get("/api/playback/queue?lat=51.5074&lon=-0.1278", headers=headers)
    assert response.status_code == 200
    queue = response.json()
    
    assert len(queue) == 10
    # Verify the speech blocks are present
    speech_items = [item for item in queue if item["type"] != "song"]
    assert len(speech_items) > 0
    # Every speech item must have a non-empty transcript
    for item in speech_items:
        assert item["transcript"] != ""
