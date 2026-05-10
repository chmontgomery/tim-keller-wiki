import time
from typing import Any, Iterator

from .http_retry import retrying_get

BASE_URL = "https://gospelinlife.com/wp-json/wp/v2/sermon"
TIM_KELLER_SPEAKER_ID = 23
PAGE_SIZE = 100
PAGE_DELAY_SECONDS = 1.0


def iter_sermons(http_client) -> Iterator[dict[str, Any]]:
    """Yield SermonStub dicts for every Tim Keller sermon, date descending.

    Walks the WP REST API with pagination. Stops when either
    X-WP-TotalPages is reached or the API returns an empty page.
    Inserts a 1 second delay between page requests.
    """
    page = 1
    while True:
        params = {
            "speaker": TIM_KELLER_SPEAKER_ID,
            "per_page": PAGE_SIZE,
            "orderby": "date",
            "order": "desc",
            "page": page,
        }
        resp = retrying_get(http_client, BASE_URL, params=params)
        resp.raise_for_status()

        items = resp.json()
        if not items:
            return

        for item in items:
            yield {
                "id": item["id"],
                "slug": item["slug"],
                "link": item["link"],
                "title": item["title"]["rendered"],
                "date": item["date"],
            }

        total_pages = int(resp.headers.get("X-WP-TotalPages", "1"))
        if page >= total_pages:
            return

        page += 1
        time.sleep(PAGE_DELAY_SECONDS)
