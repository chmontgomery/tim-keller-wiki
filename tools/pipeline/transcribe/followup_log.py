import json
from pathlib import Path


def load_entries(log_path: Path) -> list[dict]:
    """Load all entries. Returns [] if log does not exist."""
    if not log_path.exists():
        return []
    return json.loads(log_path.read_text())


def add_entry(log_path: Path, sermon: str, flags: list[dict]) -> None:
    """Append or update an entry in the followup log."""
    entries = load_entries(log_path)
    for entry in entries:
        if entry["sermon"] == sermon:
            entry["flags"] = flags
            log_path.write_text(json.dumps(entries, indent=2))
            return
    entries.append({"sermon": sermon, "flags": flags})
    log_path.write_text(json.dumps(entries, indent=2))


def remove_entry(log_path: Path, sermon: str) -> None:
    """Remove a sermon entry from the followup log."""
    entries = load_entries(log_path)
    filtered = [e for e in entries if e["sermon"] != sermon]
    if len(filtered) == len(entries):
        return
    log_path.write_text(json.dumps(filtered, indent=2))
