"""Feedback-processing utilities.

Simple, conservative implementation that:
- Finds generated outputs containing a given phrase.
- Writes runtime facts to `context/runtime_facts.json`.
- Adds a short guard to all prompt templates to instruct models to consult runtime facts.

This is intentionally lightweight and safe — it does not attempt complex NLP rewrites.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any

from config import PROMPTS_DIR, CONTEXT_DIR, OUTPUT_DIR


RUNTIME_FACTS = CONTEXT_DIR / "runtime_facts.json"
PROMPT_GUARD_MARKER = "<!-- RUNTIME_FACTS_GUARD -->"
PROMPT_GUARD_TEXT = (
    "<!-- RUNTIME_FACTS_GUARD -->\n"
    "Note to model: consult runtime facts in context/runtime_facts.json. "
    "Do not assert product launch or other company state unless the runtime fact `product_launched` is true.\n\n"
)


def find_outputs_containing(phrase: str) -> List[Path]:
    matches: List[Path] = []
    for file in OUTPUT_DIR.rglob("*.md"):
        try:
            txt = file.read_text(encoding="utf-8")
        except Exception:
            continue
        if phrase in txt:
            matches.append(file)
    return matches


def _ensure_runtime_facts():
    if not CONTEXT_DIR.exists():
        CONTEXT_DIR.mkdir(parents=True, exist_ok=True)
    if not RUNTIME_FACTS.exists():
        RUNTIME_FACTS.write_text(json.dumps({}, indent=2), encoding="utf-8")


def set_runtime_fact(key: str, value: Any) -> None:
    _ensure_runtime_facts()
    try:
        data = json.loads(RUNTIME_FACTS.read_text(encoding="utf-8"))
    except Exception:
        data = {}
    data[key] = value
    RUNTIME_FACTS.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_runtime_facts() -> Dict[str, Any]:
    _ensure_runtime_facts()
    try:
        return json.loads(RUNTIME_FACTS.read_text(encoding="utf-8"))
    except Exception:
        return {}


def ensure_prompt_guards() -> List[Path]:
    """Prepend a guard to each prompt file if not already present.

    Returns list of modified prompt file paths.
    """
    modified: List[Path] = []
    if not PROMPTS_DIR.exists():
        return modified
    for p in PROMPTS_DIR.glob("*.md"):
        try:
            txt = p.read_text(encoding="utf-8")
        except Exception:
            continue
        if PROMPT_GUARD_MARKER in txt:
            continue
        newtxt = PROMPT_GUARD_TEXT + txt
        try:
            p.write_text(newtxt, encoding="utf-8")
            modified.append(p)
        except Exception:
            continue
    return modified


def process_feedback(feedback: str, phrase: str = None) -> Dict[str, Any]:
    """Process user feedback and apply conservative fixes.

    Heuristics implemented for now:
    - If feedback indicates product not launched (contain "not launch", "haven't launched", "haven't launched"), set `product_launched` to false and add prompt guards.
    - If phrase provided, find outputs containing it and return their paths.
    """
    out: Dict[str, Any] = {"actions": [], "matches": []}

    lf = feedback.lower()
    if "not launch" in lf or "haven't launched" in lf or "haven not launched" in lf or "haven't even launched" in lf or "we havent launched" in lf:
        set_runtime_fact("product_launched", False)
        out["actions"].append("set product_launched = false")
        modified = ensure_prompt_guards()
        out["actions"].append(f"added prompt guards to {len(modified)} prompt files")

    if phrase:
        matches = find_outputs_containing(phrase)
        out["matches"] = [str(p) for p in matches]
        out["actions"].append(f"found {len(matches)} outputs containing phrase")

    return out
