import os
import re
import urllib.request
import logging
from pathlib import Path
import yt_dlp
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB

from app.core.ffmpeg_utils import get_ffmpeg_path
from app.core.config import load_settings, BASE_DIR

logger = logging.getLogger(__name__)

# Path to yt-dlp config file with --remote-components and --js-runtimes
YT_DLP_CONF = BASE_DIR / "yt-dlp.conf"

def _apply_yt_dlp_extras(ydl_opts: dict) -> dict:
    """Apply cookies and config file to ydl_opts."""
    settings = load_settings()
    cookies_path = Path(settings.cookies_file)
    if cookies_path.exists():
        ydl_opts["cookiefile"] = str(cookies_path)
    if YT_DLP_CONF.exists():
        ydl_opts["config_locations"] = [str(YT_DLP_CONF)]
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

def download_youtube_track(video_url: str, output_dir: Path, preferred_quality: str = "320k", progress_hook=None) -> dict:
    import subprocess
    import json as _json
    import shutil

    output_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg_bin = get_ffmpeg_path()
    
    preferred_ext = "mp3" if preferred_quality in ["320k", "standard"] else "flac"
    out_tmpl = str(output_dir / "%(title)s.%(ext)s")
    
    # Find yt-dlp binary (inside venv)
    yt_dlp_bin = shutil.which("yt-dlp")
    if not yt_dlp_bin:
        # Fallback: try to find it relative to this Python
        import sys
        venv_bin = Path(sys.executable).parent
        yt_dlp_bin = str(venv_bin / "yt-dlp")

    # Build CLI command (proven to work from terminal)
    cmd = [
        yt_dlp_bin,
        "--format", "bestaudio/best",
        "--extract-audio",
        "--audio-format", preferred_ext,
        "--audio-quality", "320" if preferred_quality == "320k" else "192",
        "--output", out_tmpl,
        "--write-thumbnail",
        "--retries", "10",
        "--fragment-retries", "10",
        "--js-runtimes", "node",
        "--remote-components", "ejs:github",
        "--no-warnings",
        "--print-json",
    ]

    # Add cookies if available
    settings = load_settings()
    cookies_path = Path(settings.cookies_file)
    if cookies_path.exists():
        cmd.extend(["--cookies", str(cookies_path)])
        logger.info(f"Using YouTube cookies from: {cookies_path}")

    # Add ffmpeg location
    if ffmpeg_bin:
        cmd.extend(["--ffmpeg-location", os.path.dirname(ffmpeg_bin)])

    # Add the video URL
    cmd.append(video_url)

    # Notify progress
    if progress_hook:
        progress_hook({"status": "downloading", "_percent_str": "0%", "downloaded_bytes": 0, "total_bytes": 0})

    max_attempts = 3
    last_error = None
    info = None

    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(f"Download attempt {attempt}/{max_attempts} for {video_url}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                # Parse JSON output from --print-json
                stdout_lines = result.stdout.strip().split("\n")
                for line in reversed(stdout_lines):
                    try:
                        info = _json.loads(line)
                        break
                    except _json.JSONDecodeError:
                        continue
                break
            else:
                last_error = result.stderr.strip() or result.stdout.strip()
                logger.warning(f"Download attempt {attempt}/{max_attempts} failed for {video_url}: {last_error}")
                if attempt < max_attempts:
                    import time
                    time.sleep(2.0)
        except subprocess.TimeoutExpired:
            last_error = "Download timed out after 5 minutes"
            logger.warning(f"Download attempt {attempt}/{max_attempts} timed out for {video_url}")
        except Exception as e:
            last_error = str(e)
            logger.warning(f"Download attempt {attempt}/{max_attempts} failed for {video_url}: {e}")
            if attempt < max_attempts:
                import time
                time.sleep(2.0)

    if not info:
        raise RuntimeError(f"Download failed after {max_attempts} attempts: {last_error}")

    title = info.get("title", "downloaded_track")
    artist = info.get("uploader") or info.get("channel") or "Unknown Artist"
    thumbnail_url = info.get("thumbnail")
    
    clean_t = clean_filename(title)
    final_file = output_dir / f"{clean_t}.{preferred_ext}"

    if not final_file.exists():
        files = list(output_dir.glob(f"*.{preferred_ext}"))
        if files:
            final_file = max(files, key=os.path.getctime)

    # Notify progress complete
    if progress_hook:
        progress_hook({"status": "finished", "filename": str(final_file)})

    # Inject ID3 tags if MP3
    if final_file.exists() and preferred_ext == "mp3":
        try:
            audio = MP3(final_file, ID3=ID3)
            try:
                audio.add_tags()
            except Exception:
                pass

            audio.tags.add(TIT2(encoding=3, text=title))
            audio.tags.add(TPE1(encoding=3, text=artist))
            audio.tags.add(TALB(encoding=3, text="YouTube Release"))

            # Download thumbnail and embed as cover art
            if thumbnail_url:
                try:
                    thumb_path = output_dir / f"temp_{info.get('id')}.jpg"
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

    return {
        "title": title,
        "artist": artist,
        "file_path": str(final_file),
        "file_name": final_file.name if final_file.exists() else f"{title}.{preferred_ext}",
        "quality": preferred_quality,
        "engine": "youtube"
    }

