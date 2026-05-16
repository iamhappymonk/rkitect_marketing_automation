# Agents

Agents are reusable role definitions. They must stay brand-agnostic and load brand context at runtime.

## Required Runtime Context

Agents should load:

1. `brand_alchemy/00-start-here.md`
2. Relevant files from `brand_alchemy/brand-bible/_context/`
3. Relevant files from `brand_alchemy/brand-bible/_strategy/`
4. Relevant SOPs and templates

## Rules

- Do not hardcode rkitect.ai positioning into reusable agent files.
- Keep each agent role non-overlapping.
- State assumptions clearly.
- Mark unresolved questions.
- Check claims before public-facing output.
