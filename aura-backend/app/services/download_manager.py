import uuid
import time
import asyncio
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel

from app.core.config import load_settings, DOWNLOADS_DIR
from app.core.db import SessionLocal
from app.models.track_model import TrackModel
from app.services.youtube_service import download_youtube_track
from app.services.deezer_service import download_deezer_track
from app.services.websocket_manager import ws_manager

logger = logging.getLogger(__name__)

class DownloadItem(BaseModel):
    id: str
    title: str
    artist: str
    thumbnail: str
    engine: str
    quality: str
    status: str  # "queued", "downloading", "processing", "completed", "error"
    progress: float  # 0.0 to 100.0
    speed: str = "0 KB/s"
    eta: str = "--:--"
    file_name: str = ""
    file_path: str = ""
    error_message: str = ""
    created_at: float

class DownloadManager:
    def __init__(self, max_concurrent: int = 2):
        self.queue: dict[str, DownloadItem] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)

    def _broadcast_event(self, event_type: str, item: DownloadItem):
        payload = {
            "type": event_type,
            "item": item.model_dump()
        }
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.run_coroutine_threadsafe(ws_manager.broadcast(payload), loop)
            else:
                asyncio.run(ws_manager.broadcast(payload))
        except Exception:
            try:
                asyncio.run(ws_manager.broadcast(payload))
            except Exception:
                pass

    def add_to_queue(self, track_info: dict, quality: str = "320k") -> DownloadItem:
        download_id = str(uuid.uuid4())
        item = DownloadItem(
            id=download_id,
            title=track_info.get("title", "Unknown Title"),
            artist=track_info.get("artist", "Unknown Artist"),
            thumbnail=track_info.get("thumbnail", ""),
            engine=track_info.get("engine", "youtube"),
            quality=quality,
            status="queued",
            progress=0.0,
            created_at=time.time()
        )
        self.queue[download_id] = item
        self._broadcast_event("download_queued", item)

        # Submit to thread pool
        self.executor.submit(self._process_download, download_id, track_info)
        return item

    def get_all(self) -> list[DownloadItem]:
        return sorted(self.queue.values(), key=lambda x: x.created_at, reverse=True)

    def get_by_id(self, download_id: str) -> DownloadItem | None:
        return self.queue.get(download_id)

    def _save_to_db(self, item: DownloadItem, track_info: dict):
        try:
            db = SessionLocal()
            try:
                db_track = db.query(TrackModel).filter(TrackModel.id == item.id).first()
                if not db_track:
                    db_track = TrackModel(
                        id=item.id,
                        title=item.title,
                        artist=item.artist,
                        album=track_info.get("album", "Aura Music"),
                        thumbnail=item.thumbnail,
                        duration=track_info.get("duration", "00:00"),
                        duration_sec=track_info.get("duration_sec", 0),
                        file_path=item.file_path,
                        file_name=item.file_name,
                        quality=item.quality,
                        engine=item.engine,
                        is_favorite=False
                    )
                    db.add(db_track)
                else:
                    db_track.file_path = item.file_path
                    db_track.file_name = item.file_name

                db.commit()
                logger.info(f"Saved track '{item.title}' to database.")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Failed saving track to database: {e}")

    def _process_download(self, download_id: str, track_info: dict):
        item = self.queue.get(download_id)
        if not item:
            return

        item.status = "downloading"
        item.progress = 1.0
        item.speed = "Buscando audio..."
        self._broadcast_event("download_progress", item)

        settings = load_settings()
        out_dir = Path(settings.download_dir) if settings.download_dir else DOWNLOADS_DIR

        def progress_hook(d):
            if d.get("status") == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                downloaded = d.get("downloaded_bytes", 0)
                if total > 0:
                    item.progress = round((downloaded / total) * 100, 1)
                
                speed_bytes = d.get("speed") or 0
                if speed_bytes > 1024 * 1024:
                    item.speed = f"{speed_bytes / (1024 * 1024):.1f} MB/s"
                elif speed_bytes > 1024:
                    item.speed = f"{speed_bytes / 1024:.0f} KB/s"
                else:
                    item.speed = f"{speed_bytes:.0f} B/s"

                eta_sec = d.get("eta")
                if eta_sec is not None:
                    mins = eta_sec // 60
                    secs = eta_sec % 60
                    item.eta = f"{mins:02d}:{secs:02d}"

                self._broadcast_event("download_progress", item)

            elif d.get("status") == "finished":
                item.status = "processing"
                item.progress = 95.0
                item.speed = "Etiquetando ID3..."
                self._broadcast_event("download_progress", item)

        try:
            if item.engine == "deezer":
                result = download_deezer_track(
                    track_id=track_info.get("id"),
                    track_title=item.title,
                    artist_name=item.artist,
                    output_dir=out_dir,
                    arl_token=settings.arl_token,
                    preferred_quality=item.quality,
                    progress_hook=progress_hook,
                    track_url=track_info.get("url", "")
                )
            else:
                video_url = track_info.get("url")
                result = download_youtube_track(
                    video_url=video_url,
                    output_dir=out_dir,
                    preferred_quality=item.quality,
                    progress_hook=progress_hook
                )

            item.status = "completed"
            item.progress = 100.0
            item.file_name = result.get("file_name", "")
            item.file_path = result.get("file_path", "")

            # Save to database
            self._save_to_db(item, track_info)
            self._broadcast_event("download_completed", item)
            logger.info(f"Download completed successfully for {item.title}")

        except Exception as e:
            logger.error(f"Download failed for {item.title}: {e}")
            item.status = "error"
            item.error_message = str(e)
            self._broadcast_event("download_error", item)

download_manager = DownloadManager()
