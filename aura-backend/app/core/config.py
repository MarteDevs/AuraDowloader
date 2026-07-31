import os
import json
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env from backend root
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Allow DOWNLOAD_DIR to be overridden via env variable (important for VPS)
_env_download_dir = os.getenv("DOWNLOAD_DIR", "").strip()
DOWNLOADS_DIR = Path(_env_download_dir) if _env_download_dir else BASE_DIR / "downloads"
TEMP_DIR = BASE_DIR / "temp"
SETTINGS_FILE = BASE_DIR / "settings.json"
COOKIES_FILE = BASE_DIR / "youtube_cookies.txt"  # Exportar desde Chrome/Firefox con extensión "Get cookies.txt"

DOWNLOADS_DIR.mkdir(exist_ok=True, parents=True)
TEMP_DIR.mkdir(exist_ok=True, parents=True)

class AppSettings(BaseModel):
    arl_token: str = ""
    default_quality: str = "flac"  # "flac", "320k", "standard"
    download_dir: str = str(DOWNLOADS_DIR)
    cookies_file: str = str(COOKIES_FILE)  # Ruta al archivo cookies.txt de YouTube

def load_settings() -> AppSettings:
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return AppSettings(**data)
        except Exception:
            pass
    return AppSettings()

def save_settings(settings: AppSettings) -> AppSettings:
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings.model_dump(), f, indent=2)
    return settings
