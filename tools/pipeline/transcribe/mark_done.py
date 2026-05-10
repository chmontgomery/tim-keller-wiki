import argparse
from pathlib import Path
from typing import Optional

from .followup_log import remove_entry

LOG_PATH = Path("raw/sermons/.llm_followup.json")


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description="Remove a sermon entry from the LLM followup log."
    )
    parser.add_argument("sermon", help="Sermon folder name to remove from the log")
    args = parser.parse_args(argv)
    remove_entry(LOG_PATH, args.sermon)


if __name__ == "__main__":
    main()
