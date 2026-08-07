
from fastapi import APIRouter, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import load_settings
from app.services.deezer_service import (
    get_deezer_album_tracks_async,
    search_deezer_albums_async,
    search_deezer_async,
)
from app.services.youtube_service import (
    get_youtube_playlist_tracks,
    search_youtube,
    search_youtube_albums,
)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/search")
@limiter.limit("30/minute")
async def search_tracks(
    request: Request,
    q: str = Query(..., min_length=1, description="Search query string"),
    engine: str = Query("youtube", description="Engine type: 'youtube' or 'deezer'"),
    limit: int = Query(15, ge=1, le=50)
):
    settings = load_settings()
    has_arl = bool(settings.arl_token.strip())

    if engine.lower() == "deezer":
        results = await search_deezer_async(q, limit=limit, has_arl=has_arl)
        # Fallback to YouTube if Deezer returned no results.
        if not results:
            results = search_youtube(q, limit=limit)
    else:
        results = search_youtube(q, limit=limit)

    return {
        "query": q,
        "engine": engine,
        "count": len(results),
        "results": results
    }


@router.get("/search/albums")
@limiter.limit("30/minute")
async def search_albums(
    request: Request,
    q: str = Query(..., min_length=1, description="Search query string"),
    engine: str = Query("youtube", description="Engine type: 'youtube' or 'deezer'"),
    limit: int = Query(15, ge=1, le=50)
):
    if engine.lower() == "deezer":
        results = await search_deezer_albums_async(q, limit=limit)
    else:
        results = search_youtube_albums(q, limit=limit)

    return {
        "query": q,
        "engine": engine,
        "count": len(results),
        "results": results
    }


@router.get("/album/{album_id}/tracks")
@limiter.limit("30/minute")
async def get_album_tracks(
    request: Request,
    album_id: str,
    engine: str = Query("youtube", description="Engine type: 'youtube' or 'deezer'")
):
    if engine.lower() == "deezer":
        tracks = await get_deezer_album_tracks_async(album_id)
    else:
        tracks = get_youtube_playlist_tracks(album_id)

    return {
        "album_id": album_id,
        "engine": engine,
        "count": len(tracks),
        "tracks": tracks
    }
