"""
Integration tests — Image Template Pipeline

Runs the full pipeline for each image template and writes results to the
REAL review queue so they appear in the dashboard for human review.

LLM calls and image generation are mocked (no API cost).
Research, filter, self-improve, and post-history writes are also mocked.
The publish queue, OUTPUT_DIR, and QA logic run for real.

Run:
    cd rkitect-pipeline
    python -m pytest tests/test_template_integration.py -v
"""
from __future__ import annotations

import base64
import io
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure rkitect-pipeline is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# ── Template IDs (one test per template) ─────────────────────────────────────

ALL_TEMPLATES = [
    "sketch-to-render-3step",
    "property-showcase-twitter-linkedin",
    "property-showcase-instagram",
    "floorplan-2d-to-3d",
    "room-style-variants-carousel",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _tiny_jpeg_b64_uri() -> str:
    """Create a tiny 4×4 JPEG and return it as a base64 data URI."""
    try:
        from PIL import Image as PILImage
        buf = io.BytesIO()
        PILImage.new("RGB", (4, 4), color=(80, 100, 120)).save(buf, format="JPEG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        return f"data:image/jpeg;base64,{b64}"
    except ImportError:
        # Minimal valid 1×1 JPEG (no PIL needed)
        raw = (
            b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
            b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t'
            b'\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a'
            b'\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\x1e'
            b'\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00'
            b'\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00'
            b'\x08\x01\x01\x00\x00?\x00\xfb\xd5\xa5\x14Q@\x1f\xff\xd9'
        )
        return "data:image/jpeg;base64," + base64.b64encode(raw).decode()


def _mock_call_model(task: str, system: str, user: str, **kwargs) -> str:
    """
    Smart call_model mock — returns valid JSON for every pipeline task.

    Keyed on 'task' (same arg name as model_router.call_model's first param).
    """
    import re as _re

    if task == "qa":
        return json.dumps({
            "score": 88,
            "passed": True,
            "critique": "Test content — pipeline integration test",
        })

    elif task == "template_renderer":
        # Parse expected slide count from the user prompt so every template
        # gets the exact number it requires (avoids slide-count mismatch fallback).
        match = _re.search(r"slide_count:\s*(\d+)", user)
        n_slides = int(match.group(1)) if match else 3

        slides = [
            {
                "slide": i + 1,
                "prompt": (
                    f"Architectural scene {i + 1}: photorealistic render of an "
                    f"interior space, natural light, no people, no text."
                ),
                "color_palette": "warm neutrals, cream #F5F1ED, concrete grey #A89A8D",
                "mood": "inspirational",
                "dimensions": "1080x1350",
                "style": "architectural",
            }
            for i in range(n_slides)
        ]

        # Works for BOTH custom (room-style-variants) and generic renderers.
        # room-style-variants reads: room_base_scene, room_type
        # Generic renderers read:   spatial_anchor, carousel_slides
        return json.dumps({
            "room_base_scene": (
                "A sunlit open-plan living room with 3 m ceilings, "
                "floor-to-ceiling glazing on the south wall, and polished "
                "concrete floors — an ideal canvas for style exploration."
            ),
            "room_type": "living room",
            "spatial_anchor": (
                "South-facing penthouse apartment, corner unit, 180-degree city view, "
                "double-height ceilings with exposed steel truss."
            ),
            "carousel_slides": slides,
        })

    elif task == "carousel":
        return json.dumps({
            "caption": (
                "AI-powered architectural visualization changes everything. "
                "See your space before it's built. #rkitect #architecture"
            ),
            "slides": [
                {
                    "slide": 1,
                    "headline": "Before",
                    "visual_description": "Empty shell of a room",
                },
                {
                    "slide": 2,
                    "headline": "Design",
                    "visual_description": "Architect reviewing AI renders",
                },
                {
                    "slide": 3,
                    "headline": "After",
                    "visual_description": "Completed space matching the vision",
                },
            ],
        })

    elif task == "linkedin":
        return json.dumps({
            "post": (
                "Architecture is the thoughtful making of space.\n\n"
                "At rkitect.ai we make that transformation accessible to every "
                "studio — from first sketch to photorealistic render in minutes.\n\n"
                "#architecture #design #AI"
            )
        })

    elif task == "twitter":
        return json.dumps({
            "tweets": [
                "Architecture is the art of how to waste space — said no AI tool ever. "
                "rkitect.ai visualises your vision before ground breaks. #arch #AI",
                "From concept sketch to photorealistic render in under 5 minutes. "
                "Try rkitect.ai free.",
            ]
        })

    elif task == "reddit":
        return json.dumps({
            "title": "How AI architectural visualisation changed my studio's workflow (3-month review)",
            "body": (
                "I've been using rkitect.ai for 3 months and the productivity shift "
                "is real. Client approvals went from weeks to days because they can "
                "actually *see* the space before construction begins.\n\n"
                "Happy to answer any questions."
            ),
        })

    # Fallback for any other task (self_improve, filter, etc.)
    return json.dumps({"result": "ok", "score": 85, "passed": True})


# ── Parametrized test ─────────────────────────────────────────────────────────

@pytest.mark.parametrize("template_id", ALL_TEMPLATES)
def test_template_runs_and_lands_in_queue(template_id: str):
    """
    Each template must:
      1. Run the full pipeline without raising an exception
      2. Produce at least one new item in the review queue
      3. Have template_meta.template_id matching the forced template
      4. Have status = "pending_review"
    """
    import main as main_mod
    from utils.context_loader import load_review_queue

    tiny_jpeg = _tiny_jpeg_b64_uri()

    # Snapshot queue IDs before the run so we can diff afterwards
    queue_before_ids = {item["id"] for item in load_review_queue()}

    with (
        # Skip expensive stages
        patch.object(main_mod, "run_research",    MagicMock(return_value={"topics": []})),
        patch.object(main_mod, "run_filter",       MagicMock(return_value={})),
        patch.object(main_mod, "run_self_improve", MagicMock()),
        patch.object(main_mod, "update_post_history", MagicMock()),
        patch.object(main_mod, "write_log",        MagicMock()),
        patch.object(main_mod, "get_calendar_entry_for_date", return_value=None),
        # Enable template + image generation (so we test the real flow)
        patch.object(main_mod, "IMAGE_GENERATION_ENABLED", True),
        patch.object(main_mod, "IMAGE_TEMPLATE_ENABLED",   True),
        # Mock all LLM calls — no API cost.
        # Patch each module's local import (from model_router import call_model).
        patch("agents.generate.call_model",       side_effect=_mock_call_model),
        patch("agents.qa.call_model",             side_effect=_mock_call_model),
        patch("agents.template_engine.call_model", side_effect=_mock_call_model),
        # Mock image generation — return tiny JPEG as base64 data URI
        patch(
            "agents.image_generator._generate_openrouter_image",
            return_value=tiny_jpeg,
        ),
        # Skip compositor (uses PIL compositing, fine to mock for queue test)
        patch("agents.compositor.run_compositor", return_value={}),
        # Skip video assembly (FFmpeg not guaranteed in CI)
        patch("agents.video_assembler.run_video_assembly", return_value=None),
        # Skip video prompt writer
        patch("agents.video_prompt_writer.run_video_prompt_writer", return_value=None),
        # Skip sleep delays between image API calls
        patch("time.sleep"),
    ):
        main_mod.main(forced_template_id=template_id)

    # ── Assert ────────────────────────────────────────────────────────────────
    queue_after = load_review_queue()
    new_items = [item for item in queue_after if item["id"] not in queue_before_ids]

    assert new_items, (
        f"No new review queue items created for template '{template_id}'. "
        "Check that at least one format passed QA."
    )

    # At least one item should carry the template_meta
    template_items = [
        item for item in new_items
        if item.get("template_meta")
        and item["template_meta"].get("template_id") == template_id
    ]
    assert template_items, (
        f"No queue items carry template_meta.template_id='{template_id}'.\n"
        f"New items template_meta: {[i.get('template_meta') for i in new_items]}"
    )

    # Structural checks on each new item
    for item in new_items:
        assert item.get("status") == "pending_review", (
            f"Item {item['id']} has wrong status: {item.get('status')!r}"
        )
        assert item.get("content"), f"Item {item['id']} has empty content"
        assert item.get("format") in ("linkedin", "carousel", "twitter", "reddit"), (
            f"Item {item['id']} has unexpected format: {item.get('format')!r}"
        )
        assert item.get("score", 0) >= 0, f"Item {item['id']} has negative score"

    print(
        f"\n  [PASS] [{template_id}] -> {len(new_items)} item(s) in review queue: "
        + ", ".join(i["id"] for i in new_items)
    )
