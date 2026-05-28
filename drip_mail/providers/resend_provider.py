"""Resend email provider."""

from __future__ import annotations

import resend

from drip_mail.config import MAIL_FROM, RESEND_API_KEY
from drip_mail.providers.base import SendResult


class ResendProvider:
    def __init__(self, api_key: str | None = None, default_from: str | None = None) -> None:
        self._api_key = api_key or RESEND_API_KEY
        self._default_from = default_from or MAIL_FROM
        if self._api_key:
            resend.api_key = self._api_key

    def send(
        self,
        *,
        to: str,
        subject: str,
        html: str,
        from_addr: str | None = None,
    ) -> SendResult:
        if not self._api_key:
            return SendResult(success=False, error="RESEND_API_KEY is not set")

        params: resend.Emails.SendParams = {
            "from": from_addr or self._default_from,
            "to": [to],
            "subject": subject,
            "html": html,
        }
        try:
            response = resend.Emails.send(params)
            message_id = None
            if isinstance(response, dict):
                message_id = response.get("id")
            elif hasattr(response, "get"):
                message_id = response.get("id")  # type: ignore[union-attr]
            return SendResult(success=True, message_id=message_id)
        except Exception as exc:  # noqa: BLE001 — surface provider errors to audit
            return SendResult(success=False, error=str(exc))
