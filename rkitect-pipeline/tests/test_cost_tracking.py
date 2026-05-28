"""
TDD: Cost tracking — calculate_cost() and model_router cost extraction.

Tests written BEFORE implementation. Failing tests confirm bug present.
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import tempfile
import json

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


# ── calculate_cost ─────────────────────────────────────────────────────────────

def test_calculate_cost_gpt4o_mini():
    """gpt-4o-mini: 1000 input + 500 output = $0.000450."""
    from utils.costs import calculate_cost
    cost = calculate_cost("openai/gpt-4o-mini", input_tokens=1000, output_tokens=500)
    assert abs(cost - 0.000450) < 1e-8


def test_calculate_cost_anthropic_sonnet():
    """claude-sonnet-4-20250514: 2000 input + 1000 output = $0.021000."""
    from utils.costs import calculate_cost
    cost = calculate_cost("claude-sonnet-4-20250514", input_tokens=2000, output_tokens=1000)
    assert abs(cost - 0.021000) < 1e-8


def test_calculate_cost_unknown_model_returns_zero():
    """Unknown model returns 0.0 — no crash."""
    from utils.costs import calculate_cost
    cost = calculate_cost("some/unknown-model", input_tokens=5000, output_tokens=2000)
    assert cost == 0.0


def test_calculate_cost_zero_tokens():
    """Zero tokens → zero cost."""
    from utils.costs import calculate_cost
    cost = calculate_cost("openai/gpt-4o-mini", input_tokens=0, output_tokens=0)
    assert cost == 0.0


# ── model_router: Anthropic cost extraction ────────────────────────────────────

def test_anthropic_call_stores_nonzero_cost(tmp_path):
    """Claude call with token usage stores a non-zero cost entry."""
    costs_file = tmp_path / "costs.json"
    costs_file.write_text("[]")

    fake_usage = MagicMock()
    fake_usage.input_tokens = 1000
    fake_usage.output_tokens = 500

    fake_block = MagicMock()
    fake_block.type = "text"
    fake_block.text = "hello"

    fake_response = MagicMock()
    fake_response.content = [fake_block]
    fake_response.usage = fake_usage

    with patch("config.COSTS_FILE", costs_file), \
         patch("utils.costs.COSTS_FILE", costs_file), \
         patch("anthropic.Anthropic") as MockAnthropic:

        mock_client = MagicMock()
        mock_client.messages.create.return_value = fake_response
        MockAnthropic.return_value = mock_client

        import importlib
        import model_router
        importlib.reload(model_router)
        # Reset singleton so our mock client is used
        model_router._anthropic_client = mock_client

        from config import MODEL_ROUTING
        with patch.dict(MODEL_ROUTING, {
            "linkedin": {"provider": "claude", "model": "claude-sonnet-4-20250514"}
        }):
            model_router.call_model("linkedin", system="sys", user="usr")

    entries = json.loads(costs_file.read_text())
    assert len(entries) == 1
    assert entries[0]["cost"] is not None
    assert entries[0]["cost"] > 0, f"Expected cost > 0, got {entries[0]['cost']}"


def test_openrouter_call_stores_nonzero_cost(tmp_path):
    """OpenRouter call with token usage stores a non-zero cost entry."""
    costs_file = tmp_path / "costs.json"
    costs_file.write_text("[]")

    fake_usage = MagicMock()
    fake_usage.prompt_tokens = 800
    fake_usage.completion_tokens = 400

    fake_message = MagicMock()
    fake_message.content = "response text"

    fake_choice = MagicMock()
    fake_choice.message = fake_message

    fake_response = MagicMock()
    fake_response.choices = [fake_choice]
    fake_response.usage = fake_usage

    with patch("config.COSTS_FILE", costs_file), \
         patch("utils.costs.COSTS_FILE", costs_file), \
         patch("openai.OpenAI") as MockOpenAI:

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = fake_response
        MockOpenAI.return_value = mock_client

        import importlib
        import model_router
        importlib.reload(model_router)
        model_router._openrouter_client = mock_client

        from config import MODEL_ROUTING
        with patch.dict(MODEL_ROUTING, {
            "linkedin": {"provider": "openrouter", "model": "openai/gpt-4o-mini"}
        }):
            model_router.call_model("linkedin", system="sys", user="usr")

    entries = json.loads(costs_file.read_text())
    assert len(entries) == 1
    assert entries[0]["cost"] is not None
    assert entries[0]["cost"] > 0, f"Expected cost > 0, got {entries[0]['cost']}"


# ── sum_costs_between skips None ───────────────────────────────────────────────

def test_sum_costs_skips_none_entries(tmp_path):
    """sum_costs_between ignores entries where cost is None."""
    from datetime import date
    costs_file = tmp_path / "costs.json"
    today = date.today().isoformat()
    costs_file.write_text(json.dumps([
        {"timestamp": f"{today}T10:00:00Z", "provider": "openrouter", "model": "x", "task": "linkedin", "cost": None},
        {"timestamp": f"{today}T10:01:00Z", "provider": "openrouter", "model": "x", "task": "linkedin", "cost": 0.001},
    ]))

    with patch("utils.costs.COSTS_FILE", costs_file):
        from utils.costs import sum_costs_between
        total = sum_costs_between(date.today(), date.today())

    assert abs(total - 0.001) < 1e-8


def test_sum_costs_all_none_returns_zero(tmp_path):
    """If all cost entries are None, total is 0.0."""
    from datetime import date
    costs_file = tmp_path / "costs.json"
    today = date.today().isoformat()
    costs_file.write_text(json.dumps([
        {"timestamp": f"{today}T10:00:00Z", "provider": "openrouter", "model": "x", "task": "linkedin", "cost": None},
        {"timestamp": f"{today}T10:01:00Z", "provider": "openrouter", "model": "x", "task": "linkedin", "cost": None},
    ]))

    with patch("utils.costs.COSTS_FILE", costs_file):
        from utils.costs import sum_costs_between
        total = sum_costs_between(date.today(), date.today())

    assert total == 0.0


# ── cost stored with correct metadata ─────────────────────────────────────────

def test_cost_entry_includes_token_counts(tmp_path):
    """Cost entry stores input_tokens and output_tokens in meta."""
    costs_file = tmp_path / "costs.json"
    costs_file.write_text("[]")

    fake_usage = MagicMock()
    fake_usage.prompt_tokens = 300
    fake_usage.completion_tokens = 150

    fake_message = MagicMock()
    fake_message.content = "ok"

    fake_choice = MagicMock()
    fake_choice.message = fake_message

    fake_response = MagicMock()
    fake_response.choices = [fake_choice]
    fake_response.usage = fake_usage

    with patch("config.COSTS_FILE", costs_file), \
         patch("utils.costs.COSTS_FILE", costs_file), \
         patch("openai.OpenAI") as MockOpenAI:

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = fake_response
        MockOpenAI.return_value = mock_client

        import importlib
        import model_router
        importlib.reload(model_router)
        model_router._openrouter_client = mock_client

        from config import MODEL_ROUTING
        with patch.dict(MODEL_ROUTING, {
            "twitter": {"provider": "openrouter", "model": "openai/gpt-4o-mini"}
        }):
            model_router.call_model("twitter", system="sys", user="usr")

    entries = json.loads(costs_file.read_text())
    assert len(entries) == 1
    meta = entries[0].get("meta", {})
    assert meta.get("input_tokens") == 300
    assert meta.get("output_tokens") == 150
