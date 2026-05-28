"""Config check tests."""

from drip_mail.engine.check import run_checks


def test_check_reports_missing_env(monkeypatch, tmp_path):
    monkeypatch.setattr("drip_mail.engine.check.config.RESEND_API_KEY", "")
    monkeypatch.setattr("drip_mail.engine.check.config.GOOGLE_SHEET_ID", "")
    monkeypatch.setattr(
        "drip_mail.engine.check.config.GOOGLE_SERVICE_ACCOUNT_JSON",
        str(tmp_path / "missing.json"),
    )
    report = run_checks()
    assert report["ok"] is False
    names = {c["name"] for c in report["checks"]}
    assert "RESEND_API_KEY" in names
    assert "GOOGLE_SHEET_ID" in names
