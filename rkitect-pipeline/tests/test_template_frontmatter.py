"""
TDD: Template frontmatter parser — multi-line YAML list support.

The room-style-variants-carousel template uses block sequences:
    style_pool:
      - Japanese Wabi-Sabi
      - Indian Traditional
      ...

Current parser skips lines without ':' — style_pool gets parsed as "" → empty.
These tests confirm the fix.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


ROOM_STYLE_FRONTMATTER = """\
---
id: room-style-variants-carousel
name: Same Room / Four Interior Styles Carousel
slide_count: 6
image_size: "1080x1350"
compatible_platforms: ["instagram", "linkedin"]
style_pool:
  - Japanese Wabi-Sabi
  - Indian Traditional
  - Scandinavian Minimal
  - American Contemporary
  - Chinese Imperial
  - Brutalist Concrete
style_pick_count: 4
style_pick_method: random_each_run
text_overlay_policy: CODE_ONLY
---

Body text here.
"""


def test_style_pool_is_list_not_empty_string():
    """style_pool must be parsed as a list, not an empty string."""
    from agents.template_engine import _parse_frontmatter
    meta, _ = _parse_frontmatter(ROOM_STYLE_FRONTMATTER)
    style_pool = meta.get("style_pool")
    assert isinstance(style_pool, list), f"Expected list, got {type(style_pool)}: {style_pool!r}"
    assert len(style_pool) > 0, "style_pool must not be empty"


def test_style_pool_contains_correct_items():
    """style_pool list contains all declared style names."""
    from agents.template_engine import _parse_frontmatter
    meta, _ = _parse_frontmatter(ROOM_STYLE_FRONTMATTER)
    pool = meta["style_pool"]
    assert "Japanese Wabi-Sabi" in pool
    assert "Scandinavian Minimal" in pool
    assert "Brutalist Concrete" in pool


def test_style_pool_has_correct_count():
    """style_pool list has exactly 6 items (as declared in the template)."""
    from agents.template_engine import _parse_frontmatter
    meta, _ = _parse_frontmatter(ROOM_STYLE_FRONTMATTER)
    assert len(meta["style_pool"]) == 6


def test_scalar_fields_after_list_parsed_correctly():
    """Fields after the multi-line list (style_pick_count) are still parsed."""
    from agents.template_engine import _parse_frontmatter
    meta, _ = _parse_frontmatter(ROOM_STYLE_FRONTMATTER)
    assert meta.get("style_pick_count") == 4
    assert meta.get("style_pick_method") == "random_each_run"
    assert meta.get("text_overlay_policy") == "CODE_ONLY"


def test_non_list_fields_unaffected():
    """Scalar fields before the list are still parsed correctly."""
    from agents.template_engine import _parse_frontmatter
    meta, _ = _parse_frontmatter(ROOM_STYLE_FRONTMATTER)
    assert meta.get("id") == "room-style-variants-carousel"
    assert meta.get("slide_count") == 6
    assert meta.get("image_size") == "1080x1350"


def test_inline_list_field_unaffected():
    """Inline list fields (compatible_platforms) still parsed correctly."""
    from agents.template_engine import _parse_frontmatter
    meta, _ = _parse_frontmatter(ROOM_STYLE_FRONTMATTER)
    platforms = meta.get("compatible_platforms")
    assert isinstance(platforms, list)
    assert "instagram" in platforms
    assert "linkedin" in platforms


def test_body_returned_unchanged():
    """Body text after --- is returned intact."""
    from agents.template_engine import _parse_frontmatter
    _, body = _parse_frontmatter(ROOM_STYLE_FRONTMATTER)
    assert "Body text here." in body


def test_room_style_template_loads_with_full_style_pool(tmp_path):
    """Full template file loads with style_pool as a 12-item list."""
    from agents.template_engine import _parse_frontmatter
    import os
    # Load the actual template file
    template_path = Path(__file__).parent.parent / "image_templates" / "room-style-variants-carousel.md"
    if not template_path.exists():
        import pytest
        pytest.skip("Template file not found")
    content = template_path.read_text(encoding="utf-8")
    meta, _ = _parse_frontmatter(content)
    pool = meta.get("style_pool", [])
    assert isinstance(pool, list), f"style_pool should be list, got {type(pool)}"
    assert len(pool) == 12, f"Expected 12 styles in pool, got {len(pool)}: {pool}"
