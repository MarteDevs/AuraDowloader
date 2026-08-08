import asyncio
import logging
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pydantic import BaseModel

from app.core.config import DOWNLOADS_DIR, load_settings, safe_alpath
from app.core.db import SessionLocal
from app.models.track_model import TrackModel
from app.services.deezer_service import download_deezer_track
from app.services.websocket_manager import ws_manager
from app.services.youtube_service import download_youtube_track

logger = logging.getLogger(__name__)


class _DownloadCancelled(Exception):
    """Internal sentinel raised to break out of yt_dlp callbacks when cancelled."""

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
        # Stores the original track_info dict per download id so we can retry.
        self._track_info: dict[str, dict] = {}
        # Cancellation flags — set to True to ask the worker to stop ASAP.
        self._cancel_flags: dict[str, bool] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
        self._loop: asyncio.AbstractEventLoop | None = None

    def bind_event_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Store the FastAPI event loop so worker threads can broadcast safely."""
        self._loop = loop
        logger.info("DownloadManager bound to event loop.")

    def _broadcast_event(self, event_type: str, item: DownloadItem) -> None:
        payload = {
            "type": event_type,
            "item": item.model_dump()
        }
        if self._loop is None or self._loop.is_closed():
            logger.warning("Event loop not bound or closed; skipping broadcast for %s", event_type)
            return
        try:
            asyncio.run_coroutine_threadsafe(ws_manager.broadcast(payload), self._loop)
        except Exception as e:
            logger.error(f"Failed to schedule broadcast ({event_type}): {e}")

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
        self._track_info[download_id] = dict(track_info)
        self._cancel_flags[download_id] = False
        self._broadcast_event("download_queued", item)

        # Submit to thread pool
        self.executor.submit(self._process_download, download_id, track_info)
        return item

    def cancel(self, download_id: str) -> bool:
        """Mark a download as cancelled. Returns True if the id was found."""
        item = self.queue.get(download_id)
        if not item:
            return False
        if item.status in ("completed", "error", "cancelled"):
            return False
        self._cancel_flags[download_id] = True
        item.status = "cancelled"
        item.error_message = "Cancelled by user"
        self._broadcast_event("download_cancelled", item)
        return True

    def remove(self, download_id: str) -> bool:
        """Drop an item from the in-memory queue. File on disk is preserved."""
        item = self.queue.pop(download_id, None)
        self._track_info.pop(download_id, None)
        self._cancel_flags.pop(download_id, None)
        return item is not None

    def retry(self, download_id: str) -> DownloadItem | None:
        """Re-queue a previously errored/cancelled download, if its track_info is still in memory."""
        info = self._track_info.get(download_id)
        if not info:
            return None
        old = self.queue.get(download_id)
        quality = old.quality if old else info.get("quality", "320k")
        # Reset the in-memory item to a fresh queued state.
        new_item = DownloadItem(
            id=download_id,
            title=info.get("title", "Unknown Title"),
            artist=info.get("artist", "Unknown Artist"),
            thumbnail=info.get("thumbnail", ""),
            engine=info.get("engine", "youtube"),
            quality=quality,
            status="queued",
            progress=0.0,
            created_at=time.time(),
        )
        self.queue[download_id] = new_item
        self._cancel_flags[download_id] = False
        self._broadcast_event("download_queued", new_item)
        self.executor.submit(self._process_download, download_id, info)
        return new_item

    def is_cancelled(self, download_id: str) -> bool:
        return self._cancel_flags.get(download_id, False)

    def get_all(self) -> list[DownloadItem]:
        return sorted(self.queue.values(), key=lambda x: x.created_at, reverse=True)

    def get_by_id(self, download_id: str) -> DownloadItem | None:
        item = self.queue.get(download_id)
        if item:
            return item

        # If not in memory (e.g. after restart), try to load from DB
        try:
            db = SessionLocal()
            try:
                db_track = db.query(TrackModel).filter(TrackModel.id == download_id).first()
                if db_track and db_track.file_path:
                    # Reconstruct a DownloadItem
                    item = DownloadItem(
                        id=db_track.id,
                        title=db_track.title,
                        artist=db_track.artist,
                        thumbnail=db_track.thumbnail,
                        engine=db_track.engine,
                        quality=db_track.quality,
                        status="completed",
                        progress=100.0,
                        file_name=db_track.file_name,
                        file_path=db_track.file_path,
                        created_at=time.time()
                    )
                    # Cache it back in memory
                    self.queue[download_id] = item
                    return item
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error loading track {download_id} from DB: {e}")

        return None
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

        if self.is_cancelled(download_id):
            return

        item.status = "downloading"
        item.progress = 1.0
        item.speed = "Buscando audio..."
        self._broadcast_event("download_progress", item)

        settings = load_settings()
        out_dir: Path | None = None
        if settings.download_dir:
            try:
                candidate = safe_alpath(settings.download_dir)
                candidate.mkdir(parents=True, exist_ok=True)
                out_dir = candidate
            except (ValueError, OSError) as e:
                logger.warning(
                    f"download_dir '{settings.download_dir}' unusable ({e}); "
                    f"falling back to default '{DOWNLOADS_DIR}'"
                )
        if out_dir is None:
            try:
                out_dir = DOWNLOADS_DIR
                out_dir.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                logger.error(f"Default download_dir '{DOWNLOADS_DIR}' unusable: {e}")
                item.status = "error"
                item.error_message = f"Invalid download_dir: {settings.download_dir or DOWNLOADS_DIR}"
                self._broadcast_event("download_error", item)
                return

        # Shared dict so the worker thread can mutate progress without
        # touching the Pydantic model from inside a hook callback.
        shared = {
            "progress": item.progress,
            "speed": item.speed,
            "eta": item.eta,
            "status": item.status,
        }

        def broadcast_from_hook(_shared: dict | None = None) -> None:
            # Honor cancellation mid-download.
            if self.is_cancelled(download_id):
                raise _DownloadCancelled()
            item.progress = shared["progress"]
            item.speed = shared["speed"]
            item.eta = shared["eta"]
            item.status = shared["status"]
            self._broadcast_event("download_progress", item)

        from app.services.youtube_service import _build_progress_hook
        progress_hook = _build_progress_hook(shared, broadcast_from_hook)

        try:
            if self.is_cancelled(download_id):
                return

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

            if self.is_cancelled(download_id):
                return

            item.status = "completed"
            item.progress = 100.0
            item.file_name = result.get("file_name", "")
            item.file_path = result.get("file_path", "")

            # Save to database
            self._save_to_db(item, track_info)
            self._broadcast_event("download_completed", item)
            logger.info(f"Download completed successfully for {item.title}")

        except _DownloadCancelled:
            logger.info(f"Download {download_id} cancelled mid-flight.")
        except Exception as e:
            if self.is_cancelled(download_id):
                return
            logger.error(f"Download failed for {item.title}: {e}")
            item.status = "error"
            item.error_message = str(e)
            self._broadcast_event("download_error", item)

download_manager = DownloadManager()


def get_download_manager() -> DownloadManager:
    """FastAPI dependency — returns the process-wide DownloadManager singleton."""
    return download_manager
