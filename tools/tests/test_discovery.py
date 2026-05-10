import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from tools.pipeline.download.discovery import iter_sermons, TIM_KELLER_SPEAKER_ID

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr("pipeline.download.discovery.time.sleep", lambda _s: None)


def _fake_response(body_path: str, total_pages: int = 1):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = json.loads((FIXTURES / body_path).read_text())
    resp.headers = {"X-WP-TotalPages": str(total_pages)}
    resp.raise_for_status = MagicMock()
    return resp


def test_iter_sermons_yields_stubs_from_single_page():
    client = MagicMock()
    client.get.return_value = _fake_response("discovery_page1.json", total_pages=1)

    stubs = list(iter_sermons(client))

    assert len(stubs) == 2
    assert stubs[0]["id"] == 1001
    assert stubs[0]["slug"] == "peace"
    assert stubs[0]["link"] == "https://gospelinlife.com/sermon/peace/"
    assert stubs[0]["title"] == "Peace – Overcoming Anxiety"
    assert stubs[0]["date"] == "1990-02-18T00:00:00"


def test_iter_sermons_queries_tim_keller_speaker():
    client = MagicMock()
    client.get.return_value = _fake_response("discovery_page1.json", total_pages=1)

    list(iter_sermons(client))

    call_args = client.get.call_args
    assert call_args is not None
    url_or_params = str(call_args)
    assert str(TIM_KELLER_SPEAKER_ID) in url_or_params
    assert "sermon" in url_or_params
    assert "date" in url_or_params


def test_iter_sermons_paginates_until_total_pages_exhausted():
    client = MagicMock()
    client.get.side_effect = [
        _fake_response("discovery_page1.json", total_pages=2),
        _fake_response("discovery_page1.json", total_pages=2),
    ]

    stubs = list(iter_sermons(client))

    assert len(stubs) == 4
    assert client.get.call_count == 2


def test_iter_sermons_stops_on_empty_page():
    empty_resp = MagicMock()
    empty_resp.status_code = 200
    empty_resp.json.return_value = []
    empty_resp.headers = {"X-WP-TotalPages": "99"}
    empty_resp.raise_for_status = MagicMock()

    client = MagicMock()
    client.get.side_effect = [
        _fake_response("discovery_page1.json", total_pages=99),
        empty_resp,
    ]

    stubs = list(iter_sermons(client))
    assert len(stubs) == 2  # just the first page
