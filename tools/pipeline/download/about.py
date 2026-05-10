from typing import Any

EM_DASH = "—"


def _fmt(value: Any) -> str:
    if value is None or value == "" or value == []:
        return EM_DASH
    if isinstance(value, list):
        return ", ".join(value)
    return str(value)


def render_about_md(metadata: dict[str, Any]) -> str:
    """Render sermon metadata to the about.md markdown format."""
    rows = [
        ("Sermon Name", metadata["title"]),
        ("Speaker", metadata["speaker"]),
        ("Date", metadata["date"]),
        ("Downloaded From", metadata["source_url"]),
        ("Series", metadata.get("series")),
        ("Topics", metadata.get("topics", [])),
        ("Duration", metadata.get("duration")),
        ("Scripture", metadata.get("scripture")),
        ("SKU", metadata.get("sku")),
    ]

    lines = ["# Metadata", "| Key | Value |", "|-----|-------|"]
    for key, value in rows:
        lines.append(f"| {key} | {_fmt(value)} |")

    overview = metadata.get("overview") or ""
    lines.append("")
    lines.append("# Overview")
    lines.append(overview if overview else EM_DASH)
    lines.append("")

    return "\n".join(lines)
