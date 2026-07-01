import os
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "PrivateFM AI Backend"
    
    # Database Settings
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/privatefm",
        validation_alias="DATABASE_URL"
    )
    
    # Redis Settings
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="REDIS_URL"
    )
    
    # MinIO / Object Storage Settings
    MINIO_ENDPOINT: str = Field(
        default="http://localhost:9000",
        validation_alias="MINIO_ENDPOINT"
    )
    MINIO_ACCESS_KEY: str = Field(
        default="minioadmin",
        validation_alias="MINIO_ACCESS_KEY"
    )
    MINIO_SECRET_KEY: str = Field(
        default="minioadminpassword",
        validation_alias="MINIO_SECRET_KEY"
    )
    MINIO_BUCKET_NAME: str = "music-library"
    
    # Security Settings
    JWT_SECRET: str = Field(
        default="supersecretjwtkeyforprivatefmaiproj",
        validation_alias="JWT_SECRET"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Third-Party Music catalog
    SPOTIFY_CLIENT_ID: str = Field(default="", validation_alias="SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET: str = Field(default="", validation_alias="SPOTIFY_CLIENT_SECRET")
    YOUTUBE_API_KEY: str = Field(default="", validation_alias="YOUTUBE_API_KEY")
    
    # AI DJ & Speech Synthesis
    GEMINI_API_KEY: str = Field(default="", validation_alias="GEMINI_API_KEY")
    GOOGLE_APPLICATION_CREDENTIALS: str = Field(default="", validation_alias="GOOGLE_APPLICATION_CREDENTIALS")
    GCLOUD_TTS_API_KEY: str = Field(default="", validation_alias="GCLOUD_TTS_API_KEY")

    class Config:
        case_sensitive = True

settings = Settings()
