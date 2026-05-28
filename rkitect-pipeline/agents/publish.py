"""
rkitect.ai Content Pipeline — Publish Agent

Posts approved content via:
  1. Buffer GraphQL API (createPost → schedule to queue)
  2. Zernio REST API (posts:create → schedule to connected accounts)
When auto publish is off, QA-passed content is written to a manual review queue.
Supports optional image attachments via Buffer media upload API.
"""

from datetime import date, datetime
import mimetypes
from pathlib import Path
from uuid import uuid4

import re as _re
import httpx
from config import (
    BUFFER_ACCESS_TOKEN,
    BUFFER_PROFILES,
    PLATFORM_MAP,
    BUFFER_ORGANIZATION_ID,
    OUTPUT_DIR,
    PUBLIC_BASE_URL,
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


# ── Buffer: public asset URLs ───────────────────────────────────────────────

def _path_to_public_url(image_path: str) -> str | None:
    """Convert a local output image path to a public URL Buffer can fetch."""
    try:
        path = Path(image_path)
        if path.is_absolute() and str(path).startswith(str(OUTPUT_DIR)):
            rel = path.relative_to(OUTPUT_DIR).as_posix()
        else:
            rel = image_path.lstrip("/")

        base_url = PUBLIC_BASE_URL.rstrip("/")
        if not base_url:
            return None
        return f"{base_url}/output/{rel}"
    except Exception:
        return None


def _upload_image_to_buffer(image_path: str, token: str) -> str | None:
    """Upload an image to Buffer and return the media ID if successful.

    Buffer's /1/media/upload endpoint expects raw binary with Content-Type set
    to the image MIME type — NOT multipart/form-data.  httpx's `files=` helper
    sends multipart which Buffer rejects with 'Unsupported Content-Type'.

    MIME types are normalised explicitly because Windows' mimetypes registry can
    return non-standard values (e.g. image/pjpeg for .jpg) that Buffer refuses.
    """
    # Explicit extension → MIME map avoids platform-specific registry quirks.
    _EXT_MIME: dict[str, str] = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    ext = Path(image_path).suffix.lower()
    mime_type = _EXT_MIME.get(ext)
    if not mime_type:
        guessed, _ = mimetypes.guess_type(image_path)
        mime_type = guessed or "image/jpeg"

    try:
        with open(image_path, "rb") as f:
            image_data = f.read()

        response = httpx.post(
            BUFFER_MEDIA_UPLOAD_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": mime_type,
            },
            content=image_data,   # raw binary, not multipart
            timeout=60,
        )

        data = response.json()
        media_id = data.get("id") or data.get("media_id")
        if not media_id:
            print(f"      [publish] Buffer upload rejected {Path(image_path).name}: {data}")
        return media_id
    except Exception as e:
        print(f"      [publish] Image upload failed: {e}")
        return None


def _resolve_buffer_assets(image_paths: list[str] | None = None, image_urls: list[str] | None = None) -> list[dict]:
    """Build Buffer `assets` entries from public image URLs."""
    resolved = []
    candidates = list(image_urls or [])
    for image_path in image_paths or []:
        public_url = _path_to_public_url(image_path)
        if public_url:
            candidates.append(public_url)

    seen = set()
    for url in candidates:
        if not url or url in seen:
            continue
        seen.add(url)
        if url.startswith("http://") or url.startswith("https://"):
            resolved.append({"image": {"url": url}})
    return resolved


def _resolve_buffer_image_urls(image_paths: list[str] | None = None, image_urls: list[str] | None = None) -> list[str]:
    """Resolve all usable image URLs from queue data and local output paths."""
    resolved = []
    seen = set()

    for url in image_urls or []:
        if url and url not in seen and (url.startswith("http://") or url.startswith("https://")):
            seen.add(url)
            resolved.append(url)

    for image_path in image_paths or []:
        public_url = _path_to_public_url(image_path)
        if public_url and public_url not in seen:
            seen.add(public_url)
            resolved.append(public_url)

    return resolved


# ── Buffer: schedule to channel queue via GraphQL ──────────────────────────

ZERNIO_PLATFORM_MAP = {
    "twitter": "twitter",
    "linkedin": "linkedin",
    "instagram": "instagram",
}


