from unittest.mock import MagicMock

import httpx
import pytest

from tools.pipeline.download.http_retry import (
    BASE_BACKOFF_SECONDS,
    MAX_ATTEMPTS,
    retrying_get,
)


def _resp(status: int = 200) -> MagicMock:
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status
    return resp


def test_returns_first_response_on_success():
    client = MagicMock()
    client.get.return_value = _resp(200)
    sleeps: list[float] = []

    result = retrying_get(client, "https://example.com", sleep=sleeps.append)

    assert result.status_code == 200
    assert client.get.call_count == 1
    assert sleeps == []


def test_retries_on_transport_error_then_succeeds():
    client = MagicMock()
    client.get.side_effect = [
        httpx.ConnectError("boom"),
        _resp(200),
    ]
    sleeps: list[float] = []

    result = retrying_get(client, "https://example.com", sleep=sleeps.append)

    assert result.status_code == 200
    assert client.get.call_count == 2
    assert sleeps == [BASE_BACKOFF_SECONDS]


def test_gives_up_after_max_attempts_on_transport_error():
    client = MagicMock()
    client.get.side_effect = httpx.ConnectError("persistent failure")
    sleeps: list[float] = []

    with pytest.raises(httpx.ConnectError):
        retrying_get(client, "https://example.com", sleep=sleeps.append)

    assert client.get.call_count == MAX_ATTEMPTS
    # Sleeps between attempts: 1s, 2s — no sleep after the final failure
    assert sleeps == [BASE_BACKOFF_SECONDS, BASE_BACKOFF_SECONDS * 2]


def test_retries_retryable_http_status_then_succeeds():
    client = MagicMock()
    client.get.side_effect = [
        _resp(503),
        _resp(200),
    ]
    sleeps: list[float] = []

    result = retrying_get(client, "https://example.com", sleep=sleeps.append)

    assert result.status_code == 200
    assert client.get.call_count == 2
    assert sleeps == [BASE_BACKOFF_SECONDS]


def test_retries_429_with_exponential_backoff():
    client = MagicMock()
    client.get.side_effect = [_resp(429), _resp(429), _resp(200)]
    sleeps: list[float] = []

    result = retrying_get(client, "https://example.com", sleep=sleeps.append)

    assert result.status_code == 200
    assert sleeps == [BASE_BACKOFF_SECONDS, BASE_BACKOFF_SECONDS * 2]


def test_returns_final_response_when_all_attempts_return_retryable_status():
    client = MagicMock()
    client.get.return_value = _resp(503)
    sleeps: list[float] = []

    result = retrying_get(client, "https://example.com", sleep=sleeps.append)

    # After MAX_ATTEMPTS retryable statuses, return the last response so the
    # caller can raise_for_status() or inspect it — don't silently swallow.
    assert result.status_code == 503
    assert client.get.call_count == MAX_ATTEMPTS
    assert sleeps == [BASE_BACKOFF_SECONDS, BASE_BACKOFF_SECONDS * 2]


def test_non_retryable_status_returns_immediately():
    client = MagicMock()
    client.get.return_value = _resp(404)
    sleeps: list[float] = []

    result = retrying_get(client, "https://example.com", sleep=sleeps.append)

    assert result.status_code == 404
    assert client.get.call_count == 1
    assert sleeps == []


def test_passes_params_through():
    client = MagicMock()
    client.get.return_value = _resp(200)

    retrying_get(client, "https://example.com", params={"page": 3})

    client.get.assert_called_once_with("https://example.com", params={"page": 3})
