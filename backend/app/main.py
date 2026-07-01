from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, stations, catalog, music, playback
from app.services.tts_service import tts_service

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Set CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to initialize DB tables
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        # Create all tables if they do not exist
        await conn.run_sync(Base.metadata.create_all)
    await tts_service.create_placeholder_file_if_missing()

# Register routers
app.include_router(auth.router, prefix="/api")
app.include_router(stations.router, prefix="/api")
app.include_router(catalog.router, prefix="/api")
app.include_router(music.router, prefix="/api")
app.include_router(playback.router, prefix="/api")

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "database": "connected"
    }
