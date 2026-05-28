"""
rkitect.ai Content Pipeline — Dashboard Server

Flask web UI showing today's topics, generated content, QA scores,
image briefs, and Buffer schedule. Protected by env-based username/password.
"""

import json
import glob
import subprocess
import functools
import sys
import logging
from pathlib import Path
from datetime import date, datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from flask import (
    Flask, render_template, jsonify, request, Response
)

from config import (
    DASHBOARD_PORT, DASHBOARD_SECRET_KEY,
    DASHBOARD_USERNAME, DASHBOARD_PASSWORD,
    LOGS_DIR, OUTPUT_DIR, PERF_LOG,
    BUFFER_ACCESS_TOKEN, BUFFER_PROFILES,
    IMAGE_TEMPLATES_DIR,
)
from agents.publish import _clean_content_for_platform
from agents.feedback import (
    apply_feedback,
    enrich_skill_performance,
    enrich_post_history,
    enrich_image_feedback,
    regenerate_images_for_item,
)
from utils.calendar import load_calendar, save_calendar, get_calendar_entry_for_date
from utils.context_loader import (
    load_publish_settings,
    save_publish_settings,
    load_review_queue,
    save_review_queue,
)
from utils.costs import load_costs, sum_costs_between, get_entries_between

app = Flask(__name__, template_folder='templates')
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.jinja_env.auto_reload = True
app.secret_key = DASHBOARD_SECRET_KEY

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
)
logger = logging.getLogger("rkitect.dashboard")


# ── Basic Auth ───────────────────────────────────────────────────────────────

def check_auth(username: str, password: str) -> bool:
    """Verify username and password against env vars."""
    return username == DASHBOARD_USERNAME and password == DASHBOARD_PASSWORD


def authenticate():
    """Send a 401 response to trigger browser auth dialog."""
    return Response(
        "Access denied. Please provide valid credentials.",
        401,
        {"WWW-Authenticate": 'Basic realm="rkitect.ai Dashboard"'},
    )


def requires_auth(f):
    """Decorator for routes that require authentication."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


# ── Data Helpers ─────────────────────────────────────────────────────────────

def get_recent_logs(n: int = 7) -> list:
    """Load the N most recent run logs."""
    logs = []
    if not LOGS_DIR.exists():
        return logs
    log_files = sorted(LOGS_DIR.glob("*.json"), reverse=True)[:n]
    for path in log_files:
        try:
            with open(path, encoding="utf-8") as f:
                logs.append(json.load(f))
        except (json.JSONDecodeError, IOError):
            continue
    return logs


def _latest_run_folder(day_folder: Path) -> Path:
    """Return the most recent run_HHMMSS subfolder within a day folder.

    Falls back to the day folder itself for backward compatibility with
    items written before the per-run subfolder structure was introduced.
    """
    if not day_folder.exists():
        return day_folder
    run_dirs = sorted(
        d for d in day_folder.iterdir()
        if d.is_dir() and d.name.startswith("run_")
    )
    return run_dirs[-1] if run_dirs else day_folder


def get_today_output() -> dict:
    """Load today's generated content files from the most recent run folder."""
    day_folder = OUTPUT_DIR / str(date.today())
    folder = _latest_run_folder(day_folder)
    outputs = {}
    if folder.exists():
        # Only attempt to read text-based files. Binary files (images) will
        # raise UnicodeDecodeError when read as UTF-8; skip them instead.
        text_exts = {".md", ".txt", ".json", ".html", ".csv"}
        for fpath in folder.iterdir():
            key = fpath.stem
            try:
                if fpath.suffix.lower() in text_exts:
                    outputs[key] = fpath.read_text(encoding="utf-8")
                else:
                    # Skip binary or unknown file types; the frontend only
                    # expects textual outputs for today_output.
                    continue
            except (IOError, UnicodeDecodeError):
                # Be resilient to corrupt or partially-written files.
                continue
    return outputs


