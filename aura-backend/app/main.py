import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI

# Load .env from backend root as early as possible
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import DOWNLOADS_DIR
from app.core.ffmpeg_utils import ensure_ffmpeg
from app.core.db import engine, Base
from app.api.endpoints.search import router as search_router
from app.api.endpoints.download import router as download_router
from app.api.endpoints.settings import router as settings_router
from app.api.endpoints.library import router as library_router
from app.api.endpoints.websocket import router as websocket_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("aura_backend")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Aura Music Downloader Backend...")
    ensure_ffmpeg()
    
    # Auto-create database tables on startup (checkfirst=True prevents "already exists" errors)
    try:
        logger.info("Creating database tables if not exist...")
        Base.metadata.create_all(bind=engine, checkfirst=True)
        logger.info("Database tables initialized successfully.")
    except Exception as db_err:
        err_msg = str(db_err)
        if "already exists" in err_msg:
            logger.info("Database tables already exist — skipping creation.")
        else:
            logger.error(f"Error creating DB tables: {db_err}")

    yield
    logger.info("Shutting down Aura Music Downloader Backend...")

app = FastAPI(
    title="Aura Music Downloader API",
    version="2.0.0",
    description="Client-server API for music search, high-quality audio extraction, ID3 tagging, WebSocket real-time updates, and database persistence.",
    lifespan=lifespan
)

# Enable CORS for React frontend
_frontend_url = os.getenv("FRONTEND_URL", "*")
_cors_origins = [_frontend_url] if _frontend_url != "*" else ["*"]
# Always allow localhost for development
if "*" not in _cors_origins:
    _cors_origins += ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include HTTP & WebSocket routers
app.include_router(search_router, prefix="/api", tags=["Search"])
app.include_router(download_router, prefix="/api", tags=["Download"])
app.include_router(settings_router, prefix="/api", tags=["Settings"])
app.include_router(library_router, prefix="/api", tags=["Library"])
app.include_router(websocket_router, tags=["WebSocket"])

# Serve downloads static directory
app.mount("/downloads", StaticFiles(directory=DOWNLOADS_DIR), name="downloads")

@app.get("/api/health")
def health_check():
    return {"status": "online", "app": "Aura Music Downloader", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
