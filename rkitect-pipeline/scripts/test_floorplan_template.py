#!/usr/bin/env python3
"""
Test script: force the floorplan-2d-to-3d template and run image + video generation.

Usage (from rkitect-pipeline/):
    python scripts/test_floorplan_template.py

Outputs land in output/<today>/ and are visible on the dashboard.
"""
import json
import sys
from pathlib import Path
from datetime import date, datetime

# Add pipeline root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    IMAGE_GENERATION_ENABLED, IMAGE_TEMPLATE_ENABLED,
    IMAGE_TEMPLATES_DIR, OUTPUT_DIR, LOGS_DIR,
)
from utils.context_loader import load_brand_context
from agents.template_engine import (
    load_templates, run_template_selection,
    build_platform_image_paths, write_template_manifest,
)
from agents.image_generator import run_image_generation
from agents.video_assembler import run_video_assembly

# ── Hardcoded test topic (skips research + filter) ──────────────────────────
TOPIC = {
    "selected_topic": "AI transforms flat floor plans into 3D renders instantly",
    "pillar": "proof",
    "angle": "transformation",
    "format": "carousel",
}

FORCE_TEMPLATE_ID = "floorplan-2d-to-3d"


def main():
    today = str(date.today())
    # Always use a unique timestamped folder — never overwrite previous runs
    run_ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = OUTPUT_DIR / run_ts
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'=' * 54}")
    print(f"  rkitect.ai -- Template Test: {FORCE_TEMPLATE_ID}")
    print(f"  Run: {run_ts}  |  Output: {out_dir}")
    print(f"{'=' * 54}\n")

    # ── Step 1: Load + force template ─────────────────────────────────────
    templates = load_templates(Path(IMAGE_TEMPLATES_DIR))
    target = next(
        (t for t in templates if t["meta"].get("id") == FORCE_TEMPLATE_ID), None
    )
    if not target:
        print(f"[ERROR] Template '{FORCE_TEMPLATE_ID}' not found in {IMAGE_TEMPLATES_DIR}")
        print(f"  Available: {[t['meta'].get('id') for t in templates]}")
        sys.exit(1)

    slide_count = target["meta"].get("slide_count", "?")
    print(f"[1] Template: {target['meta'].get('name')} ({slide_count} slides)")
    print(f"    Transition: {target['meta'].get('video_transition')} / {target['meta'].get('transition_direction')}")

    # ── Step 2: Render briefs (force this template) ───────────────────────
    print("\n[2] Rendering template briefs via LLM...")
    brand_context = load_brand_context()

    from agents import template_engine as _te
    _orig = _te.select_template
    _te.select_template = lambda topic, templates: target
    generated = run_template_selection(TOPIC, {}, brand_context)
    _te.select_template = _orig

    template_meta = generated.pop("_template_meta", None)
    carousel_brief_raw = generated.get("carousel_image_brief", "")

    if not carousel_brief_raw:
        print("[ERROR] No carousel brief returned. Check template_renderer.md / API key.")
        sys.exit(1)

    try:
        briefs = json.loads(carousel_brief_raw)
        print(f"    {len(briefs)} slide brief(s) generated OK.")
        for i, b in enumerate(briefs):
            preview = b.get("prompt", "")[:120].replace("\n", " ")
            print(f"    Slide {i+1}: {preview}...")
    except Exception as e:
        print(f"[ERROR] Brief JSON parse failed: {e}")
        print(f"  Raw (first 400 chars): {carousel_brief_raw[:400]}")
        sys.exit(1)

    if template_meta:
        anchor = template_meta.get("spatial_anchor", "")
        if anchor:
            print(f"\n    Spatial anchor ({len(anchor)} chars):")
            print(f"    {anchor[:240]}...")
        safe_meta = {k: v for k, v in template_meta.items() if k != "spatial_anchor"}
        print(f"\n    Template meta: {json.dumps(safe_meta, indent=6)}")

    # ── Step 3: Image generation ──────────────────────────────────────────
    if not IMAGE_GENERATION_ENABLED:
        print("\n[3] Image generation DISABLED (IMAGE_GENERATION_ENABLED=false in .env)")
        print("    Tip: set IMAGE_GENERATION_ENABLED=true to generate real images.")
        image_paths = {"carousel": [], "linkedin": [], "twitter": [], "errors": []}
    else:
        print("\n[3] Generating images (Flux via OpenRouter)...")
        image_paths = run_image_generation(generated, out_dir)
        c = len(image_paths.get("carousel", []))
        print(f"    Carousel slides generated: {c}")
        for p in image_paths.get("carousel", []):
            print(f"      {p}")
        for err in image_paths.get("errors", []):
            print(f"      [WARN] {err}")

        if template_meta:
            image_paths = build_platform_image_paths(image_paths, template_meta)
            write_template_manifest(template_meta, image_paths, out_dir)
            print(f"    Manifest -> {out_dir / 'template_manifest.json'}")

    # -- Step 4a: AI video prompts (Kling / Wan / Veo / Runway) ---------------
    video_prompts = None
    ai_prompts_path = None
    if template_meta:
        print("\n[4a] Generating AI video prompts (Kling / Wan / Veo / Runway)...")
        try:
            from agents.video_prompt_writer import run_video_prompt_writer
            video_prompts = run_video_prompt_writer(template_meta, out_dir)
            if video_prompts:
                ai_prompts_path = out_dir / "ai_video_prompts.json"
                print(f"    Kling  : {video_prompts['kling'][:80]}...")
                print(f"    Wan    : {video_prompts['wan'][:80]}...")
                print(f"    Veo    : {video_prompts['veo'][:80]}...")
                print(f"    Runway : {video_prompts['runway'][:80]}...")
            else:
                print("    [WARN] Prompt generation failed -- check API key / prompt file.")
        except Exception as e:
            print(f"    [ERROR] video_prompt_writer: {e}")

    # -- Step 4b: AI video generation (Grok) -----------------------------------
    ai_video_path = None
    if template_meta:
        print("\n[4b] Generating AI video via Grok (x-ai/grok-imagine-video)...")
        try:
            from agents.ai_video_generator import run_ai_video_generation
            ai_video_path = run_ai_video_generation(template_meta, video_prompts, out_dir)
            if ai_video_path:
                print(f"    AI video -> {ai_video_path}")
            else:
                print("    [WARN] AI video generation failed -- falling back to FFmpeg.")
        except Exception as e:
            print(f"    [ERROR] ai_video_generator: {e}")

    # -- Step 4c: FFmpeg fallback (if AI video failed) -------------------------
    video_path = ai_video_path
    carousel_slides = image_paths.get("carousel", [])
    if not video_path and len(carousel_slides) >= 2 and template_meta:
        print("\n[4c] FFmpeg fallback video assembly...")
        video_path = run_video_assembly(carousel_slides, template_meta, out_dir)
        if video_path:
            print(f"    FFmpeg video -> {video_path}")
        else:
            print("    Video skipped (FFmpeg unavailable or build failed).")
    elif not video_path:
        reason = "no images" if not carousel_slides else "only 1 image (need >=2)"
        print(f"\n[4c] FFmpeg fallback skipped ({reason}).")

    # ── Step 5: Write log (dashboard reads this) ──────────────────────────
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / f"{run_ts}.json"
    run_log = {
        "date": today,
        "test_mode": True,
        "template_id": FORCE_TEMPLATE_ID,
        "stages": {
            "research": {"topic_count": 1},
            "filter": TOPIC,
            "generation": ["carousel"],
            "template_engine": {
                "template": template_meta.get("template_id") if template_meta else None,
                "slide_count": len(briefs),
                "spatial_anchor_chars": len(template_meta.get("spatial_anchor", "")) if template_meta else 0,
            },
            "image_generation": {
                "carousel_slides": len(image_paths.get("carousel", [])),
                "linkedin_images": len(image_paths.get("linkedin", [])),
                "errors": image_paths.get("errors", []),
            },
            "video_assembly": {
                "ai_video_path": ai_video_path,
                "ffmpeg_video_path": video_path if video_path != ai_video_path else None,
                "transition": template_meta.get("video_transition") if template_meta else None,
                "direction": template_meta.get("transition_direction") if template_meta else None,
                "ai_prompts_path": str(ai_prompts_path) if ai_prompts_path else None,
            },
        },
    }
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(run_log, f, indent=2)
    print(f"\n[5] Run log -> {log_path}")

    print(f"\n{'-' * 54}")
    print(f"  Done. Open the dashboard to review.")
    print(f"  Output: {out_dir}")
    print(f"{'-' * 54}\n")


if __name__ == "__main__":
    main()
