from fastapi import APIRouter, Query, HTTPException, status, Depends
from typing import List, Dict, Any
from app.services.catalog_service import SpotifyCatalogService, YouTubeMusicCatalogService
from app.models.models import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/catalog", tags=["catalog"])

spotify_service = SpotifyCatalogService()
youtube_service = YouTubeMusicCatalogService()

@router.get("/search", response_model=List[Dict[str, Any]])
async def search_catalog(
    q: str = Query(..., min_length=1, description="Search query"),
    provider: str = Query("spotify", regex="^(spotify|youtube)$", description="Music provider catalog to search"),
    current_user: User = Depends(get_current_user)
):
    try:
        if provider == "spotify":
            tracks = await spotify_service.search_tracks(q)
        else:
            tracks = await youtube_service.search_tracks(q)
            
        return [track.to_dict() for track in tracks]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying music catalog: {str(e)}"
        )
