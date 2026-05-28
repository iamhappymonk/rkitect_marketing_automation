"""
rkitect.ai Content Pipeline — Generation Agent

Generates content for all active formats in parallel using ThreadPoolExecutor.
Also generates image briefs by calling the image_brief_writer prompt.

FORMATS = ["linkedin", "carousel", "twitter", "reddit"]
Reels are REMOVED from v2 scope. max_workers=4.
"""

import concurrent.futures
import json
import re
from typing import Tuple

from model_router import call_model
from utils.context_loader import load_brand_context, load_prompt
from config import FORMATS, IMAGE_TEMPLATE_ENABLED, IMAGE_GENERATION_ENABLED, PLATFORM_MAP

# Inverse of PLATFORM_MAP: platform name → internal format name
# e.g. "instagram" → "carousel", "linkedin" → "linkedin", "twitter" → "twitter"
PLATFORM_TO_FORMAT: dict[str, str] = {plat: fmt for fmt, plat in PLATFORM_MAP.items()}


def _iter_json_candidates(text: str):
    """Yield JSON candidate strings from text.

    Yields fenced ```json``` blocks first, then all brace-balanced top-level
    objects found via character scanning. This avoids greedy regex matching
    that would merge unrelated JSON blobs (e.g. calendar metadata echoed back
    by the model followed by the real payload in a code fence).
    """
    # 1. Fenced code blocks (```json ... ``` or ``` ... ```)
    for m in re.finditer(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text):
        yield m.group(1)
    # 2. All brace-balanced objects via character scanning
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


def _parse_generation_result(fmt: str, raw: str) -> str:
    """Extract clean post text from a JSON model response.

    Searches for the first JSON object that contains the expected schema key
    for the given format (e.g. "slides" for carousel, "tweets" for twitter).
    Falls back to the raw string if no valid matching JSON is found, so
    content is never silently lost on a parse error.

    The greedy regex approach (re.search r"\\{.*\\}") is intentionally avoided
    because it merges unrelated JSON blobs — e.g. calendar metadata the model
    echoes back followed by the real payload in a code fence.
    """
    # Expected top-level key per format — used to identify the right JSON blob
    SCHEMA_KEYS: dict[str, str] = {
        "linkedin": "post",
        "twitter": "tweets",
        "carousel": "slides",
        "reddit": "body",
    }
    expected_key = SCHEMA_KEYS.get(fmt)

    data = None

    # First pass: find a JSON object that contains the expected schema key
    if expected_key:
        for candidate in _iter_json_candidates(raw):
            try:
                parsed = json.loads(candidate)
                if expected_key in parsed:
                    data = parsed
                    break
            except json.JSONDecodeError:
                continue

    # Second pass: any valid JSON (fallback when schema key not found)
    if data is None:
        for candidate in _iter_json_candidates(raw):
            try:
                data = json.loads(candidate)
                break
            except json.JSONDecodeError:
                continue

    if data is None:
        return raw

    if fmt == "linkedin":
        return data.get("post", raw)
    elif fmt == "twitter":
        tweets = data.get("tweets", [])
        return "\n\n".join(tweets) if tweets else raw
    elif fmt == "carousel":
        # Return clean JSON string so _generate_image_brief gets all slide visual
        # descriptions. Caption extraction for display/Buffer happens in
        # _clean_content_for_platform.
        try:
            return json.dumps(data)
        except Exception:
            return raw
    elif fmt == "reddit":
        title = data.get("title", "")
        body = data.get("body", raw)
        return f"{title}\n\n{body}".strip() if title else body
    return raw


