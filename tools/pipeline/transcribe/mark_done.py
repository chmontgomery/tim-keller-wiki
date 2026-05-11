import argparse
from pathlib import Path
from typing import Optional

from .followup_log import remove_entry

DEFAULT_DIR = Path("raw/sermons")


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description="Remove a sermon entry from the LLM followup log."
    )
    parser.add_argument("sermon", help="Sermon folder name to remove from the log")
    parser.add_argument(
        "--dir",
        type=Path,
        default=DEFAULT_DIR,
        help="Root directory containing .llm_followup.json (default: raw/sermons)",
    )
    args = parser.parse_args(argv)
    log_path = args.dir / ".llm_followup.json"
    remove_entry(log_path, args.sermon)


if __name__ == "__main__":
    main()
