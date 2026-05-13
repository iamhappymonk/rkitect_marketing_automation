# CLAUDE.md

This is the marketing team workspace for rkitect.ai.

## Workspace Map

- `brand_alchemy/brand-bible/_context/` contains brand foundation context files.
- `brand_alchemy/brand-bible/` contains approved brand strategy, messaging, audience, voice, and visual direction.
- `brand_alchemy/company-os/` contains operating rules, ownership, decisions, glossary, and change logs.
- `brand_alchemy/research/` contains market, audience, competitor, channel, and community intelligence.
- `brand_alchemy/sops/` contains standard operating procedures for marketing workflows.
- `brand_alchemy/templates/` contains reusable Markdown templates.
- `brand_alchemy/tasks/` contains the active task board, milestones, open questions, and validation log.
- `brand_alchemy/agents/` contains reusable agent role definitions.
- `brand_alchemy/skills/` contains reusable process skills.
- `brand_alchemy/archive/` contains superseded drafts and deprecated notes.
- `skills/` contains vendored Codex skill directories that can be shared with the team through Git.

## Key Rules

- All durable project outputs must be Markdown files.
- All marketing outputs must follow the brand voice and positioning in `brand_alchemy/brand-bible/`.
- Load additional files from `brand_alchemy/brand-bible/_context/` and `brand_alchemy/research/` when they are directly relevant to the task.
- When creating skills for this project, keep them brand-agnostic. Skills define workflow and process only.
- Vendored skills in `skills/` must also stay brand-agnostic. Do not bake rkitect.ai facts into them.
- When creating agents, keep them brand-agnostic. Agents must not hardcode rkitect.ai-specific details.
- Agents and skills should pull brand context at runtime from `brand_alchemy/brand-bible/_context/`, `brand_alchemy/research/`, and `brand_alchemy/brand-bible/_strategy/`.
- Each agent must have a clear, non-overlapping role.
- Public claims about speed, accuracy, pricing, compliance, registration, customer outcomes, and competitors must be checked against `brand_alchemy/brand-bible/_context/claims-and-proof.md` before use.
- AI outputs are drafts until reviewed by a human owner.
- Do not publish, send outreach, or make customer-facing claims without approval.

## Required Context Loading Order

1. `brand_alchemy/00-start-here.md`
2. `brand_alchemy/brand-bible/_context/company-profile.md`
3. `brand_alchemy/brand-bible/_context/brand-bible.md`
4. Any relevant context, research, SOP, or template file for the specific task.

## Output Rules

- Use short, clear, studio-native language.
- Avoid generic AI hype.
- Prefer specific workflow language over abstract marketing language.
- Mark assumptions clearly.
- Add unresolved decisions to `brand_alchemy/tasks/open-questions.md`.
- Add approved strategic changes to `brand_alchemy/company-os/change-log.md`.
