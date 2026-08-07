"""Adds common security headers to every response.

Headers set:
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: no-referrer
  Permissions-Policy: microphone=(), camera=(), geolocation=()
  Cross-Origin-Opener-Policy: same-origin
  Content-Security-Policy: a strict default (see _build_csp)
  Strict-Transport-Security: only when HSTS_ENABLED=1
"""
import os

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


def _build_csp() -> str:
    """Strict CSP. Tailwind/JSDelivr allowed because we serve the bundle ourselves."""
    directives = [
        "default-src 'self'",
        # Inline styles are needed by Tailwind + a few inline style attrs.
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
        "font-src 'self' https://fonts.gstatic.com data:",
        "img-src 'self' data: https:",
        # Backend API on same origin; we don't use websockets to other hosts.
        "connect-src 'self' ws: wss:",
        "script-src 'self' 'unsafe-inline'",
        "frame-ancestors 'none'",
        "base-uri 'self'",
        "form-action 'self'",
    ]
    return "; ".join(directives)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Permissions-Policy",
            "microphone=(), camera=(), geolocation=()",
        )
        response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        response.headers.setdefault("Content-Security-Policy", _build_csp())
        if os.getenv("HSTS_ENABLED", "0") == "1":
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains",
            )
        return response
