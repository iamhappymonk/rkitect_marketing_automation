"""Central configuration for drip_mail."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "resend").lower()
MAIL_FROM = os.getenv("MAIL_FROM", "rkitect.ai <no-reply@rkitect.ai>")

def _resolve_path(raw: str, default: Path) -> Path:
    p = Path(raw) if raw else default
    if not p.is_absolute():
        p = ROOT / p
    return p.resolve()


GOOGLE_SERVICE_ACCOUNT_JSON = str(
    _resolve_path(
        os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", ""),
        ROOT / "secrets" / "google-service-account.json",
    )
)
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
GOOGLE_SHEET_TAB = os.getenv("GOOGLE_SHEET_TAB", "Signups")

DRIP_POLL_INTERVAL_SECONDS = int(os.getenv("DRIP_POLL_INTERVAL_SECONDS", "300"))
DRIP_DRY_RUN = os.getenv("DRIP_DRY_RUN", "false").lower() in ("1", "true", "yes")
SIGNUP_LOOKBACK_DAYS = int(os.getenv("SIGNUP_LOOKBACK_DAYS", "30"))

# Optional: override ALL recipient addresses (useful while testing with
# onboarding@resend.dev which only allows your own Resend account email).
# Set to empty string or omit to use actual contact emails from the sheet.
TEST_RECIPIENT_OVERRIDE = os.getenv("TEST_RECIPIENT_OVERRIDE", "")

FLOWS_DIR = ROOT / "flows"
TEMPLATES_DIR = ROOT / "templates"

DASHBOARD_SECRET = os.getenv("DASHBOARD_SECRET", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")
# For Railway deploy: paste full service-account JSON string here instead of a file
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON", "")
