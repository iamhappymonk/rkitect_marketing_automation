---
archived: 2026-05-23
archived-by: agentic-saas-marketing-expert
reason: MarketMeNow handoff — dead tooling
superseded-by: none — MarketMeNow deprecated
recovery: git mv brand_alchemy/archive/2026-05-23/tasks/IDE-AI-HANDOFF-2026-05-14.md brand_alchemy/tasks/IDE-AI-HANDOFF-2026-05-14.md
---

> **ARCHIVED 2026-05-23** — see frontmatter for context. Do not edit. Recovery instructions in frontmatter.

# IDE AI Handoff - 2026-05-14

## Current State

- MarketMeNow dashboard is stable on port `8001`.
- Port `8000` was returning an auth error from a different service, not the dashboard.
- `MMN_WEB_RELOAD` now controls dashboard reload behavior and is off by default.
- `uv` is not available in this Windows shell, so the CLI fallback uses `c:/python313/python.exe -m marketmenow.cli`.
- OpenRouter is wired in as the LLM provider.
- LinkedIn generation now works with project context passed through correctly.

## Verified Commands

- `c:/python313/python.exe -m marketmenow.cli --help`
- `c:/python313/python.exe -m marketmenow.cli run linkedin-post --count 1 --dry-run`

## Important File Changes

- [marketmenow/src/web/app.py](../../marketmenow/src/web/app.py)
- [marketmenow/src/web/cli_runner.py](../../marketmenow/src/web/cli_runner.py)
- [marketmenow/src/marketmenow/integrations/providers/openrouter.py](../../marketmenow/src/marketmenow/integrations/providers/openrouter.py)
- [marketmenow/src/marketmenow/integrations/llm.py](../../marketmenow/src/marketmenow/integrations/llm.py)
- [marketmenow/src/marketmenow/steps/linkedin_post.py](../../marketmenow/src/marketmenow/steps/linkedin_post.py)
- [marketmenow/src/adapters/linkedin/content_generator.py](../../marketmenow/src/adapters/linkedin/content_generator.py)
- [brand_alchemy/tasks/marketmenow-integration-checklist.md](marketmenow-integration-checklist.md)

## .env Status

- `OPENROUTER_API_KEY` is set.
- `LLM_PROVIDER=openrouter`.
- `IMAGE_PROVIDER=openrouter`.
- Buffer channel IDs are present.
- `MMN_WEB_BUFFER_API_TOKEN` still needs a real token.

## What Was Fixed

- Dashboard reload loop.
- CLI startup issues caused by missing optional imports.
- OpenRouter provider integration.
- LinkedIn step failing with `brand is undefined`.

## What Still Needs Work

- Add the real Buffer bearer token.
- Test the LinkedIn, Instagram, and X/Twitter publish flows end to end.
- Confirm Buffer scheduling works from the dashboard approval path.

## Best Next Read

- [brand_alchemy/tasks/marketmenow-integration-checklist.md](marketmenow-integration-checklist.md)
- [marketmenow/.env](../../marketmenow/.env)
- [marketmenow/src/marketmenow/steps/linkedin_post.py](../../marketmenow/src/marketmenow/steps/linkedin_post.py)
