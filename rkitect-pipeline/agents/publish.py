"""
rkitect.ai Content Pipeline — Publish Agent

Posts approved content to Buffer for scheduling.
When auto publish is off, QA-passed content is written to a manual review queue.
Image briefs are NOT published — stored for manual use only.
"""

from datetime import date, datetime
from uuid import uuid4

import httpx
from config import BUFFER_ACCESS_TOKEN, BUFFER_PROFILES, PLATFORM_MAP
from utils.context_loader import (
    load_publish_settings,
    load_review_queue,
    save_review_queue,
)

BUFFER_API = "https://api.bufferapp.com/1"


def _post_to_buffer(profile_id: str, text: str) -> dict:
    """
    Post content to Buffer for scheduling.

    Args:
        profile_id: Buffer profile ID for the platform.
        text: The content text to schedule.

    Returns:
        dict with Buffer API response or error info.
    """
    if not profile_id:
        return {"error": "No profile ID configured for this platform"}

    if not BUFFER_ACCESS_TOKEN:
        return {"error": "BUFFER_ACCESS_TOKEN not set in .env"}

    try:
        r = httpx.post(
            f"{BUFFER_API}/updates/create.json",
            data={
                "profile_ids[]": profile_id,
                "text": text,
                "now": False,
            },
            headers={"Authorization": f"Bearer {BUFFER_ACCESS_TOKEN}"},
            timeout=30,
        )
        return r.json()
    except httpx.TimeoutException:
        return {"error": "Buffer API timeout"}
    except Exception as e:
        return {"error": f"Buffer API error: {e}"}


def _build_review_item(fmt: str, platform: str, result: dict, topic: dict) -> dict:
    """Build a queue item for manual approval."""
    return {
        "id": f"{date.today()}-{fmt}-{uuid4().hex[:8]}",
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "format": fmt,
        "platform": platform,
        "topic": topic.get("selected_topic", "unknown"),
        "pillar": topic.get("pillar", "unknown"),
        "angle": topic.get("angle", ""),
        "content": result.get("content", ""),
        "score": result.get("score", 0),
        "status": "pending_review",
    }


def publish_review_item(item: dict) -> dict:
    """Publish a single reviewed item to Buffer."""
    platform = item.get("platform")
    profile_id = BUFFER_PROFILES.get(platform)
    content = item.get("content", "")

    buffer_result = _post_to_buffer(profile_id, content)
    if buffer_result.get("success"):
        return {"status": "queued", "response": buffer_result}
    return {
        "status": buffer_result.get("message", buffer_result.get("error", "unknown")),
        "response": buffer_result,
    }


def run_publish(qa_results: dict, topic: dict | None = None) -> dict:
    """
    Publish QA-passed content to Buffer.

    Args:
        qa_results: dict from run_qa() with score, passed, content per format.

    Returns:
        dict mapping platform names to Buffer API responses.
    """
    topic = topic or {}
    settings = load_publish_settings()
    publish_log = {}

    for fmt, platform in PLATFORM_MAP.items():
        result = qa_results.get(fmt, {})

        if not result.get("passed"):
            publish_log[platform] = {"status": "skipped", "reason": "QA failed"}
            continue

        content = result.get("content", "")
        if not content:
            publish_log[platform] = {"status": "skipped", "reason": "No content"}
            continue

        if settings.get("auto_publish", False):
            buffer_result = _post_to_buffer(
                BUFFER_PROFILES.get(platform),
                content,
            )

            if buffer_result.get("success"):
                status = "queued"
            else:
                status = buffer_result.get("message", buffer_result.get("error", "unknown"))

            publish_log[platform] = {"status": status, "response": buffer_result}
            print(f"      [{platform}] Buffer: {status}")
        else:
            queue = load_review_queue()
            item = _build_review_item(fmt, platform, result, topic)
            queue.append(item)
            save_review_queue(queue)
            publish_log[platform] = {
                "status": "pending_review",
                "queue_id": item["id"],
            }
            print(f"      [{platform}] queued for review: {item['id']}")

    return publish_log
