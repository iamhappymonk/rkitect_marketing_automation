"""Tests for FastAPI endpoints: health, webhook, dashboard auth."""

from __future__ import annotations

import base64
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from drip_mail import config
from drip_mail.api import app

client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------

def test_health_returns_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}


# ---------------------------------------------------------------------------
# /webhook/signup
# ---------------------------------------------------------------------------

def test_webhook_no_secret_returns_401():
    resp = client.post("/webhook/signup")
    assert resp.status_code == 401


def test_webhook_wrong_secret_returns_401(monkeypatch):
    monkeypatch.setattr(config, "WEBHOOK_SECRET", "correct-secret")
    resp = client.post("/webhook/signup", headers={"x-webhook-secret": "wrong"})
    assert resp.status_code == 401


def test_webhook_correct_secret_runs_flow(monkeypatch):
    monkeypatch.setattr(config, "WEBHOOK_SECRET", "test-secret")
    fake_stats = {"processed": 0, "sent": 0, "failed": 0, "skipped": 0}
    with patch("drip_mail.api.FlowRunner") as MockRunner:
        MockRunner.return_value.run_once.return_value = fake_stats
        resp = client.post("/webhook/signup", headers={"x-webhook-secret": "test-secret"})
    assert resp.status_code == 200
    assert resp.json() == fake_stats
    MockRunner.return_value.run_once.assert_called_once_with(flow_filter="welcome_on_signup")


# ---------------------------------------------------------------------------
# Dashboard basic auth
# ---------------------------------------------------------------------------

def _basic(password: str) -> str:
    token = base64.b64encode(f"user:{password}".encode()).decode()
    return f"Basic {token}"


def test_dashboard_no_auth_returns_401(monkeypatch):
    monkeypatch.setattr(config, "DASHBOARD_SECRET", "secret")
    resp = client.get("/", headers={})
    assert resp.status_code == 401


def test_dashboard_wrong_password_returns_401(monkeypatch):
    monkeypatch.setattr(config, "DASHBOARD_SECRET", "secret")
    resp = client.get("/", headers={"Authorization": _basic("wrong")})
    assert resp.status_code == 401


def test_dashboard_correct_password_loads(monkeypatch):
    monkeypatch.setattr(config, "DASHBOARD_SECRET", "secret")
    fake_stats = {"flows": 1, "sent": 2, "failed": 0, "contacts": 2}
    fake_errors: list = []
    with (
        patch("drip_mail.dashboard.routes._flow_stats", return_value=fake_stats),
        patch("drip_mail.dashboard.routes._load_errors", return_value=fake_errors),
    ):
        resp = client.get("/", headers={"Authorization": _basic("secret")})
    assert resp.status_code == 200
    assert "drip_mail" in resp.text


def test_dashboard_no_secret_set_is_open(monkeypatch):
    monkeypatch.setattr(config, "DASHBOARD_SECRET", "")
    fake_stats = {"flows": 0, "sent": 0, "failed": 0, "contacts": 0}
    with (
        patch("drip_mail.dashboard.routes._flow_stats", return_value=fake_stats),
        patch("drip_mail.dashboard.routes._load_errors", return_value=[]),
    ):
        resp = client.get("/", headers={})
    assert resp.status_code == 200


def test_templates_page_loads(monkeypatch):
    monkeypatch.setattr(config, "DASHBOARD_SECRET", "")
    with patch("drip_mail.dashboard.routes._load_template_list", return_value=[
        {"id": "welcome_signup", "subject": "Welcome", "required_fields": ["Email"], "html_source": "<p>Hi</p>"},
    ]):
        resp = client.get("/templates")
    assert resp.status_code == 200
    assert "welcome_signup" in resp.text


def test_send_page_loads(monkeypatch):
    monkeypatch.setattr(config, "DASHBOARD_SECRET", "")
    with patch("drip_mail.dashboard.routes._load_template_list", return_value=[]):
        resp = client.get("/send")
    assert resp.status_code == 200
    assert "Send Email" in resp.text


def test_send_post_success(monkeypatch):
    monkeypatch.setattr(config, "DASHBOARD_SECRET", "")
    monkeypatch.setattr(config, "MAIL_FROM", "test@test.com")
    mock_result = MagicMock(success=True, message_id="msg-123", error=None)
    with (
        patch("drip_mail.dashboard.routes._load_template_list", return_value=[
            {"id": "welcome_signup", "subject": "Welcome", "required_fields": ["Email"], "html_source": ""},
        ]),
        patch("drip_mail.dashboard.routes.render_template", return_value=("Welcome", "<p>Hi</p>")),
        patch("drip_mail.dashboard.routes.get_email_provider") as mock_provider,
    ):
        mock_provider.return_value.send.return_value = mock_result
        resp = client.post("/send", data={
            "template_id": "welcome_signup",
            "to_email": "test@example.com",
            "name": "Test User",
        })
    assert resp.status_code == 200
    assert "msg-123" in resp.text


def test_send_post_failure(monkeypatch):
    monkeypatch.setattr(config, "DASHBOARD_SECRET", "")
    monkeypatch.setattr(config, "MAIL_FROM", "test@test.com")
    mock_result = MagicMock(success=False, message_id=None, error="API key invalid")
    with (
        patch("drip_mail.dashboard.routes._load_template_list", return_value=[]),
        patch("drip_mail.dashboard.routes.render_template", return_value=("Welcome", "<p>Hi</p>")),
        patch("drip_mail.dashboard.routes.get_email_provider") as mock_provider,
    ):
        mock_provider.return_value.send.return_value = mock_result
        resp = client.post("/send", data={
            "template_id": "welcome_signup",
            "to_email": "test@example.com",
            "name": "",
        })
    assert resp.status_code == 200
    assert "API key invalid" in resp.text
