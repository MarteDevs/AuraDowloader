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
        "count": len(results),
        "results": results
    }

@router.get("/search/albums")
def search_albums(
    q: str = Query(..., min_length=1, description="Search query string"),
    engine: str = Query("youtube", description="Engine type: 'youtube' or 'deezer'"),
    limit: int = Query(15, ge=1, le=50)
):
    if engine.lower() == "deezer":
        from app.services.deezer_service import search_deezer_albums
        results = search_deezer_albums(q, limit=limit)
    else:
        from app.services.youtube_service import search_youtube_albums
        results = search_youtube_albums(q, limit=limit)

    return {
        "query": q,
        "engine": engine,
        "count": len(results),
        "results": results
    }

@router.get("/album/{album_id}/tracks")
def get_album_tracks(
    album_id: str,
    engine: str = Query("youtube", description="Engine type: 'youtube' or 'deezer'")
):
    if engine.lower() == "deezer":
        from app.services.deezer_service import get_deezer_album_tracks
        tracks = get_deezer_album_tracks(album_id)
    else:
        from app.services.youtube_service import get_youtube_playlist_tracks
        tracks = get_youtube_playlist_tracks(album_id)

    return {
        "album_id": album_id,
        "engine": engine,
        "count": len(tracks),
        "tracks": tracks
    }
