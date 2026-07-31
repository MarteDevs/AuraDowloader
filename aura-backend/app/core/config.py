import os
import json
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOWNLOADS_DIR = BASE_DIR / "downloads"
TEMP_DIR = BASE_DIR / "temp"
SETTINGS_FILE = BASE_DIR / "settings.json"

DOWNLOADS_DIR.mkdir(exist_ok=True, parents=True)
TEMP_DIR.mkdir(exist_ok=True, parents=True)

class AppSettings(BaseModel):
    arl_token: str = ""
    default_quality: str = "flac"  # "flac", "320k", "standard"
    download_dir: str = str(DOWNLOADS_DIR)

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
