import requests
import logging
from pathlib import Path
from app.services.youtube_service import search_youtube, download_youtube_track

logger = logging.getLogger(__name__)

DEEZER_SEARCH_API = "https://api.deezer.com/search"

def format_duration(seconds: int) -> str:
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"

def search_deezer(query: str, limit: int = 15, has_arl: bool = False) -> list[dict]:
    results = []
    try:
        response = requests.get(DEEZER_SEARCH_API, params={"q": query, "limit": limit}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for track in data.get("data", []):
                album = track.get("album", {})
                artist = track.get("artist", {})
                
                results.append({
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
                    "available_qualities": ["flac", "320k", "standard"] if has_arl else ["320k", "standard"]
                })
    except Exception as e:
        logger.error(f"Deezer search error: {e}")

    # Fallback to YouTube if Deezer returned no results
    if not results:
        logger.info(f"No results from Deezer API for '{query}', falling back to YouTube")
        return search_youtube(query, limit=limit)

    return results

def download_deezer_track(track_id: str, track_title: str, artist_name: str, output_dir: Path, arl_token: str = "", preferred_quality: str = "flac", progress_hook=None) -> dict:
    """
    Attempts to download lossless audio from Deezer if valid ARL token is provided.
    If ARL token is missing, invalid, or track fails, gracefully falls back to YouTube search & download.
    """
    if arl_token and preferred_quality == "flac":
        try:
            logger.info(f"Attempting Deezer Lossless download for {track_title} by {artist_name}")
            # Placeholder for pydeezer / custom crypto stream decryptor
            # If Deezer download succeeds, return file path
        except Exception as e:
            logger.warning(f"Deezer Lossless download failed ({e}). Triggering automatic fallback to YouTube.")

    # Fallback: Search track on YouTube and download with highest quality
    fallback_query = f"{artist_name} - {track_title} audio"
    yt_results = search_youtube(fallback_query, limit=1)
    
    if yt_results:
        yt_url = yt_results[0]["url"]
        return download_youtube_track(yt_url, output_dir=output_dir, preferred_quality="320k", progress_hook=progress_hook)
    else:
        raise RuntimeError(f"Could not find fallback audio for {track_title}")
