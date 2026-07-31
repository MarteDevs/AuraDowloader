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

@router.post("/download")
def start_download(req: DownloadRequest):
    track_info = req.model_dump()
    item = download_manager.add_to_queue(track_info, quality=req.quality)
    return {
        "status": "queued",
        "download_id": item.id,
        "item": item
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
