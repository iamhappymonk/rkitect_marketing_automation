"""
rkitect.ai Content Pipeline — Publish Agent

Posts approved content to Buffer for scheduling.
Reddit section is commented out until posting tool is confirmed.
Image briefs are NOT published — stored for manual use only.
"""

import httpx
from config import BUFFER_ACCESS_TOKEN, BUFFER_PROFILES, PLATFORM_MAP

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


def run_publish(qa_results: dict) -> dict:
    """
    Publish QA-passed content to Buffer.

    Args:
        qa_results: dict from run_qa() with score, passed, content per format.

    Returns:
        dict mapping platform names to Buffer API responses.
    """
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

    return publish_log
