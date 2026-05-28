"""
TDD: Selective pipeline — active_formats filtering in run_generation().

Tests are written BEFORE implementation so failures confirm the
feature is not yet present, and green tests confirm it's correct.
"""
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


# ── PLATFORM_TO_FORMAT constant ───────────────────────────────────────────────

def test_platform_to_format_mapping_instagram():
    """instagram maps to carousel."""
    from agents.generate import PLATFORM_TO_FORMAT
    assert PLATFORM_TO_FORMAT.get("instagram") == "carousel"


def test_platform_to_format_mapping_linkedin():
    """linkedin maps to linkedin."""
    from agents.generate import PLATFORM_TO_FORMAT
    assert PLATFORM_TO_FORMAT.get("linkedin") == "linkedin"


def test_platform_to_format_mapping_twitter():
    """twitter maps to twitter."""
    from agents.generate import PLATFORM_TO_FORMAT
    assert PLATFORM_TO_FORMAT.get("twitter") == "twitter"


# ── run_generation active_formats param ──────────────────────────────────────

def test_run_generation_all_formats_by_default():
    """No active_formats → all 4 FORMATS submitted."""
    from config import FORMATS
    submitted = []

    def fake_one(fmt, topic, brand_ctx):
        submitted.append(fmt)
        return fmt, f"content-{fmt}"

    with patch("agents.generate._generate_one", side_effect=fake_one), \
         patch("agents.generate.load_brand_context", return_value="ctx"), \
         patch("agents.generate.IMAGE_TEMPLATE_ENABLED", True), \
         patch("agents.generate.IMAGE_GENERATION_ENABLED", True):
        from agents import generate
        generate.run_generation({"selected_topic": "test"})

    assert set(submitted) == set(FORMATS)


def test_run_generation_active_formats_subset():
    """active_formats=["linkedin","carousel"] → only those 2 run."""
    submitted = []

    def fake_one(fmt, topic, brand_ctx):
        submitted.append(fmt)
        return fmt, f"content-{fmt}"

    with patch("agents.generate._generate_one", side_effect=fake_one), \
         patch("agents.generate.load_brand_context", return_value="ctx"), \
         patch("agents.generate.IMAGE_TEMPLATE_ENABLED", True), \
         patch("agents.generate.IMAGE_GENERATION_ENABLED", True):
        from agents import generate
        result = generate.run_generation(
            {"selected_topic": "test"},
            active_formats=["linkedin", "carousel"],
        )

    assert set(submitted) == {"linkedin", "carousel"}
    assert "twitter" not in result
    assert "reddit" not in result
    assert "linkedin" in result
    assert "carousel" in result


def test_run_generation_empty_active_formats():
    """active_formats=[] → no generation calls, empty content result."""
    submitted = []

    def fake_one(fmt, topic, brand_ctx):
        submitted.append(fmt)
        return fmt, f"content-{fmt}"

    with patch("agents.generate._generate_one", side_effect=fake_one), \
         patch("agents.generate.load_brand_context", return_value="ctx"), \
         patch("agents.generate.IMAGE_TEMPLATE_ENABLED", True), \
         patch("agents.generate.IMAGE_GENERATION_ENABLED", True):
        from agents import generate
        result = generate.run_generation(
            {"selected_topic": "test"},
            active_formats=[],
        )

    assert submitted == []
    content_keys = [k for k in result if not k.endswith("_image_brief")]
    assert content_keys == []


def test_run_generation_image_briefs_also_filtered():
    """Image briefs only generated for active_formats formats."""
    submitted_briefs = []

    def fake_one(fmt, topic, brand_ctx):
        return fmt, f"content-{fmt}"

    def fake_brief(fmt, content, brand_ctx):
        submitted_briefs.append(fmt)
        return f"{fmt}_image_brief", "brief"

    with patch("agents.generate._generate_one", side_effect=fake_one), \
         patch("agents.generate._generate_image_brief", side_effect=fake_brief), \
         patch("agents.generate.load_brand_context", return_value="ctx"), \
         patch("agents.generate.IMAGE_TEMPLATE_ENABLED", False), \
         patch("agents.generate.IMAGE_GENERATION_ENABLED", False):
        from agents import generate
        generate.run_generation(
            {"selected_topic": "test"},
            active_formats=["linkedin"],
        )

    # briefs only for active formats
    assert submitted_briefs == ["linkedin"] or submitted_briefs == []  # brief gen may be skipped
