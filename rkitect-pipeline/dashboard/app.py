"""
rkitect.ai Content Pipeline — Dashboard Server

Flask web UI showing today's topics, generated content, QA scores,
image briefs, and Buffer schedule. Protected by env-based username/password.
"""

import json
import glob
import subprocess
import functools
from pathlib import Path
from datetime import date

from flask import (
    Flask, render_template, jsonify, request, Response
)
from config import (
    DASHBOARD_PORT, DASHBOARD_SECRET_KEY,
    DASHBOARD_USERNAME, DASHBOARD_PASSWORD,
    LOGS_DIR, OUTPUT_DIR, PERF_LOG,
    BUFFER_ACCESS_TOKEN, BUFFER_PROFILES,
)

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


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
@requires_auth
def index():
    """Serve the dashboard page."""
    return render_template("index.html")


@app.route("/api/data")
@requires_auth
def api_data():
    """Return all dashboard data as JSON."""
    logs = get_recent_logs()
    outputs = get_today_output()
    perf = get_performance_data()
    scheduled = get_buffer_scheduled()

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
    })


@app.route("/api/trigger", methods=["POST"])
@requires_auth
def trigger_pipeline():
    """Manually trigger a pipeline run from the dashboard."""
    subprocess.Popen(["python3", "main.py"])
    return jsonify({"status": "Pipeline triggered"})


# ── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=DASHBOARD_PORT, debug=False)
