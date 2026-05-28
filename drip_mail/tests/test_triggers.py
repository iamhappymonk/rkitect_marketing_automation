"""Trigger box unit tests."""

from datetime import datetime, timedelta, timezone

from drip_mail.boxes.triggers import after_days, broadcast, on_signup
from drip_mail.sources.base import Contact


def _contact(**fields: str) -> Contact:
    return Contact(row_index=2, fields=fields)


def test_on_signup_valid_new_row():
    c = _contact(
        Email="user@example.com",
        Timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
    )
    assert on_signup.should_trigger(c, "welcome") is True


def test_on_signup_skips_already_sent():
    c = _contact(Email="user@example.com", welcome_status="sent")
    assert on_signup.should_trigger(c, "welcome") is False


def test_on_signup_skips_invalid_email():
    c = _contact(Email="not-an-email", welcome_status="")
    assert on_signup.should_trigger(c, "welcome") is False


def test_on_signup_skips_old_timestamp():
    old = (datetime.now(timezone.utc) - timedelta(days=60)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    c = _contact(Email="user@example.com", Timestamp=old)
    assert on_signup.should_trigger(c, "welcome", lookback_days=30) is False


def test_after_days_not_ready():
    recent = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    c = _contact(Email="user@example.com", Timestamp=recent)
    assert after_days.should_trigger(c, "feedback", days=7) is False


def test_after_days_ready():
    old = (datetime.now(timezone.utc) - timedelta(days=10)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    c = _contact(Email="user@example.com", Timestamp=old)
    assert after_days.should_trigger(c, "feedback", days=7) is True


def test_broadcast_requires_flag_when_configured():
    c = _contact(Email="user@example.com", send_newsletter="no")
    assert broadcast.should_trigger(c, "feature", flag_column="send_newsletter") is False

    c2 = _contact(Email="user@example.com", send_newsletter="yes")
    assert broadcast.should_trigger(c2, "feature", flag_column="send_newsletter") is True
