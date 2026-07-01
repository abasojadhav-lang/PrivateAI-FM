import pytest
import base64
from unittest.mock import patch, AsyncMock
from app.services.gemini_service import gemini_service
from app.services.tts_service import tts_service

pytestmark = pytest.mark.asyncio

async def test_gemini_fallback_without_key():
    # Ensure fallback works when key is empty
    with patch.object(gemini_service, 'api_key', None):
        commentary = await gemini_service.generate_dj_commentary("Calm", "Song A", "Artist B")
        assert len(commentary) > 0
        # Should contain Calm vocabulary
        calm_words = ["glide", "gentle", "quiet", "relax", "peaceful", "soft", "breath"]
        assert any(word in commentary.lower() for word in calm_words)

async def test_tts_fallback_without_key():
    # Ensure fallback works when key is empty
    with patch.object(tts_service, 'api_key', None):
        key = await tts_service.synthesize_speech("Hello world")
        assert key == "local://speech_placeholder.mp3"

async def test_gemini_api_call_success():
    # Mock successful Gemini API response
    with patch.object(gemini_service, 'api_key', "fake_key"):
        mock_response = "Here is a custom generated script by Gemini!"
        with patch.object(gemini_service, '_generate_text', AsyncMock(return_value=mock_response)):
            script = await gemini_service.generate_dj_commentary("Funny", "Song A", "Artist B")
            assert script == mock_response

async def test_tts_api_call_success():
    # Mock successful GCloud TTS API response and upload
    with patch.object(tts_service, 'api_key', "fake_key"):
        dummy_audio_b64 = base64.b64encode(b"dummy_mp3_content").decode("utf-8")
        
        # Patch client.post call inside tts_service
        class MockResponse:
            status_code = 200
            def json(self):
                return {"audioContent": dummy_audio_b64}
                
        mock_post = AsyncMock(return_value=MockResponse())
        
        with patch("httpx.AsyncClient.post", mock_post):
            # Patch storage upload to return a mock key
            with patch("app.services.storage_service.storage_service.upload_file", AsyncMock(return_value="tts_mocked.mp3")):
                key = await tts_service.synthesize_speech("Read this text aloud", "Male")
                assert key == "tts_mocked.mp3"
