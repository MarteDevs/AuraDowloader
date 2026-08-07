import json
import os
import tempfile
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env from backend root exactly once.
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=_env_path, override=False)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Filesystem layout — pure paths, no env-driven behavior. Kept as module-level
# constants for backwards-compat with the original config.
# ---------------------------------------------------------------------------
_env_download_dir = os.getenv("DOWNLOAD_DIR", "").strip()
DOWNLOADS_DIR = Path(_env_download_dir) if _env_download_dir else BASE_DIR / "downloads"
TEMP_DIR = BASE_DIR / "temp"
SETTINGS_FILE = BASE_DIR / "settings.json"
COOKIES_FILE = BASE_DIR / "youtube_cookies.txt"  # Exportar desde Chrome/Firefox con extensión "Get cookies.txt"

DOWNLOADS_DIR.mkdir(exist_ok=True, parents=True)
TEMP_DIR.mkdir(exist_ok=True, parents=True)


# ---------------------------------------------------------------------------
# Whitelist of directories where the user is allowed to write downloads.
# Computed once at import time; safe_alpath() refuses anything outside these.
# ---------------------------------------------------------------------------
def _build_allowed_roots() -> tuple[Path, ...]:
    roots: list[Path] = [DOWNLOADS_DIR.resolve(), (BASE_DIR / "downloads").resolve()]
    extra = os.getenv("ALLOWED_DOWNLOAD_DIRS", "").strip()
    if extra:
        roots.extend(Path(p).expanduser().resolve() for p in extra.split(os.pathsep) if p)
    roots.append(Path(tempfile.gettempdir()).resolve())
    return tuple(roots)

ALLOWED_DOWNLOAD_ROOTS: tuple[Path, ...] = _build_allowed_roots()


def safe_alpath(path: str | Path) -> Path:
    """Resolve *path* and verify it lives under one of ALLOWED_DOWNLOAD_ROOTS.

    Raises ValueError on path traversal attempts or out-of-whitelist targets.
    """
    if not path:
        raise ValueError("Path is empty")
    resolved = Path(path).expanduser().resolve()
    for root in ALLOWED_DOWNLOAD_ROOTS:
        try:
            resolved.relative_to(root)
            return resolved
        except ValueError:
            continue
    raise ValueError(
        f"Path '{resolved}' is outside allowed roots: "
        f"{[str(r) for r in ALLOWED_DOWNLOAD_ROOTS]}"
    )


# ---------------------------------------------------------------------------
# Settings (the JSON-backed user-tweakable ones) — still a plain BaseModel
# because the user can save and reload them at runtime via the UI.
# ---------------------------------------------------------------------------
class AppSettings(BaseModel):
    arl_token: str = ""
    default_quality: str = "flac"  # "flac", "320k", "standard"
    download_dir: str = str(DOWNLOADS_DIR)
    cookies_file: str = str(COOKIES_FILE)  # Ruta al archivo cookies.txt de YouTube


def load_settings() -> AppSettings:
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, encoding="utf-8") as f:
                data = json.load(f)
                return AppSettings(**data)
        except Exception:
            pass
    return AppSettings()


def save_settings(settings: AppSettings) -> AppSettings:
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings.model_dump(), f, indent=2)
    return settings


# ---------------------------------------------------------------------------
# Env-driven app config (host, port, DB, CORS) — pydantic-settings, loaded
# once and cached. Replaces ad-hoc os.getenv() calls scattered through the
# codebase.
# ---------------------------------------------------------------------------
class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_env_path),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    host: str = "127.0.0.1"
    port: int = 8000

    db_user: str = "root"
    db_password: str = "marte"
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "aura_music_db"
    database_url: str | None = None  # if set, overrides individual DB_* fields

    download_dir: str = ""  # empty -> use default
    frontend_url: str = "http://localhost:5173"

    # Authentication. Empty -> auth disabled (dev mode). In production set
    # AURA_AUTH_TOKEN to a long random string.
    auth_token: str = ""

    # Max bytes for a single download. Default 500 MiB.
    max_download_bytes: int = 500 * 1024 * 1024

    @property
    def auth_enabled(self) -> bool:
        return bool(self.auth_token.strip())

    @property
    def mysql_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache(maxsize=1)
def get_env_settings() -> EnvSettings:
    """Cached env settings — call this everywhere instead of os.getenv()."""
    return EnvSettings()

