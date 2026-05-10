import json
from unittest.mock import patch

import pytest

from tools.pipeline.download.manifest import (
    Manifest,
    ManifestError,
    load_manifest,
    save_manifest,
    upsert_stub,
    update_status,
    select_pending,
    reset_failed_to_pending,
)


def test_load_missing_file_returns_empty(tmp_path):
    m = load_manifest(tmp_path / "manifest.json")
    assert m.version == 1
    assert m.sermons == {}


def test_save_then_load_roundtrip(tmp_path):
    path = tmp_path / "manifest.json"
    m = load_manifest(path)
    m.sermons["peace"] = {
        "wp_id": 1234,
        "slug": "peace",
        "source_url": "https://gospelinlife.com/sermon/peace/",
        "folder": "Peace_Overcoming_Anxiety",
        "status": "downloaded",
        "attempts": 1,
        "first_seen_at": "2026-04-12T14:00:02Z",
        "downloaded_at": "2026-04-12T14:00:14Z",
        "last_error": None,
    }
    save_manifest(path, m)

    loaded = load_manifest(path)
    assert loaded.sermons["peace"]["wp_id"] == 1234
    assert loaded.sermons["peace"]["status"] == "downloaded"


def test_save_is_atomic_temp_file_removed(tmp_path):
    path = tmp_path / "manifest.json"
    m = load_manifest(path)
    save_manifest(path, m)

    # Only the final file should exist, no .tmp leftover
    files = sorted(p.name for p in tmp_path.iterdir())
    assert files == ["manifest.json"]


def test_save_updates_updated_at(tmp_path):
    path = tmp_path / "manifest.json"
    m = load_manifest(path)
    save_manifest(path, m)

    data = json.loads(path.read_text())
    assert "updated_at" in data
    assert data["updated_at"].endswith("Z")


def test_load_corrupt_json_raises(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text("{not valid json")
    with pytest.raises(ManifestError):
        load_manifest(path)


def test_load_wrong_version_raises(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({"version": 999, "sermons": {}, "updated_at": "x"}))
    with pytest.raises(ManifestError):
        load_manifest(path)


def test_save_cleans_up_tmp_on_write_failure(tmp_path):
    path = tmp_path / "manifest.json"
    m = load_manifest(path)

    with patch("pipeline.download.manifest.os.replace", side_effect=OSError("boom")):
        with pytest.raises(OSError):
            save_manifest(path, m)

    # No .tmp file left behind
    leftovers = [p.name for p in tmp_path.iterdir() if p.name.endswith(".tmp")]
    assert leftovers == []


def test_upsert_stub_adds_new_pending(tmp_path):
    m = load_manifest(tmp_path / "manifest.json")
    stub = {
        "id": 1234,
        "slug": "peace",
        "link": "https://gospelinlife.com/sermon/peace/",
        "title": "Peace",
        "date": "2020-01-01T00:00:00",
    }
    upsert_stub(m, stub)

    entry = m.sermons["peace"]
    assert entry["wp_id"] == 1234
    assert entry["slug"] == "peace"
    assert entry["source_url"] == "https://gospelinlife.com/sermon/peace/"
    assert entry["status"] == "pending"
    assert entry["attempts"] == 0
    assert entry["first_seen_at"].endswith("Z")
    assert entry["last_error"] is None


def test_upsert_stub_does_not_overwrite_existing(tmp_path):
    m = load_manifest(tmp_path / "manifest.json")
    stub = {"id": 1, "slug": "peace", "link": "url", "title": "t", "date": "d"}
    upsert_stub(m, stub)
    m.sermons["peace"]["status"] = "downloaded"

    upsert_stub(m, stub)
    assert m.sermons["peace"]["status"] == "downloaded"


def test_update_status_sets_fields(tmp_path):
    m = load_manifest(tmp_path / "manifest.json")
    upsert_stub(m, {"id": 1, "slug": "peace", "link": "u", "title": "t", "date": "d"})

    update_status(m, "peace", "downloaded", folder="Peace_X", attempts=1)
    entry = m.sermons["peace"]
    assert entry["status"] == "downloaded"
    assert entry["folder"] == "Peace_X"
    assert entry["attempts"] == 1
    assert entry["downloaded_at"].endswith("Z")


def test_update_status_failed_sets_last_error(tmp_path):
    m = load_manifest(tmp_path / "manifest.json")
    upsert_stub(m, {"id": 1, "slug": "peace", "link": "u", "title": "t", "date": "d"})

    update_status(m, "peace", "failed", last_error="HTTP 500")
    assert m.sermons["peace"]["status"] == "failed"
    assert m.sermons["peace"]["last_error"] == "HTTP 500"


def test_select_pending_preserves_insertion_order(tmp_path):
    m = load_manifest(tmp_path / "manifest.json")
    for i, slug in enumerate(["a", "b", "c", "d"]):
        upsert_stub(m, {"id": i, "slug": slug, "link": "u", "title": "t", "date": "d"})
    update_status(m, "b", "downloaded")

    selected = select_pending(m, limit=2)
    assert [e["slug"] for e in selected] == ["a", "c"]


def test_select_pending_limit_zero_means_all(tmp_path):
    m = load_manifest(tmp_path / "manifest.json")
    for slug in ["a", "b", "c"]:
        upsert_stub(m, {"id": 0, "slug": slug, "link": "u", "title": "t", "date": "d"})

    selected = select_pending(m, limit=0)
    assert len(selected) == 3


def test_reset_failed_to_pending(tmp_path):
    m = load_manifest(tmp_path / "manifest.json")
    upsert_stub(m, {"id": 1, "slug": "a", "link": "u", "title": "t", "date": "d"})
    upsert_stub(m, {"id": 2, "slug": "b", "link": "u", "title": "t", "date": "d"})
    update_status(m, "a", "failed", last_error="boom")
    update_status(m, "b", "downloaded")

    reset_failed_to_pending(m)
    assert m.sermons["a"]["status"] == "pending"
    assert m.sermons["a"]["last_error"] is None
    assert m.sermons["b"]["status"] == "downloaded"
