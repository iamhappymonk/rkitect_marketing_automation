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
from config import FORMATS


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
        + f"Write the {fmt} content now."
    )

    try:
        result = call_model(fmt, system, user, max_tokens=2000)
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


def run_generation(topic: dict) -> dict:
    """
    Generate content for all formats in parallel, then generate image briefs.

    Args:
        topic: Selected topic dict from filter agent.

    Returns:
        dict mapping format names to generated content strings,
        plus image brief keys.
    """
    brand_context = load_brand_context()
    results = {}

    # Step 1: Generate text content in parallel (4 formats, 4 workers)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(_generate_one, fmt, topic, brand_context): fmt
            for fmt in FORMATS
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
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        for fmt in FORMATS:
            content = results.get(fmt, "")
            if content and not content.startswith("ERROR"):
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
