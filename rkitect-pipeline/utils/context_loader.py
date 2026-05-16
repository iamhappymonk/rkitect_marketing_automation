"""
rkitect.ai Content Pipeline — Context Loader

Loads prompt files, brand context, and JSON data files for all agents.
All paths relative to the pipeline root via config.py.
"""

import json
from pathlib import Path
from config import (
    PROMPTS_DIR,
    CONTEXT_DIR,
    POST_HISTORY,
    PERF_LOG,
    SKILLS_DIR,
    PUBLISH_SETTINGS,
    PUBLISH_QUEUE,
)


RUNTIME_FACTS = CONTEXT_DIR / "runtime_facts.json"


def load_prompt(name: str) -> str:
    """
    Load a prompt file by name (without extension).
    E.g., load_prompt("research_agent") loads prompts/research_agent.md
    """
    path = PROMPTS_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


def load_skill(name: str) -> str:
    """
    Load a local skill file by name (without extension).
    E.g., load_skill("meta-prompt-improver") loads skills/meta-prompt-improver.md
    """
    path = SKILLS_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Skill file not found: {path}")
    return path.read_text(encoding="utf-8")


def load_brand_context() -> str:
    """
    Load the unified BRAND-CONTEXT-MASTER.md file.
    This is the single source of truth, derived from brand_alchemy.
    Prepended to every agent's system prompt at startup.
    """
    master_path = CONTEXT_DIR / "BRAND-CONTEXT-MASTER.md"
    
    if master_path.exists():
        base_context = master_path.read_text(encoding="utf-8")
    else:
        # Fallback: concatenate individual files if master doesn't exist
        print(f"  [context_loader] Warning: {master_path} not found. Using fallback context files.")
        context_files = [
            "brand_bible.md",
            "voice_rules.md",
            "content_pillars.md",
            "competitor_watch.md",
            "image_style_guide.md",
        ]

        parts = []
        for fname in context_files:
            path = CONTEXT_DIR / fname
            if path.exists():
                parts.append(path.read_text(encoding="utf-8"))
            else:
                print(f"  [context_loader] Warning: {path} not found, skipping.")

        base_context = "\n\n---\n\n".join(parts)

    if RUNTIME_FACTS.exists():
        try:
            runtime_facts = json.loads(RUNTIME_FACTS.read_text(encoding="utf-8"))
            runtime_block = json.dumps(runtime_facts, indent=2)
            return base_context + "\n\n---\n\nRUNTIME FACTS\n" + runtime_block
        except json.JSONDecodeError:
            return base_context

    return base_context


def load_post_history() -> dict:
    """Load the post history JSON for deduplication checks."""
    if not POST_HISTORY.exists():
        return {"last_7_days": []}
    with open(POST_HISTORY, encoding="utf-8") as f:
        return json.load(f)


def save_post_history(history: dict) -> None:
    """Save updated post history back to disk."""
    with open(POST_HISTORY, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def load_performance_log() -> dict:
    """Load the skill performance log."""
    if not PERF_LOG.exists():
        return {}
    with open(PERF_LOG, encoding="utf-8") as f:
        return json.load(f)


def save_performance_log(log: dict) -> None:
    """Save updated performance log back to disk."""
    PERF_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(PERF_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)


def _load_json(path: Path, default):
    if not path.exists():
        return default
    with open(path, encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default


def _save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_publish_settings() -> dict:
    """Load dashboard publish settings, defaulting to review-first mode."""
    settings = _load_json(
        PUBLISH_SETTINGS,
        {"auto_publish": False, "updated_at": None},
    )
    if "auto_publish" not in settings:
        settings["auto_publish"] = False
    return settings


def save_publish_settings(settings: dict) -> None:
    """Persist publish settings back to disk."""
    payload = {
        "auto_publish": bool(settings.get("auto_publish", False)),
        "updated_at": settings.get("updated_at"),
    }
    _save_json(PUBLISH_SETTINGS, payload)


def load_review_queue() -> list:
    """Load the manual review queue."""
    return _load_json(PUBLISH_QUEUE, [])


def save_review_queue(queue: list) -> None:
    """Persist the manual review queue."""
    _save_json(PUBLISH_QUEUE, queue)
