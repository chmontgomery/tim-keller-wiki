import json
import os
import subprocess
import sys
from pathlib import Path

from tools.pipeline.transcribe.followup_log import add_entry, load_entries

REPO_ROOT = Path(__file__).parent.parent


def _run(cwd: Path, sermon: str) -> subprocess.CompletedProcess:
    """Run mark_done CLI from cwd with PYTHONPATH set to repo root."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    return subprocess.run(
        [sys.executable, "-m", "pipeline.transcribe.mark_done", sermon],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )


def test_removes_named_entry(tmp_path):
    sermons = tmp_path / "raw" / "sermons"
    sermons.mkdir(parents=True)
    log = sermons / ".llm_followup.json"
    add_entry(log, "Anxiety", [])
    add_entry(log, "Born_Again1", [])

    _run(tmp_path, "Anxiety")

    remaining = load_entries(log)
    assert [e["sermon"] for e in remaining] == ["Born_Again1"]


def test_missing_entry_is_noop(tmp_path):
    sermons = tmp_path / "raw" / "sermons"
    sermons.mkdir(parents=True)
    log = sermons / ".llm_followup.json"
    add_entry(log, "Anxiety", [])

    _run(tmp_path, "Ghost")

    remaining = load_entries(log)
    assert [e["sermon"] for e in remaining] == ["Anxiety"]


def test_missing_log_is_noop(tmp_path):
    sermons = tmp_path / "raw" / "sermons"
    sermons.mkdir(parents=True)
    _run(tmp_path, "Whatever")
    assert not (sermons / ".llm_followup.json").exists()
