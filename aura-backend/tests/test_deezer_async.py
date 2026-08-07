"""Tests for the new async Deezer client."""
from unittest.mock import AsyncMock, patch

import pytest

from app.services.deezer_service import (
    format_duration,
    get_deezer_album_tracks_async,
    search_deezer_albums_async,
    search_deezer_async,
)


def test_format_duration_basic():
    assert format_duration(0) == "00:00"
    assert format_duration(125) == "02:05"


@pytest.mark.asyncio
async def test_search_deezer_async_parses_results():
    fake_payload = {
        "data": [
            {
                "id": 1,
                "title": "Test Track",
                "duration": 200,
                "link": "https://deezer.com/track/1",
                "artist": {"name": "Artist A"},
                "album": {"title": "Album X", "cover_medium": "img.jpg"},
            }
        ]
    }
    with patch("app.services.deezer_service._deezer_get", new=AsyncMock(return_value=fake_payload)):
        results = await search_deezer_async("anything", limit=5, has_arl=True)
    assert len(results) == 1
    r = results[0]
    assert r["id"] == "1"
    assert r["title"] == "Test Track"
    assert r["artist"] == "Artist A"
    assert r["has_flac"] is True
    assert "flac" in r["available_qualities"]


@pytest.mark.asyncio
async def test_search_deezer_async_empty_on_error():
    with patch("app.services.deezer_service._deezer_get", new=AsyncMock(return_value=None)):
        results = await search_deezer_async("x")
    assert results == []


@pytest.mark.asyncio
async def test_search_deezer_albums_async():
    fake = {"data": [{"id": 7, "title": "X", "nb_tracks": 12, "artist": {"name": "A"}, "cover_medium": "img"}]}
    with patch("app.services.deezer_service._deezer_get", new=AsyncMock(return_value=fake)):
        out = await search_deezer_albums_async("x")
    assert out[0]["id"] == "7"
    assert out[0]["nb_tracks"] == 12
    assert out[0]["engine"] == "deezer"


@pytest.mark.asyncio
async def test_get_deezer_album_tracks_async_numbers():
    fake = {"data": [{"id": 1, "title": "t1", "duration": 90, "artist": {"name": "A"}},
                     {"id": 2, "title": "t2", "duration": 100, "artist": {"name": "A"}}]}
    with patch("app.services.deezer_service._deezer_get", new=AsyncMock(return_value=fake)):
        out = await get_deezer_album_tracks_async("7")
    assert [t["track_number"] for t in out] == [1, 2]
    assert out[0]["duration"] == "01:30"
