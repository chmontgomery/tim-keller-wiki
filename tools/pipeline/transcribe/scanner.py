from pathlib import Path
from typing import List, Optional


def find_untranscribed(
    sermons_dir: Path,
    force: bool = False,
    sermon_filter: Optional[str] = None,
) -> List[Path]:
    """Find MP3 files that don't have a corresponding .txt transcript."""
    mp3s = []
    for mp3_path in sorted(sermons_dir.rglob("*.mp3")):
        if sermon_filter and mp3_path.parent.name != sermon_filter:
            continue
        txt_path = mp3_path.with_suffix(".txt")
        if force or not txt_path.exists():
            mp3s.append(mp3_path)
    return mp3s
