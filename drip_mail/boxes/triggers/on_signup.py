"""Trigger: new signup row eligible for welcome email."""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from drip_mail.config import SIGNUP_LOOKBACK_DAYS
from drip_mail.sources.base import Contact

_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _parse_timestamp(raw: str) -> datetime | None:
    raw = (raw or "").strip()
    if not raw:
        return None
    formats = (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y",
    )
    for fmt in formats:
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def should_trigger(
    contact: Contact,
    step_id: str,
    *,
    lookback_days: int | None = None,
) -> bool:
    email = contact.get("Email")
    if not email or not _EMAIL_RE.match(email):
        return False

    status = contact.audit_status(step_id)
    if status == "sent":
        return False
    if status == "skipped":
        return False

    days = lookback_days if lookback_days is not None else SIGNUP_LOOKBACK_DAYS
    if days > 0:
        ts = _parse_timestamp(contact.get("Timestamp"))
        if ts is not None:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            if ts < cutoff:
                return False

    return True
