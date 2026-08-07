"""Shared pytest fixtures."""
from pathlib import Path

import pytest


@pytest.fixture
def temp_download_dir(tmp_path: Path) -> Path:
    """Return a clean temporary download directory."""
    d = tmp_path / "downloads"
    d.mkdir(parents=True, exist_ok=True)
    return d


@pytest.fixture
def fake_settings(tmp_path: Path, monkeypatch):
    """Patch load_settings/save_settings with a controllable in-memory object."""
    from app.core import config

    fake = config.AppSettings(
        arl_token="",
        default_quality="320k",
        download_dir=str(tmp_path / "downloads"),
        cookies_file=str(tmp_path / "cookies.txt"),
    )
    (tmp_path / "downloads").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(config, "load_settings", lambda: fake)
    monkeypatch.setattr(config, "save_settings", lambda s: fake)
    return fake
