---
name: image-style-lock
version: 1.0.0
description: >
  Extracts a locked style fingerprint from the first generated slide and enforces it across
  all subsequent slides in a carousel sequence. Prevents palette drift, lighting drift, and
  composition drift when generating multi-slide carousels. Also responsible for building
  per-slide prompts that respect the locked style while varying scene content.
  Use this skill in conjunction with carousel-image-generator.
---

# Image Style Lock

The single biggest cause of inconsistent carousels is each slide being generated independently.
This skill prevents that by extracting a "style DNA" from slide 1 and injecting it into every
subsequent prompt — regardless of how different the scene content is.

---

## The Core Problem

When you generate slide 1 and then slide 3 with similar-sounding prompts:

```
Slide 1 prompt: "Architect at desk, warm oak tones, soft light"
Slide 3 prompt: "Floor plan render, clean minimal, architectural"
```

The model interprets these independently. Slide 1 might be warm amber, slide 3 cold white.
The carousel looks like two different brands.

**This skill fixes that by:**
1. Extracting specific, quantified style attributes from the slide 1 brief
2. Building a locked style block that overrides vague model interpretation
3. Prepending that block to every subsequent slide prompt

---

## Style Extraction (from Slide 1 Brief)

After the `image_brief_writer` generates briefs and before calling the image API,
extract the style fingerprint from the slide 1 brief JSON:

```python
def extract_style_fingerprint(slide_1_brief: dict) -> dict:
    """
    Extract quantified style attributes from the slide 1 brief.
    These become the locked style applied to all subsequent slides.
    """
    return {
        "color_palette": slide_1_brief.get("color_palette", ""),
        # e.g. "warm neutrals (cream #F5F1ED, concrete gray #A89A8D), sage green #9CAF88"

        "lighting": _infer_lighting(slide_1_brief),
        # e.g. "soft diffuse natural light, warm afternoon, no harsh shadows"

        "camera_style": _infer_camera(slide_1_brief),
        # e.g. "35mm architectural photography, slight wide angle"

        "rendering_style": _infer_render(slide_1_brief),
        # e.g. "photorealistic, minimal architectural, studio-grade"

        "mood": slide_1_brief.get("mood", "professional"),
        # e.g. "calm professional confidence"

        "material_language": _extract_materials(slide_1_brief),
        # e.g. "concrete, oak wood, linen, matte glass"

        "composition_principle": "safe text area top 80%, no text in bottom 20%",
        # Always enforced for Instagram carousels
    }
```

---

## Inference Helpers

These map brief metadata to concrete prompt language:

```python
def _infer_lighting(brief: dict) -> str:
    mood = brief.get("mood", "professional")
    style = brief.get("style", "architectural")
    mapping = {
        "professional": "soft diffuse natural light, warm afternoon, subtle fill light, no harsh shadows",
        "urgent": "high contrast, single directional light, sharp edge shadows",
        "inspirational": "golden hour warmth, broad soft window light, lens flare subtle",
        "educational": "even studio light, no directional preference, clean visibility",
    }
    return mapping.get(mood, "soft diffuse natural light, clean and even")


def _infer_camera(brief: dict) -> str:
    platform = brief.get("platform", "instagram")
    dims = brief.get("dimensions", "1080x1350")
    if "1350" in dims:
        return "35mm equivalent, slight wide angle, portrait framing, architectural photography style"
    elif "627" in dims:
        return "35mm equivalent, landscape framing, generous negative space left-right"
    return "35mm equivalent, neutral perspective"


def _infer_render(brief: dict) -> str:
    style = brief.get("style", "architectural")
    mapping = {
        "architectural": "photorealistic architectural visualization, minimal post-processing",
        "data-viz": "clean vector-style graphic, flat design, no photorealism",
        "before-after": "split composition, photorealistic both sides",
        "sektura-segment": "photorealistic render with clean UI annotation overlays",
        "minimal": "minimal, high white space, clean typography",
    }
    return mapping.get(style, "photorealistic, clean, minimal")


def _extract_materials(brief: dict) -> str:
    # Extract material nouns from the prompt text
    prompt = brief.get("prompt", "").lower()
    materials = []
    material_map = {
        "concrete": "polished concrete",
        "oak": "warm oak wood",
        "linen": "natural linen texture",
        "glass": "matte glass",
        "marble": "veined marble",
        "steel": "brushed steel",
        "brick": "raw brick",
    }
    for key, label in material_map.items():
        if key in prompt:
            materials.append(label)
    return ", ".join(materials) if materials else "natural materials, architectural finishes"
```

---

## Locked Style Block Builder

The output of this skill is a string that gets prepended to every slide 2-N prompt:

```python
def build_style_lock_block(fingerprint: dict) -> str:
    """
    Build the locked style string to prepend to slides 2-N.
    This is injected BEFORE scene-specific content in every prompt.
    """
    return f"""LOCKED VISUAL STYLE — DO NOT DEVIATE:
Color palette: {fingerprint['color_palette']}
Lighting: {fingerprint['lighting']}
Camera style: {fingerprint['camera_style']}
Rendering: {fingerprint['rendering_style']}
Materials: {fingerprint['material_language']}
Mood: {fingerprint['mood']}
Composition: {fingerprint['composition_principle']}
Text in image: NONE — no text, labels, or captions in the generated image.
---
SCENE (varies per slide):
"""
```

---

## Per-Slide Prompt Assembly

For each slide, combine the locked style block + the scene-specific content from the brief:

