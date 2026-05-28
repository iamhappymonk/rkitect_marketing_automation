"""
TDD: Template fast path — skip research + filter when forced_template_id is set.

When main() is called with a forced_template_id the pipeline must:
  1. Not call run_research (saves search API credits)
  2. Not call run_filter  (saves LLM tokens)
  3. Produce a valid topic dict with at least selected_topic, pillar, angle
  4. If a calendar entry exists for today, use it for the topic details
  5. If no calendar entry, derive a friendly topic from the template id
  6. Log stages.research.skipped == True
  7. Log stages.filter.skipped  == True
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


# ─── Shared mock helpers ─────────────────────────────────────────────────────

def _minimal_generated():
    """Minimal generated dict that passes downstream validation."""
    return {
        "linkedin": "LinkedIn content",
        "carousel": '{"caption": "Test caption", "slides": []}',
        "twitter": '{"tweets": ["tweet 1"]}',
        "reddit": "Reddit post",
    }


def _minimal_qa_results():
    return {
        "linkedin":  {"score": 85, "passed": True,  "content": "LinkedIn content"},
        "carousel":  {"score": 85, "passed": True,  "content": '{"caption":"c","slides":[]}'},
        "twitter":   {"score": 85, "passed": True,  "content": '{"tweets":["t"]}'},
        "reddit":    {"score": 85, "passed": True,  "content": "Reddit post"},
    }


def _all_stage_patches(main_mod, tmp_path, *, calendar_entry=None,
                       extra_patches=None) -> list:
    """Return the full list of patches needed to run main() without real I/O."""
    patches = [
        patch.object(main_mod, "run_research",    MagicMock(return_value={"topics": []})),
        patch.object(main_mod, "run_filter",       MagicMock(return_value={})),
        patch.object(main_mod, "run_generation",   MagicMock(return_value=_minimal_generated())),
        patch.object(main_mod, "run_qa",           MagicMock(return_value=_minimal_qa_results())),
        patch.object(main_mod, "run_publish",      MagicMock(return_value={})),
        patch.object(main_mod, "run_self_improve", MagicMock()),
        patch.object(main_mod, "update_post_history", MagicMock()),
        patch.object(main_mod, "write_log",        MagicMock()),
        patch.object(main_mod, "load_brand_context", MagicMock(return_value={})),
        patch.object(main_mod, "IMAGE_TEMPLATE_ENABLED",  True),
        patch.object(main_mod, "IMAGE_GENERATION_ENABLED", False),   # skip image gen stages
        patch.object(main_mod, "OUTPUT_DIR",  tmp_path),
        patch.object(main_mod, "LOGS_DIR",    tmp_path / "logs"),
        patch.object(main_mod, "FORMATS",     ["linkedin", "carousel"]),
        patch.object(main_mod, "get_calendar_entry_for_date", return_value=calendar_entry),
        patch("agents.template_engine.load_templates", return_value=[]),
    ]
    if extra_patches:
        patches.extend(extra_patches)
    return patches


# ─── Tests ──────────────────────────────────────────────────────────────────

def test_research_not_called_when_template_forced(tmp_path):
    """run_research must NOT be called when forced_template_id is provided."""
    import main as main_mod

    mock_research = MagicMock(return_value={"topics": []})
    mock_filter   = MagicMock(return_value={})

    with (
        patch.object(main_mod, "run_research",        mock_research),
        patch.object(main_mod, "run_filter",           mock_filter),
        patch.object(main_mod, "run_generation",       MagicMock(return_value=_minimal_generated())),
        patch.object(main_mod, "run_qa",               MagicMock(return_value=_minimal_qa_results())),
        patch.object(main_mod, "run_publish",          MagicMock(return_value={})),
        patch.object(main_mod, "run_self_improve",     MagicMock()),
        patch.object(main_mod, "update_post_history",  MagicMock()),
        patch.object(main_mod, "write_log",            MagicMock()),
        patch.object(main_mod, "IMAGE_TEMPLATE_ENABLED",  True),
        patch.object(main_mod, "IMAGE_GENERATION_ENABLED", False),
        patch.object(main_mod, "OUTPUT_DIR",  tmp_path),
        patch.object(main_mod, "LOGS_DIR",    tmp_path / "logs"),
        patch.object(main_mod, "FORMATS",     ["linkedin", "carousel"]),
        patch.object(main_mod, "get_calendar_entry_for_date", return_value=None),
        patch("agents.template_engine.load_templates", return_value=[]),
    ):
        main_mod.main(forced_template_id="room-style-variants-carousel")

    mock_research.assert_not_called()


def test_filter_not_called_when_template_forced(tmp_path):
    """run_filter must NOT be called when forced_template_id is provided."""
    import main as main_mod

    mock_research = MagicMock(return_value={"topics": []})
    mock_filter   = MagicMock(return_value={})

    with (
        patch.object(main_mod, "run_research",        mock_research),
        patch.object(main_mod, "run_filter",           mock_filter),
        patch.object(main_mod, "run_generation",       MagicMock(return_value=_minimal_generated())),
        patch.object(main_mod, "run_qa",               MagicMock(return_value=_minimal_qa_results())),
        patch.object(main_mod, "run_publish",          MagicMock(return_value={})),
        patch.object(main_mod, "run_self_improve",     MagicMock()),
        patch.object(main_mod, "update_post_history",  MagicMock()),
        patch.object(main_mod, "write_log",            MagicMock()),
        patch.object(main_mod, "IMAGE_TEMPLATE_ENABLED",  True),
        patch.object(main_mod, "IMAGE_GENERATION_ENABLED", False),
        patch.object(main_mod, "OUTPUT_DIR",  tmp_path),
        patch.object(main_mod, "LOGS_DIR",    tmp_path / "logs"),
        patch.object(main_mod, "FORMATS",     ["linkedin", "carousel"]),
        patch.object(main_mod, "get_calendar_entry_for_date", return_value=None),
        patch("agents.template_engine.load_templates", return_value=[]),
    ):
        main_mod.main(forced_template_id="room-style-variants-carousel")

    mock_filter.assert_not_called()


def test_topic_dict_has_required_keys_no_calendar(tmp_path):
    """With no calendar entry, topic passed to run_generation has selected_topic, pillar, angle."""
    import main as main_mod

    captured_topic: dict = {}

    def _capture(topic, **kwargs):
        captured_topic.update(topic)
        return _minimal_generated()

    with (
        patch.object(main_mod, "run_research",        MagicMock(return_value={"topics": []})),
        patch.object(main_mod, "run_filter",           MagicMock(return_value={})),
        patch.object(main_mod, "run_generation",       _capture),
        patch.object(main_mod, "run_qa",               MagicMock(return_value=_minimal_qa_results())),
        patch.object(main_mod, "run_publish",          MagicMock(return_value={})),
        patch.object(main_mod, "run_self_improve",     MagicMock()),
        patch.object(main_mod, "update_post_history",  MagicMock()),
        patch.object(main_mod, "write_log",            MagicMock()),
        patch.object(main_mod, "IMAGE_TEMPLATE_ENABLED",  True),
        patch.object(main_mod, "IMAGE_GENERATION_ENABLED", False),
        patch.object(main_mod, "OUTPUT_DIR",  tmp_path),
        patch.object(main_mod, "LOGS_DIR",    tmp_path / "logs"),
        patch.object(main_mod, "FORMATS",     ["linkedin", "carousel"]),
        patch.object(main_mod, "get_calendar_entry_for_date", return_value=None),
        patch("agents.template_engine.load_templates", return_value=[]),
    ):
        main_mod.main(forced_template_id="room-style-variants-carousel")

    assert "selected_topic" in captured_topic, "topic must have selected_topic"
    assert "pillar"          in captured_topic, "topic must have pillar"
    assert "angle"           in captured_topic, "topic must have angle"
    assert captured_topic["selected_topic"],    "selected_topic must not be empty"


def test_topic_derived_from_template_id_when_no_calendar(tmp_path):
    """selected_topic is a human-readable form of the template id — no raw dashes."""
    import main as main_mod

    captured_topic: dict = {}

    def _capture(topic, **kwargs):
        captured_topic.update(topic)
        return _minimal_generated()

    with (
        patch.object(main_mod, "run_research",        MagicMock(return_value={"topics": []})),
        patch.object(main_mod, "run_filter",           MagicMock(return_value={})),
        patch.object(main_mod, "run_generation",       _capture),
        patch.object(main_mod, "run_qa",               MagicMock(return_value=_minimal_qa_results())),
        patch.object(main_mod, "run_publish",          MagicMock(return_value={})),
        patch.object(main_mod, "run_self_improve",     MagicMock()),
        patch.object(main_mod, "update_post_history",  MagicMock()),
        patch.object(main_mod, "write_log",            MagicMock()),
        patch.object(main_mod, "IMAGE_TEMPLATE_ENABLED",  True),
        patch.object(main_mod, "IMAGE_GENERATION_ENABLED", False),
        patch.object(main_mod, "OUTPUT_DIR",  tmp_path),
        patch.object(main_mod, "LOGS_DIR",    tmp_path / "logs"),
        patch.object(main_mod, "FORMATS",     ["linkedin", "carousel"]),
        patch.object(main_mod, "get_calendar_entry_for_date", return_value=None),
        patch("agents.template_engine.load_templates", return_value=[]),
    ):
        main_mod.main(forced_template_id="floorplan-2d-to-3d")

    assert "-" not in captured_topic["selected_topic"], (
        f"selected_topic should be human-readable, got: {captured_topic['selected_topic']!r}"
    )


def test_calendar_entry_used_when_available(tmp_path):
    """If a calendar entry exists for today, its topic/pillar/angle are used."""
    import main as main_mod

    fake_calendar = {
        "topic": "Living Room Transformation Case Study",
        "pillar": "portfolio",
        "angle": "before-after reveal",
    }
    captured_topic: dict = {}

    def _capture(topic, **kwargs):
        captured_topic.update(topic)
        return _minimal_generated()

    with (
        patch.object(main_mod, "run_research",        MagicMock(return_value={"topics": []})),
        patch.object(main_mod, "run_filter",           MagicMock(return_value={})),
        patch.object(main_mod, "run_generation",       _capture),
        patch.object(main_mod, "run_qa",               MagicMock(return_value=_minimal_qa_results())),
        patch.object(main_mod, "run_publish",          MagicMock(return_value={})),
        patch.object(main_mod, "run_self_improve",     MagicMock()),
        patch.object(main_mod, "update_post_history",  MagicMock()),
        patch.object(main_mod, "write_log",            MagicMock()),
        patch.object(main_mod, "IMAGE_TEMPLATE_ENABLED",  True),
        patch.object(main_mod, "IMAGE_GENERATION_ENABLED", False),
        patch.object(main_mod, "OUTPUT_DIR",  tmp_path),
        patch.object(main_mod, "LOGS_DIR",    tmp_path / "logs"),
        patch.object(main_mod, "FORMATS",     ["linkedin", "carousel"]),
        patch.object(main_mod, "get_calendar_entry_for_date", return_value=fake_calendar),
        patch("agents.template_engine.load_templates", return_value=[]),
    ):
        main_mod.main(forced_template_id="room-style-variants-carousel")

    assert captured_topic["selected_topic"] == "Living Room Transformation Case Study"
    assert captured_topic["pillar"]          == "portfolio"
    assert captured_topic["angle"]           == "before-after reveal"


def test_run_log_marks_stages_skipped(tmp_path):
    """run_log stages.research and stages.filter must have skipped=True."""
    import main as main_mod

    logged: list[dict] = []

    def _capture_log(run_log):
        logged.append(run_log)

    with (
        patch.object(main_mod, "run_research",        MagicMock(return_value={"topics": []})),
        patch.object(main_mod, "run_filter",           MagicMock(return_value={})),
        patch.object(main_mod, "run_generation",       MagicMock(return_value=_minimal_generated())),
        patch.object(main_mod, "run_qa",               MagicMock(return_value=_minimal_qa_results())),
        patch.object(main_mod, "run_publish",          MagicMock(return_value={})),
        patch.object(main_mod, "run_self_improve",     MagicMock()),
        patch.object(main_mod, "update_post_history",  MagicMock()),
        patch.object(main_mod, "write_log",            _capture_log),
        patch.object(main_mod, "IMAGE_TEMPLATE_ENABLED",  True),
        patch.object(main_mod, "IMAGE_GENERATION_ENABLED", False),
        patch.object(main_mod, "OUTPUT_DIR",  tmp_path),
        patch.object(main_mod, "LOGS_DIR",    tmp_path / "logs"),
        patch.object(main_mod, "FORMATS",     ["linkedin", "carousel"]),
        patch.object(main_mod, "get_calendar_entry_for_date", return_value=None),
        patch("agents.template_engine.load_templates", return_value=[]),
    ):
        main_mod.main(forced_template_id="room-style-variants-carousel")

    assert logged, "write_log must have been called"
    log = logged[0]
    assert log["stages"]["research"].get("skipped") is True, "research stage must be logged as skipped"
    assert log["stages"]["filter"].get("skipped")   is True, "filter stage must be logged as skipped"


def test_normal_run_still_calls_research_and_filter(tmp_path):
    """Without forced_template_id, stages 1 and 2 still execute normally."""
    import main as main_mod

    mock_research = MagicMock(return_value={"topics": [{"title": "T1"}]})
    mock_filter   = MagicMock(return_value={
        "selected_topic": "T1", "pillar": "education", "angle": ""
    })

    with (
        patch.object(main_mod, "run_research",        mock_research),
        patch.object(main_mod, "run_filter",           mock_filter),
        patch.object(main_mod, "run_generation",       MagicMock(return_value=_minimal_generated())),
        patch.object(main_mod, "run_qa",               MagicMock(return_value=_minimal_qa_results())),
        patch.object(main_mod, "run_publish",          MagicMock(return_value={})),
        patch.object(main_mod, "run_self_improve",     MagicMock()),
        patch.object(main_mod, "update_post_history",  MagicMock()),
        patch.object(main_mod, "write_log",            MagicMock()),
        patch.object(main_mod, "IMAGE_TEMPLATE_ENABLED",  False),
        patch.object(main_mod, "IMAGE_GENERATION_ENABLED", False),
        patch.object(main_mod, "OUTPUT_DIR",  tmp_path),
        patch.object(main_mod, "LOGS_DIR",    tmp_path / "logs"),
        patch.object(main_mod, "FORMATS",     ["linkedin", "carousel"]),
        patch.object(main_mod, "get_calendar_entry_for_date", return_value=None),
    ):
        main_mod.main(forced_template_id=None)

    mock_research.assert_called_once()
    mock_filter.assert_called_once()
