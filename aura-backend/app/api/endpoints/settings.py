from fastapi import APIRouter
from app.core.config import load_settings, save_settings, AppSettings

router = APIRouter()

@router.get("/settings")
def get_app_settings():
    return load_settings()

@router.post("/settings")
def update_app_settings(settings: AppSettings):
    updated = save_settings(settings)
    return {
        "status": "success",
        "settings": updated
    }
