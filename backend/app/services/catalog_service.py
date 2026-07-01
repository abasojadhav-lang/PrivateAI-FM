from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import httpx
from app.core.config import settings

class TrackMetadata:
    def __init__(
        self,
        title: str,
        artist: str,
        album: Optional[str] = None,
        duration: int = 180,  # default in seconds
        spotify_id: Optional[str] = None,
        youtube_id: Optional[str] = None,
        cover_url: Optional[str] = None,
        genre: Optional[str] = None
    ):
        self.title = title
        self.artist = artist
        self.album = album
        self.duration = duration
        self.spotify_id = spotify_id
        self.youtube_id = youtube_id
        self.cover_url = cover_url
        self.genre = genre

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "duration": self.duration,
            "spotify_id": self.spotify_id,
            "youtube_id": self.youtube_id,
            "cover_url": self.cover_url,
            "genre": self.genre
        }

class BaseCatalogService(ABC):
    @abstractmethod
    async def search_tracks(self, query: str, limit: int = 10) -> List[TrackMetadata]:
        """Search music catalog for tracks matching query"""
        pass

    @abstractmethod
    async def get_track_by_id(self, track_id: str) -> Optional[TrackMetadata]:
        """Fetch details of a single track by its ID"""
        pass


class SpotifyCatalogService(BaseCatalogService):
    def __init__(self):
        self.client_id = settings.SPOTIFY_CLIENT_ID
        self.client_secret = settings.SPOTIFY_CLIENT_SECRET
        self.access_token: Optional[str] = None

    async def _authenticate(self) -> bool:
        if not self.client_id or not self.client_secret or self.client_id == "mock_spotify_id":
            return False
        
        url = "https://accounts.spotify.com/api/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, data=data)
                if response.status_code == 200:
                    self.access_token = response.json().get("access_token")
                    return True
            except Exception:
                pass
        return False

    async def search_tracks(self, query: str, limit: int = 10) -> List[TrackMetadata]:
        if not self.access_token:
            authenticated = await self._authenticate()
            if not authenticated:
                return self._get_mock_tracks(query, limit)

        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit={limit}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                tracks = response.json().get("tracks", {}).get("items", [])
                results = []
                for item in tracks:
                    album = item.get("album", {})
                    artists = item.get("artists", [])
                    artist_name = artists[0].get("name") if artists else "Unknown Artist"
                    images = album.get("images", [])
                    cover_url = images[0].get("url") if images else None
                    
                    results.append(
                        TrackMetadata(
                            title=item.get("name"),
                            artist=artist_name,
                            album=album.get("name"),
                            duration=int(item.get("duration_ms", 0) / 1000),
                            spotify_id=item.get("id"),
                            cover_url=cover_url
                        )
                    )
                return results
            
        return self._get_mock_tracks(query, limit)

    async def get_track_by_id(self, track_id: str) -> Optional[TrackMetadata]:
        if not self.access_token:
            authenticated = await self._authenticate()
            if not authenticated:
                return None

        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"https://api.spotify.com/v1/tracks/{track_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                item = response.json()
                album = item.get("album", {})
                artists = item.get("artists", [])
                artist_name = artists[0].get("name") if artists else "Unknown Artist"
                images = album.get("images", [])
                cover_url = images[0].get("url") if images else None
                
                return TrackMetadata(
                    title=item.get("name"),
                    artist=artist_name,
                    album=album.get("name"),
                    duration=int(item.get("duration_ms", 0) / 1000),
                    spotify_id=item.get("id"),
                    cover_url=cover_url
                )
        return None

    def _get_mock_tracks(self, query: str, limit: int) -> List[TrackMetadata]:
        # Return mock results for testing without credentials
        mock_library = [
            TrackMetadata("Blinding Lights", "The Weeknd", "After Hours", 200, "spotify_blinding", "yt_blinding", "https://i.scdn.co/image/ab67616d0000b2738863d6e38f6c12a9c68210d4", "Synthwave"),
            TrackMetadata("As It Was", "Harry Styles", "Harry's House", 167, "spotify_asitwas", "yt_asitwas", "https://i.scdn.co/image/ab67616d0000b273b46b730da962df2f17045b85", "Indie Pop"),
            TrackMetadata("Shape of You", "Ed Sheeran", "Divide", 233, "spotify_shapeofyou", "yt_shapeofyou", "https://i.scdn.co/image/ab67616d0000b273ba5db46f4b83884b27e6a002", "Pop"),
            TrackMetadata("Levitating", "Dua Lipa", "Future Nostalgia", 203, "spotify_levitating", "yt_levitating", "https://i.scdn.co/image/ab67616d0000b273bd54e7d46c8793b8ec862590", "Dance Pop"),
            TrackMetadata("STAY", "The Kid LAROI & Justin Bieber", "F*CK LOVE 3", 141, "spotify_stay", "yt_stay", "https://i.scdn.co/image/ab67616d0000b27341e309eed84b008d2a722f4d", "Pop Rock"),
        ]
        
        filtered = [t for t in mock_library if query.lower() in t.title.lower() or query.lower() in t.artist.lower()]
        return (filtered if filtered else mock_library)[:limit]


class YouTubeMusicCatalogService(BaseCatalogService):
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY

    async def search_tracks(self, query: str, limit: int = 10) -> List[TrackMetadata]:
        if not self.api_key or self.api_key == "mock_youtube_key":
            return self._get_mock_tracks(query, limit)

        # Query YouTube API v3 search endpoint
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": f"{query} song",
            "type": "video",
            "videoCategoryId": "10",  # Music category
            "key": self.api_key,
            "maxResults": limit
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                items = response.json().get("items", [])
                results = []
                for item in items:
                    snippet = item.get("snippet", {})
                    video_id = item.get("id", {}).get("videoId")
                    title = snippet.get("title")
                    channel_title = snippet.get("channelTitle")  # usually Artist or Artist - Topic
                    thumbnails = snippet.get("thumbnails", {})
                    cover_url = thumbnails.get("high", {}).get("url") or thumbnails.get("default", {}).get("url")
                    
                    results.append(
                        TrackMetadata(
                            title=title,
                            artist=channel_title.replace(" - Topic", ""),
                            youtube_id=video_id,
                            cover_url=cover_url,
                            duration=180 # YouTube search doesn't return video duration directly, requires another API call. Let's default.
                        )
                    )
                return results

        return self._get_mock_tracks(query, limit)

    async def get_track_by_id(self, track_id: str) -> Optional[TrackMetadata]:
        if not self.api_key or self.api_key == "mock_youtube_key":
            return None
            
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet,contentDetails",
            "id": track_id,
            "key": self.api_key
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                items = response.json().get("items", [])
                if items:
                    item = items[0]
                    snippet = item.get("snippet", {})
                    # Parsing YT duration like PT3M20S is complex; let's mock 180 seconds or do simple parsing if needed
                    # For Phase 1 we will default
                    return TrackMetadata(
                        title=snippet.get("title"),
                        artist=snippet.get("channelTitle").replace(" - Topic", ""),
                        youtube_id=track_id,
                        duration=180
                    )
        return None

    def _get_mock_tracks(self, query: str, limit: int) -> List[TrackMetadata]:
        # Reuse Spotify mock loader since we want consistent mock catalog for testing
        spotify_service = SpotifyCatalogService()
        return spotify_service._get_mock_tracks(query, limit)