def _generate_one(
    fmt: str, topic: dict, brand_context: str
) -> Tuple[str, str]:
    """
    Generate content for a single format.

    Args:
        fmt: Format name (linkedin, carousel, twitter, reddit).
        topic: Selected topic dict from filter agent.
        brand_context: Pre-loaded brand context string.

    Returns:
        Tuple of (format_name, generated_content).
    """
    prompt_name = f"{fmt}_writer"
    try:
        prompt = load_prompt(prompt_name)
    except FileNotFoundError:
        return fmt, f"ERROR: Prompt file {prompt_name}.md not found"

    system = brand_context + "\n\n---\n\n" + prompt

    critique_note = ""
    if topic.get("critique"):
        critique_note = (
            f"\n\nPREVIOUS VERSION FAILED QA. "
            f"Critique to address:\n{topic['critique']}"
        )

    user = (
        f"Topic: {topic.get('selected_topic', 'No topic')}\n"
        f"Pillar: {topic.get('pillar', 'unknown')}\n"
        f"Angle: {topic.get('angle', 'general')}"
        f"{critique_note}\n\n"
        + (
            "Planned calendar context:\n"
            f"- Format: {topic.get('format', '')}\n"
            f"- Psychological hook: {topic.get('psychological_hook', '')}\n"
            f"- Caption theme: {topic.get('caption_theme', '')}\n"
            f"- Caption: {topic.get('caption', '')}\n\n"
            if topic.get("calendar_entry") or topic.get("format") or topic.get("caption")
            else ""
        )
        + f"Write the {fmt} content now. Return valid JSON only."
    )

    try:
        result = call_model(fmt, system, user, max_tokens=2000)
        result = _parse_generation_result(fmt, result)
        return fmt, result
    except Exception as e:
        return fmt, f"ERROR: {e}"


def _generate_image_brief(
    fmt: str, content: str, brand_context: str
) -> Tuple[str, str]:
    """
    Generate an image brief for a piece of content.

    Args:
        fmt: Platform format name.
        content: The generated text content.
        brand_context: Pre-loaded brand context string.

    Returns:
        Tuple of (brief_key, generated_brief_json).
    """
    try:
        prompt = load_prompt("image_brief_writer")
    except FileNotFoundError:
        return f"{fmt}_image_brief", "ERROR: image_brief_writer.md not found"

    system = brand_context + "\n\n---\n\n" + prompt
    user = (
        f"Platform: {fmt}\n\n"
        f"Content:\n---\n{content}\n---\n\n"
        "Generate the image brief(s) as JSON."
    )

    try:
        result = call_model("image_brief", system, user, max_tokens=1500)
        return f"{fmt}_image_brief", result
    except Exception as e:
        return f"{fmt}_image_brief", f"ERROR: {e}"


def run_generation(topic: dict, active_formats: list[str] | None = None) -> dict:
    """
    Generate content for all formats in parallel, then generate image briefs.

    Args:
        topic: Selected topic dict from filter agent.
        active_formats: Optional subset of FORMATS to generate. When None all
                        FORMATS run (default behaviour). Pass an explicit list
                        to restrict generation to specific channels — useful
                        when a template targets only a subset of platforms so
                        unneeded LLM calls (and tokens) are skipped.

    Returns:
        dict mapping format names to generated content strings,
        plus image brief keys.
    """
    brand_context = load_brand_context()
    results = {}

    # Resolve which formats to generate. None means "all" for backward compat.
    formats_to_run = active_formats if active_formats is not None else FORMATS

    if not formats_to_run:
        return results

    # Step 1: Generate text content in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(formats_to_run)) as executor:
        futures = {
            executor.submit(_generate_one, fmt, topic, brand_context): fmt
            for fmt in formats_to_run
        }
        for future in concurrent.futures.as_completed(futures):
            try:
                fmt, result = future.result()
                results[fmt] = result
            except Exception as e:
                fmt = futures[future]
                results[fmt] = f"ERROR: {e}"

    # Step 2: Generate image briefs for successful content
    brief_futures = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(len(formats_to_run), 1)) as executor:
        for fmt in formats_to_run:
            content = results.get(fmt, "")
            if content and not content.startswith("ERROR"):
                # Skip ALL image briefs when template engine is enabled — Stage 3.25
                # owns carousel_image_brief, and LinkedIn/Twitter images are sourced
                # from carousel slides via build_platform_image_paths().
                # Free-form LLM briefs drift from brand and cannot reliably avoid
                # rendering text in generated images.
                if IMAGE_TEMPLATE_ENABLED and IMAGE_GENERATION_ENABLED:
                    print(f"      [generate] Skipping {fmt} image brief — template engine owns all image briefs (Stage 3.25)")
                    continue
                future = executor.submit(
                    _generate_image_brief, fmt, content, brand_context
                )
                brief_futures[future] = fmt

        for future in concurrent.futures.as_completed(brief_futures):
            try:
                key, brief = future.result()
                results[key] = brief
            except Exception as e:
                fmt = brief_futures[future]
                results[f"{fmt}_image_brief"] = f"ERROR: {e}"

    return results
