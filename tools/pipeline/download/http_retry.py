"""Retry wrapper for HTTP GET requests used by discovery and HTML fetch.

Wraps ``httpx.Client.get`` with retries on transient network errors and
retryable HTTP statuses (429, 5xx). Uses exponential backoff (1s, 2s, 4s).
Does not retry 4xx other than 429 — those are permanent.
"""

import time
from typing import Any, Callable, Optional

import httpx

MAX_ATTEMPTS = 3
BASE_BACKOFF_SECONDS = 1.0
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


def retrying_get(
    client: httpx.Client,
    url: str,
    *,
    params: Optional[dict[str, Any]] = None,
    sleep: Callable[[float], None] = time.sleep,
) -> httpx.Response:
    """GET ``url`` with up to ``MAX_ATTEMPTS`` attempts on transient failures.

    Retryable conditions:
      * ``httpx.TransportError`` (includes ``ConnectError``, ``ReadError``,
        ``RemoteProtocolError``) and ``httpx.TimeoutException``
      * HTTP status codes in ``RETRYABLE_STATUS``

    Between attempts sleeps ``BASE_BACKOFF_SECONDS * 2**attempt``.

    On transport failure all attempts, re-raises the last exception.
    On retryable-status failure all attempts, returns the last response so
    the caller can ``raise_for_status()`` or inspect it.
    """
    last_exc: Optional[BaseException] = None
    for attempt in range(MAX_ATTEMPTS):
        is_last = attempt + 1 >= MAX_ATTEMPTS
        try:
            resp = client.get(url, params=params)
        except (httpx.TransportError, httpx.TimeoutException) as e:
            last_exc = e
            if is_last:
                raise
            sleep(BASE_BACKOFF_SECONDS * (2 ** attempt))
            continue

        if resp.status_code in RETRYABLE_STATUS and not is_last:
            sleep(BASE_BACKOFF_SECONDS * (2 ** attempt))
            continue

        return resp

    # Unreachable: loop either returns, raises, or continues.
    assert last_exc is not None
    raise last_exc
