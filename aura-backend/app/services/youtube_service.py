import logging
import os
import re
import urllib.request
from pathlib import Path

import yt_dlp
from mutagen.id3 import APIC, ID3, TALB, TIT2, TPE1
from mutagen.mp3 import MP3

from app.core.config import BASE_DIR, load_settings
from app.core.ffmpeg_utils import get_ffmpeg_path

logger = logging.getLogger(__name__)

# Path to yt-dlp config file with --remote-components and --js-runtimes
YT_DLP_CONF = BASE_DIR / "yt-dlp.conf"

def _apply_yt_dlp_extras(ydl_opts: dict) -> dict:
    """Apply cookies, config file, and extractor args to ydl_opts.

    The ``bgutil-ytdlp-pot-provider`` plugin (pip package) is auto-loaded by
    yt-dlp and provides the GVS PO Token required by the ``mweb`` client.
    """
    settings = load_settings()
    cookies_path = Path(settings.cookies_file)
    if cookies_path.exists():
        ydl_opts["cookiefile"] = str(cookies_path)
    if YT_DLP_CONF.exists():
        ydl_opts["config_locations"] = [str(YT_DLP_CONF)]
    ydl_opts["extractor_args"] = {"youtube": {"player_client": ["mweb"]}}
    return ydl_opts


def format_duration(seconds: int | float | None) -> str:
    if not seconds:
        return "00:00"
    seconds = int(seconds)
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"

def clean_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name)

def search_youtube(query: str, limit: int = 15) -> list[dict]:
    ffmpeg_bin = get_ffmpeg_path()
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "default_search": f"ytsearch{limit}",
    }
    _apply_yt_dlp_extras(ydl_opts)
    if ffmpeg_bin:
        ydl_opts["ffmpeg_location"] = os.path.dirname(ffmpeg_bin)

    results = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
            entries = info.get("entries", [])
            for item in entries:
                if not item:
                    continue
                video_id = item.get("id")
                title = item.get("title", "Unknown Title")
                uploader = item.get("uploader") or item.get("channel") or "Unknown Artist"
                duration_sec = item.get("duration")
                thumbnail = item.get("thumbnail") or f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

                results.append({
                    "id": video_id,
                    "title": title,
                    "artist": uploader,
                    "album": "YouTube Audio",
                    "duration": format_duration(duration_sec),
                    "duration_sec": duration_sec or 0,
                    "thumbnail": thumbnail,
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "engine": "youtube",
                    "quality_badge": "HQ (256k)",
                    "available_qualities": ["standard", "320k"]
                })
    except Exception as e:
        logger.error(f"Error searching YouTube for '{query}': {e}")

    return results

def search_youtube_albums(query: str, limit: int = 15) -> list[dict]:
    ffmpeg_bin = get_ffmpeg_path()
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
    }
    _apply_yt_dlp_extras(ydl_opts)
    if ffmpeg_bin:
        ydl_opts["ffmpeg_location"] = os.path.dirname(ffmpeg_bin)

    results = []
    try:
        search_term = f"ytsearch{limit}:{query} full album"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_term, download=False)
            entries = info.get("entries", [])
            for item in entries:
                if not item:
                    continue
                video_id = item.get("id")
                title = item.get("title", "Unknown Album")
                uploader = item.get("uploader") or item.get("channel") or "Unknown Artist"
                entry_count = item.get("playlist_count") or 1
                thumbnail = item.get("thumbnail") or f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

                results.append({
                    "id": video_id,
                    "title": title,
                    "artist": uploader,
                    "thumbnail": thumbnail,
                    "nb_tracks": entry_count,
                    "type": "album",
                    "engine": "youtube",
                    "url": item.get("url") or f"https://www.youtube.com/watch?v={video_id}"
                })
    except Exception as e:
        logger.error(f"Error searching YouTube albums for '{query}': {e}")

    return results

def get_youtube_playlist_tracks(playlist_url_or_id: str) -> list[dict]:
    ffmpeg_bin = get_ffmpeg_path()
    url = playlist_url_or_id if playlist_url_or_id.startswith("http") else f"https://www.youtube.com/watch?v={playlist_url_or_id}"

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
    }
    _apply_yt_dlp_extras(ydl_opts)
    if ffmpeg_bin:
        ydl_opts["ffmpeg_location"] = os.path.dirname(ffmpeg_bin)

    tracks = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            entries = info.get("entries", [])

            if entries:
                for i, item in enumerate(entries, start=1):
                    if not item:
                        continue
                    video_id = item.get("id")
                    tracks.append({
                        "id": video_id,
                        "title": item.get("title", f"Track {i}"),
                        "artist": item.get("uploader") or item.get("channel") or info.get("uploader") or "Unknown Artist",
                        "duration": format_duration(item.get("duration")),
                        "duration_sec": item.get("duration") or 0,
                        "thumbnail": item.get("thumbnail") or f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "track_number": i,
                        "engine": "youtube"
                    })
            else:
                # Single video album
                video_id = info.get("id") or playlist_url_or_id
                tracks.append({
                    "id": video_id,
                    "title": info.get("title", "Full Album"),
                    "artist": info.get("uploader") or info.get("channel") or "Unknown Artist",
                    "duration": format_duration(info.get("duration")),
                    "duration_sec": info.get("duration") or 0,
                    "thumbnail": info.get("thumbnail") or f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "track_number": 1,
                    "engine": "youtube"
                })
    except Exception as e:
        logger.error(f"Error extracting playlist tracks: {e}")

    return tracks


