"""Tests for the safe_alpath path-traversal guard."""
from pathlib import Path

import pytest

from app.core import config
from app.core.config import safe_alpath


def test_safe_alpath_accepts_downloads_root(tmp_path: Path, monkeypatch):
    fake_root = tmp_path / "downloads"
    fake_root.mkdir()
    monkeypatch.setattr(config, "ALLOWED_DOWNLOAD_ROOTS", (fake_root.resolve(),))
    target = safe_alpath(str(fake_root / "subdir" / "track.mp3"))
    assert target == (fake_root / "subdir" / "track.mp3").resolve()


def test_safe_alpath_rejects_traversal(tmp_path: Path, monkeypatch):
    fake_root = tmp_path / "downloads"
    fake_root.mkdir()
    monkeypatch.setattr(config, "ALLOWED_DOWNLOAD_ROOTS", (fake_root.resolve(),))
    outside = tmp_path / "secret" / "leak.txt"
    outside.parent.mkdir()
    outside.write_text("nope")
    with pytest.raises(ValueError):
        safe_alpath(str(outside))


def test_safe_alpath_rejects_dotdot(tmp_path: Path, monkeypatch):
    fake_root = tmp_path / "downloads"
    fake_root.mkdir()
    monkeypatch.setattr(config, "ALLOWED_DOWNLOAD_ROOTS", (fake_root.resolve(),))
    with pytest.raises(ValueError):
        safe_alpath(str(fake_root / ".." / ".." / "etc" / "passwd"))


def test_safe_alpath_rejects_empty():
    with pytest.raises(ValueError):
        safe_alpath("")
