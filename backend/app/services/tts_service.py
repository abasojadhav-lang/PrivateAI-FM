import base64
import httpx
import logging
import uuid
from typing import Optional
from app.core.config import settings
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self):
        self.api_key = settings.GCLOUD_TTS_API_KEY
        self.endpoint = "https://texttospeech.googleapis.com/v1/text:synthesize"

    async def synthesize_speech(self, text: str, voice_gender: str = "Female") -> str:
        """Synthesize text to speech using Google Cloud TTS, upload to storage, and return storage key."""
        
        # If API key is not configured, fallback immediately
        if not self.api_key or self.api_key == "mock_tts_key":
            logger.info("GCloud TTS API key not set. Using placeholder voice file.")
            return "local://speech_placeholder.mp3"
            
        url = f"{self.endpoint}?key={self.api_key}"
        
        # Choose voice name based on configured gender
        voice_name = "en-US-Neural2-F" if voice_gender.lower() == "female" else "en-US-Neural2-M"
        
        payload = {
            "input": {"text": text},
            "voice": {
                "languageCode": "en-US",
                "name": voice_name
            },
            "audioConfig": {
                "audioEncoding": "MP3",
                "speakingRate": 1.0,
                "pitch": 0.0
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=8.0)
                if response.status_code == 200:
                    data = response.json()
                    audio_content_b64 = data.get("audioContent", "")
                    audio_bytes = base64.b64decode(audio_content_b64)
                    
                    # Generate a unique storage name for this TTS file
                    unique_filename = f"tts_{uuid.uuid4()}.mp3"
                    
                    # Save to storage (S3 or fallback)
                    storage_key = await storage_service.upload_file(audio_bytes, unique_filename)
                    return storage_key
            except Exception as e:
                logger.error(f"Google Cloud TTS synthesis failed: {str(e)}")
                
        # Return fallback if API fails
        return "local://speech_placeholder.mp3"

    async def create_placeholder_file_if_missing(self):
        """Creates a short silent dummy audio file on local disk to act as the speech placeholder."""
        fallback_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "static_storage"
        )
        os.makedirs(fallback_dir, exist_ok=True)
        placeholder_path = os.path.join(fallback_dir, "speech_placeholder.mp3")
        
        # If it doesn't exist, write a tiny dummy silent MP3 file (100 bytes)
        if not os.path.exists(placeholder_path):
            try:
                dummy_mp3 = b"ID3\x03\x00\x00\x00\x00\x00\x00" + b"\x00" * 100
                with open(placeholder_path, "wb") as f:
                    f.write(dummy_mp3)
                logger.info(f"Created local fallback voice placeholder at: {placeholder_path}")
            except Exception as e:
                logger.error(f"Failed to create dummy voice placeholder: {str(e)}")

import os
tts_service = TTSService()

