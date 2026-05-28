"""
Integration tests — AI Content Generation per Format

Exercises the content generation pipeline for each format independently
(linkedin, carousel, twitter, reddit) and writes results to the REAL
review queue so they are visible in the dashboard.

LLM calls are mocked (no API cost). Research, filter, image generation,
self-improve, and post-history writes are also mocked.
QA scoring, queue writing, and OUTPUT_DIR writes run for real.

Run:
    cd rkitect-pipeline
    python -m pytest tests/test_ai_generation_integration.py -v
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure rkitect-pipeline is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))


# ── Format list ───────────────────────────────────────────────────────────────

ALL_FORMATS = ["linkedin", "carousel", "twitter", "reddit"]

# Platform label shown in queue (matches PLATFORM_MAP in config.py)
_FORMAT_TO_PLATFORM = {
    "linkedin": "linkedin",
    "carousel": "instagram",
    "twitter": "twitter",
    "reddit": "reddit",
}


# ── Mock helpers ──────────────────────────────────────────────────────────────

def _make_topic(fmt: str) -> dict:
    """Return a minimal topic dict for a given format test."""
    return {
        "selected_topic": f"AI-Powered Architectural Visualisation — {fmt.upper()} format test",
        "pillar": "education",
        "angle": "how-to guide",
    }


def _mock_call_model_for_format(target_fmt: str):
    """
    Return a call_model side-effect function scoped to a specific format.

    The QA call happens AFTER content generation, so both tasks need valid JSON.
    """

    def _side_effect(task: str, system: str, user: str, **kwargs) -> str:
        if task == "qa":
            return json.dumps({
                "score": 87,
                "passed": True,
                "critique": f"Quality content for {target_fmt} format — test run",
            })

        elif task == "linkedin":
            return json.dumps({
                "post": (
                    "Architecture is the thoughtful making of space.\n\n"
                    "At rkitect.ai we compress weeks of visualisation work into "
                    "minutes — so studios can focus on design, not drafting.\n\n"
                    "#architecture #design #AI #PropTech"
                )
            })

        elif task == "carousel":
            return json.dumps({
                "caption": (
                    "5 ways AI is changing architectural design in 2026. "
                    "Swipe to see the full picture. #architecture #rkitect"
                ),
                "slides": [
                    {
                        "slide": 1,
                        "headline": "The Problem",
                        "visual_description": (
                            "Architect surrounded by physical model prototypes "
                            "and stacks of hand-drawn plans, looking overwhelmed"
                        ),
                    },
                    {
                        "slide": 2,
                        "headline": "Speed",
                        "visual_description": (
                            "Clock graphic — 6 weeks collapsed to 6 minutes "
                            "with glowing AI acceleration arrow"
                        ),
                    },
                    {
                        "slide": 3,
                        "headline": "Accuracy",
                        "visual_description": (
                            "Split screen: hand-drawn sketch left, "
                            "photorealistic AI render right — near-perfect match"
                        ),
                    },
                    {
                        "slide": 4,
                        "headline": "Client Trust",
                        "visual_description": (
                            "Client and architect shaking hands in front of "
                            "a large render printout — confident, aligned"
                        ),
                    },
                    {
                        "slide": 5,
                        "headline": "Try it free",
                        "visual_description": (
                            "rkitect.ai dashboard on screen, clean UI, "
                            "project in progress, minimal chrome"
                        ),
                    },
                ],
            })

        elif task == "twitter":
            return json.dumps({
                "tweets": [
                    (
                        "Architecture is the art of organising space — "
                        "rkitect.ai is the art of seeing it before it exists. "
                        "#arch #AI #design"
                    ),
                    (
                        "Sketch → photorealistic render in under 5 minutes. "
                        "Your clients will thank you. Try rkitect.ai free → link in bio."
                    ),
                ]
            })

        elif task == "reddit":
            return json.dumps({
                "title": (
                    "After 3 months of daily use: honest review of AI architectural "
                    "visualisation tools (2026)"
                ),
                "body": (
                    "I run a small architecture studio and we adopted AI visualisation "
                    "tools 3 months ago. Here's what actually changed:\n\n"
                    "**Client approval speed**: Went from 2-3 revision rounds over 4 weeks "
                    "to 1 round in 3 days. Clients can *see* the space — ambiguity drops.\n\n"
                    "**Cost**: Saved roughly 40 h/month of junior drafter time. "
                    "Reinvested into design iteration.\n\n"
                    "**Quality**: Still needs human review — AI misses local building codes "
                    "and material constraints. It's a drafting accelerator, not a designer.\n\n"
                    "Happy to answer questions."
                ),
            })

        # Fallback
        return json.dumps({"result": "ok"})

    return _side_effect


# ── Parametrized tests ────────────────────────────────────────────────────────

@pytest.mark.parametrize("fmt", ALL_FORMATS)
def test_format_generates_content_and_lands_in_queue(fmt: str):
    """
    For each format:
      1. The pipeline runs without exceptions
      2. At least one new item appears in the review queue
      3. The item's format matches the tested format
      4. The item has non-empty content and a positive QA score
    """
    import main as main_mod
    from utils.context_loader import load_review_queue

    topic = _make_topic(fmt)
    queue_before_ids = {item["id"] for item in load_review_queue()}

    with (
        # Research returns a topic list; filter returns our topic dict
        patch.object(
            main_mod, "run_research",
            MagicMock(return_value={"topics": [{"title": topic["selected_topic"]}]}),
        ),
        patch.object(main_mod, "run_filter", MagicMock(return_value=topic)),
        # Skip non-generation stages
        patch.object(main_mod, "run_self_improve",    MagicMock()),
        patch.object(main_mod, "update_post_history", MagicMock()),
        patch.object(main_mod, "write_log",           MagicMock()),
        patch.object(main_mod, "get_calendar_entry_for_date", return_value=None),
        # Test this single format only — reduces runtime and isolates assertions
        patch.object(main_mod, "FORMATS", [fmt]),
        # No image generation — focus on text content quality
        patch.object(main_mod, "IMAGE_GENERATION_ENABLED", False),
        patch.object(main_mod, "IMAGE_TEMPLATE_ENABLED",   False),
        # Reddit is not yet in PLATFORM_MAP (Buffer profile pending).
        # Patch it in so the review queue test covers reddit content too.
        patch(
            "agents.publish.PLATFORM_MAP",
            {"linkedin": "linkedin", "carousel": "instagram",
             "twitter": "twitter", "reddit": "reddit"},
        ),
        # Mock all LLM calls — no API cost.
        # Patch each module's local import (from model_router import call_model)
        # not the model_router module itself, otherwise local refs are unaffected.
        patch("agents.generate.call_model",      side_effect=_mock_call_model_for_format(fmt)),
        patch("agents.qa.call_model",            side_effect=_mock_call_model_for_format(fmt)),
        patch("agents.template_engine.call_model", side_effect=_mock_call_model_for_format(fmt)),
        patch("time.sleep"),
    ):
        main_mod.main(forced_template_id=None)

    # ── Assert ────────────────────────────────────────────────────────────────
    queue_after = load_review_queue()
    new_items = [item for item in queue_after if item["id"] not in queue_before_ids]

    assert new_items, (
        f"No new queue items after running pipeline for format '{fmt}'. "
        "Check that QA passed and auto_publish is False."
    )

    # The item for our format should be there
    fmt_items = [item for item in new_items if item.get("format") == fmt]
    assert fmt_items, (
        f"No queue item with format='{fmt}' found among new items. "
        f"Formats present: {[i.get('format') for i in new_items]}"
    )

    item = fmt_items[0]

    assert item.get("status") == "pending_review", (
        f"Item {item['id']} status is {item.get('status')!r}, expected 'pending_review'"
    )
    assert item.get("content"), f"Item {item['id']} has empty content"
    assert item.get("score", 0) > 0, f"Item {item['id']} has zero/negative QA score"
    assert item.get("topic") == topic["selected_topic"], (
        f"Topic mismatch: {item.get('topic')!r} vs {topic['selected_topic']!r}"
    )

    print(
        f"\n  [PASS] [{fmt}] -> queue item {item['id']} "
        f"(score={item['score']}, platform={item.get('platform')})"
    )


@pytest.mark.parametrize("fmt", ALL_FORMATS)
def test_format_content_is_non_empty_and_parseable(fmt: str):
    """
    Content generated for each format must be parseable to extract
    the canonical display text (same logic as _clean_content_for_platform).

    This test calls run_generation directly — no queue write, pure unit test.
    """
    from agents.generate import _generate_one
    from agents.publish import _clean_content_for_platform

    topic = _make_topic(fmt)
    brand_context = "rkitect.ai — AI-powered architectural visualisation platform."

    with patch("agents.generate.call_model", side_effect=_mock_call_model_for_format(fmt)):
        _, raw_content = _generate_one(fmt, topic, brand_context)

    assert raw_content, f"_generate_one returned empty content for '{fmt}'"
    assert not raw_content.startswith("ERROR:"), (
        f"_generate_one returned an error for '{fmt}': {raw_content}"
    )

    # Clean and verify we get a non-empty display string
    cleaned = _clean_content_for_platform(raw_content, fmt=fmt)
    assert cleaned, f"_clean_content_for_platform returned empty string for '{fmt}'"

    # Format-specific checks
    if fmt == "twitter":
        # Twitter content should contain tweets joined with blank line
        assert len(cleaned) > 10, "Twitter content too short"
    elif fmt == "carousel":
        # Cleaned carousel content is the caption (no slide JSON)
        assert len(cleaned) > 5, "Carousel caption too short"
    elif fmt == "linkedin":
        assert "#" in cleaned or len(cleaned) > 50, "LinkedIn post too short"
    elif fmt == "reddit":
        # Reddit: title + body joined
        assert len(cleaned) > 20, "Reddit post too short"

    print(f"\n  [PASS] [{fmt}] content length={len(cleaned)} chars (preview: {cleaned[:60]!r}...)")
