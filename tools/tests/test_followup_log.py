import json
from pathlib import Path

import pytest

from tools.pipeline.transcribe.followup_log import add_entry, load_entries, remove_entry


def test_load_entries_missing_file(tmp_path):
    result = load_entries(tmp_path / ".llm_followup.json")
    assert result == []


def test_add_entry_creates_file(tmp_path):
    log = tmp_path / ".llm_followup.json"
    add_entry(log, "Anxiety", [])
    assert log.exists()
    data = json.loads(log.read_text())
    assert data == [{"sermon": "Anxiety", "flags": []}]


def test_add_entry_with_flags(tmp_path):
    log = tmp_path / ".llm_followup.json"
    flags = [{"line": 5, "char_start": 10, "char_end": 15, "reason": "non_latin"}]
    add_entry(log, "Born_Again1", flags)
    data = json.loads(log.read_text())
    assert data[0]["flags"] == flags


def test_add_entry_updates_existing(tmp_path):
    log = tmp_path / ".llm_followup.json"
    add_entry(log, "Anxiety", [])
    new_flags = [{"line": 3, "char_start": 0, "char_end": 5, "reason": "non_latin"}]
    add_entry(log, "Anxiety", new_flags)
    data = json.loads(log.read_text())
    assert len(data) == 1
    assert data[0]["flags"] == new_flags


def test_add_multiple_entries(tmp_path):
    log = tmp_path / ".llm_followup.json"
    add_entry(log, "Anxiety", [])
    add_entry(log, "Born_Again1", [])
    data = json.loads(log.read_text())
    assert len(data) == 2
    assert {e["sermon"] for e in data} == {"Anxiety", "Born_Again1"}


def test_remove_entry(tmp_path):
    log = tmp_path / ".llm_followup.json"
    add_entry(log, "Anxiety", [])
    add_entry(log, "Born_Again1", [])
    remove_entry(log, "Anxiety")
    data = json.loads(log.read_text())
    assert len(data) == 1
    assert data[0]["sermon"] == "Born_Again1"


def test_remove_nonexistent_entry_is_noop(tmp_path):
    log = tmp_path / ".llm_followup.json"
    add_entry(log, "Anxiety", [])
    remove_entry(log, "DoesNotExist")
    data = json.loads(log.read_text())
    assert len(data) == 1


def test_remove_entry_on_missing_file_is_noop(tmp_path):
    log = tmp_path / ".llm_followup.json"
    # Should not raise, should not create the file
    remove_entry(log, "Nonexistent")
    assert not log.exists()


def test_load_entries_round_trip(tmp_path):
    log = tmp_path / ".llm_followup.json"
    flags = [{"line": 1, "char_start": 0, "char_end": 3, "reason": "non_latin"}]
    add_entry(log, "Sermon_A", flags)
    entries = load_entries(log)
    assert entries == [{"sermon": "Sermon_A", "flags": flags}]
