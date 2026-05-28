"""Execute drip flows: trigger → template → send → audit."""

from __future__ import annotations

import logging
import time
from typing import Any

from drip_mail import config
from drip_mail.boxes.audit import sheet_audit
from drip_mail.engine.registry import (
    evaluate_trigger,
    flow_audit_columns,
    load_flows,
    render_template,
)
from drip_mail.providers import get_email_provider
from drip_mail.sources.base import ContactSource
from drip_mail.sources.google_sheets import GoogleSheetsSource

logger = logging.getLogger(__name__)


class FlowRunner:
    def __init__(
        self,
        source: ContactSource | None = None,
        dry_run: bool | None = None,
    ) -> None:
        self.source = source or GoogleSheetsSource()
        self.dry_run = config.DRIP_DRY_RUN if dry_run is None else dry_run
        self.provider = get_email_provider()

    def run_once(self, flow_filter: str | None = None) -> dict[str, int]:
        flows = load_flows()
        if flow_filter:
            flows = [f for f in flows if f.get("id") == flow_filter]
        if not flows:
            logger.warning("No enabled flows found")
            return {"processed": 0, "sent": 0, "failed": 0, "skipped": 0}

        step_ids = [f.get("step_id", f.get("id", "step")) for f in flows]
        if not self.dry_run:
            self.source.ensure_audit_columns(step_ids)

        contacts = self.source.fetch_contacts()
        stats = {"processed": 0, "sent": 0, "failed": 0, "skipped": 0}

        for flow in flows:
            flow_id = flow.get("id", "unknown")
            template_id = flow.get("template")
            step_id = flow.get("step_id", flow_id)
            logger.info("Running flow %s (step_id=%s)", flow_id, step_id)

            for contact in contacts:
                if not evaluate_trigger(contact, flow):
                    continue

                stats["processed"] += 1
                email = contact.get("Email")
                name = contact.get("Name") or email

                try:
                    subject, html = render_template(template_id, contact)
                except Exception as exc:  # noqa: BLE001
                    logger.error(
                        "Template error row %s: %s", contact.row_index, exc
                    )
                    stats["failed"] += 1
                    if not self.dry_run:
                        sheet_audit.record_failure(
                            self.source, contact, step_id, str(exc)
                        )
                    continue

                if self.dry_run:
                    logger.info(
                        "[DRY RUN] Would send %r to %s (%s): %s",
                        flow_id,
                        email,
                        name,
                        subject,
                    )
                    stats["sent"] += 1
                    continue

                actual_to = config.TEST_RECIPIENT_OVERRIDE or email
                if config.TEST_RECIPIENT_OVERRIDE and actual_to != email:
                    logger.info(
                        "[TEST_OVERRIDE] Redirecting %s → %s", email, actual_to
                    )
                result = self.provider.send(
                    to=actual_to,
                    subject=subject,
                    html=html,
                    from_addr=config.MAIL_FROM,
                )
                if result.success:
                    sheet_audit.record_success(
                        self.source, contact, step_id, result
                    )
                    logger.info(
                        "Sent %s to %s (message_id=%s)",
                        flow_id,
                        email,
                        result.message_id,
                    )
                    stats["sent"] += 1
                else:
                    sheet_audit.record_failure(
                        self.source,
                        contact,
                        step_id,
                        result.error or "Unknown send error",
                    )
                    logger.error(
                        "Failed %s to %s: %s", flow_id, email, result.error
                    )
                    stats["failed"] += 1

                time.sleep(0.2)

        return stats

    def run_watch(
        self,
        interval_seconds: int | None = None,
        flow_filter: str | None = None,
    ) -> None:
        interval = interval_seconds or config.DRIP_POLL_INTERVAL_SECONDS
        if interval <= 0:
            raise ValueError("Poll interval must be > 0 for watch mode")
        logger.info("Watching every %s seconds (Ctrl+C to stop)", interval)
        while True:
            self.run_once(flow_filter=flow_filter)
            time.sleep(interval)


def list_flows_summary() -> list[dict[str, Any]]:
    summaries = []
    for flow in load_flows():
        summaries.append(
            {
                "id": flow.get("id"),
                "step_id": flow.get("step_id"),
                "template": flow.get("template"),
                "trigger": flow.get("trigger"),
                "audit_columns": flow_audit_columns(flow),
                "path": flow.get("_path"),
            }
        )
    return summaries
