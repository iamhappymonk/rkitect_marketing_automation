"""
TDD: Per-post feedback — enrich_skill_performance and enrich_post_history.

Tests are written BEFORE implementation. Run with:
  cd rkitect-pipeline && python -m pytest tests/test_per_post_feedback.py -v
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


# ── enrich_skill_performance ─────────────────────────────────────────────────

class TestEnrichSkillPerformance:
    def test_adds_human_feedback_to_latest_entry(self, tmp_path):
        """Adds human_feedback and feedback_at to the most recent format entry."""
        perf_log = {
            "linkedin": [
                {"date": "2026-05-24", "score": 85, "passed": True, "violations": []},
                {"date": "2026-05-25", "score": 87, "passed": True, "violations": []},
            ]
        }
        perf_file = tmp_path / "skill_performance.json"
        perf_file.write_text(json.dumps(perf_log))

        from agents.feedback import enrich_skill_performance
        enrich_skill_performance("linkedin", "too formal", perf_path=perf_file)

        updated = json.loads(perf_file.read_text())
        latest = updated["linkedin"][-1]
        assert latest["human_feedback"] == "too formal"
        assert "feedback_at" in latest

    def test_earlier_entries_not_modified(self, tmp_path):
        """Only the last entry gets human_feedback; earlier ones untouched."""
        perf_log = {
            "linkedin": [
                {"date": "2026-05-24", "score": 85, "passed": True, "violations": []},
                {"date": "2026-05-25", "score": 87, "passed": True, "violations": []},
            ]
        }
        perf_file = tmp_path / "skill_performance.json"
        perf_file.write_text(json.dumps(perf_log))

        from agents.feedback import enrich_skill_performance
        enrich_skill_performance("linkedin", "too formal", perf_path=perf_file)

        updated = json.loads(perf_file.read_text())
        first = updated["linkedin"][0]
        assert "human_feedback" not in first

    def test_creates_format_entry_if_missing(self, tmp_path):
        """If format absent from perf log, creates a synthetic entry with human_feedback."""
        perf_file = tmp_path / "skill_performance.json"
        perf_file.write_text("{}")

        from agents.feedback import enrich_skill_performance
        enrich_skill_performance("twitter", "too bland", perf_path=perf_file)

        updated = json.loads(perf_file.read_text())
        assert "twitter" in updated
        entry = updated["twitter"][-1]
        assert entry["human_feedback"] == "too bland"

    def test_missing_file_does_not_crash(self, tmp_path):
        """If perf file does not exist, function creates it gracefully."""
        perf_file = tmp_path / "nonexistent.json"

        from agents.feedback import enrich_skill_performance
        # Should not raise
        enrich_skill_performance("linkedin", "note", perf_path=perf_file)


# ── enrich_post_history ───────────────────────────────────────────────────────

class TestEnrichPostHistory:
    def test_appends_feedback_notes_by_topic(self, tmp_path):
        """Appends feedback_notes to the matching topic entry."""
        history = {
            "last_7_days": [
                {"date": "2026-05-25", "pillar": "edu", "topic": "test topic"}
            ]
        }
        hist_file = tmp_path / "post_history.json"
        hist_file.write_text(json.dumps(history))

        from agents.feedback import enrich_post_history
        enrich_post_history("test topic", "CTA weak", hist_path=hist_file)

        updated = json.loads(hist_file.read_text())
        entry = updated["last_7_days"][0]
        assert "feedback_notes" in entry
        assert "CTA weak" in entry["feedback_notes"]

    def test_appends_to_existing_feedback_notes(self, tmp_path):
        """Appends to an existing feedback_notes list, not overwriting."""
        history = {
            "last_7_days": [
                {
                    "date": "2026-05-25",
                    "pillar": "edu",
                    "topic": "test",
                    "feedback_notes": ["first note"],
                }
            ]
        }
        hist_file = tmp_path / "post_history.json"
        hist_file.write_text(json.dumps(history))

        from agents.feedback import enrich_post_history
        enrich_post_history("test", "second note", hist_path=hist_file)

        updated = json.loads(hist_file.read_text())
        assert updated["last_7_days"][0]["feedback_notes"] == ["first note", "second note"]

    def test_no_matching_topic_does_not_crash(self, tmp_path):
        """No match found → function completes without error, no data changed."""
        history = {"last_7_days": []}
        hist_file = tmp_path / "post_history.json"
        hist_file.write_text(json.dumps(history))

        from agents.feedback import enrich_post_history
        enrich_post_history("nonexistent topic", "note", hist_path=hist_file)

        updated = json.loads(hist_file.read_text())
        assert updated["last_7_days"] == []

    def test_missing_file_does_not_crash(self, tmp_path):
        """If post history file missing, function completes without error."""
        hist_file = tmp_path / "nonexistent.json"

        from agents.feedback import enrich_post_history
        # Should not raise
        enrich_post_history("some topic", "note", hist_path=hist_file)
