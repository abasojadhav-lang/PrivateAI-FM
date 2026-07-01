import os
import io
import uuid
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from app.core.database import get_db
from app.models.models import Song, User
from app.api.deps import get_current_user
from app.services.storage_service import storage_service

router = APIRouter(prefix="/music", tags=["music"])

def extract_mp3_metadata(file_bytes: bytes, filename: str) -> dict:
    """Extract metadata (Title, Artist, Album, Genre, Duration) from MP3 file bytes."""
    metadata = {
        "title": os.path.splitext(filename)[0],
        "artist": "Unknown Artist",
        "album": "Unknown Album",
        "genre": "Unknown Genre",
        "duration": 180  # Default 3 minutes
    }
    
    try:
        # Wrap bytes in a file-like object
        file_obj = io.BytesIO(file_bytes)
        
        # Load audio file for duration
        audio = MP3(file_obj)
        metadata["duration"] = int(audio.info.length)
        
        # Reset pointer for ID3 reading
        file_obj.seek(0)
        
        # Read tags
        try:
            tags = EasyID3(file_obj)
            if tags.get("title"):
                metadata["title"] = tags["title"][0]
            if tags.get("artist"):
                metadata["artist"] = tags["artist"][0]
            if tags.get("album"):
                metadata["album"] = tags["album"][0]
            if tags.get("genre"):
                metadata["genre"] = tags["genre"][0]
        except Exception:
            # EasyID3 fails if tags are missing, keep defaults
            pass
            
    except Exception as e:
        # Mutagen fails if file is corrupted, keep defaults
        pass
        
    return metadata

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_music(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename.lower().endswith('.mp3'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only MP3 audio files are supported."
        )
        
    file_bytes = await file.read()
    
    # Extract metadata using Mutagen
    metadata = extract_mp3_metadata(file_bytes, file.filename)
    
    # Generate unique filename for storage
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    
    # Upload to storage service (S3 or local filesystem fallback)
    storage_key = await storage_service.upload_file(file_bytes, unique_filename)
    
    # Create song record in DB
    song = Song(
        title=metadata["title"],
        artist=metadata["artist"],
        album=metadata["album"],
        genre=metadata["genre"],
        duration=metadata["duration"],
        storage_url=storage_key
    )
    db.add(song)
    await db.commit()
    await db.refresh(song)
    
    return song

@router.get("/songs", response_model=List[dict])
async def get_songs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Song))
    songs = result.scalars().all()
    
    # Generate presigned streaming URLs for each song
    song_list = []
    for s in songs:
        streaming_url = await storage_service.get_streaming_url(s.storage_url)
        song_list.append({
            "id": s.id,
            "title": s.title,
            "artist": s.artist,
            "album": s.album,
            "genre": s.genre,
            "duration": s.duration,
            "spotify_id": s.spotify_id,
            "youtube_id": s.youtube_id,
            "cover_url": s.cover_url,
            "stream_url": streaming_url
        })
    return song_list

@router.get("/file/{file_name}")
async def get_local_file(file_name: str):
    """Serve files directly from local fallback static_storage when MinIO is not running."""
    local_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "static_storage",
        file_name
    )
    if not os.path.exists(local_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio file not found."
        )
    return FileResponse(local_path, media_type="audio/mpeg")