def _build_progress_hook(shared_item, broadcast_fn):
    """Return a yt_dlp progress hook that updates shared_item and broadcasts via broadcast_fn."""
    def hook(d: dict) -> None:
        status = d.get("status")
        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            if total > 0:
                shared_item["progress"] = round((downloaded / total) * 100, 2)

            speed_bytes = d.get("speed") or 0
            if speed_bytes > 1024 * 1024:
                shared_item["speed"] = f"{speed_bytes / (1024 * 1024):.1f} MB/s"
            elif speed_bytes > 1024:
                shared_item["speed"] = f"{speed_bytes / 1024:.0f} KB/s"
            else:
                shared_item["speed"] = f"{speed_bytes:.0f} B/s"

            eta_sec = d.get("eta")
            if eta_sec is not None:
                mins = int(eta_sec) // 60
                secs = int(eta_sec) % 60
                shared_item["eta"] = f"{mins:02d}:{secs:02d}"

            broadcast_fn(shared_item)

        elif status == "finished":
            shared_item["progress"] = 95.0
            shared_item["status"] = "processing"
            shared_item["speed"] = "Etiquetando ID3..."
            broadcast_fn(shared_item)
    return hook


def _tag_mp3(file_path: Path, title: str, artist: str, album: str, thumbnail_url: str | None) -> None:
    """Embed ID3 tags and cover art into an MP3 file."""
    try:
        audio = MP3(file_path, ID3=ID3)
        try:
            audio.add_tags()
        except Exception:
            pass

        audio.tags.add(TIT2(encoding=3, text=title))
        audio.tags.add(TPE1(encoding=3, text=artist))
        audio.tags.add(TALB(encoding=3, text=album))

        if thumbnail_url:
            try:
                thumb_path = file_path.parent / f"temp_{file_path.stem}.jpg"
                urllib.request.urlretrieve(thumbnail_url, thumb_path)
                with open(thumb_path, "rb") as img_file:
                    audio.tags.add(
                        APIC(
                            encoding=3,
                            mime="image/jpeg",
                            type=3,
                            desc="Cover",
                            data=img_file.read()
                        )
                    )
                if thumb_path.exists():
                    thumb_path.unlink()
            except Exception as img_err:
                logger.warning(f"Failed to embed thumbnail: {img_err}")

        audio.save()
    except Exception as tag_err:
        logger.warning(f"Error tagging MP3 file: {tag_err}")


def download_youtube_track(
    video_url: str,
    output_dir: Path,
    preferred_quality: str = "320k",
    progress_hook=None,
) -> dict:
    """Download audio from YouTube using yt_dlp's Python API with real-time progress hooks."""
    output_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg_bin = get_ffmpeg_path()

    preferred_ext = "mp3" if preferred_quality in ["320k", "standard"] else "flac"
    out_tmpl = str(output_dir / "%(id)s.%(ext)s")

    ydl_opts: dict = {
        "format": "bestaudio[acodec!=none]/bestaudio/best",
        "outtmpl": out_tmpl,
        "extract_audio": True,
        "audio_format": preferred_ext,
        "audio_quality": "320" if preferred_quality == "320k" else "192",
        "writethumbnail": True,
        "retries": 10,
        "fragment_retries": 10,
        "noprogress": True,
        "quiet": True,
        "no_warnings": True,
    }
    _apply_yt_dlp_extras(ydl_opts)
    if ffmpeg_bin:
        ydl_opts["ffmpeg_location"] = os.path.dirname(ffmpeg_bin)

    # Notify progress at start
    if progress_hook:
        progress_hook({"status": "downloading", "_percent_str": "0%", "downloaded_bytes": 0, "total_bytes": 0})

    info: dict | None = None
    last_error: str | None = None
    max_attempts = 3

    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(f"yt-dlp download attempt {attempt}/{max_attempts} for {video_url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
            if info:
                break
        except Exception as e:
            last_error = str(e)
            logger.warning(f"yt-dlp attempt {attempt}/{max_attempts} failed: {e}")
            if attempt < max_attempts:
                import time as _time
                _time.sleep(2.0)

    if not info:
        raise RuntimeError(f"Download failed after {max_attempts} attempts: {last_error}")

    title = info.get("title", "downloaded_track")
    artist = info.get("uploader") or info.get("channel") or "Unknown Artist"
    album = info.get("album") or "YouTube Release"
    thumbnail_url = info.get("thumbnail")
    video_id = info.get("id", "unknown_id")
    clean_t = clean_filename(title)

    final_file = output_dir / f"{video_id}.{preferred_ext}"
    if not final_file.exists():
        logger.warning(f"File not found at exact expected path {final_file}. Falling back to recent files.")
        candidates = list(output_dir.glob(f"*.{preferred_ext}"))
        if candidates:
            final_file = max(candidates, key=os.path.getctime)

    if progress_hook:
        progress_hook({"status": "finished", "filename": str(final_file)})

    if final_file.exists() and preferred_ext == "mp3":
        _tag_mp3(final_file, title, artist, album, thumbnail_url)

    return {
        "title": title,
        "artist": artist,
        "file_path": str(final_file),
        "file_name": f"{clean_t}.{preferred_ext}",
        "quality": preferred_quality,
        "engine": "youtube"
    }

