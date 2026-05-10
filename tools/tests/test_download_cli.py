import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from tools.pipeline.download.__main__ import parse_args, main


def test_parse_args_defaults():
    args = parse_args([])
    assert args.limit == 5
    assert args.retry_failed is False
    assert args.dry_run is False
    assert args.verbose is False


def test_parse_args_all_flags():
    args = parse_args(["--limit", "100", "--retry-failed", "--dry-run", "--verbose"])
    assert args.limit == 100
    assert args.retry_failed is True
    assert args.dry_run is True
    assert args.verbose is True


@pytest.fixture
def no_sleep(monkeypatch):
    monkeypatch.setattr("pipeline.download.__main__.time.sleep", lambda _s: None)


@pytest.fixture
def fake_stub():
    return {
        "id": 1001,
        "slug": "peace",
        "link": "https://gospelinlife.com/sermon/peace/",
        "title": "Peace",
        "date": "1990-02-18T00:00:00",
    }


@pytest.fixture
def fake_metadata():
    return {
        "title": "Peace",
        "speaker": "Tim Keller",
        "date": "Feb 18, 1990",
        "series": None,
        "topics": [],
        "duration": None,
        "scripture": None,
        "sku": None,
        "overview": "About peace.",
        "mp3_url": "https://s3.amazonaws.com/rpc-sermons/Peace_X.mp3",
        "source_url": "https://gospelinlife.com/sermon/peace/",
    }


def test_main_downloads_one_sermon_happy_path(
    tmp_path, no_sleep, fake_stub, fake_metadata, capsys
):
    sermons_dir = tmp_path / "raw" / "sermons"
    sermons_dir.mkdir(parents=True)

    with patch("pipeline.download.__main__.SERMONS_DIR", sermons_dir), \
         patch("pipeline.download.__main__.iter_sermons", return_value=iter([fake_stub])), \
         patch("pipeline.download.__main__._fetch_sermon_html", return_value="<html></html>"), \
         patch("pipeline.download.__main__.parse_sermon_page", return_value=fake_metadata), \
         patch("pipeline.download.__main__.download_sermon") as mock_dl, \
         patch("pipeline.download.__main__.httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value = MagicMock()

        def fake_download(client, meta, sermons_dir):
            folder = sermons_dir / "Peace_X"
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "Peace_X.mp3").write_bytes(b"audio")
            return folder
        mock_dl.side_effect = fake_download

        main(["--limit", "1"])

    manifest = json.loads((sermons_dir / "manifest.json").read_text())
    assert manifest["sermons"]["peace"]["status"] == "downloaded"
    assert manifest["sermons"]["peace"]["folder"] == "Peace_X"

    about = sermons_dir / "Peace_X" / "about.md"
    assert about.exists()
    assert "Tim Keller" in about.read_text()

    out = capsys.readouterr().out
    assert "downloaded 1" in out.lower() or "downloaded: 1" in out.lower()


def test_main_marks_failed_on_parse_error(
    tmp_path, no_sleep, fake_stub, capsys
):
    from tools.pipeline.download.parser import ParseError

    sermons_dir = tmp_path / "raw" / "sermons"
    sermons_dir.mkdir(parents=True)

    with patch("pipeline.download.__main__.SERMONS_DIR", sermons_dir), \
         patch("pipeline.download.__main__.iter_sermons", return_value=iter([fake_stub])), \
         patch("pipeline.download.__main__._fetch_sermon_html", return_value="<html></html>"), \
         patch(
            "pipeline.download.__main__.parse_sermon_page",
            side_effect=ParseError("no mp3"),
         ), \
         patch("pipeline.download.__main__.httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value = MagicMock()
        main(["--limit", "1"])

    manifest = json.loads((sermons_dir / "manifest.json").read_text())
    assert manifest["sermons"]["peace"]["status"] == "failed"
    assert "no mp3" in manifest["sermons"]["peace"]["last_error"]

    debug = sermons_dir / ".debug" / "peace.html"
    assert debug.exists()


def test_main_dry_run_does_not_download(
    tmp_path, no_sleep, fake_stub
):
    sermons_dir = tmp_path / "raw" / "sermons"
    sermons_dir.mkdir(parents=True)

    with patch("pipeline.download.__main__.SERMONS_DIR", sermons_dir), \
         patch("pipeline.download.__main__.iter_sermons", return_value=iter([fake_stub])), \
         patch("pipeline.download.__main__.download_sermon") as mock_dl, \
         patch("pipeline.download.__main__._fetch_sermon_html") as mock_fetch, \
         patch("pipeline.download.__main__.httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value = MagicMock()
        main(["--dry-run", "--limit", "1"])

    mock_dl.assert_not_called()
    mock_fetch.assert_not_called()
    manifest = json.loads((sermons_dir / "manifest.json").read_text())
    assert manifest["sermons"]["peace"]["status"] == "pending"


def test_main_exits_when_nothing_pending(tmp_path, no_sleep, capsys):
    sermons_dir = tmp_path / "raw" / "sermons"
    sermons_dir.mkdir(parents=True)

    with patch("pipeline.download.__main__.SERMONS_DIR", sermons_dir), \
         patch("pipeline.download.__main__.iter_sermons", return_value=iter([])), \
         patch("pipeline.download.__main__.httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value = MagicMock()
        main([])

    out = capsys.readouterr().out
    assert "nothing to do" in out.lower() or "no sermons" in out.lower()
