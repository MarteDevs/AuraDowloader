"""Tests for cancel/retry/remove actions on the DownloadManager."""
import pytest

from app.services.download_manager import DownloadManager, _DownloadCancelled


@pytest.fixture
def manager(monkeypatch):
    """Build a DownloadManager that doesn't actually run downloads."""
    monkeypatch.setattr(
        "app.services.download_manager.DownloadManager._process_download",
        lambda self, *a, **kw: None,
    )
    return DownloadManager()


def test_add_creates_item_with_status_queued(manager):
    item = manager.add_to_queue({"title": "t", "artist": "a", "url": "u", "engine": "youtube"})
    assert item.status == "queued"
    assert item.id in manager.queue
    assert item.id in manager._track_info
    assert manager.is_cancelled(item.id) is False


def test_cancel_marks_status_and_returns_true_for_active(manager):
    item = manager.add_to_queue({"title": "t", "artist": "a", "url": "u", "engine": "youtube"})
    assert manager.cancel(item.id) is True
    assert manager.queue[item.id].status == "cancelled"
    assert manager.is_cancelled(item.id) is True


def test_cancel_returns_false_for_unknown_id(manager):
    assert manager.cancel("nonexistent") is False


def test_cancel_returns_false_for_completed(manager):
    item = manager.add_to_queue({"title": "t", "artist": "a", "url": "u", "engine": "youtube"})
    item.status = "completed"
    assert manager.cancel(item.id) is False


def test_retry_resets_cancelled_item_to_queued(manager):
    item = manager.add_to_queue({"title": "t", "artist": "a", "url": "u", "engine": "youtube"})
    manager.cancel(item.id)
    new = manager.retry(item.id)
    assert new is not None
    assert new.status == "queued"
    assert new.id == item.id
    assert manager.is_cancelled(item.id) is False


def test_retry_returns_none_for_unknown_id(manager):
    assert manager.retry("nonexistent") is None


def test_remove_drops_in_memory_state(manager):
    item = manager.add_to_queue({"title": "t", "artist": "a", "url": "u", "engine": "youtube"})
    assert manager.remove(item.id) is True
    assert item.id not in manager.queue
    assert item.id not in manager._track_info
    assert item.id not in manager._cancel_flags


def test_remove_returns_false_for_unknown_id(manager):
    assert manager.remove("nonexistent") is False


def test_cancelled_exception_is_a_subclass_of_exception():
    assert issubclass(_DownloadCancelled, Exception)
