from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.core.database import get_db
from app.models.models import Station, User
from app.schemas.schemas import StationCreate, StationResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/stations", tags=["stations"])

@router.post("", response_model=StationResponse, status_code=status.HTTP_201_CREATED)
async def create_station(
    station_in: StationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_station = Station(
        user_id=current_user.id,
        name=station_in.name,
        mood=station_in.mood,
        music_preferences=station_in.music_preferences,
        voice_config=station_in.voice_config
    )
    db.add(db_station)
    await db.commit()
    await db.refresh(db_station)
    return db_station

@router.get("", response_model=List[StationResponse])
async def list_stations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Station).where(Station.user_id == current_user.id))
    return result.scalars().all()

@router.put("/{station_id}", response_model=StationResponse)
async def update_station(
    station_id: int,
    station_in: StationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Station).where(Station.id == station_id, Station.user_id == current_user.id)
    )
    station = result.scalars().first()
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found or not owned by user."
        )
    
    station.name = station_in.name
    station.mood = station_in.mood
    station.music_preferences = station_in.music_preferences
    station.voice_config = station_in.voice_config
    
    await db.commit()
    await db.refresh(station)
    return station

@router.delete("/{station_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_station(
    station_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Station).where(Station.id == station_id, Station.user_id == current_user.id)
    )
    station = result.scalars().first()
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found or not owned by user."
        )
    
    await db.delete(station)
    await db.commit()
    return None

