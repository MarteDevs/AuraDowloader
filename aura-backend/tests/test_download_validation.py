"""Tests for the quality validation logic in the download endpoint."""
import pytest

from app.api.endpoints.download import _normalize_quality


@pytest.mark.parametrize(
    "engine,quality,expected",
    [
        ("deezer", "flac", "flac"),
        ("deezer", "320k", "320k"),
        ("deezer", "standard", "standard"),
        ("youtube", "320k", "320k"),
        ("youtube", "standard", "standard"),
        # FLAC isn't supported on the YouTube engine — must fall back.
        ("youtube", "flac", "320k"),
        # Unknown quality falls back to 320k.
        ("youtube", "ultra", "320k"),
    ],
)
def test_normalize_quality(engine, quality, expected):
    assert _normalize_quality(engine, quality) == expected


def test_pydantic_download_request_normalizes_quality():
    from app.api.endpoints.download import DownloadRequest
    req = DownloadRequest(
        id="abc",
        title="t",
        artist="a",
        engine="youtube",
        quality="flac",  # invalid for YouTube
    )
    assert req.quality == "320k"


def test_pydantic_album_download_request_normalizes_quality():
    from app.api.endpoints.download import AlbumDownloadRequest
    req = AlbumDownloadRequest(
        album_id="x",
        album_title="X",
        artist="a",
        engine="deezer",
        quality="flac",
        tracks=[],
    )
    assert req.quality == "flac"
