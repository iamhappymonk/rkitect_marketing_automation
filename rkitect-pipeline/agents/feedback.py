"""Feedback agent.

Applies user feedback, patches runtime context / prompt guards, regenerates the
selected post with the feedback as critique, and requeues the revised draft for
manual review.
"""
from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

from config import OUTPUT_DIR, PLATFORM_MAP
from agents.generate import _generate_one
from utils.context_loader import (
    load_brand_context,
    load_review_queue,
    save_review_queue,
)
from utils.feedback import process_feedback, write_feedback_diff


def _load_topic_for_feedback(source_file: str = "") -> dict:
    """Load the topic JSON that generated the selected output."""
    candidates = []
    if source_file:
        src = Path(source_file)
        candidates.append(src.parent / "topics.md")
    candidates.append(OUTPUT_DIR / str(date.today()) / "topics.md")

    for path in candidates:
        if not path.exists():
            continue
        try:
            raw = path.read_text(encoding="utf-8")
            return json.loads(raw)
        except Exception:
            continue
    return {}


def _load_source_text(source_file: str = "") -> str:
    if not source_file:
        return ""
    path = Path(source_file)
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _infer_format(source_file: str = "", fallback: str = "linkedin") -> str:
    if source_file:
        stem = Path(source_file).stem
        if stem.endswith("_image_brief"):
            stem = stem.replace("_image_brief", "")
        if stem in PLATFORM_MAP or stem in {"linkedin", "carousel", "twitter", "reddit"}:
            return stem
    return fallback


def _build_review_item(fmt: str, content: str, topic: dict, feedback: str, source_file: str = "") -> dict:
    platform = PLATFORM_MAP.get(fmt, fmt)
    return {
        "id": f"fb-{date.today()}-{fmt}-{uuid4().hex[:8]}",
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "format": fmt,
        "platform": platform,
        "topic": topic.get("selected_topic", "unknown"),
        "pillar": topic.get("pillar", "unknown"),
        "angle": topic.get("angle", ""),
        "content": content,
        "score": 0,
        "status": "pending_review",
        "feedback": feedback,
        "source_file": source_file,
    }


def apply_feedback(
    feedback: str,
    phrase: Optional[str] = None,
    source_file: Optional[str] = None,
    format_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Apply feedback and regenerate the affected draft.

    Returns a dict with the regenerated content, queue id, and patch metadata.
    """
    source_file = source_file or ""
    fmt = _infer_format(source_file, fallback=format_name or "linkedin")
    topic = _load_topic_for_feedback(source_file)
    source_text = _load_source_text(source_file)

    if not topic:
        return {
            "status": "failed",
            "error": "Could not load topic context for regeneration",
        }

    feedback_result = process_feedback(feedback, phrase=phrase, source_file=source_file)

    # Regenerate using the feedback as critique so the next draft directly addresses the issue.
    try:
        revised_topic = {**topic, "critique": feedback}
        brand_context = load_brand_context()
        _, revised_content = _generate_one(fmt, revised_topic, brand_context)
    except Exception as e:
        return {
            "status": "failed",
            "error": f"Regeneration failed: {e}",
            "feedback": feedback_result,
        }

    hinted_path = Path(source_file) if source_file else None
    if hinted_path and hinted_path.exists():
        target_path = hinted_path
    else:
        target_path = OUTPUT_DIR / str(date.today()) / f"{fmt}.md"
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(revised_content, encoding="utf-8")

    queue_item = _build_review_item(fmt, revised_content, topic, feedback, str(target_path))
    queue = load_review_queue()
    queue.append(queue_item)
    save_review_queue(queue)

    diff_path = write_feedback_diff(
        feedback=feedback,
        source_file=str(target_path),
        before=source_text,
        after=revised_content,
    )

    feedback_result.update(
        {
            "status": "requeued",
            "format": fmt,
            "queue_id": queue_item["id"],
            "source_file": str(target_path),
            "diff_file": str(diff_path),
            "content": revised_content,
            "review_queue_count": len(queue),
        }
    )
    return feedback_result
