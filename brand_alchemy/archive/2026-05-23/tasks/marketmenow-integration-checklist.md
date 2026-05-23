---
archived: 2026-05-23
archived-by: agentic-saas-marketing-expert
reason: MarketMeNow dead tooling
superseded-by: none — MarketMeNow deprecated
recovery: git mv brand_alchemy/archive/2026-05-23/tasks/marketmenow-integration-checklist.md brand_alchemy/tasks/marketmenow-integration-checklist.md
---

> **ARCHIVED 2026-05-23** — see frontmatter for context. Do not edit. Recovery instructions in frontmatter.

# MarketMeNow Integration Checklist

**Scope:** rkitect.ai posting workflow for LinkedIn, Instagram, and X/Twitter only.  
**Approval path:** Dashboard first, Telegram optional for alerts only.  
**Status:** In progress

---

## What is already decided

- Buffer will handle scheduling and queueing.
- Posts will be generated from rkitect brand context and templates.
- Human approval will happen in the dashboard.
- Telegram is optional and only for notifications.
- Hashtags should come from [brand_alchemy/research/social-community-intelligence-report.md](../research/social-community-intelligence-report.md).

## Buffer channel map

- LinkedIn: `6a020577090476fb990aecc6`
- Instagram: `6a020514090476fb990aeaf3`
- X / Twitter: `6a02054e090476fb990aec04`

## What still needs to be done

- [x] Add OpenRouter API key in `.env` / secret store (you will add)
- [x] Add Buffer bearer token in `.env` / secret store (you will add)
- [x] Map rkitect brand context into the content generation prompt
- [x] Map the template system into the prompt and output format
- [x] Wire the dashboard approval step before Buffer publish
- [x] Keep Telegram as alerts-only fallback, not the main approval path
- [ ] Test LinkedIn post flow end-to-end
- [ ] Test Instagram post flow end-to-end
- [ ] Test X/Twitter post flow end-to-end
- [x] Verify hashtag selection against the rkitect research report
- [x] Confirm platform-specific post length and formatting rules in prompt overrides

## Implemented in code

- [x] Buffer GraphQL publisher module added in `marketmenow/src/web/buffer_publisher.py`
- [x] Dashboard approval now routes LinkedIn/Instagram/Twitter to Buffer publish command
- [x] Buffer config + channel IDs added to `marketmenow/src/web/config.py`
- [x] Buffer env placeholders added to `marketmenow/.env.example`
- [x] rkitect prompt overrides added for LinkedIn, Twitter, and Instagram in imported MarketMeNow project

## Placeholder values to fill later

- `OPENROUTER_API_KEY`
- `BUFFER_BEARER_TOKEN`
- `LINKEDIN_CHANNEL_ID`
- `INSTAGRAM_CHANNEL_ID`
- `TWITTER_CHANNEL_ID`
- `MODEL_NAME`
- `TELEGRAM_ALERT_CHAT_ID` (optional)

## Content rules for generated posts

- Use rkitect brand voice: direct, helpful, studio-native, non-hype.
- Verify claims against [brand_alchemy/brand-bible/_context/claims-and-proof.md](../brand-bible/_context/claims-and-proof.md).
- Prefer the 5 content pillars from [brand_alchemy/brand-bible/_strategy/04-content-system.md](../brand-bible/_strategy/04-content-system.md).
- Use the top hashtags from the rkitect social-community-intelligence report, not generic trend tags.

## Current operating order

1. Generate draft content.
2. Show it in the dashboard.
3. Human approves.
4. Send approved post to Buffer.
5. Buffer schedules or queues it.

## Notes

- Keep this file updated as soon as any key, channel ID, or workflow rule changes.
- Do not add a new workflow until the current one is validated end to end.