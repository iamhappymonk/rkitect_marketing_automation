"""Trigger: broadcast to all rows not yet sent (optional manual flag column)."""

from __future__ import annotations

import re

from drip_mail.sources.base import Contact

_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def should_trigger(
    contact: Contact,
    step_id: str,
    *,
    flag_column: str | None = None,
) -> bool:
    email = contact.get("Email")
    if not email or not _EMAIL_RE.match(email):
        return False

    status = contact.audit_status(step_id)
    if status in ("sent", "skipped"):
        return False

    if flag_column:
        flag = contact.get(flag_column).lower()
        if flag not in ("yes", "true", "1", "y"):
            return False

    return True
