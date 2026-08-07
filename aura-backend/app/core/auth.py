"""Bearer-token authentication middleware.

If `EnvSettings.auth_token` is empty, auth is disabled and every request is
allowed. Otherwise, requests must include `Authorization: Bearer <token>`,
matching the configured token via a constant-time comparison.

Public endpoints exempt from auth:
  - /api/health
  - /api/auth/status   (used by the frontend to detect if login is required)
  - /api/auth/login    (the login endpoint itself)
  - /ws/downloads      (WebSocket — auth is checked in the WS endpoint itself)
  - /docs, /openapi.json, /redoc
"""
import hmac
import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_env_settings

logger = logging.getLogger(__name__)

PUBLIC_PATHS = {
    "/api/health",
    "/api/auth/status",
    "/api/auth/login",
    "/docs",
    "/docs/oauth2-redirect",
    "/openapi.json",
    "/redoc",
}


def _is_authorized(request: Request) -> bool:
    env = get_env_settings()
    if not env.auth_enabled:
        return True

    # Allow token in either Authorization header or ?token=... query string
    # (the query string variant supports the WebSocket which can't send custom
    # headers in browsers).
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        provided = auth[7:].strip()
    else:
        provided = request.query_params.get("token", "")

    if not provided:
        return False
    return hmac.compare_digest(provided, env.auth_token)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path in PUBLIC_PATHS or path.startswith("/downloads/"):
            return await call_next(request)

        if not _is_authorized(request):
            logger.warning(f"Blocked unauthenticated request to {path}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication required"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        return await call_next(request)
