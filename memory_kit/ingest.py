"""Ingest references/ documents into rkitect-marketing mem0 namespace.

Walks the knowledge bank under ../references/drive_dump/HappyMonk/ + repo-level
docs (CLAUDE.md, references/README.md), chunks long files, and writes them to
mem0 with stable agent_id labels for source tracking.

Usage:
    uv run python ingest.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from client import memory, USER_ID

ROOT = Path(__file__).resolve().parents[1]
REFS = ROOT / "references" / "drive_dump" / "HappyMonk"
EXTRACTED = REFS / "marketing" / "_extracted"
SAMPLE = REFS / "sample-content"

# (label, text, metadata) tuples
SOURCES: list[tuple[str, Path, dict]] = []


def _add_text(label: str, path: Path, meta: dict | None = None) -> None:
    if not path.exists():
        return
    SOURCES.append((label, path, meta or {}))


def _add_json_manifest(label: str, path: Path) -> None:
    if not path.exists():
        return
    try:
        data = json.loads(path.read_text())
    except Exception as e:  # noqa: BLE001
        print(f"  skip (json error) {path}: {e}", flush=True)
        return
    SOURCES.append((label, path, {"items": len(data) if isinstance(data, list) else 1}))


def _build_sources() -> None:
    # 1. Strategy + intel docs
    _add_text("brand:linkedin-strategy",
              EXTRACTED / "linkedin-strat.txt",
              {"kind": "strategy", "channel": "linkedin"})
    _add_text("brand:social-community-intel",
              EXTRACTED / "social-community-intel-report.txt",
              {"kind": "research", "channel": "x+linkedin", "scope": "outreach-targets"})
    _add_text("brand:content-generation-pipeline",
              EXTRACTED / "content-generation-strings.txt",
              {"kind": "operations", "scope": "content-pipeline"})
    _add_text("brand:carousel-doc",
              EXTRACTED / "carousel-doc-partial.txt",
              {"kind": "creative-brief", "scope": "carousel"})

    # 2. Finished sample posts (10 platform-ready posts)
    _add_text("brand:sample-posts",
              SAMPLE / "posts.md",
              {"kind": "creative-output", "channel": "multi", "count": 10})

    # 3. Manifests (asset metadata schemas)
    _add_json_manifest("brand:before-after-manifest",
                       REFS / "before-after" / "manifest.json")
    _add_json_manifest("brand:posts-manifest",
                       REFS / "posts" / "manifest.json")
    _add_json_manifest("brand:reels-manifest",
                       REFS / "reels" / "manifest.json")
    _add_json_manifest("brand:posts-final",
                       SAMPLE / "posts-final.json")

    # 4. Project context
    _add_text("project:claude-md",
              ROOT / "CLAUDE.md",
              {"kind": "project-context"})
    _add_text("project:references-readme",
              ROOT / "references" / "README.md",
              {"kind": "project-context"})


def _read(path: Path, max_chars: int = 40_000) -> str:
    text = path.read_text(errors="replace")
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[truncated]"
    return text


def _chunk(text: str, target: int = 6_000) -> list[str]:
    """Split into ~target-char paragraphs without breaking sentences hard."""
    if len(text) <= target:
        return [text]
    paras = text.split("\n\n")
    out: list[str] = []
    cur = ""
    for p in paras:
        if len(cur) + len(p) + 2 > target and cur:
            out.append(cur.strip())
            cur = p + "\n\n"
        else:
            cur += p + "\n\n"
    if cur.strip():
        out.append(cur.strip())
    return out


def main() -> int:
    _build_sources()
    print(f"Sources to ingest: {len(SOURCES)}", flush=True)
    mem = memory()
    print(f"Mem0 ready · user_id={USER_ID}", flush=True)

    total_chunks = 0
    started = time.time()
    for label, path, meta in SOURCES:
        try:
            text = _read(path)
        except Exception as e:  # noqa: BLE001
            print(f"  skip {path}: {e}", flush=True)
            continue
        if not text.strip():
            print(f"  skip empty {path}", flush=True)
            continue
        chunks = _chunk(text)
        print(f"\n[{label}] {path.name} · {len(text):,} chars · {len(chunks)} chunk(s)", flush=True)
        for i, ch in enumerate(chunks, 1):
            try:
                # mem0 v1 add() returns dict w/ 'results' key on success
                res = mem.add(
                    ch,
                    user_id=USER_ID,
                    agent_id=label,
                    metadata={**meta, "source_path": str(path), "chunk": i, "of": len(chunks)},
                )
                added = (res or {}).get("results", res)
                print(f"  · chunk {i}/{len(chunks)} added · {len(ch):,} chars", flush=True)
                total_chunks += 1
            except Exception as e:  # noqa: BLE001
                print(f"  ! chunk {i} error: {e}", flush=True)
        time.sleep(0.4)  # gentle on Gemini quota

    elapsed = time.time() - started
    print(f"\nDONE · {total_chunks} chunks ingested in {elapsed:.1f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
