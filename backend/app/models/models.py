from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    stations = relationship("Station", back_populates="user", cascade="all, delete-orphan")
    playback_history = relationship("PlaybackHistory", back_populates="user", cascade="all, delete-orphan")

class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    mood = Column(String, default="Neutral")
    
    # Store dynamic preference settings (e.g. favorite genres, artists)
    music_preferences = Column(JSON, default=dict)
    
    # Store settings for DJ (e.g. personality, TTS voice, frequency of weather/news)
    voice_config = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="stations")

class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    artist = Column(String, nullable=False, index=True)
    album = Column(String, nullable=True)
    genre = Column(String, nullable=True)
    duration = Column(Integer, nullable=False)  # in seconds
    
    # IDs mapped to external services
    spotify_id = Column(String, unique=True, index=True, nullable=True)
    youtube_id = Column(String, unique=True, index=True, nullable=True)
    
    cover_url = Column(String, nullable=True)
    storage_url = Column(String, nullable=True)  # URL to cached/uploaded MP3 file
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    playback_history = relationship("PlaybackHistory", back_populates="song")

class PlaybackHistory(Base):
    __tablename__ = "playback_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    song_id = Column(Integer, ForeignKey("songs.id", ondelete="RESTRICT"), nullable=False)
    played_at = Column(DateTime, default=datetime.utcnow)
    skipped = Column(Boolean, default=False)
    duration_played = Column(Integer, default=0)  # in seconds

    # Relationships
    user = relationship("User", back_populates="playback_history")
    song = relationship("Song", back_populates="playback_history")
