"""
rkitect.ai Content Pipeline — Central Configuration

All settings, model assignments, API keys, paths, and thresholds.
Reels are removed from v2 scope. Reddit is placeholder (commented).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── API Keys ────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ── Model Routing ────────────────────────────────────────────────────────────
# Format: {"provider": "claude" | "openrouter", "model": "model-string"}
#
# TESTING MODE (current) — uses cheaper models across the board.
# Swap to PRODUCTION MODE comments below when ready for higher-quality output.
#
# Claude models:     claude-sonnet-4-20250514 | claude-haiku-4-5-20251001
# OpenRouter models: google/gemini-flash-1.5 | mistralai/mistral-7b-instruct
#                    openai/gpt-4o-mini | meta-llama/llama-3.1-8b-instruct
#                    anthropic/claude-sonnet-4-5 (Claude via OpenRouter)

MODEL_ROUTING = {
    # ── TESTING MODE (cheap models) ──────────────────────────────────────

    # Research — needs web search, speed > quality.
    "research":      {"provider": "openrouter", "model": "google/gemini-flash-1.5"},

    # Filter — lightweight reasoning.
    "filter":        {"provider": "openrouter", "model": "mistralai/mistral-7b-instruct"},

    # LinkedIn — founder voice, thesis-driven. (Testing: GPT-4o-mini)
    "linkedin":      {"provider": "openrouter", "model": "openai/gpt-4o-mini"},

    # Carousel — visual-first educational slides. (Testing: GPT-4o-mini)
    "carousel":      {"provider": "openrouter", "model": "openai/gpt-4o-mini"},

    # Twitter — short, sharp, raw. (Testing: Mistral 7B)
    "twitter":       {"provider": "openrouter", "model": "mistralai/mistral-7b-instruct"},

    # Reddit — placeholder until posting tool confirmed. (Testing: GPT-4o-mini)
    "reddit":        {"provider": "openrouter", "model": "openai/gpt-4o-mini"},

    # QA — brand rule enforcement needs precision. (Testing: GPT-4o-mini)
    "qa":            {"provider": "openrouter", "model": "openai/gpt-4o-mini"},

    # Self-improve — meta-reasoning on prompts. (Testing: GPT-4o-mini)
    "self_improve":  {"provider": "openrouter", "model": "openai/gpt-4o-mini"},

    # Image brief — generates image prompts from content. (Testing: GPT-4o-mini)
    "image_brief":   {"provider": "openrouter", "model": "openai/gpt-4o-mini"},

    # ── PRODUCTION MODE (uncomment and swap when ready) ──────────────────
    # "linkedin":    {"provider": "claude",     "model": "claude-sonnet-4-20250514"},
    # "qa":          {"provider": "claude",     "model": "claude-sonnet-4-20250514"},
    # "self_improve":{"provider": "claude",     "model": "claude-sonnet-4-20250514"},
    # "carousel":    {"provider": "openrouter", "model": "openai/gpt-4o"},
    # "image_brief": {"provider": "openrouter", "model": "openai/gpt-4o"},
}

# ── Content Formats ──────────────────────────────────────────────────────────
# Reels are REMOVED from v2 scope. Only these 4 formats are active.
FORMATS = ["linkedin", "carousel", "twitter", "reddit"]

# ── Buffer ───────────────────────────────────────────────────────────────────
BUFFER_ACCESS_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN")
BUFFER_PROFILES = {
    "instagram": os.getenv("BUFFER_INSTAGRAM_PROFILE_ID"),
    "linkedin":  os.getenv("BUFFER_LINKEDIN_PROFILE_ID"),
    "twitter":   os.getenv("BUFFER_TWITTER_PROFILE_ID"),
    # "reddit":  os.getenv("BUFFER_REDDIT_PROFILE_ID"),  # Uncomment once confirmed
}

# Map internal format names to Buffer platform names
PLATFORM_MAP = {
    "linkedin":  "linkedin",
    "carousel":  "instagram",
    "twitter":   "twitter",
    # "reddit": "reddit",  # Uncomment once confirmed
}

# ── Content Pillars ──────────────────────────────────────────────────────────
CONTENT_PILLARS = {
    "education_insight":            0.35,
    "social_proof_transformation":  0.25,
    "inspiration_trend":            0.20,
    "behind_the_product":           0.10,
    "cta_conversion":               0.10,
}

# ── QA Settings ──────────────────────────────────────────────────────────────
QA_PASS_THRESHOLD = 80
QA_MAX_RETRIES = 3

# ── Self-Improvement ─────────────────────────────────────────────────────────
SELF_IMPROVE_EVERY_N_RUNS = 7     # Rewrite underperforming prompts every 7 runs
SELF_IMPROVE_THRESHOLD = 75       # Rewrite prompt if average score is below this

# ── Paths (relative from rkitect-pipeline/ root) ─────────────────────────────
BASE_DIR = Path(__file__).parent
PROMPTS_DIR = BASE_DIR / "prompts"
CONTEXT_DIR = BASE_DIR / "context"
SKILLS_DIR = BASE_DIR / "skills"
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"
VERSIONS_DIR = PROMPTS_DIR / "versions"
PERF_LOG = CONTEXT_DIR / "skill_performance.json"
POST_HISTORY = CONTEXT_DIR / "post_history.json"

# ── Dashboard ────────────────────────────────────────────────────────────────
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", 5050))
DASHBOARD_SECRET_KEY = os.getenv("DASHBOARD_SECRET_KEY", "dev-secret")
DASHBOARD_USERNAME = os.getenv("DASHBOARD_USERNAME", "admin")
DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "changeme")
