import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

# Load .env from backend root as early as possible
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.download import router as download_router
from app.api.endpoints.library import router as library_router
from app.api.endpoints.search import router as search_router
from app.api.endpoints.settings import router as settings_router
from app.api.endpoints.websocket import router as websocket_router
from app.core.auth import AuthMiddleware
from app.core.config import DOWNLOADS_DIR, get_env_settings
from app.core.db import Base, engine
from app.core.ffmpeg_utils import ensure_ffmpeg
from app.core.rate_limit import limiter as shared_limiter
from app.core.security_headers import SecurityHeadersMiddleware
from app.services.download_manager import download_manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("aura_backend")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Aura Music Downloader Backend...")

    # Capture the running event loop so background threads (download workers)
    # can schedule WebSocket broadcasts safely via run_coroutine_threadsafe.
    loop = asyncio.get_running_loop()
    download_manager.bind_event_loop(loop)

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

# Security: Bearer-token auth (when AURA_AUTH_TOKEN is set) + security headers.
app.add_middleware(AuthMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Wire the rate limiter as a global exception handler and app state.
app.state.limiter = shared_limiter
# Make sure endpoint-level limiters share the same limiter instance so the
# exception handler + storage stay consistent.
search_router.limiter = shared_limiter
download_router.limiter = shared_limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enable CORS for React frontend — explicit origins only.
# Browsers reject Access-Control-Allow-Origin: * when credentials are allowed.
_env_settings = get_env_settings()
_cors_origins = [
    o.strip() for o in _env_settings.frontend_url.split(",") if o.strip()
]
# Always allow localhost for development
for dev_origin in ("http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"):
    if dev_origin not in _cors_origins:
        _cors_origins.append(dev_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include HTTP & WebSocket routers
app.include_router(search_router, prefix="/api", tags=["Search"])
app.include_router(download_router, prefix="/api", tags=["Download"])
app.include_router(settings_router, prefix="/api", tags=["Settings"])
app.include_router(library_router, prefix="/api", tags=["Library"])
app.include_router(auth_router, prefix="/api", tags=["Auth"])
app.include_router(websocket_router, tags=["WebSocket"])

# Serve downloads static directory
app.mount("/downloads", StaticFiles(directory=DOWNLOADS_DIR), name="downloads")

@app.get("/api/health")
def health_check():
    return {"status": "online", "app": "Aura Music Downloader", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    _env = get_env_settings()
    uvicorn.run("main:app", host=_env.host, port=_env.port, reload=True)
