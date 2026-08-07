from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import safe_alpath
from app.services.download_manager import DownloadManager, get_download_manager

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

# Map of quality -> engines that support it. Used to reject nonsense combinations.
QUALITY_SUPPORT = {
    "flac": {"deezer"},
    "320k": {"youtube", "deezer"},
    "standard": {"youtube", "deezer"},
}


def _normalize_quality(engine: str, quality: str) -> str:
    """Fall back to 320k when the requested quality isn't supported by the engine."""
    engine_norm = (engine or "youtube").lower()
    quality_norm = (quality or "320k").lower()
    if quality_norm in QUALITY_SUPPORT and engine_norm in QUALITY_SUPPORT[quality_norm]:
        return quality_norm
    return "320k"

class DownloadRequest(BaseModel):
    id: str
    title: str
    artist: str
    thumbnail: str = ""
    url: str = ""
    engine: str = "youtube"
    quality: str = "320k"

    @field_validator("quality")
    @classmethod
    def _validate_quality(cls, v: str, info) -> str:
        engine = (info.data.get("engine") or "youtube").lower()
        return _normalize_quality(engine, v)


class AlbumDownloadRequest(BaseModel):
    album_id: str
    album_title: str
    artist: str
    engine: str = "youtube"
    quality: str = "320k"
    tracks: list[dict]

    @field_validator("quality")
    @classmethod
    def _validate_quality(cls, v: str, info) -> str:
        engine = (info.data.get("engine") or "youtube").lower()
        return _normalize_quality(engine, v)


@router.post("/download")
@limiter.limit("10/minute")
def start_download(request: Request, req: DownloadRequest, dm: DownloadManager = Depends(get_download_manager)):
    track_info = req.model_dump()
    item = dm.add_to_queue(track_info, quality=req.quality)
    return {
        "status": "queued",
        "download_id": item.id,
        "item": item
    }

@router.post("/download/album")
@limiter.limit("5/minute")
def start_album_download(request: Request, req: AlbumDownloadRequest, dm: DownloadManager = Depends(get_download_manager)):
    queued_items = []
    for track in req.tracks:
        track_info = {
            "id": track.get("id"),
            "title": track.get("title", "Unknown Track"),
            "artist": track.get("artist") or req.artist,
            "album": req.album_title,
            "thumbnail": track.get("thumbnail") or "",
            "url": track.get("url") or "",
            "engine": req.engine
        }
        item = dm.add_to_queue(track_info, quality=req.quality)
        queued_items.append(item)

    return {
        "status": "album_queued",
        "album_title": req.album_title,
        "total_tracks": len(queued_items),
        "items": queued_items
    }

@router.get("/download/queue")
def get_queue(dm: DownloadManager = Depends(get_download_manager)):
    items = dm.get_all()
    return {
        "count": len(items),
        "items": items
    }


@router.post("/download/cancel/{download_id}")
def cancel_download(download_id: str, dm: DownloadManager = Depends(get_download_manager)):
    if not dm.cancel(download_id):
        raise HTTPException(status_code=404, detail="Download not found or already finished")
    return {"status": "cancelled", "download_id": download_id}


@router.post("/download/retry/{download_id}")
def retry_download(download_id: str, dm: DownloadManager = Depends(get_download_manager)):
    item = dm.retry(download_id)
    if not item:
        raise HTTPException(status_code=404, detail="Download not found in memory — try re-adding it")
    return {"status": "queued", "item": item}


@router.delete("/download/{download_id}")
def remove_download(download_id: str, dm: DownloadManager = Depends(get_download_manager)):
    if not dm.remove(download_id):
        raise HTTPException(status_code=404, detail="Download not found")
    return {"status": "removed", "download_id": download_id}


@router.get("/download/file/{download_id}")
def serve_file(download_id: str, dm: DownloadManager = Depends(get_download_manager)):
    item = dm.get_by_id(download_id)
    if not item or item.status != "completed" or not item.file_path:
        raise HTTPException(status_code=404, detail="File not ready or not found")

    try:
        file_path = safe_alpath(item.file_path)
    except ValueError as e:
        # File path is outside any allowed root — refuse to serve it.
        raise HTTPException(status_code=403, detail="Forbidden file path") from e

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Physical file missing on server")

    filename = item.file_name or file_path.name
    # RFC 5986 — handle non-ASCII filenames correctly in Content-Disposition.
    encoded = quote(filename)
    headers = {
        "Content-Disposition": (
            f"attachment; filename=\"aura_track_{item.id}\"; "
            f"filename*=UTF-8''{encoded}"
        )
    }
    return FileResponse(
        path=file_path,
        headers=headers,
        media_type="application/octet-stream",
    )
