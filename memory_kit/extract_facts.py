"""Pull all stored memories from mem0 and emit a deduplicated facts.md.

Groups by source agent_id, keeps per-fact memory_id for traceability.

Usage:
    uv run python extract_facts.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from client import memory, USER_ID

OUT_DIR = Path(__file__).parent / "data"
OUT_MD = OUT_DIR / "facts.md"
OUT_JSON = OUT_DIR / "facts.json"


def main() -> int:
    OUT_DIR.mkdir(exist_ok=True, parents=True)
    mem = memory()
    print(f"reading user_id={USER_ID} ...", flush=True)

    # mem0 v1: get_all returns dict with 'results' list
    res = mem.get_all(user_id=USER_ID)
    items = (res or {}).get("results", res) or []
    print(f"facts in store: {len(items)}", flush=True)

    by_agent: dict[str, list[dict]] = {}
    for it in items:
        agent = (it.get("agent_id") or "_unknown").strip() or "_unknown"
        by_agent.setdefault(agent, []).append(it)

    # Markdown
    lines: list[str] = [
        "# rkitect-marketing · extracted facts",
        "",
        f"Source: mem0 namespace `user_id={USER_ID}` · "
        f"{len(items)} facts across {len(by_agent)} sources.",
        "",
    ]
    for agent in sorted(by_agent.keys()):
        facts = by_agent[agent]
        lines.append(f"## {agent}  ({len(facts)})")
        lines.append("")
        for f in facts:
            mem_id = (f.get("id") or "").split("-")[0]
            text = (f.get("memory") or f.get("data") or "").strip()
            if not text:
                continue
            lines.append(f"- {text}  `[{mem_id}]`")
        lines.append("")

    OUT_MD.write_text("\n".join(lines))
    OUT_JSON.write_text(json.dumps(items, indent=2, default=str))
    print(f"wrote {OUT_MD} ({OUT_MD.stat().st_size:,} bytes)", flush=True)
    print(f"wrote {OUT_JSON} ({OUT_JSON.stat().st_size:,} bytes)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
