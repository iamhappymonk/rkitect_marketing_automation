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
from utils.context_loader import (
    load_publish_settings,
    save_publish_settings,
    load_review_queue,
    save_review_queue,
)
from utils.costs import load_costs, sum_costs_between, get_entries_between

app = Flask(__name__)
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
        for fpath in folder.iterdir():
            key = fpath.stem
            try:
                outputs[key] = fpath.read_text(encoding="utf-8")
            except IOError:
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
    """Fetch pending posts from Buffer API."""
    if not BUFFER_ACCESS_TOKEN:
        return []
    try:
        import httpx
        profile_ids = [v for v in BUFFER_PROFILES.values() if v]
        results = []
        for pid in profile_ids:
            r = httpx.get(
                f"https://api.bufferapp.com/1/profiles/{pid}/updates/pending.json",
                headers={"Authorization": f"Bearer {BUFFER_ACCESS_TOKEN}"},
                timeout=10,
            )
            if r.status_code == 200:
                data = r.json()
                results.extend(data.get("updates", []))
        return results
    except Exception as e:
        return [{"error": str(e)}]


def get_review_queue() -> list:
    """Load the pending manual review queue."""
    queue = load_review_queue()
    return sorted(queue, key=lambda item: item.get("created_at", ""), reverse=True)


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
    })


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
    if not feedback:
        return jsonify({"error": "missing feedback"}), 400
    from agents.feedback import apply_feedback
    try:
        res = apply_feedback(feedback, phrase=phrase, source_file=source)
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
    subprocess.Popen(["python3", "main.py"])
    return jsonify({"status": "Pipeline triggered"})


# ── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=DASHBOARD_PORT, debug=False)
