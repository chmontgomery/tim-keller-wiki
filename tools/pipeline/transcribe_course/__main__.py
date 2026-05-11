"""Transcribe Tim Keller teaching-course lectures.

Mirrors `tools.pipeline.transcribe` but operates on raw/teaching-courses/
and adds an intro-stripping step that removes the TGC announcer's
introduction before Keller begins speaking.
"""
import argparse
import sys
from pathlib import Path

from tools.pipeline.transcribe.followup_log import add_entry
from tools.pipeline.transcribe.markers import process_segments
from tools.pipeline.transcribe.scanner import find_untranscribed
from tools.pipeline.transcribe.transcriber import transcribe_audio
from tools.pipeline.transcribe.verifier import regex_clean

from .intro_strip import strip_intro

COURSES_DIR = Path("raw/teaching-courses")
LOG_PATH = COURSES_DIR / ".llm_followup.json"


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Transcribe Tim Keller teaching-course lectures",
    )
    parser.add_argument(
        "--lecture",
        help="Transcribe a single lecture folder by name",
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

    if not COURSES_DIR.exists():
        print(f"Error: {COURSES_DIR} not found. Run from the project root.")
        sys.exit(1)

    mp3s = find_untranscribed(
        COURSES_DIR,
        force=args.force,
        sermon_filter=args.lecture,
    )

    if not mp3s:
        print("No lectures to transcribe.")
        return

    print(f"Found {len(mp3s)} lecture(s) to transcribe.")

    transcribed = 0
    failed = 0

    for mp3_path in mp3s:
        name = mp3_path.parent.name
        print(f"\nTranscribing: {name}...")

        try:
            segments = transcribe_audio(mp3_path)
            raw_text = process_segments(segments)
            cleaned_text, flags = regex_clean(raw_text)
            stripped_text, intro_found = strip_intro(cleaned_text)

            if not intro_found:
                flags = flags + [{"reason": "intro_not_stripped"}]

            txt_path = mp3_path.with_suffix(".txt")
            txt_path.write_text(stripped_text)
            add_entry(LOG_PATH, name, flags)

            print(f"  Done: {txt_path.name}")
            if args.verbose:
                print(f"  Segments: {len(segments)}")
                print(f"  Intro stripped: {intro_found}")
                if flags:
                    print(f"  Flags: {len(flags)}")
            elif not intro_found:
                print("  Warning: announcer hand-off not found; intro left intact")
            transcribed += 1
        except Exception as e:
            print(f"  Error: {e}")
            failed += 1

    skipped_msg = ""
    if args.lecture is None and not args.force:
        total_mp3s = len(list(COURSES_DIR.rglob("*.mp3")))
        skipped = total_mp3s - len(mp3s)
        if skipped > 0:
            skipped_msg = f", skipped {skipped}"

    print(f"\nSummary: Transcribed {transcribed}, failed {failed}{skipped_msg}")


if __name__ == "__main__":
    main()
