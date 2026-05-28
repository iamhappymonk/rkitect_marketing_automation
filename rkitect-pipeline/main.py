#!/usr/bin/env python3
"""
rkitect.ai Content Pipeline — Main Orchestrator

6-stage daily pipeline:
  1. Research  -> find trending topics
  2. Filter    -> select best topic for today
  3. Generate  -> create content for all platforms (parallel)
  4. QA        -> score and retry if needed
  5. Publish   -> queue approved content to Buffer
  6. Self-Improve -> update perf log, rewrite prompts if needed

Run: python main.py
"""

import json
import sys
from datetime import date, datetime
from pathlib import Path

from agents.research import run_research
from agents.filter import run_filter
from agents.generate import run_generation, _generate_one
from agents.qa import run_qa, score_content
from agents.publish import run_publish
from agents.self_improve import run_self_improve
from utils.context_loader import (
    load_brand_context,
    load_post_history,
    save_post_history,
)
from utils.calendar import get_calendar_entry_for_date
from config import QA_MAX_RETRIES, OUTPUT_DIR, LOGS_DIR, FORMATS, IMAGE_GENERATION_ENABLED, IMAGE_TEMPLATE_ENABLED


def save_outputs(folder: Path, data: dict) -> None:
    """Save generated content and image briefs to output folder."""
    folder.mkdir(parents=True, exist_ok=True)

    # Separate text content and image briefs
    image_briefs = {}
    for key, content in data.items():
        if key.endswith("_image_brief"):
            image_briefs[key] = content
            path = folder / f"{key}.md"
        else:
            path = folder / f"{key}.md"

        with open(path, "w", encoding="utf-8") as f:
            if isinstance(content, str):
                f.write(content)
            else:
                f.write(json.dumps(content, indent=2))

    # Also save image briefs as structured JSON
    if image_briefs:
        briefs_path = folder / "image_briefs.json"
        with open(briefs_path, "w", encoding="utf-8") as f:
            json.dump(image_briefs, f, indent=2)


def write_log(run_log: dict) -> None:
    """Write the run log to logs/ directory.

    Uses run_id from the log dict so multiple runs on the same day each get
    their own log file (e.g. 2026-05-23_143022.json) instead of overwriting.
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / f"{run_log.get('run_id', str(date.today()))}.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(run_log, f, indent=2)


def update_post_history(topic: dict) -> None:
    """Add today's topic to post history for deduplication."""
    history = load_post_history()
    history["last_7_days"].append({
        "date": str(date.today()),
        "pillar": topic.get("pillar", "unknown"),
        "topic": topic.get("selected_topic", "unknown"),
    })
    # Keep only last 7 days
    history["last_7_days"] = history["last_7_days"][-7:]
    save_post_history(history)


