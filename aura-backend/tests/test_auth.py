"""Tests for the bearer-token auth middleware and login endpoint."""
import pytest
from fastapi.testclient import TestClient

from app.core import config


@pytest.fixture
def auth_env(monkeypatch):
    """Enable auth with a known token."""
    monkeypatch.setenv("AUTH_TOKEN", "test-secret-123")
    config.get_env_settings.cache_clear()


@pytest.fixture
def no_auth_env(monkeypatch):
    """Disable auth (default behaviour)."""
    monkeypatch.setenv("AUTH_TOKEN", "")
    config.get_env_settings.cache_clear()


@pytest.fixture
def client_factory():
    from app.main import app
    return lambda: TestClient(app)


def test_auth_status_no_auth_required(client_factory, no_auth_env):
    with client_factory() as c:
        r = c.get("/api/auth/status")
        assert r.status_code == 200
        assert r.json()["auth_required"] is False


def test_auth_status_with_auth_required(client_factory, auth_env):
    with client_factory() as c:
        r = c.get("/api/auth/status")
        assert r.status_code == 200
        assert r.json()["auth_required"] is True


def test_public_endpoints_accessible_without_token(client_factory, auth_env):
    with client_factory() as c:
        r = c.get("/api/health")
        assert r.status_code == 200


def test_protected_endpoint_requires_token(client_factory, auth_env):
    with client_factory() as c:
        r = c.get("/api/library")
        assert r.status_code == 401
        assert r.headers.get("www-authenticate", "").lower() == "bearer"


def test_protected_endpoint_accepts_valid_bearer(client_factory, auth_env):
    with client_factory() as c:
        r = c.get(
            "/api/library",
            headers={"Authorization": "Bearer test-secret-123"},
        )
        assert r.status_code == 200


def test_protected_endpoint_rejects_wrong_token(client_factory, auth_env):
    with client_factory() as c:
        r = c.get(
            "/api/library",
            headers={"Authorization": "Bearer wrong"},
        )
        assert r.status_code == 401


def test_protected_endpoint_accepts_token_query_param(client_factory, auth_env):
    with client_factory() as c:
        r = c.get("/api/library?token=test-secret-123")
        assert r.status_code == 200


def test_login_succeeds_with_correct_token(client_factory, auth_env):
    with client_factory() as c:
        r = c.post("/api/auth/login", json={"token": "test-secret-123"})
        assert r.status_code == 204


def test_login_fails_with_wrong_token(client_factory, auth_env):
    with client_factory() as c:
        r = c.post("/api/auth/login", json={"token": "wrong"})
        assert r.status_code == 401


def test_login_is_noop_when_auth_disabled(client_factory, no_auth_env):
    with client_factory() as c:
        r = c.post("/api/auth/login", json={"token": "anything"})
        assert r.status_code == 204


def test_security_headers_present(client_factory, no_auth_env):
    with client_factory() as c:
        r = c.get("/api/health")
        assert r.headers.get("x-content-type-options") == "nosniff"
        assert r.headers.get("x-frame-options") == "DENY"
        assert "content-security-policy" in r.headers
        assert r.headers.get("referrer-policy") == "no-referrer"


def test_security_headers_csp_blocks_inline_unsafe(client_factory, no_auth_env):
    with client_factory() as c:
        csp = c.get("/api/health").headers.get("content-security-policy", "")
        assert "default-src 'self'" in csp
        assert "frame-ancestors 'none'" in csp
