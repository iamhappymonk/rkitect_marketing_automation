"""
rkitect.ai Content Pipeline — Model Router

Single source of truth for all LLM calls.
Routes to Claude (Anthropic) or OpenRouter based on config.py MODEL_ROUTING.
"""

import anthropic
from openai import OpenAI
from config import ANTHROPIC_API_KEY, OPENROUTER_API_KEY, MODEL_ROUTING
from utils.costs import add_cost_entry, calculate_cost


def _get_anthropic_client() -> anthropic.Anthropic:
    """Lazy-init Anthropic client."""
    if not ANTHROPIC_API_KEY:
        raise ValueError(
            "ANTHROPIC_API_KEY not set. Add it to your .env file."
        )
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def _get_openrouter_client() -> OpenAI:
    """Lazy-init OpenRouter client (OpenAI-compatible API)."""
    if not OPENROUTER_API_KEY:
        raise ValueError(
            "OPENROUTER_API_KEY not set. Add it to your .env file."
        )
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        default_headers={
            "HTTP-Referer": "https://rkitect.ai",
            "X-Title": "rkitect-content-pipeline",
        },
    )


# Module-level client singletons (created on first use)
_anthropic_client = None
_openrouter_client = None


def call_model(
    task: str,
    system: str,
    user: str,
    max_tokens: int = 2000,
    use_web_search: bool = False,
) -> str:
    """
    Route a call to the correct provider + model for the given task.

    Args:
        task: The task key from MODEL_ROUTING (e.g., "research", "linkedin", "qa").
        system: The system prompt (brand context + agent prompt).
        user: The user message (today's topic, content to review, etc.).
        max_tokens: Maximum tokens in the response.
        use_web_search: If True and provider is Claude, enable web search tool.

    Returns:
        The text response as a string.
    """
    global _anthropic_client, _openrouter_client

    config = MODEL_ROUTING.get(task, MODEL_ROUTING["linkedin"])
    provider = config["provider"]
    model = config["model"]

    if provider == "claude":
        if _anthropic_client is None:
            _anthropic_client = _get_anthropic_client()

        kwargs = dict(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        if use_web_search:
            kwargs["tools"] = [
                {"type": "web_search_20250305", "name": "web_search"}
            ]

        response = _anthropic_client.messages.create(**kwargs)
        # Extract token counts from the Usage object (not a dict — use getattr)
        try:
            usage = getattr(response, "usage", None)
            input_tokens = int(getattr(usage, "input_tokens", 0) or 0)
            output_tokens = int(getattr(usage, "output_tokens", 0) or 0)
            cost = calculate_cost(model, input_tokens, output_tokens)
            add_cost_entry({
                "provider": "anthropic",
                "model": model,
                "task": task,
                "cost": cost,
                "meta": {"input_tokens": input_tokens, "output_tokens": output_tokens},
            })
        except Exception:
            pass

        return "".join(
            b.text for b in response.content if b.type == "text"
        )

    elif provider == "openrouter":
        if _openrouter_client is None:
            _openrouter_client = _get_openrouter_client()

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        response = _openrouter_client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=messages,
        )
        # Extract token counts from the CompletionUsage object (not a dict — use getattr)
        try:
            usage = getattr(response, "usage", None)
            # OpenAI-compatible: prompt_tokens / completion_tokens
            input_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
            output_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
            cost = calculate_cost(model, input_tokens, output_tokens)
            add_cost_entry({
                "provider": "openrouter",
                "model": model,
                "task": task,
                "cost": cost,
                "meta": {"input_tokens": input_tokens, "output_tokens": output_tokens},
            })
        except Exception:
            pass

        return response.choices[0].message.content or ""

    raise ValueError(f"Unknown provider: {provider}")
