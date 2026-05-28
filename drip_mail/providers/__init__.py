"""Email providers."""

from drip_mail.config import EMAIL_PROVIDER
from drip_mail.providers.base import EmailProvider, SendResult
from drip_mail.providers.resend_provider import ResendProvider


def get_email_provider() -> EmailProvider:
    if EMAIL_PROVIDER == "resend":
        return ResendProvider()
    raise ValueError(
        f"Unknown EMAIL_PROVIDER={EMAIL_PROVIDER!r}. Supported: resend"
    )


__all__ = ["EmailProvider", "SendResult", "ResendProvider", "get_email_provider"]
