import argparse
import sys
from pathlib import Path

from .followup_log import add_entry
from .markers import process_segments
from .scanner import find_untranscribed
from .transcriber import transcribe_audio
from .verifier import regex_clean

SERMONS_DIR = Path("raw/sermons")
LOG_PATH = SERMONS_DIR / ".llm_followup.json"


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Transcribe Tim Keller sermon audio files",
    )
    parser.add_argument(
        "--sermon",
        help="Transcribe a single sermon folder by name",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-transcribe even if transcript already exists",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed progress and segment detection info",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    if not SERMONS_DIR.exists():
        print(f"Error: {SERMONS_DIR} not found. Run from the project root.")
        sys.exit(1)

    mp3s = find_untranscribed(
        SERMONS_DIR,
        force=args.force,
        sermon_filter=args.sermon,
    )

    if not mp3s:
        print("No sermons to transcribe.")
        return

    print(f"Found {len(mp3s)} sermon(s) to transcribe.")

    transcribed = 0
    failed = 0

    for mp3_path in mp3s:
        name = mp3_path.parent.name
        print(f"\nTranscribing: {name}...")

        try:
            segments = transcribe_audio(mp3_path)
            raw_text = process_segments(segments)

            cleaned_text, flags = regex_clean(raw_text)

            txt_path = mp3_path.with_suffix(".txt")
            txt_path.write_text(cleaned_text)
            add_entry(LOG_PATH, name, flags)

            print(f"  Done: {txt_path.name}")
            if args.verbose:
                print(f"  Segments: {len(segments)}")
                if flags:
                    print(f"  Non-Latin flags: {len(flags)}")
            transcribed += 1
        except Exception as e:
            print(f"  Error: {e}")
            failed += 1

    skipped_msg = ""
    if args.sermon is None and not args.force:
        total_mp3s = len(list(SERMONS_DIR.rglob("*.mp3")))
        skipped = total_mp3s - len(mp3s)
        if skipped > 0:
            skipped_msg = f", skipped {skipped}"

    print(f"\nSummary: Transcribed {transcribed}, failed {failed}{skipped_msg}")


if __name__ == "__main__":
    main()
