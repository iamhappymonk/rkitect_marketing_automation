#!/usr/bin/env python3
"""
rkitect.ai Content Pipeline — Main Orchestrator

6-stage daily pipeline:
  1. Research  → find trending topics
  2. Filter    → select best topic for today
  3. Generate  → create content for all platforms (parallel)
  4. QA        → score and retry if needed
  5. Publish   → queue approved content to Buffer
  6. Self-Improve → update perf log, rewrite prompts if needed

Run: python main.py
"""

import json
import sys
from datetime import date
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
from config import QA_MAX_RETRIES, OUTPUT_DIR, LOGS_DIR, FORMATS, IMAGE_GENERATION_ENABLED


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
    """Write the run log to logs/ directory."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / f"{date.today()}.json"
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


def main():
    """Run the full 6-stage content pipeline."""
    today = str(date.today())
    out_dir = OUTPUT_DIR / today
    run_log = {"date": today, "stages": {}}

    print(f"\n{'=' * 54}")
    print(f"  rkitect.ai Content Pipeline · {today}")
    print(f"{'=' * 54}\n")

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
    calendar_entry = get_calendar_entry_for_date(today)
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

    # ── Stage 3: GENERATE ────────────────────────────────────────────────
    print("[3/6] Generation agents (parallel)...")
    try:
        generated = run_generation(topic)
    except Exception as e:
        print(f"[!] Generation failed: {e}")
        generated = {fmt: f"ERROR: {e}" for fmt in FORMATS}

    save_outputs(out_dir, generated)
    run_log["stages"]["generation"] = [
        k for k in generated.keys() if not k.endswith("_image_brief")
    ]
    print(f"      Outputs written -> {out_dir}/")

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
        publish_log = run_publish(qa_results, topic=topic, image_paths=image_paths)
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
    print(f"\n{'─' * 54}")
    print(f"  Done · {today}")
    for fmt, r in qa_results.items():
        icon = "+" if r.get("passed") else "x"
        print(f"  {icon}  {fmt:<12}  {r.get('score', 0):>3}/100")
    print(f"{'─' * 54}\n")

    write_log(run_log)


if __name__ == "__main__":
    main()
