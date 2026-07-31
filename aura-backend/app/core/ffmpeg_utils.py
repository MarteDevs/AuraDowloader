import os
import shutil
import logging

logger = logging.getLogger(__name__)

def get_ffmpeg_path() -> str | None:
    # 1. Check system PATH
    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        return sys_ffmpeg
    
    # 2. Try static_ffmpeg package
    try:
        import static_ffmpeg
        static_ffmpeg.add_paths()
        sys_ffmpeg = shutil.which("ffmpeg")
        if sys_ffmpeg:
            return sys_ffmpeg
    except Exception as e:
        logger.warning(f"Could not load static_ffmpeg: {e}")
        
    # 3. Try imageio_ffmpeg
    try:
        import imageio_ffmpeg
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        if ffmpeg_bin and os.path.exists(ffmpeg_bin):
            return ffmpeg_bin
    except Exception as e:
        logger.warning(f"Could not load imageio_ffmpeg: {e}")

    return None

def ensure_ffmpeg():
    path = get_ffmpeg_path()
    if path:
        ffmpeg_dir = os.path.dirname(path)
        if ffmpeg_dir not in os.environ.get("PATH", ""):
            os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
        logger.info(f"FFmpeg located at: {path}")
        return path
    else:
        logger.warning("FFmpeg executable not found in PATH or helper packages.")
        return None