def main(forced_template_id: str | None = None):
    """Run the full 6-stage content pipeline.

    Args:
        forced_template_id: If set, Stage 3.25 will use this specific image
                            template instead of random selection. Passed via
                            --template-id CLI flag or /api/run-template endpoint.
    """
    today = str(date.today())
    # Every run gets its own timestamped subfolder inside the date folder so
    # multiple runs on the same day never overwrite each other's images or text.
    # Structure: output/YYYY-MM-DD/run_HHMMSS/
    run_ts = datetime.now().strftime("%H%M%S")
    run_id = f"{today}_{run_ts}"
    out_dir = OUTPUT_DIR / today / f"run_{run_ts}"
    out_dir.mkdir(parents=True, exist_ok=True)
    run_log = {"date": today, "run_id": run_id, "stages": {}}

    print(f"\n{'=' * 54}")
    print(f"  rkitect.ai Content Pipeline · {today}")
    print(f"{'=' * 54}\n")

    # ── Stage 1 & 2: RESEARCH + FILTER (skipped for forced-template runs) ──
    #
    # When a specific template is forced (via --template-id or /api/run-template)
    # the research + filter LLM calls are unnecessary — the template already
    # defines what content to produce and which platforms to target.
    # We build a minimal topic dict from the template metadata (or calendar entry
    # if one exists for today) and skip both stages entirely.
    calendar_entry = get_calendar_entry_for_date(today)

    if forced_template_id and IMAGE_TEMPLATE_ENABLED:
        print(f"[1/6] Research skipped — template run ({forced_template_id})")
        print(f"[2/6] Filter skipped — template run")

        # Try to pull richer topic data from today's calendar plan first
        if calendar_entry:
            topic = {
                "selected_topic": calendar_entry.get("topic", forced_template_id),
                "pillar": calendar_entry.get("pillar", "visual"),
                "angle": calendar_entry.get("angle", ""),
                "calendar_entry": calendar_entry,
            }
            print(f"      Calendar entry: {topic['selected_topic']} [{topic['pillar']}]")
        else:
            # Derive a generic topic from the template id (e.g. "room-style-variants-carousel"
            # → "room style variants")
            friendly = forced_template_id.replace("-", " ").replace("_", " ").title()
            topic = {
                "selected_topic": friendly,
                "pillar": "visual",
                "angle": "interior design showcase",
            }

        run_log["stages"]["research"] = {"topic_count": 0, "skipped": True}
        run_log["stages"]["filter"] = {**topic, "skipped": True}
        print(f"      Topic: {topic['selected_topic']} [{topic['pillar']}]")

    else:
        # ── Stage 1: RESEARCH ────────────────────────────────────────────────
        print("[1/6] Research agent...")
        try:
            research = run_research()
        except Exception as e:
            print(f"[!] Research failed: {e}")
            research = {"topics": [], "error": str(e)}

        run_log["stages"]["research"] = {
            "topic_count": len(research.get("topics", []))
        }

        if not research.get("topics"):
            print("[!] No topics found. Aborting.")
            write_log(run_log)
            sys.exit(1)

        print(f"      {len(research['topics'])} topics found.")

        # ── Stage 2: FILTER ──────────────────────────────────────────────────
        print("[2/6] Filter agent...")
        if calendar_entry:
            print(f"      Calendar plan found for today: {calendar_entry.get('topic', 'unknown')}")
        try:
            topic = run_filter(research, calendar_entry=calendar_entry)
        except Exception as e:
            print(f"[!] Filter failed: {e}")
            topic = {"error": str(e)}

        run_log["stages"]["filter"] = topic

        if topic.get("error"):
            print(f"[!] Filter failed: {topic['error']}. Aborting.")
            write_log(run_log)
            sys.exit(1)

        selected = topic.get("selected_topic", "unknown")
        pillar = topic.get("pillar", "unknown")
        print(f"      -> {selected} [{pillar}]")

    # ── Stage 2.5: RESOLVE ACTIVE FORMATS FROM TEMPLATE METADATA ────────
    # When a template is forced, read its compatible_platforms early so
    # run_generation can skip channels the template doesn't target.
    # This avoids generating twitter/reddit content when the template only
    # targets instagram + linkedin — saving LLM calls and tokens.
    active_formats: list[str] | None = None  # None → all FORMATS (default)
    if forced_template_id and IMAGE_TEMPLATE_ENABLED and IMAGE_GENERATION_ENABLED:
        try:
            from agents.template_engine import load_templates
            from agents.generate import PLATFORM_TO_FORMAT
            from config import IMAGE_TEMPLATES_DIR
            _all_templates = load_templates(Path(IMAGE_TEMPLATES_DIR))
            _tmpl = next(
                (t for t in _all_templates if t["meta"].get("id") == forced_template_id),
                None,
            )
            if _tmpl:
                _platforms = _tmpl["meta"].get("compatible_platforms", [])
                active_formats = [
                    PLATFORM_TO_FORMAT[p] for p in _platforms if p in PLATFORM_TO_FORMAT
                ]
                if active_formats:
                    print(f"      Selective generation: {active_formats} (template targets {_platforms})")
                else:
                    print("      [WARN] Template platforms not in PLATFORM_TO_FORMAT — generating all")
                    active_formats = None
        except Exception as e:
            print(f"      [WARN] Could not resolve active formats from template ({e}). Generating all.")
            active_formats = None

    # ── Stage 3: GENERATE ────────────────────────────────────────────────
    print("[3/6] Generation agents (parallel)...")
    try:
        generated = run_generation(topic, active_formats=active_formats)
    except Exception as e:
        print(f"[!] Generation failed: {e}")
        generated = {fmt: f"ERROR: {e}" for fmt in (active_formats or FORMATS)}

    save_outputs(out_dir, generated)
    run_log["stages"]["generation"] = {
        "formats": [k for k in generated.keys() if not k.endswith("_image_brief")],
        "active_formats": active_formats,
        "selective": active_formats is not None,
    }
    print(f"      Outputs written -> {out_dir}/")

    # ── Stage 3.25: TEMPLATE-DRIVEN IMAGE BRIEF OVERRIDE ─────────────────
    template_meta = None
    if IMAGE_TEMPLATE_ENABLED and IMAGE_GENERATION_ENABLED:
        print("[3.25/6] Template engine (image brief override)...")
        if forced_template_id:
            print(f"      Forced template: {forced_template_id}")
        try:
            from agents.template_engine import run_template_selection
            generated = run_template_selection(topic, generated, load_brand_context(), forced_template_id=forced_template_id)
        except Exception as e:
            print(f"[!] Template engine failed: {e}. Continuing with LLM briefs.")

    # Extract _template_meta before QA — it's a dict, not content, and QA expects strings
    template_meta = generated.pop("_template_meta", None)

    # ── Stage 3.5: IMAGE GENERATION ──────────────────────────────────────
    image_paths = {}
    if IMAGE_GENERATION_ENABLED:
        print("[3.5/6] Image generation (carousel + LinkedIn)...")
        try:
            from agents.image_generator import run_image_generation
            image_paths = run_image_generation(generated, out_dir)
            carousel_count = len(image_paths.get("carousel", []))
            linkedin_count = len(image_paths.get("linkedin", []))
            print(f"      Carousel: {carousel_count} slides | LinkedIn: {linkedin_count} image(s)")
            if image_paths.get("errors"):
                for err in image_paths["errors"]:
                    print(f"      [WARN] {err}")

            if template_meta:
                from agents.template_engine import build_platform_image_paths, write_template_manifest
                image_paths = build_platform_image_paths(image_paths, template_meta)
                write_template_manifest(template_meta, image_paths, out_dir)
        except Exception as e:
            print(f"[!] Image generation failed: {e}. Continuing with text-only publish.")
            image_paths = {}
    else:
        print("[3.5/6] Image generation skipped (disabled in config).")

    run_log["stages"]["image_generation"] = {
        "carousel_slides": len(image_paths.get("carousel", [])),
        "linkedin_images": len(image_paths.get("linkedin", [])),
        "errors": image_paths.get("errors", []),
    }

    # ── Stage 3.55: IMAGE COMPOSITOR ─────────────────────────────────────────
    # Applies CODE_ONLY overlays: style tags, 2×2 collage cover, CTA slide.
    # Only runs when the selected template has a compositor_mode set.
    if (
        IMAGE_GENERATION_ENABLED
        and template_meta
        and template_meta.get("compositor_mode")
        and image_paths.get("carousel")
    ):
        print("[3.55/6] Image compositor (collage + style tags + CTA)...")
        try:
            from agents.compositor import run_compositor
            image_paths = run_compositor(image_paths, template_meta, out_dir)
            compositor_errors = image_paths.pop("compositor_errors", [])
            if compositor_errors:
                for err in compositor_errors:
                    print(f"      [WARN] compositor: {err}")
            final_count = len(image_paths.get("carousel", []))
            print(f"      Compositor done: {final_count} slides in final carousel")
            # Re-write template manifest with composited slide names
            from agents.template_engine import write_template_manifest
            write_template_manifest(template_meta, image_paths, out_dir)
        except Exception as e:
            print(f"[!] Compositor failed: {e}. Continuing with unprocessed images.")

    # ── Stage 3.6: VIDEO ASSEMBLY ─────────────────────────────────────────
    video_path = None
    carousel_slides = image_paths.get("carousel", [])
    if (
        IMAGE_GENERATION_ENABLED
        and IMAGE_TEMPLATE_ENABLED
        and template_meta
        and len(carousel_slides) >= 2
    ):
        print("[3.6/6] Video assembly (template transition)...")
        try:
            from agents.video_assembler import run_video_assembly
            video_path = run_video_assembly(carousel_slides, template_meta, out_dir)
            if video_path:
                print(f"      Video: {video_path}")
            else:
                print("      [WARN] Video assembly skipped (FFmpeg unavailable or failed)")
        except Exception as e:
            print(f"[!] Video assembly failed: {e}. Continuing.")
    else:
        if IMAGE_GENERATION_ENABLED and IMAGE_TEMPLATE_ENABLED:
            reason = "no template" if not template_meta else f"only {len(carousel_slides)} slide(s)"
            print(f"[3.6/6] Video assembly skipped ({reason}).")

    # ── Stage 3.7: VIDEO PROMPT WRITER ───────────────────────────────────────
    video_prompts = None
    if IMAGE_GENERATION_ENABLED and IMAGE_TEMPLATE_ENABLED and template_meta:
        print("[3.7/6] Video prompt writer (Kling / Wan / Veo / Runway)...")
        try:
            from agents.video_prompt_writer import run_video_prompt_writer
            video_prompts = run_video_prompt_writer(template_meta, out_dir)
        except Exception as e:
            print(f"[!] Video prompt writer failed: {e}. Continuing.")

    run_log["stages"]["video_assembly"] = {
        "video_path": video_path,
        "transition": template_meta.get("video_transition") if template_meta else None,
        "direction": template_meta.get("transition_direction") if template_meta else None,
        "ai_prompts": bool(video_prompts),
    }

    # ── Stage 4: QA with retry loop ──────────────────────────────────────
    print("[4/6] QA agent...")
    qa_results = run_qa(generated)

    for fmt in list(qa_results.keys()):
        retries = 0
        while not qa_results[fmt].get("passed") and retries < QA_MAX_RETRIES:
            retries += 1
            critique = qa_results[fmt].get("critique", "")
            score = qa_results[fmt].get("score", 0)
            print(
                f"      [{fmt}] score={score}/100 FAIL "
                f"— retry {retries}/{QA_MAX_RETRIES}"
            )

            try:
                _, revised = _generate_one(
                    fmt,
                    {**topic, "critique": critique},
                    load_brand_context(),
                )
                new_review = score_content(fmt, revised)
                new_review["content"] = revised
                qa_results[fmt] = new_review
            except Exception as e:
                print(f"      [{fmt}] Retry failed: {e}")
                break

        score = qa_results[fmt].get("score", 0)
        passed = qa_results[fmt].get("passed", False)
        status = "PASS" if passed else "FAIL"
        print(f"      [{fmt}] {score}/100 {status}")

    run_log["stages"]["qa"] = {
        k: {"score": v.get("score"), "passed": v.get("passed")}
        for k, v in qa_results.items()
    }

    # Save final QA-passed content back to output
    for fmt, result in qa_results.items():
        if result.get("passed") and result.get("content"):
            path = out_dir / f"{fmt}.md"
            path.write_text(result["content"], encoding="utf-8")

    # ── Stage 5: PUBLISH ─────────────────────────────────────────────────
    passed_count = sum(1 for v in qa_results.values() if v.get("passed"))
    print(f"[5/6] Publishing {passed_count} approved pieces via Buffer...")
    try:
        publish_log = run_publish(
            qa_results,
            topic=topic,
            image_paths=image_paths,
            template_meta=template_meta,
            out_dir=out_dir,
        )
    except Exception as e:
        print(f"[!] Publish failed: {e}")
        publish_log = {"error": str(e)}

    run_log["stages"]["publish"] = publish_log

    # Update post history for deduplication
    update_post_history(topic)

    # ── Stage 6: SELF-IMPROVE ────────────────────────────────────────────
    print("[6/6] Updating skill performance log...")
    try:
        run_self_improve(qa_results)
    except Exception as e:
        print(f"[!] Self-improve failed: {e}")

    # ── Summary ──────────────────────────────────────────────────────────
    print(f"\n{'-' * 54}")
    print(f"  Done - {today}")
    for fmt, r in qa_results.items():
        icon = "+" if r.get("passed") else "x"
        print(f"  {icon}  {fmt:<12}  {r.get('score', 0):>3}/100")
    print(f"{'-' * 54}\n")

    write_log(run_log)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="rkitect.ai Content Pipeline")
    parser.add_argument(
        "--template-id",
        default=None,
        help="Force a specific image template by ID (e.g. 'floorplan-2d-to-3d'). "
             "Skips random template selection in Stage 3.25.",
    )
    args = parser.parse_args()
    main(forced_template_id=args.template_id)
