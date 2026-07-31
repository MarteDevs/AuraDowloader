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

logger = logging.getLogger(__name__)

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
        "default_search": f"ytsearchplaylist{limit}",
    }
    if ffmpeg_bin:
        ydl_opts["ffmpeg_location"] = os.path.dirname(ffmpeg_bin)

    results = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearchplaylist{limit}:{query} album", download=False)
            entries = info.get("entries", [])
            for item in entries:
                if not item:
                    continue
                playlist_id = item.get("id")
                title = item.get("title", "Unknown Album")
                uploader = item.get("uploader") or item.get("channel") or "Unknown Artist"
                entry_count = item.get("playlist_count") or len(item.get("entries", [])) or 0
                thumbnail = item.get("thumbnail") or ""
                
                results.append({
                    "id": playlist_id,
                    "title": title,
                    "artist": uploader,
                    "thumbnail": thumbnail,
                    "nb_tracks": entry_count,
                    "type": "album",
                    "engine": "youtube",
                    "url": f"https://www.youtube.com/playlist?list={playlist_id}" if not playlist_id.startswith("http") else playlist_id
                })
    except Exception as e:
        logger.error(f"Error searching YouTube playlists for '{query}': {e}")

    return results

def get_youtube_playlist_tracks(playlist_url_or_id: str) -> list[dict]:
    ffmpeg_bin = get_ffmpeg_path()
    url = playlist_url_or_id if playlist_url_or_id.startswith("http") else f"https://www.youtube.com/playlist?list={playlist_url_or_id}"
    
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
    }
    if ffmpeg_bin:
        ydl_opts["ffmpeg_location"] = os.path.dirname(ffmpeg_bin)

    tracks = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            entries = info.get("entries", [])
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
    except Exception as e:
        logger.error(f"Error extracting playlist tracks: {e}")

    return tracks

def download_youtube_track(video_url: str, output_dir: Path, preferred_quality: str = "320k", progress_hook=None) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg_bin = get_ffmpeg_path()
    
    preferred_ext = "mp3" if preferred_quality in ["320k", "standard"] else "flac"
    
    out_tmpl = str(output_dir / "%(title)s.%(ext)s")
    
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": out_tmpl,
        "writethumbnail": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": preferred_ext,
                "preferredquality": "320" if preferred_quality == "320k" else "192",
            }
        ],
        "quiet": True,
        "no_warnings": True,
    }
    
    if ffmpeg_bin:
        ydl_opts["ffmpeg_location"] = os.path.dirname(ffmpeg_bin)
        
    if progress_hook:
        ydl_opts["progress_hooks"] = [progress_hook]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        title = info.get("title", "downloaded_track")
        artist = info.get("uploader") or info.get("channel") or "Unknown Artist"
        thumbnail_url = info.get("thumbnail")
        
        expected_filename = ydl.prepare_filename(info)
        base_path, _ = os.path.splitext(expected_filename)
        final_file = Path(f"{base_path}.{preferred_ext}")

        if not final_file.exists():
            # Fallback search for created file in dir
            files = list(output_dir.glob(f"*.{preferred_ext}"))
            if files:
                final_file = max(files, key=os.path.getctime)

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
