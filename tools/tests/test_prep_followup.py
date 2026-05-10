import json
import os
import subprocess
import sys
from pathlib import Path

from tools.pipeline.transcribe.followup_log import add_entry

REPO_ROOT = Path(__file__).parent.parent


def _run(cwd: Path) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    return subprocess.run(
        [sys.executable, "-m", "pipeline.transcribe.prep_followup"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )


def test_empty_log_prints_empty_array(tmp_path, monkeypatch):
    sermons = tmp_path / "raw" / "sermons"
    sermons.mkdir(parents=True)
    result = _run(tmp_path)
    assert json.loads(result.stdout) == []


def test_missing_sermons_dir_prints_empty_array(tmp_path):
    result = _run(tmp_path)
    assert json.loads(result.stdout) == []


def test_populated_log_emits_manifest(tmp_path):
    sermons = tmp_path / "raw" / "sermons"
    sermons.mkdir(parents=True)
    log = sermons / ".llm_followup.json"
    flags = [{"line": 12, "char_start": 4, "char_end": 5, "reason": "non_latin"}]
    add_entry(log, "1990-01-01-example", flags)
    add_entry(log, "Anxiety", [])

    result = _run(tmp_path)
    manifest = json.loads(result.stdout)

    assert manifest == [
        {
            "sermon": "1990-01-01-example",
            "txt_path": "raw/sermons/1990-01-01-example/1990-01-01-example.txt",
            "flags": flags,
        },
        {
            "sermon": "Anxiety",
            "txt_path": "raw/sermons/Anxiety/Anxiety.txt",
            "flags": [],
        },
    ]
