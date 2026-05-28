"""Backfill review queue items with `image_urls` for dashboard preview.

Scans each queue item's `image_paths` array. If path is under `OUTPUT_DIR`,
converts to `/output/<date>/<subpath>` URL. If item contains bare filenames,
searches `OUTPUT_DIR` for matching filename and uses newest match.

Run: python scripts/migrate_review_queue.py
"""
import json
from pathlib import Path
from datetime import datetime

from config import PUBLISH_QUEUE, OUTPUT_DIR


def find_file_in_output(filename: str) -> Path | None:
    """Search OUTPUT_DIR for filename, return newest match or None."""
    matches = list(OUTPUT_DIR.rglob(filename))
    if not matches:
        return None
    # pick most recent by mtime
    matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0]


def path_to_output_url(p: str) -> str | None:
    try:
        ppath = Path(p)
        if ppath.is_absolute():
            if str(ppath).startswith(str(OUTPUT_DIR)):
                rel = ppath.relative_to(OUTPUT_DIR)
                return f"/output/{rel.as_posix()}"
            # absolute but outside output dir -> skip
            return None

        # relative or filename: try to find in OUTPUT_DIR
        found = find_file_in_output(ppath.name)
        if found:
            rel = found.relative_to(OUTPUT_DIR)
            return f"/output/{rel.as_posix()}"
    except Exception:
        return None
    return None


def main():
    if not PUBLISH_QUEUE.exists():
        print(f"No publish queue found at {PUBLISH_QUEUE}")
        return

    with open(PUBLISH_QUEUE, encoding="utf-8") as f:
        try:
            queue = json.load(f)
        except Exception as e:
            print(f"Failed to read queue: {e}")
            return

    updated = 0
    for item in queue:
        img_paths = item.get("image_paths") or []
        urls = item.get("image_urls") or []
        for p in img_paths:
            url = path_to_output_url(p)
            if url and url not in urls:
                urls.append(url)

        if urls and not item.get("image_urls"):
            item["image_urls"] = urls
            updated += 1

    if updated:
        with open(PUBLISH_QUEUE, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=2)
        print(f"Updated {updated} queue items with image_urls. Saved to {PUBLISH_QUEUE}")
    else:
        print("No items required updating.")


if __name__ == "__main__":
    main()
