# Brand Bible Directory Structure

This is the central source of truth for rkitect.ai brand strategy, messaging, and marketing outputs.

## Navigation

### Core Strategy Documents (`_strategy/`)

These are the foundational brand documents that guide all marketing work:

- **01-identity.md** — Brand essence, values, personality, and what we want to be known for
- **02-positioning.md** — Market category, differentiation, and positioning statement
- **03-audience-personas.md** — Target audiences and customer personas
- **04-messaging.md** — Key messages, pillars, and talking points
- **05-voice-and-tone.md** — How we write and communicate
- **06-visual-direction.md** — Design system, colors, imagery, and visual style
- **07-go-to-market.md** — GTM strategy, channels, and launch plan

### Support Folders

#### \_context/

Reference materials used to inform brand strategy. Before creating any content, load context files here.

- Company background and positioning
- Market research findings
- Competitor analysis
- Customer insights and feedback

#### \_sop/

Standard operating procedures for brand work.

- Content approval workflows
- Brand review checklists
- Publishing guidelines
- Campaign launch procedures

#### \_templates/

Reusable brand-compliant templates.

- Email templates
- Social post templates
- Landing page templates
- Presentation templates
- Copywriting templates

### Channel-Specific Output Folders

Marketing outputs organized by channel and type:

- **ads/** — Paid ad copy, creative briefs, and ad variations (Google, LinkedIn, Meta, etc.)
- **pages/** — Website page copy, landing pages, and website sections
- **presentations/** — Pitch decks, webinar slides, and investor presentations
- **reports/** — Analysis reports, case studies, and data-driven reports
- **research/** — Market research, survey results, and trend analysis
- **seo/** — SEO content, keyword strategy, and organic optimization
- **social/** — Social media posts, thread content, and community content

## How Agents Should Use This Folder

1. **Start here:** Read the core strategy documents in `_strategy/` to understand brand positioning
2. **Load context:** Pull relevant context files from `_context/` for your task
3. **Use templates:** Check `_templates/` for approved content formats
4. **Follow SOPs:** Reference `_sop/` for publishing and approval workflows
5. **Output to channel folder:** Save final marketing outputs in the appropriate channel folder
6. **Link back to source:** Always reference which core strategy documents influenced your output

## Working Rules

- All marketing content must align with voice/tone (05) and positioning (02)
- Public claims must be checked against `brand_alchemy/brand-bible/_context/claims-and-proof.md`
- Outputs are drafts until reviewed by a human owner
- Do not publish without approval from brand owner
