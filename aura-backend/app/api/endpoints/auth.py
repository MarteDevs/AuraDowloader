"""Authentication endpoints.

POST /api/auth/login
  Body: { "token": "..." }
  Returns 204 No Content on success, 401 on failure.

GET /api/auth/status
  Returns { "auth_required": bool, "version": "2.0.0" }.
"""
import hmac
import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.core.config import get_env_settings

logger = logging.getLogger(__name__)

router = APIRouter()


class LoginRequest(BaseModel):
    token: str


@router.get("/auth/status")
def auth_status():
    env = get_env_settings()
    return {
        "auth_required": env.auth_enabled,
        "version": "2.0.0",
    }


@router.post("/auth/login", status_code=status.HTTP_204_NO_CONTENT)
def login(req: LoginRequest):
    env = get_env_settings()
    if not env.auth_enabled:
        # Auth disabled — log in is a no-op.
        return None
    if not hmac.compare_digest(req.token.strip(), env.auth_token):
        logger.warning("Failed login attempt with wrong token.")
        raise HTTPException(status_code=401, detail="Invalid token")
    return None
