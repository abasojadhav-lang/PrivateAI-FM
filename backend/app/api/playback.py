import random
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any
from app.core.database import get_db
from app.models.models import Song, PlaybackHistory, User, Station
from app.api.deps import get_current_user
from app.services.storage_service import storage_service
from app.services.gemini_service import gemini_service
from app.services.tts_service import tts_service
from app.services.weather_service import weather_service
from app.services.news_service import news_service
from app.services.traffic_service import traffic_service

router = APIRouter(prefix="/playback", tags=["playback"])

@router.get("/queue", response_model=List[Dict[str, Any]])
async def get_playback_queue(
    station_id: int = Query(None, description="Current active station ID"),
    lat: float = Query(None, description="Latitude of user's current location"),
    lon: float = Query(None, description="Longitude of user's current location"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Fetch station settings if station_id is provided
    genres = []
    personality = "Friendly"
    voice_gender = "Female"
    
    if station_id:
        result = await db.execute(
            select(Station).where(Station.id == station_id, Station.user_id == current_user.id)
        )
        station = result.scalars().first()
        if station:
            genres = station.music_preferences.get("genres", [])
            personality = station.voice_config.get("personality", "Friendly")
            voice_gender = station.voice_config.get("voice", "Female")

    # Fetch location-aware data (weather, news, traffic)
    # Default to Pune coordinates if not provided
    lat_val = lat if lat is not None else 18.5204
    lon_val = lon if lon is not None else 73.8567

    # 1. Fetch weather
    weather = await weather_service.get_weather(lat_val, lon_val)
    if weather:
        temp = weather["temperature"]
        cond = weather["condition"]
    else:
        temp = 29.0
        cond = "sunny"

    # 2. Fetch news
    headlines = await news_service.get_headlines()

    # 3. Fetch traffic
    traffic = traffic_service.get_traffic_report(lat_val, lon_val)
    city_name = traffic["city"]
    traffic_incident = traffic["incident"]

    # Fetch songs in DB
    result = await db.execute(select(Song))
    songs = result.scalars().all()
    
    # Fallback to mock catalog songs if none exist in database
    if not songs:
        from app.services.catalog_service import SpotifyCatalogService
        spotify = SpotifyCatalogService()
        mock_tracks = spotify._get_mock_tracks("Pop", 10)
        # Convert Mock Tracks to a temporary dictionary format
        db_songs = []
        for i, t in enumerate(mock_tracks):
            db_songs.append({
                "id": 1000 + i,
                "title": t.title,
                "artist": t.artist,
                "album": t.album,
                "genre": t.genre or "Pop",
                "duration": t.duration,
                "cover_url": t.cover_url or "https://images.unsplash.com/photo-1614613535308-eb5fbd3d2c17",
                "stream_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"  # standard streamable test MP3
            })
    else:
        db_songs = []
        for s in songs:
            stream_url = await storage_service.get_streaming_url(s.storage_url)
            db_songs.append({
                "id": s.id,
                "title": s.title,
                "artist": s.artist,
                "album": s.album,
                "genre": s.genre or "Pop",
                "duration": s.duration,
                "cover_url": s.cover_url or "https://images.unsplash.com/photo-1614613535308-eb5fbd3d2c17",
                "stream_url": stream_url
            })

    # Filter songs based on station genre preferences if specified
    if genres:
        filtered_songs = [
            s for s in db_songs 
            if any(g.lower() in s["genre"].lower() for g in genres)
        ]
        # Fallback if filtering returns nothing so station doesn't go silent
        if filtered_songs:
            db_songs = filtered_songs

    # Shuffle the songs to create a varied queue
    random.shuffle(db_songs)
    
    queue = []
    item_index = 0
    
    # We will build a queue of 10 items: alternating Song -> Speech -> Song -> Speech
    for s in db_songs[:5]:
        # Append Song
        queue.append({
            "queue_id": f"song_{item_index}",
            "type": "song",
            "id": s["id"],
            "title": s["title"],
            "artist": s["artist"],
            "album": s["album"],
            "duration": s["duration"],
            "cover_url": s["cover_url"],
            "stream_url": s["stream_url"],
            "transcript": ""
        })
        item_index += 1
        
        # Decide what speech block to insert next
        speech_type = random.choice(["dj", "weather", "news", "traffic"])
        
        if speech_type == "dj":
            transcript = await gemini_service.generate_dj_commentary(personality, s["title"], s["artist"])
            title = "AI DJ Commentary"
        elif speech_type == "weather":
            transcript = await gemini_service.generate_weather_report(
                personality, location=city_name, temperature=temp, condition=cond
            )
            title = "Local Weather Update"
        elif speech_type == "news":
            transcript = await gemini_service.generate_news_brief(personality, headlines)
            title = "Breaking News briefing"
        else:
            transcript = await gemini_service.generate_traffic_report(
                personality, location=city_name, incident=traffic_incident
            )
            title = "Local Traffic Report"
            
        # Call TTS to synthesize speech on the fly
        tts_key = await tts_service.synthesize_speech(transcript, voice_gender)
        tts_url = await storage_service.get_streaming_url(tts_key)

        # Append DJ / weather / news / traffic speech block
        queue.append({
            "queue_id": f"speech_{item_index}",
            "type": speech_type,
            "id": 2000 + item_index,
            "title": title,
            "artist": "AI Radio Service",
            "album": "Radio Broadcast",
            "duration": 6,  # 6 seconds of speech duration
            "cover_url": "https://images.unsplash.com/photo-1478737270239-2f02b77fc618",
            "stream_url": tts_url,
            "transcript": transcript
        })
        item_index += 1

    return queue

@router.post("/history", status_code=status.HTTP_201_CREATED)
async def record_playback_history(
    song_id: int,
    skipped: bool = Query(False),
    duration_played: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify song exists (only check if it's not a mock ID)
    if song_id < 1000:
        result = await db.execute(select(Song).where(Song.id == song_id))
        song = result.scalars().first()
        if not song:
            return {"status": "ignored", "detail": "Mock song history"}
            
    history = PlaybackHistory(
        user_id=current_user.id,
        song_id=song_id if song_id < 1000 else 1, # fallback to seed if mock ID
        skipped=skipped,
        duration_played=duration_played
    )
    
    if song_id < 1000:
        db.add(history)
        await db.commit()
        
    return {"status": "success", "recorded_id": song_id}
