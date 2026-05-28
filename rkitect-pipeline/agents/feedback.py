"""Feedback agent.

Applies user feedback, patches runtime context / prompt guards, regenerates the
selected post with the feedback as critique, and requeues the revised draft for
manual review.
"""
from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

from config import OUTPUT_DIR, PLATFORM_MAP, PERF_LOG, POST_HISTORY, PROMPTS_DIR, IMAGE_TEMPLATES_DIR
from agents.generate import _generate_one
from utils.context_loader import (
    load_brand_context,
    load_review_queue,
    save_review_queue,
)
from utils.feedback import process_feedback, write_feedback_diff


# ── Skill performance enrichment ─────────────────────────────────────────────

def enrich_skill_performance(
    fmt: str,
    feedback: str,
    perf_path: Optional[Path] = None,
) -> None:
    """Append human_feedback to the most recent entry for *fmt* in skill_performance.json.

    Creates a synthetic entry if the format has no history yet.
    Safe to call even if the file does not exist — it will be created.

    Args:
        fmt: Format name (linkedin, carousel, twitter, reddit).
        feedback: Human feedback string from the review page.
        perf_path: Override path to skill_performance.json (used in tests).
    """
    path = perf_path or PERF_LOG
    try:
        data: dict = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except (json.JSONDecodeError, IOError):
        data = {}

    if fmt not in data or not data[fmt]:
        # No history yet — create a stub entry so feedback is not lost.
        data[fmt] = [{"date": str(date.today()), "score": 0, "passed": False, "violations": []}]

    data[fmt][-1]["human_feedback"] = feedback
    data[fmt][-1]["feedback_at"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except IOError as exc:
        # Non-fatal — log but do not raise so the feedback flow still succeeds.
        import logging
        logging.getLogger("rkitect.feedback").warning("Could not write perf log: %s", exc)


# ── Post history enrichment ───────────────────────────────────────────────────

def enrich_post_history(
    topic_title: str,
    feedback: str,
    hist_path: Optional[Path] = None,
) -> None:
    """Append *feedback* to feedback_notes on the most recent matching history entry.

    Matches on the `topic` field of each history entry. When multiple entries
    share the same topic, only the most recent (last in the list) is updated.
    No-op if no match found or the file does not exist.

    Args:
        topic_title: The topic string to match (item.topic from review queue).
        feedback: Human feedback string.
        hist_path: Override path to post_history.json (used in tests).
    """
    path = hist_path or POST_HISTORY
    if not path.exists():
        return

    try:
        data: dict = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError):
        return

    entries: list = data.get("last_7_days", [])

    # Find the last entry matching this topic
    match_idx = None
    for i, entry in enumerate(entries):
        if entry.get("topic") == topic_title:
            match_idx = i

    if match_idx is None:
        return  # No match — silently skip

    notes: list = entries[match_idx].setdefault("feedback_notes", [])
    notes.append(feedback)

    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except IOError as exc:
        import logging
        logging.getLogger("rkitect.feedback").warning("Could not write post history: %s", exc)


def _load_topic_for_feedback(source_file: str = "") -> dict:
    """Load the topic JSON that generated the selected output."""
    candidates = []
    if source_file:
        src = Path(source_file)
        candidates.append(src.parent / "topics.md")
    candidates.append(OUTPUT_DIR / str(date.today()) / "topics.md")

    for path in candidates:
        if not path.exists():
            continue
        try:
            raw = path.read_text(encoding="utf-8")
            return json.loads(raw)
        except Exception:
            continue
    return {}


def _load_source_text(source_file: str = "") -> str:
    if not source_file:
        return ""
    path = Path(source_file)
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _infer_format(source_file: str = "", fallback: str = "linkedin") -> str:
    if source_file:
        stem = Path(source_file).stem
        if stem.endswith("_image_brief"):
            stem = stem.replace("_image_brief", "")
        if stem in PLATFORM_MAP or stem in {"linkedin", "carousel", "twitter", "reddit"}:
            return stem
    return fallback


def _build_review_item(fmt: str, content: str, topic: dict, feedback: str, source_file: str = "") -> dict:
    platform = PLATFORM_MAP.get(fmt, fmt)
    return {
        "id": f"fb-{date.today()}-{fmt}-{uuid4().hex[:8]}",
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "format": fmt,
        "platform": platform,
        "topic": topic.get("selected_topic", "unknown"),
        "pillar": topic.get("pillar", "unknown"),
        "angle": topic.get("angle", ""),
        "content": content,
        "score": 0,
        "status": "pending_review",
        "feedback": feedback,
        "source_file": source_file,
    }


# ── Image feedback helpers ────────────────────────────────────────────────────

