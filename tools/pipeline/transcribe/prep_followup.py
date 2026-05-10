import json
import sys
from pathlib import Path

from .followup_log import load_entries

SERMONS_DIR = Path("raw/sermons")
LOG_PATH = SERMONS_DIR / ".llm_followup.json"


def build_manifest(sermons_dir: Path) -> list[dict]:
    log_path = sermons_dir / ".llm_followup.json"
    entries = load_entries(log_path)
    manifest = []
    for entry in entries:
        sermon = entry["sermon"]
        txt_path = sermons_dir / sermon / f"{sermon}.txt"
        manifest.append(
            {
                "sermon": sermon,
                "txt_path": str(txt_path),
                "flags": entry.get("flags", []),
            }
        )
    return manifest


def main() -> None:
    json.dump(build_manifest(SERMONS_DIR), sys.stdout)


if __name__ == "__main__":
    main()
