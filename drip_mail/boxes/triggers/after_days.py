"""Trigger: send after N days since Timestamp (for future feedback drips)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from drip_mail.boxes.triggers.on_signup import _parse_timestamp
from drip_mail.sources.base import Contact


def should_trigger(
    contact: Contact,
    step_id: str,
    *,
    days: int = 7,
) -> bool:
    status = contact.audit_status(step_id)
    if status in ("sent", "skipped"):
        return False

    ts = _parse_timestamp(contact.get("Timestamp"))
    if ts is None:
        return False

    eligible_at = ts + timedelta(days=days)
    return datetime.now(timezone.utc) >= eligible_at
