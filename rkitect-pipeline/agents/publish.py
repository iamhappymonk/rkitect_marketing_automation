"""
rkitect.ai Content Pipeline — Publish Agent

Posts approved content via:
  1. Buffer GraphQL API (createPost → schedule to queue)
  2. Zernio REST API (posts:create → schedule to connected accounts)
When auto publish is off, QA-passed content is written to a manual review queue.
Supports optional image attachments via Buffer media upload API.
"""

from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

import httpx
from config import (
    BUFFER_ACCESS_TOKEN,
    BUFFER_PROFILES,
    PLATFORM_MAP,
    BUFFER_ORGANIZATION_ID,
)
from utils.context_loader import (
    load_publish_settings,
    load_review_queue,
    save_review_queue,
)

import os

BUFFER_GRAPHQL_API = "https://api.buffer.com/1/graphql"
BUFFER_MEDIA_UPLOAD_URL = "https://api.buffer.com/1/media/upload"
ZERNIO_API_BASE = "https://zernio.com/api/v1"
ZERNIO_API_KEY = os.getenv("ZERNIO_API_KEY", "")


# ── Buffer: image upload ───────────────────────────────────────────────────

def _upload_image_to_buffer(image_path: str, token: str) -> str | None:
    """Upload a single image to Buffer, return media ID."""
    try:
        with open(image_path, "rb") as f:
            r = httpx.post(
                BUFFER_MEDIA_UPLOAD_URL,
                headers={"Authorization": f"Bearer {token}"},
                files={"file": (Path(image_path).name, f, "image/jpeg")},
                timeout=60,
            )
        data = r.json()
        return data.get("id") or data.get("media_id")
    except Exception as e:
        print(f"      [publish] Image upload failed: {e}")
        return None


# ── Buffer: schedule to channel queue via GraphQL ──────────────────────────

def _post_to_buffer(
    profile_id: str, text: str, platform: str = "", image_paths: list[str] = None
) -> dict:
    """
    Schedule content to a Buffer channel queue via GraphQL createPost.
    Optionally uploads and attaches images.

    Args:
        profile_id: Buffer channel ID (profile ID from .env).
        text: The content text to schedule.
        platform: The target platform name for logging.
        image_paths: Optional list of local file paths to upload as media.

    Returns:
        dict with Buffer API response or error info.
    """
    if not profile_id:
        return {"error": "No profile/channel ID configured for this platform"}

    if not BUFFER_ACCESS_TOKEN:
        return {"error": "BUFFER_ACCESS_TOKEN not set in .env"}

    # Upload images first (if any)
    media_ids = []
    if image_paths:
        for img_path in image_paths:
            if not Path(img_path).exists():
                print(f"      [publish] Image file not found, skipping: {img_path}")
                continue
            media_id = _upload_image_to_buffer(img_path, BUFFER_ACCESS_TOKEN)
            if media_id:
                media_ids.append(media_id)
                print(f"      [publish] Uploaded {Path(img_path).name} -> {media_id}")
            else:
                print(f"      [publish] Failed to upload {Path(img_path).name}, continuing")

    # Build GraphQL mutation — include mediaIds if we have uploaded images
    if media_ids:
        query = """
        mutation CreatePost($channelId: ChannelId!, $text: String!, $mediaIds: [ID!], $schedulingType: SchedulingType!, $mode: ShareMode!) {
          createPost(input: {
            channelId: $channelId,
            text: $text,
            mediaIds: $mediaIds,
            schedulingType: $schedulingType,
            mode: $mode,
            saveToDraft: false
          }) {
            ... on PostActionSuccess {
              post {
                id
              }
            }
          }
        }
        """
        variables = {
            "channelId": profile_id,
            "text": text,
            "mediaIds": media_ids,
            "schedulingType": "automatic",
            "mode": "addToQueue",
        }
    else:
        query = """
        mutation CreatePost($channelId: ChannelId!, $text: String!, $schedulingType: SchedulingType!, $mode: ShareMode!) {
          createPost(input: {
            channelId: $channelId,
            text: $text,
            schedulingType: $schedulingType,
            mode: $mode,
            saveToDraft: false
          }) {
            ... on PostActionSuccess {
              post {
                id
              }
            }
          }
        }
        """
        variables = {
            "channelId": profile_id,
            "text": text,
            "schedulingType": "automatic",
            "mode": "addToQueue",
        }

    try:
        r = httpx.post(
            BUFFER_GRAPHQL_API,
            json={"query": query, "variables": variables},
            headers={"Authorization": f"Bearer {BUFFER_ACCESS_TOKEN}"},
            timeout=30,
        )
        data = r.json()
        if "errors" in data:
            return {"error": str(data["errors"])}
        return {
            "success": True,
            "response": data,
            "media_ids": media_ids if media_ids else None,
        }
    except httpx.TimeoutException:
        return {"error": "Buffer API timeout"}
    except Exception as e:
        return {"error": f"Buffer API error: {e}"}


# ── Zernio: schedule via REST API ──────────────────────────────────────────

# Map our internal platform names to Zernio platform strings
ZERNIO_PLATFORM_MAP = {
    "twitter": "twitter",
    "linkedin": "linkedin",
    "instagram": "instagram",
}


