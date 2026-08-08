import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import DOWNLOADS_DIR, AppSettings, load_settings, safe_alpath, save_settings

logger = logging.getLogger(__name__)

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
    # Normalize download_dir: reject path-traversal silently by falling back to
    # the default rather than 400-ing the user. Auto-create if missing.
    if settings.download_dir:
        try:
            candidate = safe_alpath(settings.download_dir)
            candidate.mkdir(parents=True, exist_ok=True)
        except (ValueError, OSError) as e:
            logger.warning(
                f"download_dir '{settings.download_dir}' unusable ({e}); "
                f"falling back to default '{DOWNLOADS_DIR}'"
            )
            settings.download_dir = str(DOWNLOADS_DIR)
            try:
                DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
            except OSError as fallback_err:
                raise HTTPException(
                    status_code=500,
                    detail=f"Default download_dir '{DOWNLOADS_DIR}' unusable: {fallback_err}",
                ) from fallback_err
    else:
        settings.download_dir = str(DOWNLOADS_DIR)

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
