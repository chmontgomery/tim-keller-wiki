from pathlib import Path
from typing import Any
from urllib.parse import urlparse, unquote


class FolderNameError(ValueError):
    """Raised when a folder name cannot be derived from an mp3 URL."""


def folder_name_from_mp3_url(url: str) -> str:
    """Derive the on-disk folder name from a sermon mp3 URL.

    Example: ".../Peace_Overcoming_Anxiety.mp3" -> "Peace_Overcoming_Anxiety"
    """
    path = urlparse(url).path
    filename = unquote(path.rsplit("/", 1)[-1])
    if "." not in filename:
        raise FolderNameError(f"No file extension in URL: {url}")
    stem, ext = filename.rsplit(".", 1)
    if ext.lower() != "mp3":
        raise FolderNameError(f"URL does not end in .mp3: {url}")
    if not stem:
        raise FolderNameError(f"Empty filename stem in URL: {url}")
    return stem


CHUNK_SIZE = 64 * 1024  # 64 KB


class DownloadError(Exception):
    """Raised when a sermon mp3 cannot be downloaded."""


def download_sermon(
    http_client,
    metadata: dict[str, Any],
    sermons_dir: Path,
) -> Path:
    """Download a sermon mp3 to raw/sermons/<folder>/<folder>.mp3.

    Streams to a .part file and renames on success. On any failure,
    removes the .part file and raises DownloadError.

    Returns the sermon folder path.
    """
    try:
        folder_name = folder_name_from_mp3_url(metadata["mp3_url"])
    except FolderNameError as e:
        raise DownloadError(f"Cannot derive folder name: {e}") from e
    folder = sermons_dir / folder_name
    folder.mkdir(parents=True, exist_ok=True)

    final_path = folder / f"{folder_name}.mp3"
    part_path = folder / f"{folder_name}.mp3.part"

    try:
        with http_client.stream("GET", metadata["mp3_url"]) as resp:
            resp.raise_for_status()
            with part_path.open("wb") as f:
                for chunk in resp.iter_bytes():
                    f.write(chunk)
    except Exception as e:
        if part_path.exists():
            part_path.unlink()
        raise DownloadError(f"Failed to download {metadata['mp3_url']}: {e}") from e

    part_path.rename(final_path)
    return folder
