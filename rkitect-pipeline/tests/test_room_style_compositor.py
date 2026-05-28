"""
TDD: room-style-variants-carousel compositor.

Tests verify:
  1. Template renderer custom path picks 4 styles, produces 4 image-gen briefs
  2. Compositor builds 2x2 collage with style labels in each quadrant
  3. Compositor applies corner tag to each individual slide
  4. Compositor builds CTA slide with overlay + text
  5. Final output has 6 slides in correct order
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent))


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_solid_image(path: str, color=(180, 120, 60), size=(200, 250)) -> str:
    """Write a solid-color JPEG to disk, return path."""
    img = Image.new("RGB", size, color)
    img.save(path, "JPEG")
    return path


def _make_template_meta(style_labels=None, cta_config=None, compositor_mode="room-style-variants-carousel"):
    return {
        "template_id": "room-style-variants-carousel",
        "compositor_mode": compositor_mode,
        "style_labels": style_labels or ["WABI-SABI", "SCANDINAVIAN", "ART DECO", "MOROCCAN RIAD"],
        "styles": ["Japanese Wabi-Sabi", "Scandinavian Minimal", "Art Deco Luxury", "Moroccan Riad"],
        "cta_config": cta_config or {
            "headline": "ONE ROOM. INFINITE STYLES.",
            "subline": "Follow for weekly architecture drops.",
            "handle": "rkitect.ai",
        },
    }


# ── Template engine: custom renderer path ─────────────────────────────────────

def test_room_style_renderer_returns_4_image_gen_briefs():
    """Custom renderer produces exactly 4 briefs — one per style variant (not 6)."""
    template = {
        "meta": {
            "id": "room-style-variants-carousel",
            "slide_count": 6,
            "image_size": "1080x1350",
            "style_pool": ["Wabi-Sabi", "Scandinavian", "Art Deco", "Moroccan", "Brutalist", "Tropical"],
            "style_pick_count": 4,
            "compatible_platforms": ["instagram", "linkedin"],
            "transition_direction": "left-to-right",
            "video_transition": "wipe",
            "video_duration_hint": 3,
        },
        "body": "",
    }
    topic = {"selected_topic": "open-plan living", "pillar": "inspiration"}

    with patch("model_router.call_model", return_value=json.dumps({
        "room_base_scene": "A contemporary open-plan living room with staircase and floor-to-ceiling windows.",
        "room_type": "living room",
    })):
        from agents.template_engine import _render_room_style_variants
        result = _render_room_style_variants(template, topic, "brand ctx")

    assert "carousel_image_brief" in result
    slides = json.loads(result["carousel_image_brief"])
    assert len(slides) == 4, f"Expected 4 slides, got {len(slides)}"


def test_room_style_renderer_picks_unique_styles():
    """4 styles picked are all distinct and come from style_pool."""
    template = {
        "meta": {
            "id": "room-style-variants-carousel",
            "slide_count": 6,
            "image_size": "1080x1350",
            "style_pool": ["A", "B", "C", "D", "E", "F"],
            "style_pick_count": 4,
            "compatible_platforms": ["instagram"],
        },
        "body": "",
    }
    topic = {"selected_topic": "minimal homes", "pillar": "inspiration"}

    with patch("model_router.call_model", return_value='{"room_base_scene": "A minimal loft.", "room_type": "loft"}'):
        from agents.template_engine import _render_room_style_variants
        result = _render_room_style_variants(template, topic, "ctx")

    slides = json.loads(result["carousel_image_brief"])
    style_names = [s["style_name"] for s in slides]
    assert len(set(style_names)) == 4, f"Expected 4 unique styles, got: {style_names}"
    for s in style_names:
        assert s in template["meta"]["style_pool"], f"{s} not in pool"


def test_room_style_renderer_template_meta_has_compositor_mode():
    """_template_meta includes compositor_mode = 'room-style-variants-carousel'."""
    template = {
        "meta": {
            "id": "room-style-variants-carousel",
            "slide_count": 6,
            "image_size": "1080x1350",
            "style_pool": ["Wabi-Sabi", "Scandinavian", "Art Deco", "Moroccan"],
            "style_pick_count": 4,
            "compatible_platforms": ["instagram"],
            "video_transition": "wipe",
            "transition_direction": "left-to-right",
            "video_duration_hint": 3,
        },
        "body": "",
    }
    topic = {"selected_topic": "cozy studios", "pillar": "inspiration"}

    with patch("model_router.call_model", return_value='{"room_base_scene": "A cozy studio.", "room_type": "studio"}'):
        from agents.template_engine import _render_room_style_variants
        result = _render_room_style_variants(template, topic, "ctx")

    meta = result.get("_template_meta", {})
    assert meta.get("compositor_mode") == "room-style-variants-carousel"
    assert len(meta.get("style_labels", [])) == 4
    assert "cta_config" in meta


def test_room_style_renderer_bypassed_via_render_template_briefs():
    """render_template_briefs uses custom path when template_id is room-style-variants-carousel."""
    template = {
        "meta": {
            "id": "room-style-variants-carousel",
            "slide_count": 6,
            "image_size": "1080x1350",
            "style_pool": ["Wabi-Sabi", "Scandinavian", "Art Deco", "Moroccan"],
            "style_pick_count": 4,
            "compatible_platforms": ["instagram"],
        },
        "body": "some body",
    }
    topic = {"selected_topic": "test topic", "pillar": "inspiration"}

    with patch("model_router.call_model", return_value='{"room_base_scene": "A room.", "room_type": "living room"}'):
        from agents.template_engine import render_template_briefs
        result = render_template_briefs(template, topic, "ctx")

    # Should have 4 slides — NOT 6
    slides = json.loads(result.get("carousel_image_brief", "[]"))
    assert len(slides) == 4


# ── Compositor: apply_style_tag ───────────────────────────────────────────────

def test_apply_style_tag_produces_same_size_image(tmp_path):
    """Tagged image has same dimensions as source."""
    src = _make_solid_image(str(tmp_path / "src.jpg"), size=(540, 675))
    out = str(tmp_path / "tagged.jpg")

    from agents.compositor import apply_style_tag
    apply_style_tag(src, "WABI-SABI", out)

    result = Image.open(out)
    assert result.size == (540, 675)


def test_apply_style_tag_creates_output_file(tmp_path):
    """apply_style_tag writes the output file."""
    src = _make_solid_image(str(tmp_path / "src.jpg"))
    out = str(tmp_path / "tagged.jpg")

    from agents.compositor import apply_style_tag
    apply_style_tag(src, "SCANDINAVIAN", out)

    assert Path(out).exists()


# ── Compositor: build_collage_2x2 ────────────────────────────────────────────

def test_collage_2x2_output_size(tmp_path):
    """2x2 collage is exactly 1080x1350px."""
    slides = [
        _make_solid_image(str(tmp_path / f"s{i}.jpg"), color=(i*50, 100, 200), size=(540, 675))
        for i in range(4)
    ]
    out = str(tmp_path / "collage.jpg")

    from agents.compositor import build_collage_2x2
    build_collage_2x2(slides, ["A", "B", "C", "D"], out, canvas_size=(1080, 1350))

    result = Image.open(out)
    assert result.size == (1080, 1350)


def test_collage_2x2_creates_file(tmp_path):
    """build_collage_2x2 writes the output file."""
    slides = [_make_solid_image(str(tmp_path / f"s{i}.jpg")) for i in range(4)]
    out = str(tmp_path / "collage.jpg")

    from agents.compositor import build_collage_2x2
    build_collage_2x2(slides, ["STYLE A", "STYLE B", "STYLE C", "STYLE D"], out)

    assert Path(out).exists()


# ── Compositor: build_cta_slide ───────────────────────────────────────────────

def test_cta_slide_output_size_matches_source(tmp_path):
    """CTA slide has same dimensions as source render."""
    src = _make_solid_image(str(tmp_path / "src.jpg"), size=(1080, 1350))
    out = str(tmp_path / "cta.jpg")

    from agents.compositor import build_cta_slide
    build_cta_slide(src, {
        "headline": "ONE ROOM. INFINITE STYLES.",
        "subline": "Follow for weekly architecture drops.",
        "handle": "rkitect.ai",
    }, out)

    result = Image.open(out)
    assert result.size == (1080, 1350)


def test_cta_slide_creates_file(tmp_path):
    """build_cta_slide writes the output file."""
    src = _make_solid_image(str(tmp_path / "src.jpg"))
    out = str(tmp_path / "cta.jpg")

    from agents.compositor import build_cta_slide
    build_cta_slide(src, {"headline": "H", "subline": "S", "handle": "@h"}, out)

    assert Path(out).exists()


# ── Compositor: run_compositor end-to-end ─────────────────────────────────────

def test_run_compositor_returns_6_slides(tmp_path):
    """run_compositor returns exactly 6 slides for room-style-variants-carousel."""
    carousel_dir = tmp_path / "carousel_images"
    carousel_dir.mkdir()

    render_paths = [
        _make_solid_image(str(carousel_dir / f"slide_0{i+1}.jpg"), color=(i*60, 100, 150), size=(1080, 1350))
        for i in range(4)
    ]
    image_paths = {"carousel": render_paths, "linkedin": render_paths, "twitter": render_paths[:1]}
    template_meta = _make_template_meta()

    from agents.compositor import run_compositor
    result = run_compositor(image_paths, template_meta, tmp_path)

    assert len(result["carousel"]) == 6, f"Expected 6 slides, got {len(result['carousel'])}"


def test_run_compositor_slide_1_is_collage(tmp_path):
    """First slide in final carousel is the 2x2 collage."""
    carousel_dir = tmp_path / "carousel_images"
    carousel_dir.mkdir()

    render_paths = [
        _make_solid_image(str(carousel_dir / f"slide_0{i+1}.jpg"), size=(1080, 1350))
        for i in range(4)
    ]
    image_paths = {"carousel": render_paths, "linkedin": [], "twitter": []}
    template_meta = _make_template_meta()

    from agents.compositor import run_compositor
    result = run_compositor(image_paths, template_meta, tmp_path)

    cover = result["carousel"][0]
    assert "cover" in Path(cover).name, f"Expected cover in name, got: {Path(cover).name}"
    cover_img = Image.open(cover)
    assert cover_img.size == (1080, 1350)


def test_run_compositor_slide_6_is_cta(tmp_path):
    """Last slide in final carousel is the CTA slide."""
    carousel_dir = tmp_path / "carousel_images"
    carousel_dir.mkdir()

    render_paths = [
        _make_solid_image(str(carousel_dir / f"slide_0{i+1}.jpg"), size=(1080, 1350))
        for i in range(4)
    ]
    image_paths = {"carousel": render_paths, "linkedin": [], "twitter": []}
    template_meta = _make_template_meta()

    from agents.compositor import run_compositor
    result = run_compositor(image_paths, template_meta, tmp_path)

    cta = result["carousel"][-1]
    assert "cta" in Path(cta).name, f"Expected cta in name, got: {Path(cta).name}"


def test_run_compositor_passes_through_unknown_template(tmp_path):
    """Unknown template_id: image_paths returned unchanged."""
    image_paths = {"carousel": ["a.jpg", "b.jpg"], "linkedin": [], "twitter": []}
    template_meta = {"template_id": "some-other-template", "compositor_mode": "unknown"}

    from agents.compositor import run_compositor
    result = run_compositor(image_paths, template_meta, tmp_path)

    assert result["carousel"] == ["a.jpg", "b.jpg"]


def test_run_compositor_falls_back_gracefully_with_fewer_renders(tmp_path):
    """If fewer than 4 renders exist, compositor returns original paths unchanged."""
    carousel_dir = tmp_path / "carousel_images"
    carousel_dir.mkdir()

    render_paths = [
        _make_solid_image(str(carousel_dir / f"slide_0{i+1}.jpg"))
        for i in range(2)  # only 2 renders, not 4
    ]
    image_paths = {"carousel": render_paths, "linkedin": [], "twitter": []}
    template_meta = _make_template_meta()

    from agents.compositor import run_compositor
    result = run_compositor(image_paths, template_meta, tmp_path)

    # Should return original paths (not crash)
    assert result["carousel"] == render_paths
