import re
from typing import Any, Optional

from selectolax.parser import HTMLParser


class ParseError(Exception):
    """Raised when required fields cannot be extracted from a sermon page."""


MP3_URL_PATTERN = re.compile(
    r"https://s3\.amazonaws\.com/rpc-sermons/[^\s\"'<>]+\.mp3",
    re.IGNORECASE,
)


def _text_or_none(node) -> Optional[str]:
    if node is None:
        return None
    text = node.text(strip=True)
    return text or None


def _find_mp3_url(html: str) -> Optional[str]:
    """Find the mp3 URL anywhere in the raw HTML (href, src, or script)."""
    match = MP3_URL_PATTERN.search(html)
    return match.group(0) if match else None


def _extract_title(tree: HTMLParser) -> Optional[str]:
    h1 = tree.css_first("h1")
    if h1 is not None:
        text = h1.text(strip=True)
        if text:
            return text
    title = tree.css_first("title")
    if title is not None:
        text = title.text(strip=True)
        return re.sub(r"\s*[-–|]\s*Gospel in Life.*$", "", text) or None
    return None


def _extract_meta_field(tree: HTMLParser, label: str) -> Optional[str]:
    """Extract a value from a div.gil-sermon-meta block whose text starts with label."""
    for div in tree.css("div.gil-sermon-meta"):
        text = div.text(strip=True)
        if text.lower().startswith(label.lower() + ":") or text.lower().startswith(label.lower() + "\n"):
            # The value is in .gil-sermon-meta-value span
            value_node = div.css_first("span.gil-sermon-meta-value")
            if value_node is not None:
                return value_node.text(strip=True) or None
            # Or in the series case, it's in a link
            a = div.css_first("a")
            if a is not None:
                return a.text(strip=True) or None
    return None


def _extract_series(tree: HTMLParser) -> Optional[str]:
    """Extract series from div.gil-sermon-meta that starts with 'Series:'."""
    for div in tree.css("div.gil-sermon-meta"):
        raw = div.text(strip=True)
        if raw.lower().startswith("series:"):
            a = div.css_first("a")
            if a is not None:
                return a.text(strip=True) or None
            # Fallback: strip the label
            remainder = raw[len("Series:"):].strip()
            return remainder or None
    return None


def _extract_speaker_and_date(tree: HTMLParser) -> tuple[Optional[str], str]:
    """Extract speaker and date from the paragraph like 'Tim Keller | February 18, 1990'."""
    for p in tree.css("p"):
        html_str = p.html or ""
        # Look for the paragraph that contains a taxonomy-23 span (speaker)
        if 'taxonomy-23' in html_str:
            text = p.text(strip=True)
            # text is like "Tim Keller|\xa0 February 18, 1990"
            parts = text.split("|", 1)
            speaker = parts[0].strip() or None
            date = parts[1].strip().strip("\xa0").strip() if len(parts) > 1 else ""
            return speaker, date
    return None, ""


def _extract_topics(tree: HTMLParser) -> list[str]:
    """Extract topics from the Topics gil-sermon-meta block."""
    for div in tree.css("div.gil-sermon-meta"):
        text = div.text(strip=True)
        if text.lower().startswith("topics:") or text.lower().startswith("topics\n"):
            value_node = div.css_first("span.gil-sermon-meta-value")
            if value_node is not None:
                items = [li.text(strip=True) for li in value_node.css("li")]
                return [t for t in items if t]
    return []


def _extract_overview(tree: HTMLParser) -> str:
    """Extract the sermon overview from the page.

    The overview lives in a `div.fl-rich-text` module whose first heading is
    "Overview", followed by one or more `<p>` tags. Not every sermon has one
    (e.g. Leader Talks Q&A sermons); when absent, returns an empty string.
    """
    for module in tree.css("div.fl-rich-text"):
        heading = module.css_first("h1, h2, h3, h4")
        if heading is None:
            continue
        if heading.text(strip=True).lower() != "overview":
            continue
        paragraphs = [
            p.text(strip=True) for p in module.css("p") if p.text(strip=True)
        ]
        return "\n\n".join(paragraphs)
    return ""


def parse_sermon_page(html: str, source_url: str) -> dict[str, Any]:
    """Parse a sermon detail HTML page into a SermonMetadata dict.

    Required fields: title, mp3_url. Missing either raises ParseError.
    """
    tree = HTMLParser(html)

    title = _extract_title(tree)
    mp3_url = _find_mp3_url(html)

    if not title:
        raise ParseError(f"Could not extract title from {source_url}")
    if not mp3_url:
        raise ParseError(f"Could not find mp3 URL on {source_url}")

    speaker, date = _extract_speaker_and_date(tree)

    return {
        "title": title,
        "speaker": speaker or "Tim Keller",
        "date": date,
        "series": _extract_series(tree),
        "topics": _extract_topics(tree),
        "duration": _extract_meta_field(tree, "Duration"),
        "scripture": _extract_meta_field(tree, "Scripture"),
        "sku": _extract_meta_field(tree, "SKU"),
        "overview": _extract_overview(tree),
        "mp3_url": mp3_url,
        "source_url": source_url,
    }
