"""Template rendering tests."""

from drip_mail.engine.registry import render_template
from drip_mail.sources.base import Contact


def test_welcome_signup_render():
    contact = Contact(
        row_index=2,
        fields={
            "Timestamp": "2026-05-27 10:00:00",
            "Name": "Alex",
            "Email": "alex@example.com",
            "Contact": "",
            "Role": "Architect",
        },
    )
    subject, html = render_template("welcome_signup", contact)
    assert "rkitect.ai beta cohort" in subject
    assert "Hey Alex" in html
    assert "alex@example.com" in html  # rendered in footer unsubscribe line
