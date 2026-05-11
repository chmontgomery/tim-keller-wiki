import argparse
import json
import sys
from pathlib import Path

from .followup_log import load_entries

DEFAULT_DIR = Path("raw/sermons")


def _find_transcript(folder: Path, name: str) -> Path:
    """Locate the .txt transcript for an entry.

    Sermons follow `<folder>/<folder>.txt`. Teaching-course lectures have a
    `.txt` whose stem differs from the folder name. Fall back to a glob so
    both layouts work.
    """
    expected = folder / f"{name}.txt"
    if expected.exists():
        return expected
    txts = sorted(folder.glob("*.txt"))
    if txts:
        return txts[0]
    return expected


def build_manifest(root_dir: Path) -> list[dict]:
    log_path = root_dir / ".llm_followup.json"
    entries = load_entries(log_path)
    manifest = []
    for entry in entries:
        name = entry["sermon"]
        # Direct child folder is the common case; for nested layouts (e.g.
        # teaching-courses/<course>/<lecture>/) fall back to a recursive find.
        folder = root_dir / name
        if not folder.is_dir():
            matches = [p for p in root_dir.rglob(name) if p.is_dir()]
            if matches:
                folder = matches[0]
        txt_path = _find_transcript(folder, name)
        manifest.append(
            {
                "sermon": name,
                "txt_path": str(txt_path),
                "flags": entry.get("flags", []),
            }
        )
    return manifest


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        description="Emit the LLM-followup repair manifest as JSON on stdout.",
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=DEFAULT_DIR,
        help="Root directory containing .llm_followup.json (default: raw/sermons)",
    )
    args = parser.parse_args(argv)
    json.dump(build_manifest(args.dir), sys.stdout)


if __name__ == "__main__":
    main()
