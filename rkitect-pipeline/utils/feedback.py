"""Feedback-processing utilities.

This module keeps the feedback loop conservative and deterministic:
- record runtime facts,
- patch prompt files with guardrails,
- write a human-readable diff file,
- and surface matching generated outputs for review.

It does not attempt freeform prompt rewriting. That is intentionally left
to the generation agent, which can regenerate the post using the feedback
as critique once the context has been corrected.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from config import PROMPTS_DIR, CONTEXT_DIR, OUTPUT_DIR


RUNTIME_FACTS = CONTEXT_DIR / "runtime_facts.json"
FEEDBACK_DIFFS_DIR = CONTEXT_DIR / "feedback-diffs"
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


def write_feedback_diff(feedback: str, source_file: str = "", before: str = "", after: str = "") -> Path:
    """Write a small diff-style markdown record for auditability."""
    FEEDBACK_DIFFS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    source_name = Path(source_file).stem if source_file else "feedback"
    path = FEEDBACK_DIFFS_DIR / f"{stamp}-{source_name}.md"
    body = [
        f"# Feedback Patch {stamp}",
        "",
        f"Source: {source_file or 'n/a'}",
        f"Feedback: {feedback}",
        "",
        "## Before",
        before or "",
        "",
        "## After",
        after or "",
    ]
    path.write_text("\n".join(body), encoding="utf-8")
    return path


def needs_launch_guard(feedback: str) -> bool:
    lf = feedback.lower()
    markers = [
        "not launch",
        "haven't launched",
        "haven not launched",
        "haven't even launched",
        "we havent launched",
        "hasn't launched",
        "isn't launched",
    ]
    return any(marker in lf for marker in markers)


def apply_global_feedback_fixes(feedback: str) -> Dict[str, Any]:
    """Apply broad prompt/context fixes inferred from feedback."""
    out: Dict[str, Any] = {"actions": [], "modified_prompts": []}

    if needs_launch_guard(feedback):
        set_runtime_fact("product_launched", False)
        out["actions"].append("set product_launched=false")
        modified = ensure_prompt_guards()
        out["modified_prompts"] = [str(p) for p in modified]
        out["actions"].append(f"patched {len(modified)} prompt files with launch guard")

    return out


def process_feedback(feedback: str, phrase: str = None, source_file: str = "") -> Dict[str, Any]:
    """Process user feedback and apply conservative fixes.

    Heuristics implemented for now:
    - If feedback indicates product not launched (contain "not launch", "haven't launched", "haven't launched"), set `product_launched` to false and add prompt guards.
    - If phrase provided, find outputs containing it and return their paths.
    """
    out: Dict[str, Any] = {"actions": [], "matches": []}

    global_fixes = apply_global_feedback_fixes(feedback)
    out["actions"].extend(global_fixes.get("actions", []))
    if global_fixes.get("modified_prompts"):
        out["modified_prompts"] = global_fixes["modified_prompts"]

    if phrase:
        matches = find_outputs_containing(phrase)
        out["matches"] = [str(p) for p in matches]
        out["actions"].append(f"found {len(matches)} outputs containing phrase")

    if source_file:
        out["source_file"] = source_file

    return out
