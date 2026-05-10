import argparse
import sys
import time
from pathlib import Path

import httpx

from .about import render_about_md
from .discovery import iter_sermons
from .downloader import download_sermon, DownloadError
from .http_retry import retrying_get
from .manifest import (
    load_manifest,
    save_manifest,
    upsert_stub,
    update_status,
    select_pending,
    reset_failed_to_pending,
)
from .parser import parse_sermon_page, ParseError

SERMONS_DIR = Path("raw/sermons")
USER_AGENT = "tim-keller-bot/0.1 (personal archive)"
BETWEEN_SERMON_DELAY_SECONDS = 3.0
HTTP_TIMEOUT_SECONDS = 60.0


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="python -m tools.download",
        description="Download Tim Keller sermons from gospelinlife.com",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Max sermons to download this run (0 = unlimited)",
    )
    p.add_argument(
        "--retry-failed",
        action="store_true",
        help="Reset failed entries to pending before selecting work",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and plan but do not download",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Log each step in detail",
    )
    return p.parse_args(argv)


def _fetch_sermon_html(client: httpx.Client, url: str) -> str:
    resp = retrying_get(client, url)
    resp.raise_for_status()
    return resp.text


def _save_debug_html(sermons_dir: Path, slug: str, html: str) -> None:
    debug_dir = sermons_dir / ".debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    (debug_dir / f"{slug}.html").write_text(html)


def main(argv=None) -> int:
    args = parse_args(argv)

    sermons_dir = SERMONS_DIR
    sermons_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = sermons_dir / "manifest.json"
    manifest = load_manifest(manifest_path)

    if args.retry_failed:
        reset_failed_to_pending(manifest)
        save_manifest(manifest_path, manifest)

    client_kwargs = {
        "headers": {"User-Agent": USER_AGENT},
        "timeout": HTTP_TIMEOUT_SECONDS,
        "follow_redirects": True,
    }

    with httpx.Client(**client_kwargs) as client:
        try:
            discovered = 0
            for stub in iter_sermons(client):
                if stub["slug"] not in manifest.sermons:
                    discovered += 1
                upsert_stub(manifest, stub)
            save_manifest(manifest_path, manifest)
            if args.verbose:
                print(f"Discovery: {discovered} new sermons added to manifest")
        except Exception as e:
            print(f"Discovery failed: {e}", file=sys.stderr)
            return 1

        work = select_pending(manifest, limit=args.limit)
        if not work:
            print("Nothing to do — no pending sermons.")
            return 0

        print(f"Selected {len(work)} sermon(s) for this run.")

        if args.dry_run:
            for entry in work:
                print(f"  would download: {entry['slug']}")
            return 0

        downloaded = 0
        failed = 0

        for i, entry in enumerate(work):
            slug = entry["slug"]
            source_url = entry["source_url"]
            if args.verbose:
                print(f"[{i + 1}/{len(work)}] {slug}")

            try:
                html = _fetch_sermon_html(client, source_url)
            except Exception as e:
                update_status(
                    manifest, slug, "failed",
                    attempts=entry["attempts"] + 1,
                    last_error=f"fetch failed: {e}",
                )
                save_manifest(manifest_path, manifest)
                failed += 1
                print(f"  fetch failed: {e}")
                continue

            try:
                metadata = parse_sermon_page(html, source_url)
            except ParseError as e:
                _save_debug_html(sermons_dir, slug, html)
                update_status(
                    manifest, slug, "failed",
                    attempts=entry["attempts"] + 1,
                    last_error=str(e),
                )
                save_manifest(manifest_path, manifest)
                failed += 1
                print(f"  parse failed: {e}")
                continue

            try:
                folder = download_sermon(client, metadata, sermons_dir=sermons_dir)
            except DownloadError as e:
                update_status(
                    manifest, slug, "failed",
                    attempts=entry["attempts"] + 1,
                    last_error=str(e),
                )
                save_manifest(manifest_path, manifest)
                failed += 1
                print(f"  download failed: {e}")
                continue

            try:
                (folder / "about.md").write_text(render_about_md(metadata))
            except Exception as e:
                update_status(
                    manifest, slug, "failed",
                    attempts=entry["attempts"] + 1,
                    last_error=f"about.md write failed: {e}",
                )
                save_manifest(manifest_path, manifest)
                failed += 1
                print(f"  about.md failed: {e}")
                continue

            update_status(
                manifest, slug, "downloaded",
                folder=folder.name,
                attempts=entry["attempts"] + 1,
                last_error=None,
            )
            save_manifest(manifest_path, manifest)
            downloaded += 1
            print(f"  downloaded: {folder.name}")

            if i < len(work) - 1:
                time.sleep(BETWEEN_SERMON_DELAY_SECONDS)

        print(f"\nSummary: downloaded {downloaded}, failed {failed}")
        return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
