"""Opt-in smoke tests that hit gospelinlife.com.

Run with: pytest tests/test_download_live.py -m network
"""
import httpx
import pytest

from tools.pipeline.download.discovery import iter_sermons, BASE_URL, TIM_KELLER_SPEAKER_ID
from tools.pipeline.download.parser import parse_sermon_page


pytestmark = pytest.mark.network


USER_AGENT = "tim-keller-bot/0.1 (smoke-test)"


def test_wp_rest_api_returns_tim_keller_sermons():
    """Confirm speaker ID 23 still resolves to Tim Keller sermons."""
    with httpx.Client(
        headers={"User-Agent": USER_AGENT},
        timeout=30.0,
        follow_redirects=True,
    ) as client:
        resp = client.get(
            BASE_URL,
            params={
                "speaker": TIM_KELLER_SPEAKER_ID,
                "per_page": 1,
                "page": 1,
            },
        )
        resp.raise_for_status()
        items = resp.json()
        assert len(items) == 1
        assert items[0]["type"] == "sermon"


def test_parser_works_against_live_sermon_page():
    """Catch theme drift — parse one live page."""
    url = "https://gospelinlife.com/sermon/peace/"
    with httpx.Client(
        headers={"User-Agent": USER_AGENT},
        timeout=30.0,
        follow_redirects=True,
    ) as client:
        resp = client.get(url)
        resp.raise_for_status()
        meta = parse_sermon_page(resp.text, url)

    assert "Peace" in meta["title"]
    assert meta["speaker"] == "Tim Keller"
    assert meta["mp3_url"].endswith(".mp3")
    # Overview extraction regression guard: the Peace sermon has a real
    # overview block and must never leak the newsletter-popup text that
    # the loose pre-fix selector used to grab.
    assert meta["overview"], "expected non-empty overview for peace sermon"
    assert "subscribing" not in meta["overview"].lower()
    assert "peace" in meta["overview"].lower()


def test_iter_sermons_first_page_live():
    """Discovery yields at least 10 stubs."""
    with httpx.Client(
        headers={"User-Agent": USER_AGENT},
        timeout=30.0,
        follow_redirects=True,
    ) as client:
        stubs = []
        for stub in iter_sermons(client):
            stubs.append(stub)
            if len(stubs) >= 10:
                break

    assert len(stubs) >= 10
    assert all("slug" in s and "link" in s for s in stubs)
