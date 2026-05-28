"""Validate drip_mail configuration and connectivity."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from drip_mail import config
from drip_mail.engine.registry import load_flows
from drip_mail.sources.google_sheets import GoogleSheetsSource


def run_checks() -> dict[str, Any]:
    results: dict[str, Any] = {"ok": True, "checks": []}

    def add(name: str, ok: bool, detail: str = "") -> None:
        results["checks"].append({"name": name, "ok": ok, "detail": detail})
        if not ok:
            results["ok"] = False

    # Env
    add(
        "RESEND_API_KEY",
        bool(config.RESEND_API_KEY),
        "set" if config.RESEND_API_KEY else "missing in .env",
    )
    add(
        "GOOGLE_SHEET_ID",
        bool(config.GOOGLE_SHEET_ID),
        "set" if config.GOOGLE_SHEET_ID else "missing in .env",
    )
    cred_path = Path(config.GOOGLE_SERVICE_ACCOUNT_JSON)
    add(
        "GOOGLE_SERVICE_ACCOUNT_JSON",
        cred_path.is_file(),
        str(cred_path) if cred_path.is_file() else f"file not found: {cred_path}",
    )
    add("EMAIL_PROVIDER", True, config.EMAIL_PROVIDER)
    add("MAIL_FROM", True, config.MAIL_FROM)

    flows = load_flows()
    add("flows", len(flows) > 0, f"{len(flows)} enabled flow(s)")

    # Sheet connectivity (only if creds + sheet id present)
    if cred_path.is_file() and config.GOOGLE_SHEET_ID:
        try:
            source = GoogleSheetsSource()
            contacts = source.fetch_contacts()
            add(
                "google_sheets_read",
                True,
                f"tab={config.GOOGLE_SHEET_TAB!r}, rows={len(contacts)}",
            )
            if contacts:
                sample = contacts[0]
                add(
                    "sample_row",
                    bool(sample.get("Email")),
                    f"row {sample.row_index}, email={sample.get('Email') or '(empty)'}",
                )
        except Exception as exc:  # noqa: BLE001
            add("google_sheets_read", False, str(exc))

    return results
