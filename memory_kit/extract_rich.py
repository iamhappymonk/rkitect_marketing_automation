"""Direct-to-Gemini fact + triple extractor over the same sources we ingested.

mem0's distilled atomic-memory output is small and dedupes across sources.
This script asks gemini-2.5-flash to produce a richer per-source extract:
  - 8–15 atomic facts (single sentence, no quotes)
  - 6–20 brand-graph triples in (subject, predicate, object) form

Outputs:
  data/facts.rich.md
  data/brand_graph.rich.md
  data/brand_graph.rich.json   (cytoscape-compatible nodes/edges)

Usage:
  uv run python extract_rich.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from client import _resolve_google_key
from ingest import _build_sources, SOURCES, _read

OUT_DIR = Path(__file__).parent / "data"
FACTS_MD = OUT_DIR / "facts.rich.md"
GRAPH_MD = OUT_DIR / "brand_graph.rich.md"
GRAPH_JSON = OUT_DIR / "brand_graph.rich.json"

PROMPT = """You are extracting structured knowledge from a marketing document for rkitect.ai (an architect-focused AI render studio, pre-launch).

Document label: {label}
Metadata: {meta}

Document body (truncated to 18,000 chars):
\"\"\"{body}\"\"\"

Return STRICT JSON with exactly these keys:
{{
  "facts": [<8 to 15 SHORT atomic facts, one sentence each, present-tense, NO quote marks, NO opinions; each fact must be standalone>],
  "triples": [<6 to 20 [subject, predicate, object] arrays; subjects/objects in snake_case, predicates as short verbs e.g. "uses", "targets", "competes_with", "delivers", "priced_at", "channel_for", "owned_by", "anchors_to">]
}}

Rules:
- Facts must be specific to rkitect.ai's marketing. Do NOT include software-architecture details (mem0/qdrant/SSE/etc). Do NOT include user preferences about Claude or repos.
- Triples are for a brand graph: connect product → channels, segments → pain, agents → roles, pricing → tier, etc. Avoid trivial self-loops.
- Output MUST be JSON parseable, no prose, no code fences.
"""


def _call_gemini(text: str) -> dict:
    from google import genai
    from google.genai import types as gtypes

    client = genai.Client(api_key=_resolve_google_key())
    cfg = gtypes.GenerateContentConfig(
        temperature=0.2,
        response_mime_type="application/json",
        max_output_tokens=4096,
    )
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=text,
        config=cfg,
    )
    raw = (resp.text or "").strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        # may be ```json\n...\n```
        nl = raw.find("\n")
        if nl != -1:
            raw = raw[nl + 1:].rsplit("```", 1)[0]
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  ! json parse error: {e}\n  raw head: {raw[:200]}", flush=True)
        return {"facts": [], "triples": []}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    _build_sources()
    print(f"sources: {len(SOURCES)}", flush=True)

    # Add the brand brief explicitly (it didn't ingest cleanly into mem0)
    brand_brief = OUT_DIR / "_rkitect_brand_brief.md"
    if brand_brief.exists():
        SOURCES.append(("brand:brief-synthesis", brand_brief, {"kind": "brand-brief"}))

    all_facts: dict[str, list[str]] = {}
    all_triples: list[tuple[str, str, str, str]] = []  # subj, pred, obj, source

    for label, path, meta in SOURCES:
        try:
            text = _read(path, max_chars=18_000)
        except Exception as e:  # noqa: BLE001
            print(f"  skip {path}: {e}", flush=True)
            continue
        if not text.strip():
            continue
        prompt = PROMPT.format(label=label, meta=json.dumps(meta), body=text)
        print(f"\n[{label}] extracting from {path.name} ({len(text):,} chars) ...", flush=True)
        try:
            extracted = _call_gemini(prompt)
        except Exception as e:  # noqa: BLE001
            print(f"  ! gemini error: {e}", flush=True)
            continue

        facts = [str(f).strip() for f in (extracted.get("facts") or []) if f]
        triples = [t for t in (extracted.get("triples") or []) if isinstance(t, list) and len(t) == 3]
        all_facts[label] = facts
        for t in triples:
            s, p, o = (str(t[0]).strip(), str(t[1]).strip(), str(t[2]).strip())
            if s and p and o:
                all_triples.append((s, p, o, label))
        print(f"  + {len(facts)} facts · {len(triples)} triples", flush=True)
        time.sleep(0.4)

    # — Write facts.rich.md —
    md: list[str] = [
        "# rkitect-marketing · rich facts",
        "",
        f"Direct Gemini extraction across {len(all_facts)} sources · "
        f"{sum(len(v) for v in all_facts.values())} facts total.",
        "",
    ]
    for label in sorted(all_facts.keys()):
        facts = all_facts[label]
        md.append(f"## {label}  ({len(facts)})")
        md.append("")
        for f in facts:
            md.append(f"- {f}")
        md.append("")
    FACTS_MD.write_text("\n".join(md))
    print(f"\nwrote {FACTS_MD} ({FACTS_MD.stat().st_size:,} bytes)", flush=True)

    # — Build & write brand graph —
    nodes_set = set()
    for s, p, o, _ in all_triples:
        nodes_set.add(s)
        nodes_set.add(o)
    nodes = sorted(nodes_set)
    edges_seen: dict[tuple[str, str, str], set[str]] = {}
    for s, p, o, src in all_triples:
        key = (s, p, o)
        edges_seen.setdefault(key, set()).add(src)

    cy = {
        "nodes": [{"data": {"id": n, "label": n.replace("_", " ")}} for n in nodes],
        "edges": [
            {
                "data": {
                    "id": f"{i}",
                    "source": s,
                    "target": o,
                    "label": p,
                    "sources": sorted(srcs),
                }
            }
            for i, ((s, p, o), srcs) in enumerate(sorted(edges_seen.items()))
        ],
    }
    GRAPH_JSON.write_text(json.dumps(cy, indent=2))

    by_predicate: dict[str, list[tuple[str, str, list[str]]]] = {}
    for (s, p, o), srcs in edges_seen.items():
        by_predicate.setdefault(p, []).append((s, o, sorted(srcs)))

    gmd: list[str] = [
        "# rkitect-marketing · brand graph (rich)",
        "",
        f"{len(nodes)} entities · {len(edges_seen)} unique relationships across "
        f"{len(by_predicate)} predicates · {len(all_triples)} raw triples.",
        "",
        "## Predicates",
        "",
    ]
    for pred in sorted(by_predicate.keys()):
        rows = by_predicate[pred]
        gmd.append(f"### `{pred}`  ({len(rows)})")
        gmd.append("")
        for s, o, srcs in sorted(rows):
            gmd.append(f"- `{s}`  →  `{o}`  · _from {', '.join(srcs)}_")
        gmd.append("")

    gmd.append("## Entities")
    gmd.append("")
    gmd.extend(f"- `{n}`" for n in nodes)
    GRAPH_MD.write_text("\n".join(gmd))
    print(f"wrote {GRAPH_MD} ({GRAPH_MD.stat().st_size:,} bytes)", flush=True)
    print(f"wrote {GRAPH_JSON} ({GRAPH_JSON.stat().st_size:,} bytes)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