```python
def build_slide_prompt(
    brief: dict,
    slide_index: int,
    style_lock: str | None = None
) -> str:
    """
    Args:
        brief: The image brief dict for this specific slide.
        slide_index: 0-based index. Slide 0 = no style lock injected.
        style_lock: The locked style block string. None for slide 0.

    Returns:
        Final prompt string to send to the image generation API.
    """
    scene = brief.get("prompt", "")

    if slide_index == 0:
        # Slide 1: full prompt, no style lock yet (it IS the reference)
        return f"""{scene}

Photography: photorealistic architectural, soft diffuse natural light.
Format: portrait 4:5 ratio. No text in image. No watermarks."""
    else:
        # Slides 2-N: style lock + scene delta only
        return f"""{style_lock}{scene}

Critical: maintain the exact color palette and lighting from the reference image.
Only the subject and spatial composition should differ.
No text in image. No watermarks."""
```

---

## Strength Calibration for img2img

When calling Flux Kontext Pro, the `strength` parameter (if exposed) controls how much
the model deviates from the reference image. For carousel consistency:

| Strength | Effect | Use Case |
|----------|--------|---------|
| 0.3-0.4 | Very similar to reference | Same room, different angle |
| 0.5-0.6 | Preserves palette/lighting, changes scene | **Recommended for carousels** |
| 0.7-0.8 | Loose reference, significant scene change | Data viz slides in same visual language |
| 0.9-1.0 | Almost ignores reference | Avoid |

**Default: 0.6**. Set 0.55 for visually-heavy slides (interiors, renders), 0.7 for data/text slides.

---

## Saving the Style Fingerprint

Persist the fingerprint to disk so it can be reused (e.g., for regenerating a single failed slide):

```python
import json
from pathlib import Path

def save_fingerprint(fingerprint: dict, output_dir: Path) -> None:
    path = output_dir / "style_fingerprint.json"
    path.write_text(json.dumps(fingerprint, indent=2), encoding="utf-8")

def load_fingerprint(output_dir: Path) -> dict | None:
    path = output_dir / "style_fingerprint.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())
```

---

## LinkedIn Single-Image (No Locking Needed)

LinkedIn posts generate a single hero image — no chaining, no style lock required.
Just pass the brief prompt directly to Flux 1.1 Pro t2i. No consistency overhead.

---

## Platform-Specific Enforcement Rules

These are always injected regardless of brief content:

```python
PLATFORM_GUARDS = {
    "instagram_carousel": [
        "No text, labels, or captions in the image",
        "Safe area: keep subject in top 80% of frame",
        "Portrait 4:5 ratio composition",
        "No harsh vignette on edges — carousel slides bleed into each other visually",
    ],
    "linkedin": [
        "No text or watermarks in image",
        "Wide 16:9 landscape composition",
        "Leave right third with minimal visual content for text overlay",
    ],
    "twitter": [
        "No text in image",
        "High contrast for dark mode",
        "Center-heavy composition",
    ],
}
```

---

## Integration Point in Pipeline

```python
# In agents/image_generator.py

def run_image_generation(generated: dict, output_dir: Path) -> dict:
    """
    Entry point called from main.py after run_generation() succeeds.

    Args:
        generated: Output from run_generation(), includes carousel and linkedin keys.
        output_dir: Today's output directory.

    Returns:
        dict mapping format to list of local image paths.
    """
    image_paths = {}

    # 1. Parse carousel image briefs
    carousel_briefs = parse_carousel_briefs(generated.get("carousel_image_brief", ""))

    if carousel_briefs:
        # 2. Extract style fingerprint from brief 0
        fingerprint = extract_style_fingerprint(carousel_briefs[0])
        save_fingerprint(fingerprint, output_dir)

        # 3. Build locked style block for slides 2-N
        style_lock = build_style_lock_block(fingerprint)

        # 4. Build per-slide prompts
        prompts = [
            build_slide_prompt(brief, idx, style_lock if idx > 0 else None)
            for idx, brief in enumerate(carousel_briefs)
        ]

        # 5. Generate images with chaining (see carousel-image-generator skill)
        paths = generate_carousel_images(prompts, carousel_briefs, output_dir)
        image_paths["carousel"] = paths

    # 6. LinkedIn single image
    linkedin_brief = parse_linkedin_brief(generated.get("linkedin_image_brief", ""))
    if linkedin_brief:
        path = generate_single_image(linkedin_brief, output_dir / "linkedin_image.jpg")
        image_paths["linkedin"] = [path]

    return image_paths
```

---

## Hard Rules

1. **Slide 0 is sacred.** Never modify slide 1's prompt with style lock injection — it IS the reference.
2. **Fingerprint before generation.** Extract and save fingerprint before any API call.
3. **Scene content never overrides palette.** If a brief says "cold blue tones" but the lock says "warm cream," the lock wins.
4. **Persist fingerprint.** Save to `style_fingerprint.json` so single-slide regeneration works.
5. **Platform guards always appended.** No text in images, ever.

---

## Anti-Patterns

- ❌ Applying style lock to slide 1 (creates circular reference)
- ❌ Extracting fingerprint from the TEXT brief rather than the structured brief JSON
- ❌ Letting scene-specific material descriptions override the locked palette
- ❌ Using a single flat prompt for all slides (identical outputs, not a carousel)
- ❌ Skipping fingerprint persistence (breaks single-slide regeneration)

---

## Performance Notes

Last updated: initial
