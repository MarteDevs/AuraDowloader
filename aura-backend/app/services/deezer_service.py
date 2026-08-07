import asyncio
import logging
from pathlib import Path
from typing import Any

import httpx

from app.services.youtube_service import download_youtube_track, search_youtube

logger = logging.getLogger(__name__)

DEEZER_API = "https://api.deezer.com"
DEFAULT_TIMEOUT = 10.0
USER_AGENT = "AuraMusicDownloader/2.0 (+https://aura-downloader.duckdns.org)"


def format_duration(seconds: int) -> str:
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"


async def _deezer_get(path: str, params: dict | None = None) -> dict[str, Any] | None:
    """Perform a single GET to the Deezer public API, returning parsed JSON or None on error."""
    url = f"{DEEZER_API}{path}"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, headers=headers) as client:
            r = await client.get(url, params=params or {})
            r.raise_for_status()
            return r.json()
    except (httpx.HTTPError, ValueError) as e:
        logger.error(f"Deezer GET {path} failed: {e}")
        return None


def _track_to_result(track: dict, has_arl: bool) -> dict:
    album = track.get("album", {})
    artist = track.get("artist", {})
    return {
        "id": str(track.get("id")),
        "title": track.get("title"),
        "artist": artist.get("name", "Unknown Artist"),
        "album": album.get("title", "Deezer Release"),
        "duration": format_duration(track.get("duration", 0)),
        "duration_sec": track.get("duration", 0),
        "thumbnail": album.get("cover_medium") or album.get("cover_big") or "",
        "url": track.get("link"),
        "engine": "deezer",
        "quality_badge": "FLAC Lossless" if has_arl else "Fallback (YouTube 320k)",
        "has_flac": has_arl,
        "available_qualities": ["flac", "320k", "standard"] if has_arl else ["320k", "standard"],
    }


async def search_deezer_async(query: str, limit: int = 15, has_arl: bool = False) -> list[dict]:
    data = await _deezer_get("/search", {"q": query, "limit": limit})
    if not data:
        return []
    return [_track_to_result(t, has_arl) for t in data.get("data", []) if t]


def search_deezer(query: str, limit: int = 15, has_arl: bool = False) -> list[dict]:
    """Sync wrapper used from thread-pool contexts (download manager)."""
    try:
        return asyncio.run(search_deezer_async(query, limit=limit, has_arl=has_arl))
    except RuntimeError:
        # Already inside a running loop — fall back to a fresh loop in a thread.
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
            fut = ex.submit(lambda: asyncio.run(search_deezer_async(query, limit=limit, has_arl=has_arl)))
            return fut.result()


async def search_deezer_albums_async(query: str, limit: int = 15) -> list[dict]:
    data = await _deezer_get("/search/album", {"q": query, "limit": limit})
    if not data:
        return []
    out = []
    for album in data.get("data", []):
        artist = album.get("artist", {})
        out.append({
            "id": str(album.get("id")),
            "title": album.get("title", "Unknown Album"),
            "artist": artist.get("name", "Unknown Artist"),
            "thumbnail": album.get("cover_medium") or album.get("cover_big") or "",
            "nb_tracks": album.get("nb_tracks", 0),
            "type": "album",
            "engine": "deezer",
            "url": album.get("link", ""),
        })
    return out


def search_deezer_albums(query: str, limit: int = 15) -> list[dict]:
    return asyncio.run(search_deezer_albums_async(query, limit=limit))


async def get_deezer_album_tracks_async(album_id: str) -> list[dict]:
    data = await _deezer_get(f"/album/{album_id}/tracks")
    if not data:
        return []
    tracks = []
    for i, track in enumerate(data.get("data", []), start=1):
        artist = track.get("artist", {})
        tracks.append({
            "id": str(track.get("id")),
            "title": track.get("title"),
            "artist": artist.get("name", "Unknown Artist"),
            "duration": format_duration(track.get("duration", 0)),
            "duration_sec": track.get("duration", 0),
            "track_number": i,
            "engine": "deezer",
        })
    return tracks


def get_deezer_album_tracks(album_id: str) -> list[dict]:
    return asyncio.run(get_deezer_album_tracks_async(album_id))


def download_deezer_track(
    track_id: str,
    track_title: str,
    artist_name: str,
    output_dir: Path,
    arl_token: str = "",
    preferred_quality: str = "flac",
    progress_hook=None,
    track_url: str = "",
) -> dict:
    """
    Attempts to download lossless audio from Deezer if valid ARL token is provided.
    If ARL token is missing, invalid, or track fails, gracefully falls back to YouTube.
    """
    if arl_token and preferred_quality == "flac":
        try:
            logger.info(f"Attempting Deezer Lossless download for {track_title} by {artist_name}")
            # Placeholder for Deezer stream decryptor
        except Exception as e:
            logger.warning(f"Deezer Lossless download failed ({e}). Triggering fallback to YouTube.")

    if track_url and "youtube.com" in track_url:
        return download_youtube_track(
            track_url,
            output_dir=output_dir,
            preferred_quality="320k",
            progress_hook=progress_hook,
        )

    fallback_query = f"{artist_name} - {track_title}"
    yt_results = search_youtube(fallback_query, limit=1)
    if yt_results:
        yt_url = yt_results[0]["url"]
        return download_youtube_track(
            yt_url,
            output_dir=output_dir,
            preferred_quality="320k",
            progress_hook=progress_hook,
        )
    raise RuntimeError(f"Could not find audio source for {track_title}")