def get_performance_data() -> dict:
    """Load the skill performance log."""
    if not PERF_LOG.exists():
        return {}
    try:
        with open(PERF_LOG, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def get_buffer_scheduled() -> list:
    """Fetch pending ideas from Buffer GraphQL API."""
    if not BUFFER_ACCESS_TOKEN:
        return []
    
    from config import BUFFER_ORGANIZATION_ID
    if not BUFFER_ORGANIZATION_ID:
        return []

    try:
        import httpx
        query = """
        query GetIdeas($orgId: ID!) {
          ideas(organizationId: $orgId) {
            id
            content {
              title
              text
            }
          }
        }
        """
        r = httpx.post(
            "https://api.buffer.com/1/graphql",
            json={
                "query": query,
                "variables": {"orgId": BUFFER_ORGANIZATION_ID}
            },
            headers={"Authorization": f"Bearer {BUFFER_ACCESS_TOKEN}"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            ideas = data.get("data", {}).get("ideas", [])
            return [
                {
                    "profile_service": "Idea",
                    "text": f"{idea.get('content', {}).get('title', '')}: {idea.get('content', {}).get('text', '')}",
                    "due_time": "Draft"
                }
                for idea in ideas
            ]
        return []
    except Exception as e:
        return [{"error": str(e)}]


def get_review_queue() -> list:
    """Load the pending manual review queue."""
    queue = load_review_queue()
    return sorted(queue, key=lambda item: item.get("created_at", ""), reverse=True)


def get_calendar_entries() -> list:
    """Load calendar entries sorted by date string."""
    entries = load_calendar()
    return sorted(entries, key=lambda item: item.get("date", ""))


def get_today_images() -> dict:
    """Collect today's generated images with metadata and briefs.

    Looks inside the most recent run_HHMMSS subfolder of today's date folder.
    Falls back to the date folder directly for backward compatibility.
    """
    day_folder = OUTPUT_DIR / str(date.today())
    folder = _latest_run_folder(day_folder)
    images = {}

    if not folder.exists():
        return images

    # Relative path from OUTPUT_DIR used to build serve URLs
    try:
        rel_base = folder.relative_to(OUTPUT_DIR).as_posix()
    except ValueError:
        rel_base = str(date.today())

    def load_brief(name: str) -> str:
        brief_path = folder / f"{name}_image_brief.md"
        if brief_path.exists():
            try:
                text = brief_path.read_text(encoding="utf-8").strip()
                if text.startswith("[IMAGE BRIEF:"):
                    return text
                return f"[IMAGE BRIEF: {text}]"
            except IOError:
                pass
        return ""

    # Carousel slides
    carousel_dir = folder / "carousel_images"
    if carousel_dir.exists():
        slides = sorted(carousel_dir.glob("slide_*.jpg"))
        if slides:
            images["carousel"] = {
                "type": "carousel",
                "slides": [
                    {
                        "filename": s.name,
                        "url": f"/output/{rel_base}/carousel_images/{s.name}",
                        "order": int(s.stem.split("_")[1])
                    }
                    for s in slides
                ],
                "brief": load_brief("carousel"),
                "count": len(slides)
            }

    # LinkedIn hero image
    linkedin_img = folder / "linkedin_image.jpg"
    if linkedin_img.exists():
        images["linkedin"] = {
            "type": "linkedin",
            "url": f"/output/{rel_base}/linkedin_image.jpg",
            "brief": load_brief("linkedin"),
            "filename": "linkedin_image.jpg"
        }

    # Twitter card image
    twitter_img = folder / "twitter_image.jpg"
    if twitter_img.exists():
        images["twitter"] = {
            "type": "twitter",
            "url": f"/output/{rel_base}/twitter_image.jpg",
            "brief": load_brief("twitter"),
            "filename": "twitter_image.jpg"
        }

    return images


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
@requires_auth
def index():
    """Serve the dashboard page."""
    return render_template("index.html")


@app.route("/review")
@requires_auth
def review_page():
    """Serve the manual review page."""
    return render_template("review.html")


@app.route("/api/data")
@requires_auth
def api_data():
    """Return all dashboard data as JSON."""
    logs = get_recent_logs()
    outputs = get_today_output()
    perf = get_performance_data()
    publish_settings = load_publish_settings()
    review_queue = get_review_queue()
    calendar_entries = get_calendar_entries()
    today_calendar = get_calendar_entry_for_date(str(date.today()))
    images = get_today_images()

    # Compute average scores per format from perf log
    score_summary = {}
    for fmt, entries in perf.items():
        recent = entries[-7:]
        score_summary[fmt] = {
            "avg": round(
                sum(e["score"] for e in recent) / len(recent), 1
            ) if recent else 0,
            "trend": [e["score"] for e in recent],
            "passes": sum(1 for e in recent if e.get("passed")),
        }

    return jsonify({
        "today": str(date.today()),
        "recent_logs": logs,
        "today_output": outputs,
        "score_summary": score_summary,
        "scheduled": [],
        "publish_settings": publish_settings,
        "pending_review_count": len(review_queue),
        "calendar_entries": calendar_entries,
        "today_calendar": today_calendar,
        "images": images,
    })


@app.route("/api/buffer/ideas")
@requires_auth
def api_buffer_ideas():
    """Fetch Buffer ideas on-demand only."""
    return jsonify({"scheduled": get_buffer_scheduled()})


@app.route("/api/calendar", methods=["GET", "POST"])
@requires_auth
def api_calendar():
    """Get or replace the content calendar."""
    if request.method == "POST":
        payload = request.get_json(silent=True) or {}
        entries = payload.get("entries")
        if not isinstance(entries, list):
            return jsonify({"error": "entries must be a list"}), 400
        logger.info("Calendar updated with %d entries", len(entries))
        save_calendar(entries)
    return jsonify({"entries": get_calendar_entries()})


@app.route("/api/costs")
@requires_auth
def api_costs():
    """Return cost entries and totals for a requested range.

    Query param `range` supports: `30d` (default), `7d`, `today`, `month`.
    """
    rng = request.args.get("range", "30d")
    today = date.today()
    if rng == "7d":
        start = today - timedelta(days=6)
    elif rng == "today":
        start = today
    elif rng == "month":
        start = date(today.year, today.month, 1)
    else:
        # default 30 days
        start = today - timedelta(days=29)

    end = today
    entries = get_entries_between(start, end)
    total = sum_costs_between(start, end)
    return jsonify({
        "range": rng,
        "start": str(start),
        "end": str(end),
        "total": total,
        "entries": entries,
    })


@app.route("/api/feedback", methods=["POST"]) 
@requires_auth
def api_feedback():
    """Accept user feedback and apply conservative fixes in the pipeline.

    Payload JSON: { "feedback": "...", "phrase": "optional phrase to search", "source_file": "optional path to output file" }
    """
    payload = request.get_json(silent=True) or {}
    feedback = payload.get("feedback")
    phrase = payload.get("phrase")
    source = payload.get("source_file")
    format_name = payload.get("format")
    if not feedback:
        return jsonify({"error": "missing feedback"}), 400
    try:
        logger.info("Feedback received (format=%s, source=%s)", format_name, source)
        res = apply_feedback(
            feedback,
            phrase=phrase,
            source_file=source,
            format_name=format_name,
        )
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/publish-settings", methods=["GET", "POST"])
@requires_auth
def api_publish_settings():
    """Get or update the auto-publish setting."""
    settings = load_publish_settings()

    if request.method == "POST":
        payload = request.get_json(silent=True) or {}
        if "auto_publish" in payload:
            settings["auto_publish"] = bool(payload["auto_publish"])
            logger.info("Auto publish set to %s", settings["auto_publish"])
        settings["updated_at"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        save_publish_settings(settings)

    return jsonify(settings)


@app.route("/api/review-queue")
@requires_auth
def api_review_queue():
    """Return the current manual review queue."""
    queue = get_review_queue()

    # Enrich queue items with image URLs that the dashboard can serve.
    def path_to_output_url(p: str) -> str | None:
        try:
            ppath = Path(p)
            # Only convert paths under OUTPUT_DIR
            if str(ppath).startswith(str(OUTPUT_DIR)):
                rel = ppath.relative_to(OUTPUT_DIR)
                # Serve via /output/<date>/<subpath>
                return f"/output/{rel.as_posix()}"
        except Exception:
            return None
        return None

    enriched = []
    for item in queue:
        new_item = dict(item)
        image_paths = item.get("image_paths") or []
        image_urls = []
        for p in image_paths:
            url = path_to_output_url(p)
            if url:
                image_urls.append(url)
        # Expose image_urls array for frontend preview (may be empty)
        new_item["image_urls"] = image_urls

        # Expose video_url if this item has a generated video
        video_path = item.get("video_path", "")
        video_url = None
        if video_path:
            try:
                vp = Path(video_path)
                if str(vp).startswith(str(OUTPUT_DIR)):
                    rel = vp.relative_to(OUTPUT_DIR)
                    video_url = f"/output/{rel.as_posix()}"
            except Exception:
                pass
        new_item["video_url"] = video_url

        # Ensure preview_content is always clean body text, not raw JSON.
        # If the stored item already has a clean preview_content use it; otherwise
        # run _clean_content_for_platform at serve-time so dirty items stored
        # before the parse fix are handled correctly without touching the queue file.
        if not new_item.get("preview_content"):
            fmt = item.get("format", "")
            raw_content = item.get("content", "")
            new_item["preview_content"] = _clean_content_for_platform(raw_content, fmt=fmt)

        enriched.append(new_item)

    return jsonify({"items": enriched, "count": len(enriched)})


@app.route("/api/review-queue/<item_id>/feedback", methods=["POST"])
@requires_auth
def review_item_feedback(item_id: str):
    """Accept human feedback for a specific review queue item.

    Regenerates the post with the feedback as critique, requeues the result,
    and enriches skill_performance.json + post_history.json for future runs.

    Payload JSON: { "feedback": "..." }
    """
    queue = load_review_queue()
    item = next((entry for entry in queue if entry.get("id") == item_id), None)
    if not item:
        return jsonify({"error": "Review item not found"}), 404

    payload = request.get_json(silent=True) or {}
    feedback = (payload.get("feedback") or "").strip()
    if not feedback:
        return jsonify({"error": "missing feedback"}), 400

    fmt = item.get("format", "linkedin")
    source_file = item.get("source_file", "")
    topic_title = item.get("topic", "")

    logger.info(
        "Review item feedback received (id=%s, format=%s, topic=%s)",
        item_id, fmt, topic_title,
    )

    try:
        result = apply_feedback(
            feedback,
            source_file=source_file,
            format_name=fmt,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Remove the stale original item now that a regenerated replacement is queued.
    # apply_feedback appends the new item first; we filter out the old id after.
    if result.get("status") == "requeued":
        try:
            current_queue = load_review_queue()
            current_queue = [e for e in current_queue if e.get("id") != item_id]
            save_review_queue(current_queue)
        except Exception as e:
            logger.warning("Failed to remove old queue item %s: %s", item_id, e)

    # Enrich skill performance log with human feedback
    try:
        enrich_skill_performance(fmt, feedback)
    except Exception as e:
        logger.warning("enrich_skill_performance failed: %s", e)

    # Enrich post history with feedback notes
    try:
        enrich_post_history(topic_title, feedback)
    except Exception as e:
        logger.warning("enrich_post_history failed: %s", e)

    result["perf_updated"] = True
    result["history_updated"] = bool(topic_title)
    return jsonify(result)


@app.route("/api/review-queue/<item_id>/image-feedback", methods=["POST"])
@requires_auth
def review_item_image_feedback(item_id: str):
    """Accept human feedback on generated images for a review queue item.

    Updates:
    - The image template file (## Feedback Log section)
    - template_renderer.md prompt (## Performance Notes section + version copy)
    - skill_performance.json (image_human_feedback on latest carousel entry)

    Payload JSON: { "feedback": "..." }
    """
    queue = load_review_queue()
    item = next((entry for entry in queue if entry.get("id") == item_id), None)
    if not item:
        return jsonify({"error": "Review item not found"}), 404

    payload = request.get_json(silent=True) or {}
    feedback = (payload.get("feedback") or "").strip()
    if not feedback:
        return jsonify({"error": "missing feedback"}), 400

    source_file = item.get("source_file", "")
    image_paths = item.get("image_paths") or []

    logger.info(
        "Image feedback received (id=%s, source=%s)",
        item_id, source_file,
    )

    try:
        result = enrich_image_feedback(
            source_file=source_file,
            feedback=feedback,
            image_paths=image_paths,
        )
    except Exception as e:
        logger.exception("enrich_image_feedback failed")
        return jsonify({"error": str(e)}), 500

    # Immediately rebuild the images for this exact post with feedback injected.
    regen_result = {"image_paths": [], "errors": []}
    try:
        regen_result = regenerate_images_for_item(item, feedback)
        new_image_paths = regen_result.get("image_paths", [])

        if new_image_paths:
            # Update the queue item's image_paths in-place so the dashboard
            # shows the refreshed images without requiring a new pipeline run.
            current_queue = load_review_queue()
            for entry in current_queue:
                if entry.get("id") == item_id:
                    entry["image_paths"] = new_image_paths
                    break
            save_review_queue(current_queue)

        if regen_result.get("errors"):
            for err in regen_result["errors"]:
                logger.warning("Image regen warning (id=%s): %s", item_id, err)

    except Exception as e:
        logger.warning("regenerate_images_for_item failed (id=%s): %s", item_id, e)
        regen_result = {"image_paths": [], "errors": [str(e)]}

    return jsonify({
        "status": "applied",
        "images_regenerated": bool(regen_result.get("image_paths")),
        "image_paths": regen_result.get("image_paths", []),
        "regen_errors": regen_result.get("errors", []),
        **result,
    })


@app.route("/api/review-queue/<item_id>/generate-image", methods=["POST"])
@requires_auth
def generate_image_for_item(item_id: str):
    """Generate (or re-generate) images on demand for a review queue item.

    Does NOT require feedback text — reads image_briefs.json from the item's
    run_folder and calls run_image_generation directly.

    Returns:
        {"status": "ok", "image_paths": [...], "image_urls": [...]}
    """
    queue = load_review_queue()
    item = next((e for e in queue if e.get("id") == item_id), None)
    if not item:
        return jsonify({"error": "Review item not found"}), 404

    run_folder_str = item.get("run_folder") or (
        str(Path(item.get("source_file", "")).parent)
        if item.get("source_file") else ""
    )
    if not run_folder_str:
        return jsonify({"error": "run_folder not stored in queue item — re-run pipeline to get it"}), 400

    run_folder = Path(run_folder_str)
    briefs_path = run_folder / "image_briefs.json"

    if not briefs_path.exists():
        return jsonify({
            "error": "image_briefs.json not found in run folder. "
                     "Ensure IMAGE_TEMPLATE_ENABLED=true and re-run the pipeline."
        }), 400

    try:
        import json as _json
        briefs = _json.loads(briefs_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return jsonify({"error": f"Failed to load image_briefs.json: {exc}"}), 500

    logger.info("On-demand image generation requested (id=%s)", item_id)

    try:
        from agents.image_generator import run_image_generation
        new_image_paths = run_image_generation(briefs, run_folder)
    except Exception as exc:
        logger.exception("On-demand image generation failed (id=%s)", item_id)
        return jsonify({"error": str(exc)}), 500

    errors = new_image_paths.pop("errors", [])
    all_paths = []
    for key in ("carousel", "linkedin", "twitter"):
        all_paths.extend(new_image_paths.get(key, []))

    if all_paths:
        # Update queue item image_paths in-place
        current_queue = load_review_queue()
        for entry in current_queue:
            if entry.get("id") == item_id:
                entry["image_paths"] = all_paths
                break
        save_review_queue(current_queue)

    def path_to_url(p: str):
        try:
            ppath = Path(p)
            if str(ppath).startswith(str(OUTPUT_DIR)):
                rel = ppath.relative_to(OUTPUT_DIR)
                return f"/output/{rel.as_posix()}"
        except Exception:
            pass
        return None

    image_urls = [u for u in (path_to_url(p) for p in all_paths) if u]

    return jsonify({
        "status": "ok",
        "image_paths": all_paths,
        "image_urls": image_urls,
        "errors": errors,
    })


@app.route("/api/review-queue/<item_id>/generate-video", methods=["POST"])
@requires_auth
def generate_video_for_item(item_id: str):
    """Generate a transition video on demand for a review queue item.

    Reads video_generation_mode from the item's template_meta:
      - "python" → FFmpeg xfade assembly via video_assembler.py
      - "ai"     → AI video generation via ai_video_generator.py (Veo / Kling)

    Stores video_path in the queue item and returns a serveable video_url.
    """
    queue = load_review_queue()
    item = next((e for e in queue if e.get("id") == item_id), None)
    if not item:
        return jsonify({"error": "Review item not found"}), 404

    template_meta = item.get("template_meta") or {}
    if not template_meta.get("video_transition"):
        return jsonify({"error": "No video_transition in template_meta — this item has no video direction"}), 400

    run_folder_str = item.get("run_folder") or (
        str(Path(item.get("source_file", "")).parent)
        if item.get("source_file") else ""
    )
    if not run_folder_str:
        return jsonify({"error": "run_folder not stored in queue item — re-run pipeline to get it"}), 400

    run_folder = Path(run_folder_str)
    mode = template_meta.get("video_generation_mode", "python").lower()

    logger.info("On-demand video generation requested (id=%s, mode=%s)", item_id, mode)

    video_path_str = None

    if mode == "ai":
        # Load AI video prompts if available (written by video_prompt_writer)
        video_prompts = None
        ai_prompts_path = run_folder / "ai_video_prompts.json"
        if ai_prompts_path.exists():
            try:
                import json as _json
                video_prompts = _json.loads(ai_prompts_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        try:
            from agents.ai_video_generator import run_ai_video_generation
            video_path_str = run_ai_video_generation(template_meta, video_prompts, run_folder)
        except Exception as exc:
            logger.exception("AI video generation failed (id=%s)", item_id)
            return jsonify({"error": str(exc)}), 500

    else:
        # Python / FFmpeg path
        slide_paths = item.get("image_paths") or []
        # Filter to carousel slides only (slide_NN.jpg pattern)
        carousel_slides = sorted(
            p for p in slide_paths
            if "slide_" in Path(p).stem
        )
        if not carousel_slides:
            # Fall back to all image paths
            carousel_slides = slide_paths

        if len(carousel_slides) < 2:
            return jsonify({
                "error": f"Need ≥2 images to build a video. Found {len(carousel_slides)}. Generate images first."
            }), 400

        try:
            from agents.video_assembler import run_video_assembly
            video_path_str = run_video_assembly(carousel_slides, template_meta, run_folder)
        except Exception as exc:
            logger.exception("FFmpeg video assembly failed (id=%s)", item_id)
            return jsonify({"error": str(exc)}), 500

    if not video_path_str:
        return jsonify({"error": "Video generation failed — check server logs for details"}), 500

    # Store video_path in queue item
    current_queue = load_review_queue()
    for entry in current_queue:
        if entry.get("id") == item_id:
            entry["video_path"] = video_path_str
            break
    save_review_queue(current_queue)

    # Build a serveable URL
    video_url = None
    try:
        vpath = Path(video_path_str)
        if str(vpath).startswith(str(OUTPUT_DIR)):
            rel = vpath.relative_to(OUTPUT_DIR)
            video_url = f"/output/{rel.as_posix()}"
    except Exception:
        pass

    return jsonify({
        "status": "ok",
        "video_path": video_path_str,
        "video_url": video_url,
        "mode": mode,
    })


@app.route("/api/review-queue/<item_id>/approve", methods=["POST"])
@requires_auth
def approve_review_item(item_id: str):
    """Approve: remove from review queue.

    Video generation is triggered client-side before this call when the item
    has a video_transition template. This endpoint DOES NOT publish to Buffer —
    publishing is a separate, explicit step.
    """
    queue = load_review_queue()
    item = next((entry for entry in queue if entry.get("id") == item_id), None)
    if not item:
        return jsonify({"error": "Review item not found"}), 404

    queue = [entry for entry in queue if entry.get("id") != item_id]
    save_review_queue(queue)
    return jsonify({"status": "approved"})


@app.route("/api/review-queue/<item_id>/reject", methods=["POST"])
@requires_auth
def reject_review_item(item_id: str):
    """Reject a queued post and remove it from the review queue."""
    queue = load_review_queue()
    item = next((entry for entry in queue if entry.get("id") == item_id), None)
    if not item:
        return jsonify({"error": "Review item not found"}), 404

    queue = [entry for entry in queue if entry.get("id") != item_id]
    save_review_queue(queue)
    return jsonify({"status": "rejected"})


@app.route("/api/trigger", methods=["POST"])
@requires_auth
def trigger_pipeline():
    """Manually trigger a pipeline run from the dashboard."""
    main_py = Path(__file__).parent.parent / "main.py"
    logger.info("Pipeline trigger requested; spawning %s", main_py)
    subprocess.Popen([sys.executable, str(main_py)])
    return jsonify({"status": "Pipeline triggered"})


@app.route("/templates")
@requires_auth
def templates_page():
    """Template launcher page — pick a template and start a pipeline run."""
    return render_template("templates.html")


@app.route("/api/templates")
@requires_auth
def api_templates():
    """Return all available image templates with metadata."""
    from agents.template_engine import load_templates
    templates = load_templates(Path(IMAGE_TEMPLATES_DIR))
    return jsonify({
        "templates": [
            {
                "id": t["meta"].get("id"),
                "name": t["meta"].get("name", ""),
                "slide_count": t["meta"].get("slide_count", 0),
                "compatible_platforms": t["meta"].get("compatible_platforms", []),
                "compatible_pillars": t["meta"].get("compatible_pillars", []),
                "image_size": t["meta"].get("image_size", ""),
                "video_transition": t["meta"].get("video_transition", ""),
                "transition_direction": t["meta"].get("transition_direction", ""),
                "video_duration_hint": t["meta"].get("video_duration_hint", 0),
            }
            for t in templates
        ]
    })


@app.route("/api/run-template", methods=["POST"])
@requires_auth
def run_with_template():
    """Start a pipeline run with a specific image template forced.

    Payload JSON: { "template_id": "floorplan-2d-to-3d" }
    Spawns main.py --template-id <id> as a background process.
    Returns immediately; caller polls /api/review-queue for results.
    """
    payload = request.get_json(silent=True) or {}
    template_id = (payload.get("template_id") or "").strip()
    if not template_id:
        return jsonify({"error": "template_id is required"}), 400

    # Validate the template exists before spawning a process
    from agents.template_engine import load_templates
    templates = load_templates(Path(IMAGE_TEMPLATES_DIR))
    valid_ids = [t["meta"].get("id") for t in templates]
    if template_id not in valid_ids:
        return jsonify({
            "error": f"Template '{template_id}' not found",
            "available": valid_ids,
        }), 404

    main_py = Path(__file__).parent.parent / "main.py"
    subprocess.Popen([sys.executable, str(main_py), "--template-id", template_id])

    # Find the human-readable name for the response
    name = next(
        (t["meta"].get("name", template_id) for t in templates if t["meta"].get("id") == template_id),
        template_id,
    )
    return jsonify({
        "status": "started",
        "template_id": template_id,
        "template_name": name,
        "message": "Pipeline started. Posts will appear in Review Queue in 2–4 minutes.",
    })


@app.route("/output/<date_str>/<path:subpath>")
def serve_output(date_str: str, subpath: str):
    """Serve generated images and files from the output directory.

    No auth required — output assets (images, videos) are served without a
    credential check so that <img> and <video> tags in the review page can
    load them directly.  The rest of the dashboard remains auth-gated.
    """
    fpath = OUTPUT_DIR / date_str / subpath
    if not fpath.exists() or not fpath.is_file():
        return jsonify({"error": "File not found"}), 404

    # Security: only serve from OUTPUT_DIR
    try:
        fpath.resolve().relative_to(OUTPUT_DIR.resolve())
    except ValueError:
        return jsonify({"error": "Access denied"}), 403

    # Explicit MIME map — Windows mimetypes registry returns non-standard values
    # (e.g. image/pjpeg for .jpg) that some browsers refuse to render.
    _SERVE_MIME: dict[str, str] = {
        ".jpg":  "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png":  "image/png",
        ".gif":  "image/gif",
        ".webp": "image/webp",
        ".mp4":  "video/mp4",
        ".mov":  "video/quicktime",
        ".webm": "video/webm",
    }
    mimetype = _SERVE_MIME.get(fpath.suffix.lower(), "application/octet-stream")
    with open(fpath, "rb") as f:
        return Response(f.read(), mimetype=mimetype)


# ── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=DASHBOARD_PORT, debug=False)
