from pathlib import Path

import pytest

from tools.pipeline.download.parser import parse_sermon_page, ParseError

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> str:
    return (FIXTURES / name).read_text()


def test_parses_peace_sermon_required_fields():
    html = _load("sermon_peace.html")
    meta = parse_sermon_page(html, "https://gospelinlife.com/sermon/peace/")

    assert "Peace" in meta["title"]
    assert meta["speaker"] == "Tim Keller"
    assert meta["mp3_url"].startswith("https://s3.amazonaws.com/")
    assert meta["mp3_url"].endswith(".mp3")
    assert meta["source_url"] == "https://gospelinlife.com/sermon/peace/"


def test_parses_peace_sermon_optional_fields():
    html = _load("sermon_peace.html")
    meta = parse_sermon_page(html, "https://gospelinlife.com/sermon/peace/")

    assert meta["date"]  # non-empty string
    assert "1990" in meta["date"]
    assert meta["scripture"] is not None
    assert "Philippians" in meta["scripture"]
    assert meta["sku"] is not None
    assert "RS" in meta["sku"]
    assert meta["duration"] is not None
    assert meta["overview"]  # non-empty


def test_parses_aspiration_sermon():
    html = _load("sermon_aspiration.html")
    meta = parse_sermon_page(
        html,
        "https://gospelinlife.com/sermon/aspiration-lead-us/",
    )
    assert "Aspiration" in meta["title"] or "Lead Us" in meta["title"]
    assert meta["speaker"] == "Tim Keller"
    assert meta["mp3_url"].endswith(".mp3")


def test_parses_leader_talks_has_empty_overview():
    """Leader Talks Q&A pages have no overview block. We must not fall back
    to a stray paragraph (e.g. a newsletter popup) just to produce something."""
    html = _load("sermon_leader_talks_no_overview.html")
    meta = parse_sermon_page(
        html,
        "https://gospelinlife.com/sermon/1-corinthians-12-1-47-2/",
    )
    assert meta["overview"] == ""
    # Sanity: the popup text that previously leaked through must not appear.
    assert "subscribing" not in meta["overview"].lower()


def test_peace_overview_contains_real_sermon_text():
    html = _load("sermon_peace.html")
    meta = parse_sermon_page(html, "https://gospelinlife.com/sermon/peace/")
    assert "peace and joy" in meta["overview"]
    assert "subscribing" not in meta["overview"].lower()


def test_missing_mp3_raises_parse_error():
    html = "<html><body><p>nothing here</p></body></html>"
    with pytest.raises(ParseError):
        parse_sermon_page(html, "https://example.com/x")


def test_metadata_has_all_keys():
    html = _load("sermon_peace.html")
    meta = parse_sermon_page(html, "https://gospelinlife.com/sermon/peace/")
    expected_keys = {
        "title", "speaker", "date", "series", "topics",
        "duration", "scripture", "sku", "overview",
        "mp3_url", "source_url",
    }
    assert expected_keys == set(meta.keys())
