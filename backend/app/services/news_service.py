import httpx
import logging
import xml.etree.ElementTree as ET
from typing import List

logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self):
        self.rss_url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
        # Standard fallback headlines in case RSS fetch fails
        self.fallback_headlines = [
            "Global tech companies announce new open-source AI safety protocols.",
            "Local community centers launch weekend volunteer programs for urban gardening.",
            "Astronomers discover a new earth-sized exoplanet in a nearby star system.",
            "Research suggests regular short walks significantly boost creative thinking.",
            "Renewable energy capacity saw record growth over the past fiscal quarter."
        ]

    async def get_headlines(self) -> List[str]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.rss_url, timeout=5.0)
                if response.status_code == 200:
                    root = ET.fromstring(response.content)
                    headlines = []
                    # RSS structure: channel -> item -> title
                    for item in root.findall(".//item")[:5]:
                        title_el = item.find("title")
                        if title_el is not None and title_el.text:
                            # Clean up publisher suffix (e.g. "Headline - Source")
                            title = title_el.text
                            if " - " in title:
                                title = title.rsplit(" - ", 1)[0]
                            headlines.append(title.strip())
                    if headlines:
                        return headlines
            except Exception as e:
                logger.error(f"Failed to fetch or parse news RSS: {str(e)}")
        
        return self.fallback_headlines

news_service = NewsService()
