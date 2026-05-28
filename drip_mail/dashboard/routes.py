"""Dashboard HTML routes with HTTP Basic Auth."""

from __future__ import annotations

import secrets
from pathlib import Path
from typing import Any, Optional

import yaml
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates

from drip_mail import config
from drip_mail.engine.registry import load_flows, render_template
from drip_mail.providers import get_email_provider
from drip_mail.sources.base import Contact
from drip_mail.sources.google_sheets import GoogleSheetsSource

router = APIRouter()
security = HTTPBasic(auto_error=False)

_TMPL_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(_TMPL_DIR))


def _require_auth(credentials: Optional[HTTPBasicCredentials] = Depends(security)) -> None:
    stored = config.DASHBOARD_SECRET
    if not stored:
        return  # no secret set → open (dev mode)
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Basic"},
        )
    ok = secrets.compare_digest(credentials.password.encode(), stored.encode())
    if not ok:
        raise HTTPException(
            status_code=401,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Basic"},
        )


def _load_template_list() -> list[dict[str, Any]]:
    items = []
    for meta_path in sorted(config.TEMPLATES_DIR.glob("*.meta.yaml")):
        template_id = meta_path.stem.replace(".meta", "")
        with meta_path.open(encoding="utf-8") as f:
            meta = yaml.safe_load(f) or {}
        html_path = config.TEMPLATES_DIR / f"{template_id}.html"
        html_source = html_path.read_text(encoding="utf-8") if html_path.is_file() else ""
        items.append({
            "id": template_id,
            "subject": meta.get("subject", ""),
            "required_fields": meta.get("required_fields") or [],
            "html_source": html_source,
        })
    return items


def _load_errors() -> list[dict[str, Any]]:
    """Fetch contacts from sheet, return rows with any step status=failed."""
    try:
        source = GoogleSheetsSource()
        contacts = source.fetch_contacts()
        flows = load_flows()
        step_ids = [f.get("step_id", f.get("id", "")) for f in flows]
        errors = []
        for contact in contacts:
            for step_id in step_ids:
                if contact.audit_status(step_id) == "failed":
                    errors.append({
                        "email": contact.get("Email", ""),
                        "step": step_id,
                        "error": contact.fields.get(f"{step_id}_error", ""),
                        "sent_at": contact.fields.get(f"{step_id}_sent_at", ""),
                    })
        return errors
    except Exception as exc:  # noqa: BLE001
        return [{"email": "—", "step": "—", "error": str(exc), "sent_at": "—"}]


def _flow_stats() -> dict[str, Any]:
    try:
        source = GoogleSheetsSource()
        contacts = source.fetch_contacts()
        flows = load_flows()
        step_ids = [f.get("step_id", f.get("id", "")) for f in flows]
        sent = failed = 0
        for contact in contacts:
            for step_id in step_ids:
                status = contact.audit_status(step_id)
                if status == "sent":
                    sent += 1
                elif status == "failed":
                    failed += 1
        return {"flows": len(flows), "sent": sent, "failed": failed, "contacts": len(contacts)}
    except Exception:  # noqa: BLE001
        return {"flows": 0, "sent": 0, "failed": 0, "contacts": 0}


@router.get("/", response_class=HTMLResponse)
async def overview(request: Request, _: None = Depends(_require_auth)):
    stats = _flow_stats()
    errors = _load_errors()
    return templates.TemplateResponse(request, "index.html", {
        "active": "overview",
        "stats": stats,
        "errors": errors,
    })


@router.get("/templates", response_class=HTMLResponse)
async def template_list(request: Request, _: None = Depends(_require_auth)):
    tmpl_list = _load_template_list()
    return templates.TemplateResponse(request, "templates.html", {
        "active": "templates",
        "templates": tmpl_list,
    })


@router.get("/send", response_class=HTMLResponse)
async def send_page(request: Request, template: str = "", _: None = Depends(_require_auth)):
    tmpl_list = _load_template_list()
    return templates.TemplateResponse(request, "send.html", {
        "active": "send",
        "templates": tmpl_list,
        "selected": template,
        "result": None,
    })


@router.post("/send", response_class=HTMLResponse)
async def send_email(
    request: Request,
    template_id: str = Form(...),
    to_email: str = Form(...),
    name: str = Form(""),
    _: None = Depends(_require_auth),
):
    tmpl_list = _load_template_list()
    result: dict[str, Any] = {}
    try:
        contact = Contact(row_index=0, fields={"Email": to_email.strip(), "Name": name.strip()})
        subject, html = render_template(template_id, contact)
        provider = get_email_provider()
        send_result = provider.send(
            to=to_email.strip(),
            subject=subject,
            html=html,
            from_addr=config.MAIL_FROM,
        )
        if send_result.success:
            result = {"success": True, "message": f"Sent to {to_email} (id={send_result.message_id})"}
        else:
            result = {"success": False, "message": send_result.error or "Send failed"}
    except Exception as exc:  # noqa: BLE001
        result = {"success": False, "message": str(exc)}

    return templates.TemplateResponse(request, "send.html", {
        "active": "send",
        "templates": tmpl_list,
        "selected": template_id,
        "result": result,
    })
