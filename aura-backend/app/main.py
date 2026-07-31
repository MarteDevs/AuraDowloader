import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import DOWNLOADS_DIR
from app.core.ffmpeg_utils import ensure_ffmpeg
from app.api.endpoints.search import router as search_router
from app.api.endpoints.download import router as download_router
from app.api.endpoints.settings import router as settings_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("aura_backend")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Aura Music Downloader Backend...")
    ensure_ffmpeg()
    yield
    logger.info("Shutting down Aura Music Downloader Backend...")

app = FastAPI(
    title="Aura Music Downloader API",
    version="1.0.0",
    description="Client-server API for music search, high-quality audio extraction, ID3 tagging, and lossless FLAC downloads.",
    lifespan=lifespan
)

# Enable CORS for React frontend (Vite default port 5173 or any origin during dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(search_router, prefix="/api", tags=["Search"])
app.include_router(download_router, prefix="/api", tags=["Download"])
app.include_router(settings_router, prefix="/api", tags=["Settings"])

# Serve downloads static directory
app.mount("/downloads", StaticFiles(directory=DOWNLOADS_DIR), name="downloads")

@app.get("/api/health")
def health_check():
    return {"status": "online", "app": "Aura Music Downloader", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
