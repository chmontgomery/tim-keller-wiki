import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MANIFEST_VERSION = 1


class ManifestError(Exception):
    """Raised when the manifest cannot be loaded or is corrupt."""


@dataclass
class Manifest:
    version: int = MANIFEST_VERSION
    updated_at: str = ""
    sermons: dict[str, dict[str, Any]] = field(default_factory=dict)


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_manifest(path: Path) -> Manifest:
    """Load the manifest from disk. Returns an empty Manifest if missing."""
    if not path.exists():
        return Manifest(updated_at=_utcnow_iso())
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise ManifestError(f"Manifest is corrupt JSON at {path}: {e}") from e

    if not isinstance(data, dict) or data.get("version") != MANIFEST_VERSION:
        raise ManifestError(
            f"Manifest version mismatch at {path}: "
            f"expected {MANIFEST_VERSION}, got {data.get('version')!r}"
        )
    return Manifest(
        version=data["version"],
        updated_at=data.get("updated_at", ""),
        sermons=data.get("sermons", {}),
    )


def save_manifest(path: Path, manifest: Manifest) -> None:
    """Atomically write the manifest to disk via temp file + rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    now = _utcnow_iso()
    payload = {
        "version": manifest.version,
        "updated_at": now,
        "sermons": manifest.sermons,
    }
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True))
        os.replace(tmp, path)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise
    manifest.updated_at = now


def upsert_stub(manifest: Manifest, stub: dict[str, Any]) -> None:
    """Add a newly discovered sermon stub as 'pending' if not already present."""
    slug = stub["slug"]
    if slug in manifest.sermons:
        return
    manifest.sermons[slug] = {
        "wp_id": stub["id"],
        "slug": slug,
        "source_url": stub["link"],
        "folder": None,
        "status": "pending",
        "attempts": 0,
        "first_seen_at": _utcnow_iso(),
        "downloaded_at": None,
        "last_error": None,
    }


def update_status(
    manifest: Manifest,
    slug: str,
    status: str,
    **fields: Any,
) -> None:
    """Update one sermon's status and optional fields."""
    entry = manifest.sermons[slug]
    entry["status"] = status
    for key, value in fields.items():
        entry[key] = value
    if status == "downloaded":
        entry["downloaded_at"] = _utcnow_iso()


def select_pending(manifest: Manifest, limit: int) -> list[dict[str, Any]]:
    """Return up to `limit` pending sermon entries in insertion order.

    `limit=0` means no limit.
    """
    pending = [e for e in manifest.sermons.values() if e["status"] == "pending"]
    if limit == 0:
        return pending
    return pending[:limit]


def reset_failed_to_pending(manifest: Manifest) -> None:
    """Reset all failed entries back to pending for retry."""
    for entry in manifest.sermons.values():
        if entry["status"] == "failed":
            entry["status"] = "pending"
            entry["last_error"] = None