def _post_to_buffer(
    profile_id: str,
    text: str,
    platform: str = "",
    image_paths: list[str] = None,
    image_urls: list[str] = None,
) -> dict:
    """
    Schedule content to a Buffer channel queue via GraphQL createPost.
    Optionally attaches public image URLs via Buffer assets, or falls back
    to direct media upload if no public URL is resolvable.
    """
    if not profile_id:
        return {"error": "No profile/channel ID configured for this platform", "success": False}

    if not BUFFER_ACCESS_TOKEN:
        return {"error": "BUFFER_ACCESS_TOKEN not set in .env", "success": False}

    resolved_urls = _resolve_buffer_image_urls(image_paths=image_paths, image_urls=image_urls)
    assets = _resolve_buffer_assets(image_urls=resolved_urls)
    uploaded_media_ids: list[str] = []

    # If we cannot build public URLs, fall back to Buffer media upload.
    if not assets and image_paths:
        for img_path in image_paths:
            if not Path(img_path).exists():
                print(f"      [publish] Image file not found, skipping: {img_path}")
                continue
            media_id = _upload_image_to_buffer(img_path, BUFFER_ACCESS_TOKEN)
            if media_id:
                uploaded_media_ids.append(media_id)
                print(f"      [publish] Uploaded {Path(img_path).name} -> {media_id}")
            else:
                print(f"      [publish] Failed to upload {Path(img_path).name}")

    if assets:
        query = """
        mutation CreatePost($channelId: ChannelId!, $text: String!, $assets: [CreatePostAssetInput!], $schedulingType: SchedulingType!, $mode: ShareMode!) {
            createPost(input: {
                channelId: $channelId,
                text: $text,
                assets: $assets,
                schedulingType: $schedulingType,
                mode: $mode,
                saveToDraft: false
            }) {
                ... on PostActionSuccess {
                    post { id }
                }
            }
        }
        """
        variables = {
            "channelId": profile_id,
            "text": text,
            "assets": assets,
            "schedulingType": "automatic",
            "mode": "addToQueue",
        }
    elif uploaded_media_ids:
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
                    post { id }
                }
            }
        }
        """
        variables = {
            "channelId": profile_id,
            "text": text,
            "mediaIds": uploaded_media_ids,
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
                    post { id }
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
        response = httpx.post(
            BUFFER_GRAPHQL_API,
            json={"query": query, "variables": variables},
            headers={"Authorization": f"Bearer {BUFFER_ACCESS_TOKEN}"},
            timeout=30,
        )
        data = response.json()
        if "errors" in data:
            return {"error": str(data["errors"]), "success": False}

        result = {"success": True, "response": data}
        if assets:
            result["assets"] = assets
        if uploaded_media_ids:
            result["media_ids"] = uploaded_media_ids
        if image_paths and not assets and not uploaded_media_ids:
            result["warning"] = "Published text only because no image attachment could be resolved"
        return result
    except httpx.TimeoutException:
        return {"error": "Buffer API timeout", "success": False}
    except Exception as e:
        return {"error": f"Buffer API error: {e}", "success": False}


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
    fmt: str,
    platform: str,
    result: dict,
    topic: dict,
    image_paths: list[str] = None,
    template_meta: dict = None,
    source_file: str = "",
) -> dict:
    """Build a queue item for manual approval, including image paths if available."""
    raw_content = result.get("content", "")
    cleaned_content = _clean_content_for_platform(raw_content, fmt=fmt)

    # Derive run_folder from source_file so on-demand image/video generation
    # can locate image_briefs.json and template_manifest.json.
    run_folder = str(Path(source_file).parent) if source_file else ""

    # Store only the fields needed for video assembly; strip any huge rendered
    # brief strings that don't belong in the queue file.
    _TEMPLATE_META_FIELDS = (
        "template_id", "template_name", "video_transition",
        "transition_direction", "video_duration_hint", "video_generation_mode",
        "image_size", "slide_count",
    )
    stored_template_meta = (
        {k: template_meta[k] for k in _TEMPLATE_META_FIELDS if k in template_meta}
        if template_meta else None
    )

    return {
        "id": f"{date.today()}-{fmt}-{uuid4().hex[:8]}",
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "format": fmt,
        "platform": platform,
        "topic": topic.get("selected_topic", "unknown"),
        "pillar": topic.get("pillar", "unknown"),
        "angle": topic.get("angle", ""),
        "content": cleaned_content,
        "score": result.get("score", 0),
        "status": "pending_review",
        "image_paths": image_paths or [],
        "source_file": source_file,
        "run_folder": run_folder,
        "template_meta": stored_template_meta,
    }


def _iter_json_candidates_publish(text: str):
    """Yield JSON candidate strings from text.

    Yields fenced ```json``` blocks first, then all brace-balanced top-level
    objects via character scanning. Mirrors the helper in generate.py so both
    modules use the same robust extraction logic instead of a greedy regex.
    """
    for m in _re.finditer(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text):
        yield m.group(1)
    i = 0
    while i < len(text):
        if text[i] == "{":
            depth = 0
            for j in range(i, len(text)):
                if text[j] == "{":
                    depth += 1
                elif text[j] == "}":
                    depth -= 1
                    if depth == 0:
                        yield text[i : j + 1]
                        i = j + 1
                        break
            else:
                break
        else:
            i += 1


def _clean_content_for_platform(content: str, fmt: str = "") -> str:
    """Strip image briefs, slide blocks, and visual prompts from generated content.

    For carousel format the content may be a JSON object ({"slides": [...], "caption": "..."});
    extract just the caption for Buffer posting.
    Prefer explicit caption sections when present (e.g., '## Caption').
    """
    import re
    import json as _json

    if not content:
        return ""

    # Carousel: find first JSON object with "slides" key and extract caption.
    # Uses brace-balanced scanning instead of a greedy regex so calendar metadata
    # blobs echoed before the real payload are skipped correctly.
    if fmt == "carousel":
        for _candidate in _iter_json_candidates_publish(content):
            try:
                _data = _json.loads(_candidate)
                if "slides" in _data:
                    caption = _data.get("caption", "")
                    return caption.strip() if caption else ""
            except _json.JSONDecodeError:
                continue

    # Twitter: extract tweets array from JSON if present.
    # Models sometimes echo calendar metadata instead of using the correct schema;
    # try "tweets" key first, then fall back to "caption" if it contains tweet-like
    # content (list of strings).
    if fmt == "twitter":
        for _candidate in _iter_json_candidates_publish(content):
            try:
                _data = _json.loads(_candidate)
                tweets = _data.get("tweets")
                if isinstance(tweets, list) and tweets:
                    return "\n\n".join(str(t) for t in tweets)
                # Fallback: model used "caption" as a list of tweet strings
                caption = _data.get("caption")
                if isinstance(caption, list) and caption:
                    return "\n\n".join(str(t) for t in caption)
                if isinstance(caption, str) and caption:
                    return caption.strip()
            except _json.JSONDecodeError:
                continue

    # Reddit: extract title + body from JSON if present.
    if fmt == "reddit":
        for _candidate in _iter_json_candidates_publish(content):
            try:
                _data = _json.loads(_candidate)
                if "body" in _data:
                    title = _data.get("title", "")
                    body = _data.get("body", "")
                    return f"{title}\n\n{body}".strip() if title else body.strip()
            except _json.JSONDecodeError:
                continue

    # Normalize newlines
    text = content.replace("\r\n", "\n").replace("\r", "\n")

    # Remove explicit image brief blocks
    text = re.sub(r"\[IMAGE BRIEF:[\s\S]*?\]", "", text, flags=re.I).strip()

    # Remove bold metadata markers like **Formula:** ... **Post:** but keep the post text
    text = re.sub(r"\*\*Formula\:\*\*[\s\S]*?\*\*Post\:\*\*", "", text, flags=re.I)

    # Remove standalone bold labels (clean up markers that should not be posted)
    text = re.sub(r"\*\*(?:Carousel|Carousel Content|Carousel|CAPTION|Caption|Formula)\*\*", "", text, flags=re.I)

    # If an explicit caption section exists, use it (covers '## Caption' and '## CAPTION')
    m = re.search(r"##\s*Caption\b[:\-]?[ \t]*(?:\n)?([\s\S]+)$", text, flags=re.I)
    if m:
        return m.group(1).strip()

    # Remove slide blocks like '**Slide 1:** ...' (handles '---' separators)
    text = re.sub(r"\*\*Slide\s*\d+\s*:\*\*[\s\S]*?(?=(\*\*Slide\s*\d+\s*:|\Z))", "", text, flags=re.I)
    # Remove common separators used between slides
    text = re.sub(r"(^|\n)\s*-{3,}\s*(\n|$)", "\n", text)

    # Remove visual descriptor blocks
    text = re.sub(r"\[VISUAL:[\s\S]*?\]", "", text, flags=re.I)

    # Remove Angle/Score/Created metadata lines and solitary platform tokens
    text = re.sub(r"(?m)^(?:Angle|Score|Created)\:.*$", "", text)
    text = re.sub(r"(?m)^\s*(?:linkedin|instagram|twitter|reddit|facebook|tiktok)\s*$", "", text, flags=re.I)

    # Remove residual headings like '## Carousel Content' or '## Carousel'
    text = re.sub(r"(?m)^##\s*Carousel(?: Content)?[^\n]*$", "", text, flags=re.I)

    # Remove any leftover bold markers or labels
    text = re.sub(r"\*\*[\s\S]*?\*\*", "", text)

    # Collapse multiple blank lines and trim
    text = re.sub(r"\n{2,}", "\n\n", text).strip()
    return text


def publish_review_item(item: dict) -> dict:
    """Publish a single reviewed item to Buffer + Zernio, including images."""
    platform = item.get("platform")
    profile_id = BUFFER_PROFILES.get(platform)
    content = item.get("content", "")
    # Clean content before publishing
    content = _clean_content_for_platform(content, fmt=item.get("format", ""))
    item_image_paths = item.get("image_paths", [])
    item_image_urls = item.get("image_urls", [])

    results = {}

    # Buffer (with optional images)
    buffer_result = _post_to_buffer(
        profile_id,
        content,
        platform,
        image_paths=item_image_paths or None,
        image_urls=item_image_urls or None,
    )
    results["buffer"] = buffer_result

    # Zernio (best-effort)
    if ZERNIO_API_KEY:
        zernio_result = _post_to_zernio(content, platform)
        results["zernio"] = zernio_result

    # If Buffer reported success, return queued.
    if buffer_result.get("success"):
        return {"status": "queued", "response": results}

    # Partial or failed publish — re-queue item for manual retry
    try:
        queue = load_review_queue()
        # Avoid duplicate if already present
        if not any(q.get("id") == item.get("id") for q in queue):
            queue.append(item)
            save_review_queue(queue)
            print(f"      [publish] Re-queued item after publish failure: {item.get('id')}")
    except Exception as e:
        print(f"      [publish] Failed to re-queue item: {e}")

    return {
        "status": buffer_result.get("message", buffer_result.get("error", "unknown")),
        "response": results,
    }


def run_publish(
    qa_results: dict,
    topic: dict | None = None,
    image_paths: dict | None = None,
    template_meta: dict | None = None,
    out_dir: "Path | None" = None,
) -> dict:
    """
    Publish QA-passed content to Buffer (queue) and optionally Zernio.
    Attaches images when available.

    Args:
        qa_results: dict from run_qa() with score, passed, content per format.
        topic: The selected topic dict for metadata.
        image_paths: Optional dict of image paths per format:
                     {"carousel": [path1, path2, ...], "linkedin": [path1]}
        template_meta: Optional template metadata dict (stored in queue items
                       so the dashboard can trigger on-demand image/video generation).
        out_dir: Optional path to the current run output folder. Used to
                 compute source_file paths stored in queue items.

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
            # carousel format → use "carousel" key
            if fmt == "carousel" and not fmt_images:
                fmt_images = image_paths.get("carousel", [])
            # linkedin → use "linkedin" key, fall back to carousel slides
            # (template mode shares carousel slides for LinkedIn instead of
            # generating a standalone hero, so "linkedin" may be empty)
            if fmt == "linkedin" and not fmt_images:
                fmt_images = (
                    image_paths.get("linkedin", [])
                    or image_paths.get("carousel", [])
                )

        if settings.get("auto_publish", False):
            platform_results = {}

            # Buffer scheduling (with optional images)
            # Clean content before attempting auto-publish
            cleaned = _clean_content_for_platform(content, fmt=fmt)

            buffer_result = _post_to_buffer(
                BUFFER_PROFILES.get(platform),
                cleaned,
                platform,
                image_paths=fmt_images or None,
            )
            platform_results["buffer"] = buffer_result

            if buffer_result.get("success"):
                status = "queued"
            else:
                # Re-queue on failure so human can retry
                status = "pending_review"
                try:
                    queue = load_review_queue()
                    _src = str(out_dir / f"{fmt}.md") if out_dir else ""
                    item = _build_review_item(
                        fmt, platform, result, topic,
                        image_paths=fmt_images or None,
                        template_meta=template_meta,
                        source_file=_src,
                    )
                    queue.append(item)
                    save_review_queue(queue)
                    platform_results["requeue_id"] = item["id"]
                    print(f"      [{platform}] Auto-publish failed; queued for manual review: {item['id']}")
                except Exception as e:
                    print(f"      [{platform}] Failed to re-queue after auto-publish failure: {e}")
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
            _src = str(out_dir / f"{fmt}.md") if out_dir else ""
            item = _build_review_item(
                fmt, platform, result, topic,
                image_paths=fmt_images or None,
                template_meta=template_meta,
                source_file=_src,
            )
            queue.append(item)
            save_review_queue(queue)
            publish_log[platform] = {
                "status": "pending_review",
                "queue_id": item["id"],
            }
            print(f"      [{platform}] queued for review: {item['id']}")

    return publish_log
