"""Smoke tests for pure-logic utilities."""
from app.core.config import AppSettings
from app.services.youtube_service import clean_filename, format_duration


def test_format_duration_basic():
    assert format_duration(0) == "00:00"
    assert format_duration(59) == "00:59"
    assert format_duration(60) == "01:00"
    assert format_duration(125) == "02:05"
    assert format_duration(3600) == "60:00"


def test_format_duration_none():
    assert format_duration(None) == "00:00"


def test_clean_filename_strips_unsafe_chars():
    assert clean_filename("a/b\\c:d*e?f\"g<h>i|j") == "abcdefghij"
    assert clean_filename("normal_name-1.0 (remix)") == "normal_name-1.0 (remix)"
    assert clean_filename("") == ""


def test_app_settings_defaults():
    s = AppSettings()
    assert s.arl_token == ""
    assert s.default_quality == "flac"
    assert s.cookies_file.endswith("youtube_cookies.txt")
