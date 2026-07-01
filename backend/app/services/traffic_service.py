import random
from typing import Dict, Any, List

class TrafficService:
    def __init__(self):
        # Coordinates of major cities for geocoding fallback
        self.cities = [
            {"name": "Pune", "lat": 18.5204, "lon": 73.8567},
            {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777},
            {"name": "Delhi", "lat": 28.6139, "lon": 77.2090},
            {"name": "Bangalore", "lat": 12.9716, "lon": 77.5946},
            {"name": "New York", "lat": 40.7128, "lon": -74.0060},
            {"name": "London", "lat": 51.5074, "lon": -0.1278},
            {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503},
            {"name": "San Francisco", "lat": 37.7749, "lon": -122.4194},
        ]
        
        self.incident_templates = [
            "heavy congestion on Main Street due to a minor accident at the junction",
            "moderate delays on the main bypass expressway caused by ongoing road maintenance work",
            "a complete road closure on Broad Street for the local weekend market, detour routes are active",
            "smooth flow of traffic with no major delays or incidents reported on the principal highways",
            "significant delays on the central flyover route following a vehicle breakdown in the left lane",
        ]

    def _get_closest_city(self, lat: float, lon: float) -> str:
        # Simple Euclidean distance to find nearest city
        closest_city = "your area"
        min_dist = float("inf")
        
        for city in self.cities:
            dist = ((city["lat"] - lat) ** 2 + (city["lon"] - lon) ** 2) ** 0.5
            # If within 1.5 degrees (approx 150 km), map it to that city
            if dist < 1.5 and dist < min_dist:
                min_dist = dist
                closest_city = city["name"]
                
        return closest_city

    def get_traffic_report(self, lat: float, lon: float) -> Dict[str, Any]:
        city = self._get_closest_city(lat, lon)
        # Select incident deterministically or randomly. We'll use a selection based on lat+lon
        idx = int(abs(lat + lon) * 100) % len(self.incident_templates)
        incident = self.incident_templates[idx]
        
        return {
            "city": city,
            "incident": incident,
            "summary": f"Traffic update for {city}: Expect {incident}."
        }

traffic_service = TrafficService()