def _post_to_zernio(text: str, platform: str) -> dict:
    """
    Schedule content via Zernio REST API.

    Args:
        text: The content text to schedule.
        platform: One of 'twitter', 'linkedin', 'instagram'.

    Returns:
        dict with Zernio API response or error info.
    """
    if not ZERNIO_API_KEY:
        return {"error": "ZERNIO_API_KEY not set in .env"}

    zernio_platform = ZERNIO_PLATFORM_MAP.get(platform)
    if not zernio_platform:
        return {"error": f"Zernio does not support platform: {platform}"}

    # Look up Zernio account ID from env  (e.g. ZERNIO_TWITTER_ACCOUNT_ID)
    account_id = os.getenv(f"ZERNIO_{platform.upper()}_ACCOUNT_ID", "")
    profile_id = os.getenv("ZERNIO_PROFILE_ID", "")

    if not account_id:
        return {"error": f"ZERNIO_{platform.upper()}_ACCOUNT_ID not set in .env"}
    if not profile_id:
        return {"error": "ZERNIO_PROFILE_ID not set in .env"}

    try:
        r = httpx.post(
            f"{ZERNIO_API_BASE}/posts",
            json={
                "content": text,
                "platforms": [
                    {
                        "platform": zernio_platform,
                        "accountId": account_id,
                    }
                ],
            },
            headers={
                "Authorization": f"Bearer {ZERNIO_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=30,
        )
        data = r.json()
        if r.status_code >= 400:
            return {"error": data.get("message", str(data))}
        return {"success": True, "response": data}
    except httpx.TimeoutException:
        return {"error": "Zernio API timeout"}
    except Exception as e:
        return {"error": f"Zernio API error: {e}"}


# ── Shared publish logic ──────────────────────────────────────────────────

def _build_review_item(
    fmt: str, platform: str, result: dict, topic: dict, image_paths: list[str] = None
) -> dict:
    """Build a queue item for manual approval, including image paths if available."""
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
        "image_paths": image_paths or [],
    }


def publish_review_item(item: dict) -> dict:
    """Publish a single reviewed item to Buffer + Zernio, including images."""
    platform = item.get("platform")
    profile_id = BUFFER_PROFILES.get(platform)
    content = item.get("content", "")
    item_image_paths = item.get("image_paths", [])

    results = {}

    # Buffer (with optional images)
    buffer_result = _post_to_buffer(
        profile_id, content, platform, image_paths=item_image_paths or None
    )
    results["buffer"] = buffer_result

    # Zernio (best-effort)
    if ZERNIO_API_KEY:
        zernio_result = _post_to_zernio(content, platform)
        results["zernio"] = zernio_result

    if buffer_result.get("success"):
        return {"status": "queued", "response": results}
    return {
        "status": buffer_result.get("message", buffer_result.get("error", "unknown")),
        "response": results,
    }


def run_publish(
    qa_results: dict, topic: dict | None = None, image_paths: dict | None = None
) -> dict:
    """
    Publish QA-passed content to Buffer (queue) and optionally Zernio.
    Attaches images when available.

    Args:
        qa_results: dict from run_qa() with score, passed, content per format.
        topic: The selected topic dict for metadata.
        image_paths: Optional dict of image paths per format:
                     {"carousel": [path1, path2, ...], "linkedin": [path1]}

    Returns:
        dict mapping platform names to publishing responses.
    """
    topic = topic or {}
    image_paths = image_paths or {}
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

        # Determine images for this format/platform
        # carousel format -> "carousel" images, linkedin format -> "linkedin" images
        # Reddit doesn't need images — skip image attachment for reddit
        fmt_images = []
        if fmt != "reddit":
            fmt_images = image_paths.get(fmt, [])
            # Also map: carousel format uses carousel images
            if fmt == "carousel" and not fmt_images:
                fmt_images = image_paths.get("carousel", [])
            if fmt == "linkedin" and not fmt_images:
                fmt_images = image_paths.get("linkedin", [])

        if settings.get("auto_publish", False):
            platform_results = {}

            # Buffer scheduling (with optional images)
            buffer_result = _post_to_buffer(
                BUFFER_PROFILES.get(platform),
                content,
                platform,
                image_paths=fmt_images or None,
            )
            platform_results["buffer"] = buffer_result

            if buffer_result.get("success"):
                status = "queued"
            else:
                status = buffer_result.get("message", buffer_result.get("error", "unknown"))

            # Zernio scheduling (best-effort, don't block on failure)
            if ZERNIO_API_KEY:
                zernio_result = _post_to_zernio(content, platform)
                platform_results["zernio"] = zernio_result
                zernio_status = "queued" if zernio_result.get("success") else zernio_result.get("error", "unknown")
                print(f"      [{platform}] Zernio: {zernio_status}")

            publish_log[platform] = {"status": status, "response": platform_results}
            img_count = len(fmt_images) if fmt_images else 0
            img_note = f" ({img_count} images)" if img_count else ""
            print(f"      [{platform}] Buffer: {status}{img_note}")
        else:
            queue = load_review_queue()
            item = _build_review_item(
                fmt, platform, result, topic, image_paths=fmt_images or None
            )
            queue.append(item)
            save_review_queue(queue)
            publish_log[platform] = {
                "status": "pending_review",
                "queue_id": item["id"],
            }
            print(f"      [{platform}] queued for review: {item['id']}")

    return publish_log
