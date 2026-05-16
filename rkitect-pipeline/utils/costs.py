"""Persistent cost tracking utilities.

Stores a simple JSON list of cost entries at the path configured in config.COSTS_FILE.
Each entry is a dict with keys: timestamp (ISO), provider, model, task, cost (float, optional), meta (dict, optional).
"""
from __future__ import annotations

import json
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any, Optional

from config import COSTS_FILE


def _ensure_file():
    if not COSTS_FILE.parent.exists():
        COSTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not COSTS_FILE.exists():
        COSTS_FILE.write_text("[]", encoding="utf-8")


def load_costs() -> List[Dict[str, Any]]:
    _ensure_file()
    try:
        return json.loads(COSTS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_costs(entries: List[Dict[str, Any]]) -> None:
    _ensure_file()
    COSTS_FILE.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


def add_cost_entry(entry: Dict[str, Any]) -> None:
    entries = load_costs()
    # Ensure timestamp
    if "timestamp" not in entry:
        entry["timestamp"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    entries.append(entry)
    save_costs(entries)


def _parse_iso(d: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(d.replace("Z", ""))
    except Exception:
        return None


def get_entries_between(start: date, end: date) -> List[Dict[str, Any]]:
    entries = load_costs()
    out = []
    for e in entries:
        ts = e.get("timestamp")
        if not ts:
            continue
        dt = _parse_iso(ts)
        if not dt:
            continue
        if start <= dt.date() <= end:
            out.append(e)
    return out


def sum_costs_between(start: date, end: date) -> float:
    items = get_entries_between(start, end)
    total = 0.0
    for it in items:
        try:
            c = it.get("cost")
            if c is None:
                continue
            total += float(c)
        except Exception:
            continue
    return round(total, 4)
