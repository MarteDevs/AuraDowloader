from fastapi import APIRouter, Query
from app.core.config import load_settings
from app.services.youtube_service import search_youtube
from app.services.deezer_service import search_deezer

router = APIRouter()

@router.get("/search")
def search_tracks(
    q: str = Query(..., min_length=1, description="Search query string"),
    engine: str = Query("youtube", description="Engine type: 'youtube' or 'deezer'"),
    limit: int = Query(15, ge=1, le=50)
):
    settings = load_settings()
    has_arl = bool(settings.arl_token.strip())

    if engine.lower() == "deezer":
        results = search_deezer(q, limit=limit, has_arl=has_arl)
    else:
        results = search_youtube(q, limit=limit)

    return {
        "query": q,
        "engine": engine,
        "has_arl": has_arl,
        "count": len(results),
        "results": results
    }
