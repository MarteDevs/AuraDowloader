"""Process-wide rate limiter used by the search & download endpoints.

Limits are intentionally conservative: search calls YouTube/Deezer upstream
APIs and download calls external services. Both are easy to abuse.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

# Default 30 req/min per IP for read-only endpoints, configurable via env.
SEARCH_LIMIT = "30/minute"
DOWNLOAD_LIMIT = "10/minute"
WRITE_LIMIT = "10/minute"

# storage_uri defaults to "memory://" which is fine for a single-process dev
# install. For production with multiple workers, set RATE_LIMIT_STORAGE_URI
# to a redis:// URL.
limiter = Limiter(key_func=get_remote_address)
