"""Project-scoped mem0 client for rkitect marketing.

Local-only. Gemini LLM + embeddings, Qdrant vector store, Kuzu graph.
Paths under ~/.mem0/rkitect-marketing/ to keep separate from archiai memory.
"""

from __future__ import annotations

import os
from pathlib import Path

USER_ID = "rkitect-marketing"

_BASE = Path.home() / ".mem0" / USER_ID
QDRANT_PATH = str(_BASE / "qdrant_v2")
KUZU_PATH = str(_BASE / "kuzu.db")


def _ensure_dirs() -> None:
    _BASE.mkdir(parents=True, exist_ok=True)
    # archiai's agno server holds the lock on ~/.mem0/migrations_qdrant via
    # mem0's telemetry vector store. Disable telemetry so we can co-exist.
    os.environ.setdefault("MEM0_TELEMETRY", "False")


def _resolve_google_key() -> str:
    """Pull GOOGLE_API_KEY from env or archiai/.env (read-only)."""
    key = os.getenv("GOOGLE_API_KEY", "").strip()
    if key:
        return key
    env_path = Path("/Users/b/Documents/GitHub/archiai/.env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("GOOGLE_API_KEY="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                if value:
                    os.environ["GOOGLE_API_KEY"] = value
                    return value
    raise RuntimeError("GOOGLE_API_KEY not found in env or archiai/.env")


def build_config() -> dict:
    api_key = _resolve_google_key()
    return {
        "llm": {
            "provider": "gemini",
            "config": {
                "model": "gemini-2.5-flash",
                "api_key": api_key,
            },
        },
        "embedder": {
            "provider": "gemini",
            "config": {
                "model": "models/gemini-embedding-001",
                "api_key": api_key,
                "embedding_dims": 768,
            },
        },
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "collection_name": "rkitect_marketing",
                "path": QDRANT_PATH,
                "embedding_model_dims": 768,
            },
        },
        "graph_store": {
            "provider": "kuzu",
            "config": {
                "db": KUZU_PATH,
            },
        },
    }


_memory = None


def memory():
    """Singleton mem0 Memory instance."""
    global _memory
    if _memory is not None:
        return _memory
    _ensure_dirs()
    from mem0 import Memory  # type: ignore

    _memory = Memory.from_config(build_config())
    return _memory
