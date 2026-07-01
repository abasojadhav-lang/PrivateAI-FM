import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        self.endpoint = "https://api.open-meteo.com/v1/forecast"

    def _map_weather_code(self, code: int) -> str:
        # WMO Weather interpretation codes (WW)
        codes = {
            0: "clear sky",
            1: "mainly clear",
            2: "partly cloudy",
            3: "overcast",
            45: "foggy",
            48: "depositing rime fog",
            51: "light drizzle",
            53: "moderate drizzle",
            55: "dense drizzle",
            56: "light freezing drizzle",
            57: "dense freezing drizzle",
            61: "slight rain",
            63: "moderate rain",
            65: "heavy rain",
            66: "light freezing rain",
            67: "heavy freezing rain",
            71: "slight snow fall",
            73: "moderate snow fall",
            75: "heavy snow fall",
            77: "snow grains",
            80: "slight rain showers",
            81: "moderate rain showers",
            82: "violent rain showers",
            85: "slight snow showers",
            86: "heavy snow showers",
            95: "a thunderstorm",
            96: "a thunderstorm with slight hail",
            99: "a thunderstorm with heavy hail",
        }
        return codes.get(code, "unknown weather")

    async def get_weather(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        url = f"{self.endpoint}?latitude={lat}&longitude={lon}&current_weather=true"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    current = data.get("current_weather", {})
                    temp = current.get("temperature")
                    code = current.get("weathercode")
                    
                    if temp is not None and code is not None:
                        return {
                            "temperature": temp,
                            "condition": self._map_weather_code(code),
                            "windspeed": current.get("windspeed"),
                        }
            except Exception as e:
                logger.error(f"Failed to fetch weather from Open-Meteo: {str(e)}")
        return None

weather_service = WeatherService()
