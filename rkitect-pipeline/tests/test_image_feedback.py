"""
TDD: Image feedback — enrich_image_feedback enriches template file +
template_renderer prompt + skill_performance.json from human image feedback.

Run with:
  cd rkitect-pipeline && python -m pytest tests/test_image_feedback.py -v
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def run_folder(tmp_path):
    """Simulate a pipeline output run folder with a template manifest."""
    folder = tmp_path / "output" / "2026-05-25" / "run_143022"
    folder.mkdir(parents=True)
    manifest = {
        "template_id": "property-showcase-instagram",
        "template_name": "Property Showcase — Instagram",
        "transition_direction": "left-to-right",
        "video_transition": "fade",
        "video_duration_hint": 4,
        "slides": ["slide_01.jpg", "slide_02.jpg"],
    }
    (folder / "template_manifest.json").write_text(json.dumps(manifest))
    (folder / "carousel.md").write_text("carousel content")
    return folder


@pytest.fixture
def template_file(tmp_path):
    """A minimal image template .md file."""
    tdir = tmp_path / "image_templates"
    tdir.mkdir()
    content = "---\nid: property-showcase-instagram\nname: Property Showcase\n---\n\n## Slide 1\n\n**Scene:** {hero}\n"
    f = tdir / "property-showcase-instagram.md"
    f.write_text(content)
    return f


@pytest.fixture
def renderer_prompt(tmp_path):
    """A minimal template_renderer prompt with Performance Notes section."""
    pdir = tmp_path / "prompts"
    pdir.mkdir()
    content = "You are the renderer.\n\n## Performance Notes\n\n<!-- Auto-updated -->\n\nLast updated: initial\n"
    f = pdir / "template_renderer.md"
    f.write_text(content)
    return f


@pytest.fixture
def versions_dir(tmp_path):
    """Prompts versions directory."""
    d = tmp_path / "prompts" / "versions"
    d.mkdir(parents=True)
    return d


# ── Tests: resolve_template_from_run_folder ───────────────────────────────────

class TestResolveTemplateFromRunFolder:
    def test_reads_manifest_and_returns_template_id(self, run_folder):
        from agents.feedback import resolve_template_from_item
        source_file = str(run_folder / "carousel.md")
        template_id = resolve_template_from_item(source_file=source_file)
        assert template_id == "property-showcase-instagram"

    def test_returns_none_when_no_manifest(self, tmp_path):
        from agents.feedback import resolve_template_from_item
        folder = tmp_path / "output" / "2026-05-25" / "run_999"
        folder.mkdir(parents=True)
        (folder / "carousel.md").write_text("content")
        result = resolve_template_from_item(source_file=str(folder / "carousel.md"))
        assert result is None

    def test_returns_none_when_no_source_file(self):
        from agents.feedback import resolve_template_from_item
        result = resolve_template_from_item(source_file="")
        assert result is None


# ── Tests: enrich_template_file ───────────────────────────────────────────────

class TestEnrichTemplateFile:
    def test_appends_feedback_section(self, template_file):
        from agents.feedback import enrich_template_file
        enrich_template_file(
            template_id="property-showcase-instagram",
            feedback="Slide 1 too dark. Needs brighter exterior lighting.",
            templates_dir=template_file.parent,
        )
        content = template_file.read_text()
        assert "## Feedback Log" in content
        assert "Slide 1 too dark" in content

    def test_appends_multiple_feedback_entries(self, template_file):
        from agents.feedback import enrich_template_file
        enrich_template_file("property-showcase-instagram", "first note", templates_dir=template_file.parent)
        enrich_template_file("property-showcase-instagram", "second note", templates_dir=template_file.parent)
        content = template_file.read_text()
        assert "first note" in content
        assert "second note" in content

    def test_no_crash_when_template_not_found(self, tmp_path):
        from agents.feedback import enrich_template_file
        enrich_template_file("nonexistent-template", "note", templates_dir=tmp_path)


# ── Tests: enrich_renderer_prompt ─────────────────────────────────────────────

class TestEnrichRendererPrompt:
    def test_appends_feedback_under_performance_notes(self, renderer_prompt, versions_dir):
        from agents.feedback import enrich_renderer_prompt
        enrich_renderer_prompt(
            template_id="property-showcase-instagram",
            feedback="Always use golden hour lighting for exterior shots.",
            prompts_dir=renderer_prompt.parent,
        )
        content = renderer_prompt.read_text()
        assert "golden hour lighting" in content
        assert "property-showcase-instagram" in content

    def test_saves_version_copy(self, renderer_prompt, versions_dir):
        from agents.feedback import enrich_renderer_prompt
        enrich_renderer_prompt(
            template_id="property-showcase-instagram",
            feedback="note",
            prompts_dir=renderer_prompt.parent,
        )
        version_files = list(versions_dir.glob("template_renderer_*.md"))
        assert len(version_files) >= 1

    def test_no_crash_when_prompt_missing(self, tmp_path):
        from agents.feedback import enrich_renderer_prompt
        enrich_renderer_prompt("template-id", "note", prompts_dir=tmp_path)


# ── Tests: full enrich_image_feedback flow ────────────────────────────────────

class TestEnrichImageFeedback:
    def test_full_flow_enriches_all_artifacts(
        self, run_folder, template_file, renderer_prompt, versions_dir, tmp_path
    ):
        perf_file = tmp_path / "skill_performance.json"
        perf_file.write_text(json.dumps({"carousel": [
            {"date": "2026-05-25", "score": 80, "passed": True, "violations": []}
        ]}))

        from agents.feedback import enrich_image_feedback
        result = enrich_image_feedback(
            source_file=str(run_folder / "carousel.md"),
            feedback="Too dark. More natural light please.",
            templates_dir=template_file.parent,
            prompts_dir=renderer_prompt.parent,
            perf_path=perf_file,
        )

        assert result["template_updated"] is True
        assert result["renderer_updated"] is True
        assert result["perf_updated"] is True
        assert result["template_id"] == "property-showcase-instagram"

        # Template file enriched
        assert "Too dark" in template_file.read_text()
        # Renderer enriched
        assert "Too dark" in renderer_prompt.read_text()
        # Perf log enriched
        perf = json.loads(perf_file.read_text())
        assert perf["carousel"][-1].get("image_human_feedback") == "Too dark. More natural light please."

    def test_graceful_when_no_manifest(self, tmp_path):
        """No manifest → returns partial result, no crash."""
        folder = tmp_path / "run"
        folder.mkdir()
        (folder / "carousel.md").write_text("x")

        from agents.feedback import enrich_image_feedback
        result = enrich_image_feedback(
            source_file=str(folder / "carousel.md"),
            feedback="note",
            templates_dir=tmp_path,
            prompts_dir=tmp_path,
            perf_path=tmp_path / "nonexistent.json",
        )
        assert result["template_id"] is None
        assert result["template_updated"] is False
