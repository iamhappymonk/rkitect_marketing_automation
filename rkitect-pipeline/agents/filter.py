"""
rkitect.ai Content Pipeline — Filter Agent

Reads post_history.json, applies pillar weights, selects the single best
topic for today's content. Outputs JSON.
"""

import json
import re
from datetime import date

from model_router import call_model
from utils.calendar import normalize_calendar_entry
from utils.context_loader import load_brand_context, load_prompt, load_post_history
from config import CONTENT_PILLARS


def run_filter(research: dict, calendar_entry: dict | None = None) -> dict:
    """
    Select the best topic from research results using pillar weights
    and deduplication logic.

    Args:
        research: dict from run_research() containing 'topics' list.

    Returns:
        dict with selected_topic, pillar, angle, rationale, etc.
    """
    system = load_brand_context() + "\n\n---\n\n" + load_prompt("filter_agent")

    if calendar_entry:
        planned = normalize_calendar_entry(calendar_entry)
        return {
            "selected_topic": planned.get("topic") or planned.get("caption") or "Planned calendar topic",
            "pillar": planned.get("format") or "calendar",
            "angle": planned.get("psychological_hook") or planned.get("caption_theme") or "calendar planned post",
            "rationale": "Selected from content calendar for the requested date.",
            "calendar_entry": planned,
            "planned": True,
        }

    post_history = load_post_history()

    user = (
        f"Pillar weights:\n{json.dumps(CONTENT_PILLARS, indent=2)}\n\n"
        f"Post history (last 7 days):\n{json.dumps(post_history.get('last_7_days', []), indent=2)}\n\n"
        f"Topics:\n{json.dumps(research.get('topics', []), indent=2)}\n\n"
        "Select the best topic. Return JSON."
    )

    try:
        result = call_model("filter", system, user, max_tokens=800)
    except Exception as e:
        print(f"  [filter] Error calling model: {e}")
        return {"error": str(e)}

    json_match = re.search(r"\{.*\}", result, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError as e:
            print(f"  [filter] JSON parse error: {e}")
            return {"error": f"JSON parse failed: {e}", "raw": result}

    return {"error": "Filter failed — no JSON in response", "raw": result}
