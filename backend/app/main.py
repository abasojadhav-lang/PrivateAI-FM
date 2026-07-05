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
    
    # Seed default songs if database is empty
    from app.core.database import AsyncSessionLocal
    from app.core.seeder import seed_default_songs
    async with AsyncSessionLocal() as db:
        await seed_default_songs(db)
        
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

@app.get("/api/db-status")
async def db_status():
    db_url = settings.DATABASE_URL
    is_sqlite = "sqlite" in db_url.lower()
    return {
        "database_type": "SQLite (Temporary/Ephemeral)" if is_sqlite else "PostgreSQL (Persistent)",
        "database_url_configured": not db_url.startswith("postgresql+asyncpg://postgres:password@localhost:5432"),
        "hint": "If database_type is SQLite, your stations will delete on every deploy. Configure a persistent PostgreSQL database on Render."
    }
