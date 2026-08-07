from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import AppSettings, load_settings, safe_alpath, save_settings

router = APIRouter()


class PublicSettings(BaseModel):
    """Settings safe to expose to clients — never includes the ARL token."""
    has_arl: bool
    default_quality: str
    download_dir: str
    cookies_file: str


@router.get("/settings", response_model=PublicSettings)
def get_app_settings():
    s = load_settings()
    return PublicSettings(
        has_arl=bool(s.arl_token.strip()),
        default_quality=s.default_quality,
        download_dir=s.download_dir,
        cookies_file=s.cookies_file,
    )


@router.post("/settings")
def update_app_settings(settings: AppSettings):
    # Reject download_dir pointing outside the allowed roots.
    if settings.download_dir:
        try:
            safe_alpath(settings.download_dir)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    updated = save_settings(settings)
    return {
        "status": "success",
        "settings": {
            "has_arl": bool(updated.arl_token.strip()),
            "default_quality": updated.default_quality,
            "download_dir": updated.download_dir,
            "cookies_file": updated.cookies_file,
        }
    }
