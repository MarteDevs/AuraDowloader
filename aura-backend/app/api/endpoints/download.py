from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.services.download_manager import download_manager

router = APIRouter()

class DownloadRequest(BaseModel):
    id: str
    title: str
    artist: str
    thumbnail: str = ""
    url: str = ""
    engine: str = "youtube"
    quality: str = "320k"

class AlbumDownloadRequest(BaseModel):
    album_id: str
    album_title: str
    artist: str
    engine: str = "youtube"
    quality: str = "320k"
    tracks: list[dict]

@router.post("/download")
def start_download(req: DownloadRequest):
    track_info = req.model_dump()
    item = download_manager.add_to_queue(track_info, quality=req.quality)
    return {
        "status": "queued",
        "download_id": item.id,
        "item": item
    }

@router.post("/download/album")
def start_album_download(req: AlbumDownloadRequest):
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
        item = download_manager.add_to_queue(track_info, quality=req.quality)
        queued_items.append(item)

    return {
        "status": "album_queued",
        "album_title": req.album_title,
        "total_tracks": len(queued_items),
        "items": queued_items
    }

@router.get("/download/queue")
def get_queue():
    items = download_manager.get_all()
    return {
        "count": len(items),
        "items": items
    }

@router.get("/download/file/{download_id}")
def serve_file(download_id: str):
    item = download_manager.get_by_id(download_id)
    if not item or item.status != "completed" or not item.file_path:
        raise HTTPException(status_code=404, detail="File not ready or not found")

    file_path = Path(item.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Physical file missing on server")

    return FileResponse(
        path=file_path,
        filename=item.file_name or file_path.name,
        media_type="application/octet-stream"
    )
