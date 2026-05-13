from __future__ import annotations

import argparse
import asyncio
from typing import Any
from uuid import UUID

import httpx

from web import db
from web.config import settings

CREATE_POST_MUTATION = """
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    ... on PostActionSuccess {
      post {
        id
        text
        dueAt
      }
    }
    ... on MutationError {
      message
    }
  }
}
"""


def _channel_for_platform(platform: str) -> str:
    platform = platform.lower()
    if platform == "linkedin":
        return settings.buffer_linkedin_channel_id
    if platform == "instagram":
        return settings.buffer_instagram_channel_id
    if platform in {"twitter", "x"}:
        return settings.buffer_twitter_channel_id
    return ""


def _extract_text(item: dict[str, Any]) -> str:
    preview = item.get("preview_data") or {}
    title = str(item.get("title") or "").strip()

    candidate_keys = (
        "post_body",
        "text",
        "body",
        "caption",
        "post",
        "parsedCaption",
        "parsedTweet",
    )

    if isinstance(preview, dict):
        for key in candidate_keys:
            value = preview.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        stdout = preview.get("stdout")
        if isinstance(stdout, str) and stdout.strip():
            for line in stdout.splitlines():
                line = line.strip()
                if not line:
                    continue
                if any(
                    token in line.lower()
                    for token in ("generating", "posted", "exit code", "phase")
                ):
                    continue
                if len(line) >= 20:
                    return line

    return title or "Automated post from MarketMeNow"


async def _create_buffer_post(platform: str, item_id: UUID) -> None:
    if not settings.buffer_api_token:
        raise RuntimeError("MMN_WEB_BUFFER_API_TOKEN is not set")

    channel_id = _channel_for_platform(platform)
    if not channel_id:
        raise RuntimeError(f"No Buffer channel configured for platform={platform}")

    item = await db.get_content_item(item_id)
    if item is None:
        raise RuntimeError(f"Content item not found: {item_id}")

    item_dict = dict(item)
    text = _extract_text(item_dict)

    mutation_input: dict[str, Any] = {
        "channelId": channel_id,
        "text": text,
        "schedulingType": settings.buffer_scheduling_type,
        "mode": settings.buffer_share_mode,
    }

    payload = {
        "query": CREATE_POST_MUTATION,
        "variables": {"input": mutation_input},
    }

    headers = {
        "Authorization": f"Bearer {settings.buffer_api_token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(settings.buffer_api_url, json=payload, headers=headers)

    response.raise_for_status()
    data = response.json()

    errors = data.get("errors")
    if errors:
        raise RuntimeError(f"Buffer GraphQL errors: {errors}")

    result = (data.get("data") or {}).get("createPost") or {}
    if result.get("message") and not result.get("post"):
        raise RuntimeError(f"Buffer createPost failed: {result['message']}")


def build_buffer_publish_command(platform: str, item_id: UUID) -> list[str]:
    return [
        "python",
        "-m",
        "web.buffer_publisher",
        "--platform",
        platform,
        "--item-id",
        str(item_id),
    ]


async def _amain() -> int:
    parser = argparse.ArgumentParser(description="Publish approved content to Buffer")
    parser.add_argument("--platform", required=True)
    parser.add_argument("--item-id", required=True)
    args = parser.parse_args()

    await db.init_pool()
    try:
        await _create_buffer_post(args.platform, UUID(args.item_id))
    finally:
        await db.close_pool()

    return 0


def main() -> None:
    raise SystemExit(asyncio.run(_amain()))


if __name__ == "__main__":
    main()