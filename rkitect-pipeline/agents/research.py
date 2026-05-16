"""
rkitect.ai Content Pipeline — Research Agent

Runs web search sweep across Reddit, Google Trends, LinkedIn, Twitter/X,
and competitor sites. Returns 5 scored topics as JSON.
"""

import json
import re
from datetime import date

from model_router import call_model
from utils.context_loader import load_brand_context, load_prompt


def run_research() -> dict:
    """
    Execute the research sweep and return parsed topic JSON.

    Returns:
        dict with 'topics' list, or error info if parsing fails.
    """
    system = load_brand_context() + "\n\n---\n\n" + load_prompt("research_agent")
    user = (
        f"Today is {date.today()}. Run your full research sweep. "
        "Return exactly 5 topics as a JSON object."
    )

    # Research benefits from web search — only works natively with Claude provider.
    # OpenRouter models do prompt-instructed search (best effort).
    try:
        result = call_model(
            "research", system, user, max_tokens=2000, use_web_search=True
        )
    except Exception as e:
        print(f"  [research] Error calling model: {e}")
        return {"topics": [], "error": str(e)}

    # Extract JSON from response
    json_match = re.search(r"\{.*\}", result, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError as e:
            print(f"  [research] JSON parse error: {e}")
            return {"topics": [], "raw": result, "error": f"JSON parse failed: {e}"}

    return {"topics": [], "raw": result, "error": "No JSON found in response"}
