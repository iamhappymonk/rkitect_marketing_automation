"""Discover flows, triggers, and templates."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from drip_mail import config
from drip_mail.boxes.triggers import after_days, broadcast, on_signup
from drip_mail.sources.base import Contact
from drip_mail.sources.google_sheets import audit_column_names

TriggerFn = Callable[..., bool]

TRIGGER_REGISTRY: dict[str, TriggerFn] = {
    "on_signup": on_signup.should_trigger,
    "after_days": after_days.should_trigger,
    "broadcast": broadcast.should_trigger,
}

_jinja_env: Environment | None = None


def _get_jinja() -> Environment:
    global _jinja_env  # noqa: PLW0603
    if _jinja_env is None:
        _jinja_env = Environment(
            loader=FileSystemLoader(str(config.TEMPLATES_DIR)),
            autoescape=True,
            undefined=StrictUndefined,
        )
    return _jinja_env


def load_flows(flows_dir: Path | None = None) -> list[dict[str, Any]]:
    directory = flows_dir or config.FLOWS_DIR
    flows: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.yaml")):
        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if data.get("enabled", True):
            data["_path"] = str(path)
            flows.append(data)
    return flows


def get_trigger_fn(trigger_type: str) -> TriggerFn:
    if trigger_type not in TRIGGER_REGISTRY:
        raise ValueError(
            f"Unknown trigger type {trigger_type!r}. "
            f"Available: {', '.join(TRIGGER_REGISTRY)}"
        )
    return TRIGGER_REGISTRY[trigger_type]


def evaluate_trigger(contact: Contact, flow: dict[str, Any]) -> bool:
    trigger = flow.get("trigger") or {}
    trigger_type = trigger.get("type", "on_signup")
    step_id = flow.get("step_id", flow.get("id", "step"))
    fn = get_trigger_fn(trigger_type)
    kwargs = {k: v for k, v in trigger.items() if k != "type"}
    return fn(contact, step_id, **kwargs)


def load_template_meta(template_id: str) -> dict[str, Any]:
    meta_path = config.TEMPLATES_DIR / f"{template_id}.meta.yaml"
    if not meta_path.is_file():
        return {"subject": "Message from rkitect.ai", "required_fields": []}
    with meta_path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def render_template(template_id: str, contact: Contact) -> tuple[str, str]:
    meta = load_template_meta(template_id)
    required = meta.get("required_fields") or []
    for field in required:
        if not contact.get(field):
            raise ValueError(
                f"Template {template_id!r} requires field {field!r} "
                f"(row {contact.row_index})"
            )

    env = _get_jinja()
    html_template = env.get_template(f"{template_id}.html")
    html = html_template.render(**contact.fields)

    subject_tpl = env.from_string(meta.get("subject", "Message from rkitect.ai"))
    subject = subject_tpl.render(**contact.fields)
    return subject, html


def flow_audit_columns(flow: dict[str, Any]) -> list[str]:
    step_id = flow.get("step_id", flow.get("id", "step"))
    return list(audit_column_names(step_id).values())
