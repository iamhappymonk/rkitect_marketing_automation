"""Populate `preview_content` for items in publish queue by cleaning briefs/visual blocks.

Run with PYTHONPATH set so project imports resolve:
  cmd /c "set PYTHONPATH=rkitect-pipeline&& .venv\Scripts\python.exe rkitect-pipeline\scripts\clean_review_content.py"
"""
import json
from pathlib import Path

from config import PUBLISH_QUEUE


def main():
    if not PUBLISH_QUEUE.exists():
        print(f"Publish queue not found: {PUBLISH_QUEUE}")
        return

    try:
        # Import locally to avoid early import failures
        from agents import publish as publish_mod
    except Exception as e:
        print(f"Failed to import agents.publish: {e}")
        return

    with open(PUBLISH_QUEUE, encoding="utf-8") as f:
        queue = json.load(f)

    updated = 0
    for item in queue:
        content = item.get("content", "")
        fmt = item.get("format", "")
        cleaned = publish_mod._clean_content_for_platform(content, fmt=fmt)
        # Only set preview_content if different and not empty
        if cleaned and cleaned.strip() and cleaned.strip() != content.strip():
            item["preview_content"] = cleaned
            updated += 1

    if updated:
        with open(PUBLISH_QUEUE, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=2)
        print(f"Updated {updated} items with preview_content in {PUBLISH_QUEUE}")
    else:
        print("No items needed preview update.")


if __name__ == "__main__":
    main()