def resolve_template_from_item(
    source_file: str = "",
    image_paths: list | None = None,
) -> Optional[str]:
    """Derive the template_id used for a review item by reading template_manifest.json.

    Looks in the run folder (parent of source_file, or parent of first image path).
    Returns the template_id string, or None if manifest not found / not parseable.
    """
    run_folder: Optional[Path] = None

    if source_file:
        candidate = Path(source_file).parent
        if candidate.exists():
            run_folder = candidate

    if run_folder is None and image_paths:
        candidate = Path(image_paths[0]).parent
        # carousel_images/ is one level deeper than the run folder
        if candidate.name == "carousel_images":
            candidate = candidate.parent
        if candidate.exists():
            run_folder = candidate

    if run_folder is None:
        return None

    manifest_path = run_folder / "template_manifest.json"
    if not manifest_path.exists():
        return None

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        return manifest.get("template_id") or None
    except (json.JSONDecodeError, IOError):
        return None


def enrich_template_file(
    template_id: str,
    feedback: str,
    templates_dir: Optional[Path] = None,
) -> bool:
    """Append a feedback entry to the ## Feedback Log section of the template file.

    Creates the section if it doesn't exist. Preserves all existing content.
    Returns True if the file was updated, False otherwise.
    """
    tdir = Path(templates_dir) if templates_dir else Path(IMAGE_TEMPLATES_DIR)
    target: Optional[Path] = None
    for md in tdir.glob("*.md"):
        if md.name.lower() == "readme.md":
            continue
        try:
            text = md.read_text(encoding="utf-8")
            if f"id: {template_id}" in text or f'id: "{template_id}"' in text:
                target = md
                break
        except IOError:
            continue

    if target is None:
        return False

    try:
        content = target.read_text(encoding="utf-8")
    except IOError:
        return False

    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- **{ts}** — {feedback}"

    if "## Feedback Log" in content:
        # Append after existing section header
        content = content + entry + "\n"
    else:
        content = content.rstrip() + "\n\n## Feedback Log\n" + entry + "\n"

    try:
        target.write_text(content, encoding="utf-8")
        return True
    except IOError:
        return False


def enrich_renderer_prompt(
    template_id: str,
    feedback: str,
    prompts_dir: Optional[Path] = None,
) -> bool:
    """Append a template-specific feedback note under ## Performance Notes in template_renderer.md.

    Also saves a versioned copy to prompts/versions/ for audit trail.
    Returns True if prompt was updated, False otherwise.
    """
    pdir = Path(prompts_dir) if prompts_dir else PROMPTS_DIR
    prompt_file = pdir / "template_renderer.md"

    if not prompt_file.exists():
        return False

    try:
        content = prompt_file.read_text(encoding="utf-8")
    except IOError:
        return False

    # Save version copy before modifying
    versions_dir = pdir / "versions"
    try:
        versions_dir.mkdir(parents=True, exist_ok=True)
        ts_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        version_copy = versions_dir / f"template_renderer_{ts_str}.md"
        version_copy.write_text(content, encoding="utf-8")
    except IOError:
        pass  # Non-fatal — continue with the update

    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    note = f"\n- **[{template_id}] {ts}** — {feedback}"

    if "## Performance Notes" in content:
        # Insert after the Performance Notes header
        content = content.replace(
            "## Performance Notes",
            f"## Performance Notes{note}",
            1,
        )
    else:
        content = content.rstrip() + f"\n\n## Performance Notes{note}\n"

    try:
        prompt_file.write_text(content, encoding="utf-8")
        return True
    except IOError:
        return False


