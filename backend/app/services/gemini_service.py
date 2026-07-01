import httpx
import logging
from typing import Optional
from app.core.config import settings
from app.services.script_engine import script_engine

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    async def _generate_text(self, prompt: str) -> Optional[str]:
        if not self.api_key:
            return None
            
        url = f"{self.endpoint}?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 60,
                "temperature": 0.7
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    # Clean up quotes if returned
                    return text.strip('"').strip("'")
            except Exception as e:
                logger.error(f"Gemini API request failed: {str(e)}")
        return None

    async def generate_dj_commentary(self, personality: str, song_title: str, artist: str) -> str:
        prompt = (
            f"You are a professional radio host with a '{personality}' personality. "
            f"Talk to the listener in 1 or 2 sentences (under 35 words). "
            f"You just played the song '{song_title}' by {artist} and are transitioning to the next track. "
            f"Do not include placeholders, emojis, brackets, or mention your personality name. Speak naturally."
        )
        
        script = await self._generate_text(prompt)
        if script:
            return script
            
        # Fallback to local script engine if Gemini fails or is not configured
        return script_engine.generate_dj_commentary(personality, song_title, artist)

    async def generate_weather_report(self, personality: str, location: str = "Pune", temperature: float = 29.0, condition: str = "sunny") -> str:
        prompt = (
            f"You are a professional radio host with a '{personality}' personality. "
            f"Give a short, friendly weather update for {location} in 1 or 2 sentences (under 30 words). "
            f"Mention it is currently {temperature} degrees Celsius and {condition}. "
            f"Do not include placeholders, emojis, brackets, or mention your personality name. Speak naturally."
        )
        
        script = await self._generate_text(prompt)
        if script:
            return script
            
        # Fallback
        return script_engine.generate_weather_report(personality, location)

    async def generate_news_brief(self, personality: str, headlines: list[str]) -> str:
        headlines_str = "\n".join(f"- {h}" for h in headlines)
        prompt = (
            f"You are a professional radio host with a '{personality}' personality. "
            f"Read a single, short news brief summarizing the following headlines in 1 or 2 sentences (under 35 words): "
            f"\n{headlines_str}\n"
            f"Do not plagiarize. Rewrite the update in your own words. "
            f"Do not include placeholders, emojis, brackets, or mention your personality name. Speak naturally."
        )
        
        script = await self._generate_text(prompt)
        if script:
            return script
            
        # Fallback
        return script_engine.generate_news_brief(personality)

    async def generate_traffic_report(self, personality: str, location: str, incident: str) -> str:
        prompt = (
            f"You are a professional radio host with a '{personality}' personality. "
            f"Give a short traffic update for {location} in 1 or 2 sentences (under 30 words). "
            f"Mention the traffic condition: '{incident}'. "
            f"Do not include placeholders, emojis, brackets, or mention your personality name. Speak naturally."
        )
        
        script = await self._generate_text(prompt)
        if script:
            return script
            
        # Fallback
        return f"Here is your traffic update for {location}: Expect {incident}."

gemini_service = GeminiService()
