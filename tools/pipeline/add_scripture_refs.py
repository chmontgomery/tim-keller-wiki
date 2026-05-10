"""
Scan sermon transcripts and populate/augment the Scripture field in about.md.
"""
import argparse
import re
import sys
from pathlib import Path

import pythonbible

SERMONS_DIR = Path(__file__).parent.parent / "raw" / "sermons"
SCRIPTURE_ROW_RE = re.compile(r"(\| Scripture \| )(.*?)( \|)", re.IGNORECASE)


def _ref_key(ref):
    return (ref.book, ref.start_chapter, ref.start_verse, ref.end_chapter, ref.end_verse)


def classify_reference(ref):
    book = ref.book
    num_chapters = pythonbible.get_number_of_chapters(book)
    last_chapter_verses = pythonbible.get_number_of_verses(book, num_chapters)
    if (
        ref.start_chapter == 1
        and ref.start_verse == 1
        and ref.end_chapter == num_chapters
        and ref.end_verse == last_chapter_verses
    ):
        return "whole_book"
    if ref.start_chapter == ref.end_chapter and ref.start_verse == 1:
        chapter_verses = pythonbible.get_number_of_verses(book, ref.start_chapter)
        if ref.end_verse == chapter_verses:
            return "whole_chapter"
    return "verse_ref"


def format_reference(ref):
    kind = classify_reference(ref)
    if kind == "whole_book":
        return None
    if kind == "whole_chapter":
        book_name = ref.book.title.replace("_", " ")
        return f"{book_name} {ref.start_chapter}"
    return pythonbible.format_scripture_references([ref])


def extract_references(text):
    """Return deduplicated list of (NormalizedReference, formatted_str) pairs."""
    seen_keys = set()
    results = []
    try:
        raw_refs = pythonbible.get_references(text)
    except Exception:
        return results
    for ref in raw_refs:
        key = _ref_key(ref)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        formatted = format_reference(ref)
        if formatted:
            results.append((ref, formatted))
    return results


def process_sermon(sermon_dir: Path, dry_run: bool) -> bool:
    txt_files = list(sermon_dir.glob("*.txt"))
    if not txt_files:
        print(f"WARNING: no transcript in {sermon_dir.name}", file=sys.stderr)
        return False

    transcript = txt_files[0].read_text(encoding="utf-8", errors="replace")
    transcript_refs = extract_references(transcript)
    if not transcript_refs:
        return False

    about_path = sermon_dir / "about.md"
    if not about_path.exists():
        print(f"WARNING: no about.md in {sermon_dir.name}", file=sys.stderr)
        return False

    content = about_path.read_text(encoding="utf-8")
    match = SCRIPTURE_ROW_RE.search(content)
    if not match:
        print(f"WARNING: no Scripture row in {sermon_dir.name}", file=sys.stderr)
        return False

    existing_raw = match.group(2).strip()

    if existing_raw == "—":
        new_value = ", ".join(fmt for _, fmt in transcript_refs)
    else:
        # Parse each segment of the existing value individually for accurate dedup
        # (pythonbible misparses comma-separated chapter refs as ranges)
        existing_keys = set()
        for segment in re.split(r"[;,]", existing_raw):
            segment = segment.strip()
            if segment:
                for r in pythonbible.get_references(segment):
                    existing_keys.add(_ref_key(r))
        seen_keys = set(existing_keys)
        to_append = []
        for ref, formatted in transcript_refs:
            key = _ref_key(ref)
            if key not in seen_keys:
                seen_keys.add(key)
                to_append.append(formatted)
        if not to_append:
            return False
        new_value = existing_raw + ", " + ", ".join(to_append)

    new_content = SCRIPTURE_ROW_RE.sub(
        lambda m: f"{m.group(1)}{new_value}{m.group(3)}", content
    )

    if dry_run:
        print(f"--- {sermon_dir.name}")
        print(f"  before: {existing_raw}")
        print(f"  after:  {new_value}")
        return True

    about_path.write_text(new_content, encoding="utf-8")
    return True


def main():
    parser = argparse.ArgumentParser(description="Populate Scripture refs in about.md files.")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing")
    parser.add_argument("--sermon", metavar="NAME", help="Process one sermon directory by name")
    args = parser.parse_args()

    if args.sermon:
        sermon_dir = SERMONS_DIR / args.sermon
        if not sermon_dir.is_dir():
            print(f"ERROR: {sermon_dir} not found", file=sys.stderr)
            sys.exit(1)
        dirs = [sermon_dir]
    else:
        dirs = sorted(d for d in SERMONS_DIR.iterdir() if d.is_dir())

    updated = 0
    for d in dirs:
        if process_sermon(d, dry_run=args.dry_run):
            updated += 1

    action = "Would update" if args.dry_run else "Updated"
    print(f"{action} {updated} sermon(s).")


if __name__ == "__main__":
    main()
