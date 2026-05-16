"""Feedback agent wrapper.

Provides a simple `apply_feedback` function the dashboard or other parts
of the pipeline can call to apply user feedback conservatively.
"""
from pathlib import Path
from typing import Optional, Dict, Any

from utils.feedback import process_feedback


def apply_feedback(feedback: str, phrase: Optional[str] = None, source_file: Optional[str] = None) -> Dict[str, Any]:
    result = process_feedback(feedback, phrase=phrase)

    if source_file:
        try:
            p = Path(source_file)
            if p.exists():
                txt = p.read_text(encoding="utf-8")
                note = f"\n\n<!-- FEEDBACK APPLIED: {feedback} -->\n"
                # Prepend a short note so reviewers see the change
                p.write_text(note + txt, encoding="utf-8")
                result["patched_file"] = str(p)
        except Exception as e:
            result["file_error"] = str(e)

    return result
