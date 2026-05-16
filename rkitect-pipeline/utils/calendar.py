"""Persistent content calendar helpers."""
from __future__ import annotations

import json
from datetime import date
from typing import Any, Dict, List, Optional

from config import CALENDAR_FILE


DEFAULT_CALENDAR: List[Dict[str, Any]] = []


def _ensure_file() -> None:
    CALENDAR_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not CALENDAR_FILE.exists():
        CALENDAR_FILE.write_text(json.dumps(DEFAULT_CALENDAR, indent=2), encoding="utf-8")


def load_calendar() -> List[Dict[str, Any]]:
    _ensure_file()
    try:
        raw = CALENDAR_FILE.read_text(encoding="utf-8")
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_calendar(entries: List[Dict[str, Any]]) -> None:
    _ensure_file()
    CALENDAR_FILE.write_text(json.dumps(entries, indent=2), encoding="utf-8")


def get_calendar_entry_for_date(day: str) -> Optional[Dict[str, Any]]:
    for entry in load_calendar():
        if str(entry.get("date", "")).strip() == str(day).strip():
            return entry
    return None


def upsert_calendar_entry(entry: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Insert or replace an entry by date + format, preserving list order."""
    entries = load_calendar()
    target_date = str(entry.get("date", "")).strip()
    target_format = str(entry.get("format", "")).strip()
    updated = []
    replaced = False

    for existing in entries:
        same_date = str(existing.get("date", "")).strip() == target_date
        same_format = str(existing.get("format", "")).strip() == target_format
        if same_date and same_format:
            updated.append(entry)
            replaced = True
        else:
            updated.append(existing)

    if not replaced:
        updated.append(entry)

    save_calendar(updated)
    return updated


def delete_calendar_entry(day: str, fmt: str = "") -> List[Dict[str, Any]]:
    entries = load_calendar()
    filtered = []
    for entry in entries:
        same_date = str(entry.get("date", "")).strip() == str(day).strip()
        same_format = not fmt or str(entry.get("format", "")).strip() == str(fmt).strip()
        if same_date and same_format:
            continue
        filtered.append(entry)
    save_calendar(filtered)
    return filtered


def normalize_calendar_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Return a normalized calendar entry with common keys used by the pipeline."""
    return {
        "date": str(entry.get("date", "")).strip(),
        "day_label": entry.get("day_label", ""),
        "format": entry.get("format", ""),
        "topic": entry.get("topic", ""),
        "psychological_hook": entry.get("psychological_hook", ""),
        "caption_theme": entry.get("caption_theme", ""),
        "caption": entry.get("caption", ""),
        "notes": entry.get("notes", ""),
    }
