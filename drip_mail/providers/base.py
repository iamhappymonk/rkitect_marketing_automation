"""Email provider abstraction — swap Resend for another provider via config."""

from dataclasses import dataclass
from typing import Protocol


@dataclass
class SendResult:
    success: bool
    message_id: str | None = None
    error: str | None = None


class EmailProvider(Protocol):
    def send(
        self,
        *,
        to: str,
        subject: str,
        html: str,
        from_addr: str,
    ) -> SendResult: ...
