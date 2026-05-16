"""Read Kuzu graph DB built by mem0 and emit a brand graph.

Outputs:
    data/brand_graph.json — full nodes/edges dump
    data/brand_graph.md   — human-readable adjacency by entity type

Usage:
    uv run python extract_graph.py
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import kuzu  # type: ignore

from client import KUZU_PATH

OUT_DIR = Path(__file__).parent / "data"
OUT_JSON = OUT_DIR / "brand_graph.json"
OUT_MD = OUT_DIR / "brand_graph.md"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    db_path = Path(KUZU_PATH)
    if not db_path.exists():
        print(f"no kuzu db at {db_path}", flush=True)
        return 1

    db = kuzu.Database(str(db_path), read_only=True)
    conn = kuzu.Connection(db)

    # Discover schema first
    tables = conn.execute("CALL show_tables() RETURN *;").get_as_df()
    print("tables:", tables.to_string(index=False), flush=True)

    nodes: list[dict] = []
    edges: list[dict] = []

    for _, row in tables.iterrows():
        name = row.get("name")
        kind = (row.get("type") or "").upper()
        if not name:
            continue
        try:
            if kind == "NODE":
                df = conn.execute(f"MATCH (n:{name}) RETURN n;").get_as_df()
                for _, r in df.iterrows():
                    n = r["n"]
                    nodes.append({
                        "label": name,
                        **{k: v for k, v in dict(n).items() if not k.startswith("_")},
                    })
            elif kind == "REL":
                df = conn.execute(
                    f"MATCH (a)-[r:{name}]->(b) RETURN a, r, b;"
                ).get_as_df()
                for _, r in df.iterrows():
                    a = dict(r["a"])
                    b = dict(r["b"])
                    rel = dict(r["r"])
                    edges.append({
                        "type": name,
                        "from": a.get("name") or a.get("id") or str(a)[:80],
                        "to":   b.get("name") or b.get("id") or str(b)[:80],
                        **{k: v for k, v in rel.items() if not k.startswith("_")},
                    })
        except Exception as e:  # noqa: BLE001
            print(f"  ! query {name} ({kind}) failed: {e}", flush=True)

    OUT_JSON.write_text(json.dumps({"nodes": nodes, "edges": edges}, indent=2, default=str))
    print(f"nodes: {len(nodes)}  edges: {len(edges)}", flush=True)

    # Markdown view
    by_label: dict[str, list[dict]] = defaultdict(list)
    for n in nodes:
        by_label[n["label"]].append(n)
    by_type: dict[str, list[dict]] = defaultdict(list)
    for e in edges:
        by_type[e["type"]].append(e)

    md: list[str] = [
        "# rkitect-marketing · brand graph",
        "",
        f"From mem0 Kuzu store at `{db_path}`. "
        f"{len(nodes)} entities · {len(edges)} relationships.",
        "",
        "## Entities by type",
        "",
    ]
    for label, items in sorted(by_label.items()):
        md.append(f"### {label}  ({len(items)})")
        md.append("")
        for it in items[:120]:
            name = it.get("name") or it.get("id") or "—"
            md.append(f"- {name}")
        if len(items) > 120:
            md.append(f"- … +{len(items) - 120} more")
        md.append("")

    md.append("## Relationships by type")
    md.append("")
    for rtype, items in sorted(by_type.items()):
        md.append(f"### {rtype}  ({len(items)})")
        md.append("")
        for e in items[:120]:
            md.append(f"- `{e['from']}`  →  `{e['to']}`")
        if len(items) > 120:
            md.append(f"- … +{len(items) - 120} more")
        md.append("")

    OUT_MD.write_text("\n".join(md))
    print(f"wrote {OUT_JSON} ({OUT_JSON.stat().st_size:,} bytes)", flush=True)
    print(f"wrote {OUT_MD} ({OUT_MD.stat().st_size:,} bytes)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