def enrich_image_feedback(
    source_file: str,
    feedback: str,
    image_paths: list | None = None,
    templates_dir: Optional[Path] = None,
    prompts_dir: Optional[Path] = None,
    perf_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Apply human image feedback to template, renderer prompt, and perf log.

    This is the single entry point for image feedback. Call from the
    /api/review-queue/<id>/image-feedback route.

    Args:
        source_file: Path to the generated content file (e.g. carousel.md).
                     Used to find the run folder and template_manifest.json.
        feedback: Human feedback string describing the image issues.
        image_paths: Optional list of image file paths (fallback for run folder discovery).
        templates_dir: Override for IMAGE_TEMPLATES_DIR (used in tests).
        prompts_dir: Override for PROMPTS_DIR (used in tests).
        perf_path: Override for PERF_LOG (used in tests).

    Returns dict with keys:
        template_id: str | None — the resolved template ID
        template_updated: bool
        renderer_updated: bool
        perf_updated: bool
        feedback: str — echoed back
    """
    result: Dict[str, Any] = {
        "template_id": None,
        "template_updated": False,
        "renderer_updated": False,
        "perf_updated": False,
        "feedback": feedback,
    }

    # 1. Resolve template
    template_id = resolve_template_from_item(source_file=source_file, image_paths=image_paths)
    result["template_id"] = template_id

    if template_id:
        # 2. Enrich template file
        result["template_updated"] = enrich_template_file(
            template_id, feedback, templates_dir=templates_dir
        )
        # 3. Enrich renderer prompt
        result["renderer_updated"] = enrich_renderer_prompt(
            template_id, feedback, prompts_dir=prompts_dir
        )

    # 4. Enrich skill perf log (carousel is the image format)
    try:
        _perf = Path(perf_path) if perf_path else PERF_LOG
        _data: dict = json.loads(_perf.read_text(encoding="utf-8")) if _perf.exists() else {}
        if "carousel" not in _data or not _data["carousel"]:
            _data["carousel"] = [{"date": str(date.today()), "score": 0, "passed": False, "violations": []}]
        _data["carousel"][-1]["image_human_feedback"] = feedback
        _data["carousel"][-1]["image_feedback_at"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        _perf.parent.mkdir(parents=True, exist_ok=True)
        _perf.write_text(json.dumps(_data, indent=2, ensure_ascii=False), encoding="utf-8")
        result["perf_updated"] = True
    except Exception as exc:
        import logging
        logging.getLogger("rkitect.feedback").warning("enrich_image_feedback perf update failed: %s", exc)

    return result


def regenerate_images_for_item(
    item: Dict[str, Any],
    feedback: str,
    output_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Re-generate images for a review queue item with feedback injected into prompts.

    Loads image_briefs.json from the run folder (parent of item's source_file),
    prepends a FEEDBACK CORRECTION directive to every slide prompt, then calls
    run_image_generation so new images overwrite the old ones in-place.

    Args:
        item: Review queue item dict (must have "source_file").
        feedback: Human feedback string ("needs golden hour lighting", etc.).
        output_dir: Override output directory (defaults to source_file's parent).

    Returns:
        {"image_paths": [...], "errors": [...]}
    """
    source_file = item.get("source_file", "")
    if not source_file:
        return {"image_paths": [], "errors": ["source_file missing from queue item"]}

    run_folder = Path(source_file).parent
    if not run_folder.exists():
        return {"image_paths": [], "errors": [f"run folder not found: {run_folder}"]}

    briefs_path = run_folder / "image_briefs.json"
    if not briefs_path.exists():
        return {"image_paths": [], "errors": [f"image_briefs.json not found in {run_folder}"]}

    try:
        briefs: Dict[str, Any] = json.loads(briefs_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"image_paths": [], "errors": [f"failed to load image_briefs.json: {exc}"]}

    # Inject feedback directive into every carousel slide prompt
    feedback_prefix = f"FEEDBACK CORRECTION — apply to every slide: {feedback}\n\n"
    carousel_raw = briefs.get("carousel_image_brief", "")
    if carousel_raw:
        try:
            slides = json.loads(carousel_raw)
            if isinstance(slides, list):
                for slide in slides:
                    if isinstance(slide, dict) and "prompt" in slide:
                        slide["prompt"] = feedback_prefix + slide["prompt"]
                briefs["carousel_image_brief"] = json.dumps(slides)
        except Exception:
            pass  # Non-fatal — continue with unmodified briefs

    from agents.image_generator import run_image_generation

    out_dir = output_dir or run_folder
    try:
        gen_result = run_image_generation(briefs, out_dir)
    except Exception as exc:
        return {"image_paths": [], "errors": [f"image generation failed: {exc}"]}

    new_paths: list = []
    for key in ("carousel", "linkedin", "twitter"):
        new_paths.extend(gen_result.get(key, []))

    return {"image_paths": new_paths, "errors": gen_result.get("errors", [])}


def apply_feedback(
    feedback: str,
    phrase: Optional[str] = None,
    source_file: Optional[str] = None,
    format_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Apply feedback and regenerate the affected draft.

    Returns a dict with the regenerated content, queue id, and patch metadata.
    """
    source_file = source_file or ""
    fmt = _infer_format(source_file, fallback=format_name or "linkedin")
    topic = _load_topic_for_feedback(source_file)
    source_text = _load_source_text(source_file)

    if not topic:
        return {
            "status": "failed",
            "error": "Could not load topic context for regeneration",
        }

    feedback_result = process_feedback(feedback, phrase=phrase, source_file=source_file)

    # Regenerate using the feedback as critique so the next draft directly addresses the issue.
    try:
        revised_topic = {**topic, "critique": feedback}
        brand_context = load_brand_context()
        _, revised_content = _generate_one(fmt, revised_topic, brand_context)
    except Exception as e:
        return {
            "status": "failed",
            "error": f"Regeneration failed: {e}",
            "feedback": feedback_result,
        }

    hinted_path = Path(source_file) if source_file else None
    if hinted_path and hinted_path.exists():
        target_path = hinted_path
    else:
        target_path = OUTPUT_DIR / str(date.today()) / f"{fmt}.md"
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(revised_content, encoding="utf-8")

    queue_item = _build_review_item(fmt, revised_content, topic, feedback, str(target_path))
    queue = load_review_queue()
    queue.append(queue_item)
    save_review_queue(queue)

    diff_path = write_feedback_diff(
        feedback=feedback,
        source_file=str(target_path),
        before=source_text,
        after=revised_content,
    )

    feedback_result.update(
        {
            "status": "requeued",
            "format": fmt,
            "queue_id": queue_item["id"],
            "source_file": str(target_path),
            "diff_file": str(diff_path),
            "content": revised_content,
            "review_queue_count": len(queue),
        }
    )
    return feedback_result
