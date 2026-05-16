"""
rkitect.ai Content Pipeline — Self-Improvement Agent

After every N runs, reads QA score history, identifies underperforming
prompt files, and rewrites them. Old versions are archived to prompts/versions/.
"""

import json
import shutil
from datetime import date
from pathlib import Path

from model_router import call_model
from utils.context_loader import (
    load_brand_context,
    load_prompt,
    load_skill,
    load_performance_log,
    save_performance_log,
)
from config import (
    SELF_IMPROVE_EVERY_N_RUNS,
    SELF_IMPROVE_THRESHOLD,
    PROMPTS_DIR,
    VERSIONS_DIR,
    LOGS_DIR,
)


def count_total_runs() -> int:
    """Count total pipeline runs from log files."""
    if not LOGS_DIR.exists():
        return 0
    return len([f for f in LOGS_DIR.iterdir() if f.suffix == ".json"])


def should_run_improvement() -> bool:
    """Check if it's time for an improvement cycle."""
    n = count_total_runs()
    return n > 0 and n % SELF_IMPROVE_EVERY_N_RUNS == 0


def get_underperforming_formats(perf_log: dict) -> list:
    """
    Identify formats with average scores below threshold.

    Returns:
        List of (format_name, avg_score) tuples, worst first.
    """
    underperforming = []
    for fmt, scores in perf_log.items():
        if len(scores) < 3:
            continue
        recent = scores[-7:]
        recent_avg = sum(s["score"] for s in recent) / len(recent)
        if recent_avg < SELF_IMPROVE_THRESHOLD:
            underperforming.append((fmt, recent_avg))
    return sorted(underperforming, key=lambda x: x[1])


def rewrite_prompt(fmt: str, perf_history: list, current_prompt: str) -> str:
    """
    Use the meta-prompt-improver skill to rewrite an underperforming prompt.

    Args:
        fmt: Format name.
        perf_history: List of score entries for this format.
        current_prompt: Current prompt text.

    Returns:
        New prompt text.
    """
    skill_text = load_skill("meta-prompt-improver")

    system = (
        load_brand_context()
        + "\n\n---\n\n"
        + "SKILL TO APPLY:\n"
        + skill_text
        + "\n\n---\n\n"
        + "You are a prompt engineering expert for the rkitect.ai content pipeline. "
        "Apply the skill exactly while rewriting an underperforming agent prompt "
        "to improve QA scores. Return ONLY the full rewritten prompt text."
    )

    violations_summary = []
    for entry in perf_history[-7:]:
        if entry.get("violations"):
            violations_summary.extend(entry["violations"])

    scores_list = [e["score"] for e in perf_history[-7:]]

    user = (
        f"FORMAT: {fmt}\n\n"
        f"RECENT SCORES (last 7 runs): {scores_list}\n"
        f"COMMON VIOLATIONS: {list(set(violations_summary))}\n\n"
        f"CURRENT PROMPT:\n---\n{current_prompt}\n---\n\n"
        "Rewrite this prompt to fix the failure patterns. "
        "Keep all format-specific instructions. Tighten the voice rules. "
        "Add explicit examples of what good output looks like."
    )

    return call_model("self_improve", system, user, max_tokens=3000)


def archive_prompt(fmt: str) -> None:
    """Archive the current prompt before overwriting."""
    src = PROMPTS_DIR / f"{fmt}_writer.md"
    if not src.exists():
        return
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    dst = VERSIONS_DIR / f"{fmt}_writer_v_{date.today()}.md"
    shutil.copy2(src, dst)
    print(f"      [self_improve] Archived {fmt} prompt -> {dst.name}")


def save_prompt(fmt: str, new_prompt: str) -> None:
    """Write the rewritten prompt to disk."""
    path = PROMPTS_DIR / f"{fmt}_writer.md"
    path.write_text(new_prompt, encoding="utf-8")
    print(f"      [self_improve] Updated {fmt} prompt.")


def run_self_improve(full_qa_results: dict = None) -> None:
    """
    Main entry point. Call at the end of every pipeline run.

    1. Updates performance log with today's QA results.
    2. Checks if it's improvement day (every N runs).
    3. Rewrites worst 2 underperforming prompts if needed.

    Args:
        full_qa_results: QA results dict from run_qa().
    """
    # 1. Update performance log
    if full_qa_results:
        perf_log = load_performance_log()
        for fmt, result in full_qa_results.items():
            if fmt.endswith("_image_brief"):
                continue
            if fmt not in perf_log:
                perf_log[fmt] = []
            perf_log[fmt].append({
                "date": str(date.today()),
                "score": result.get("score", 0),
                "passed": result.get("passed", False),
                "violations": result.get("violations", []),
            })
            perf_log[fmt] = perf_log[fmt][-30:]
        save_performance_log(perf_log)

    # 2. Check if it's improvement day
    if not should_run_improvement():
        return

    print("\n[self_improve] Improvement cycle triggered...")
    perf_log = load_performance_log()
    underperforming = get_underperforming_formats(perf_log)

    if not underperforming:
        print("[self_improve] All formats above threshold. No rewrites needed.")
        return

    # 3. Rewrite worst 2 formats per cycle
    for fmt, avg_score in underperforming[:2]:
        print(
            f"[self_improve] Rewriting [{fmt}] prompt "
            f"(avg score: {avg_score:.1f}/100)..."
        )
        try:
            current_prompt = load_prompt(f"{fmt}_writer")
            new_prompt = rewrite_prompt(fmt, perf_log[fmt], current_prompt)

            if new_prompt and len(new_prompt) > 200:
                archive_prompt(fmt)
                save_prompt(fmt, new_prompt)
            else:
                print(
                    f"[self_improve] [{fmt}] Rewrite too short — "
                    "skipping to protect prompt integrity."
                )
        except Exception as e:
            print(f"[self_improve] [{fmt}] Rewrite failed: {e}")
