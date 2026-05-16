"""
rkitect.ai Content Pipeline — QA Agent

Scores each format against the 100-point brand rubric.
Retry loop handled in main.py. Logs scores to skill_performance.json.
"""

import json
import re

from model_router import call_model
from utils.context_loader import load_brand_context, load_prompt
from config import QA_PASS_THRESHOLD


def score_content(fmt: str, content: str) -> dict:
    """
    Score a piece of content against the QA rubric.

    Args:
        fmt: Format name (linkedin, carousel, twitter, reddit).
        content: The generated text content to review.

    Returns:
        dict with score, passed, violations, critique.
    """
    system = load_brand_context() + "\n\n---\n\n" + load_prompt("qa_reviewer")
    user = (
        f"Format: {fmt}\n\n"
        f"Content:\n---\n{content}\n---\n\n"
        "Score this. Return JSON with: score, passed, violations, critique."
    )

    try:
        result = call_model("qa", system, user, max_tokens=600)
    except Exception as e:
        return {
            "score": 0,
            "passed": False,
            "violations": [f"QA model error: {e}"],
            "critique": str(e),
        }

    json_match = re.search(r"\{.*\}", result, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group())
            data.setdefault("passed", data.get("score", 0) >= QA_PASS_THRESHOLD)
            return data
        except json.JSONDecodeError:
            pass

    return {
        "score": 0,
        "passed": False,
        "violations": ["QA parse error — could not extract JSON"],
        "critique": result,
    }


def run_qa(generated: dict) -> dict:
    """
    Run QA on all generated content.

    Args:
        generated: dict mapping format names to content strings.

    Returns:
        dict mapping format names to QA result dicts
        (score, passed, violations, critique, content).
    """
    results = {}

    for fmt, content in generated.items():
        # Skip image briefs — only QA text content
        if fmt.endswith("_image_brief"):
            continue

        if not content or content.startswith("ERROR"):
            results[fmt] = {
                "score": 0,
                "passed": False,
                "content": content,
                "violations": ["Generation failed"],
                "critique": "Content generation returned an error.",
            }
            continue

        print(f"      Scoring {fmt}...")
        review = score_content(fmt, content)
        review["content"] = content
        results[fmt] = review

    return results
