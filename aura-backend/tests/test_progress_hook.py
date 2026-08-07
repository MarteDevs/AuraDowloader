"""Smoke test for the progress hook builder."""
from app.services.youtube_service import _build_progress_hook


def test_progress_hook_emits_progress_with_total():
    shared = {"progress": 0.0, "speed": "", "eta": "", "status": ""}
    broadcasts = []

    def broadcast(_item):
        broadcasts.append(dict(shared))

    hook = _build_progress_hook(shared, broadcast)
    hook({
        "status": "downloading",
        "downloaded_bytes": 5_000_000,
        "total_bytes": 10_000_000,
        "speed": 200_000,
        "eta": 25,
    })

    assert shared["progress"] == 50.0
    assert shared["speed"] == "195 KB/s"
    assert shared["eta"] == "00:25"
    assert len(broadcasts) == 1


def test_progress_hook_finished_marks_processing():
    shared = {"progress": 0.0, "speed": "", "eta": "", "status": ""}
    broadcasts = []

    def broadcast(_item):
        broadcasts.append(dict(shared))

    hook = _build_progress_hook(shared, broadcast)
    hook({"status": "finished"})

    assert shared["progress"] == 95.0
    assert shared["status"] == "processing"
    assert "ID3" in shared["speed"]
