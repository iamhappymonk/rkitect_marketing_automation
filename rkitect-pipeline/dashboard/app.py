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
)
from agents.publish import publish_review_item
from agents.feedback import apply_feedback
from utils.calendar import load_calendar, save_calendar, get_calendar_entry_for_date
from utils.context_loader import (
    load_publish_settings,
    save_publish_settings,
    load_review_queue,
    save_review_queue,
)
from utils.costs import load_costs, sum_costs_between, get_entries_between

app = Flask(__name__, template_folder='templates')
app.secret_key = DASHBOARD_SECRET_KEY


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


def get_today_output() -> dict:
    """Load today's generated content files."""
    folder = OUTPUT_DIR / str(date.today())
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
    """Collect today's generated images with metadata and briefs."""
    folder = OUTPUT_DIR / str(date.today())
    images = {}
    
    if not folder.exists():
        return images
    
    # Parse image briefs from markdown files
    def load_brief(name: str) -> str:
        brief_path = folder / f"{name}_image_brief.md"
        if brief_path.exists():
            try:
                text = brief_path.read_text(encoding="utf-8").strip()
                # Extract just the brief content (remove markdown markers)
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
                        "url": f"/output/{date.today()}/carousel_images/{s.name}",
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
            "url": f"/output/{date.today()}/linkedin_image.jpg",
            "brief": load_brief("linkedin"),
            "filename": "linkedin_image.jpg"
        }
    
    # Twitter card image
    twitter_img = folder / "twitter_image.jpg"
    if twitter_img.exists():
        images["twitter"] = {
            "type": "twitter",
            "url": f"/output/{date.today()}/twitter_image.jpg",
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
    scheduled = get_buffer_scheduled()
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
        "scheduled": scheduled,
        "publish_settings": publish_settings,
        "pending_review_count": len(review_queue),
        "calendar_entries": calendar_entries,
        "today_calendar": today_calendar,
        "images": images,
    })


@app.route("/api/calendar", methods=["GET", "POST"])
@requires_auth
def api_calendar():
    """Get or replace the content calendar."""
    if request.method == "POST":
        payload = request.get_json(silent=True) or {}
        entries = payload.get("entries")
        if not isinstance(entries, list):
            return jsonify({"error": "entries must be a list"}), 400
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
        settings["updated_at"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        save_publish_settings(settings)

    return jsonify(settings)


@app.route("/api/review-queue")
@requires_auth
def api_review_queue():
    """Return the current manual review queue."""
    queue = get_review_queue()
    return jsonify({"items": queue, "count": len(queue)})


@app.route("/api/review-queue/<item_id>/approve", methods=["POST"])
@requires_auth
def approve_review_item(item_id: str):
    """Approve a queued post and send it to Buffer."""
    queue = load_review_queue()
    item = next((entry for entry in queue if entry.get("id") == item_id), None)
    if not item:
        return jsonify({"error": "Review item not found"}), 404

    publish_result = publish_review_item(item)
    if publish_result.get("status") == "queued":
        queue = [entry for entry in queue if entry.get("id") != item_id]
        save_review_queue(queue)
        return jsonify({"status": "approved", "publish": publish_result})

    return jsonify({"status": "failed", "publish": publish_result}), 500


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
    subprocess.Popen([sys.executable, "main.py"])
    return jsonify({"status": "Pipeline triggered"})


@app.route("/output/<date_str>/<path:subpath>")
@requires_auth
def serve_output(date_str: str, subpath: str):
    """Serve generated images and files from the output directory."""
    fpath = OUTPUT_DIR / date_str / subpath
    if not fpath.exists() or not fpath.is_file():
        return jsonify({"error": "File not found"}), 404
    
    # Security: only serve from OUTPUT_DIR
    if not str(fpath).startswith(str(OUTPUT_DIR)):
        return jsonify({"error": "Access denied"}), 403
    
    # Serve the file with appropriate content-type
    import mimetypes
    mimetype, _ = mimetypes.guess_type(str(fpath))
    with open(fpath, 'rb') as f:
        return Response(f.read(), mimetype=mimetype or 'application/octet-stream')


# ── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=DASHBOARD_PORT, debug=False)
