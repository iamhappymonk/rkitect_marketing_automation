"""Write send results back to Google Sheet audit columns."""

from __future__ import annotations

from datetime import datetime, timezone

from drip_mail.providers.base import SendResult
from drip_mail.sources.base import Contact, ContactSource


def record_success(
    source: ContactSource,
    contact: Contact,
    step_id: str,
    result: SendResult,
) -> None:
    source.write_audit(
        contact,
        step_id,
        status="sent",
        sent_at=datetime.now(timezone.utc).isoformat(),
        message_id=result.message_id or "",
        error="",
    )


def record_failure(
    source: ContactSource,
    contact: Contact,
    step_id: str,
    error: str,
) -> None:
    source.write_audit(
        contact,
        step_id,
        status="failed",
        sent_at="",
        message_id="",
        error=error[:500],
    )
