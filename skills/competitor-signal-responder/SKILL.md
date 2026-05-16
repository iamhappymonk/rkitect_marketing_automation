---
name: competitor-signal-responder
version: 2.0.0
description: Generate rapid reactive LinkedIn + X content when competitor signals are detected, while preserving rkitect brand and QA requirements.
---

# Competitor Signal Responder

Professional reactive messaging skill for rkitect.ai. Triggered from research when competitor moves create narrative risk or opportunity.

## Core Objective

Publish fast, confident counter-positioning that reframes the market in rkitect.ai's favor without naming or attacking competitors directly.

## Trigger Conditions

Run this skill when any of these are detected:

1. New feature launch adjacent to rendering, editing, segmentation, or workflow orchestration.
2. Viral competitor post (>= 1000 engagements).
3. Pricing, packaging, or go-to-market shift.
4. Major announcement (funding, strategic partnership, expansion).

## Signal Triage

Classify the signal before writing:

- Category Narrative Risk: competitor is shaping market language.
- Feature Perception Risk: competitor appears to own a capability claim.
- Attention Spike Opportunity: market attention is elevated and can be redirected.

## Counter-Positioning Anchors

Apply these approved lines as internal guidance only.

mnml.ai anchor:
"Fast flat renders. No segmentation, no iteration, no output intelligence."

ArchiVinci anchor:
"Strong social presence. No agentic pipeline, no post-render segmentation."

MyArchitectAI anchor:
"Category window closing - respond with authority content, not product comparison."

## Hard Constraints

1. Never attack competitors by name directly.
2. Never mention competitor names in output copy.
3. Use market reframing language: "most tools," "the category," "the market," "flat output workflows."
4. Keep reactive outputs shorter and more direct than standard daily posts.
5. Reactive content still requires QA pass; no rule relaxation.
6. Preserve all rkitect brand constraints:
   - No "AI render tool"
   - No "credits" (use "Design Units" when relevant)
   - No hedging language
   - Reinforce "Agentic Spatial Intelligence"

## Writing Workflow

1. State the market shift in one line.
2. Reframe the shift as a workflow problem, not a feature race.
3. Assert rkitect thesis with conviction and specificity.
4. Close with one concrete action or audience prompt.

## Output Contract

Generate exactly two deliverables:

1. LinkedIn Reactive Post
- Length: 600-900 characters.
- Structure: hook -> market thesis -> rkitect direction -> CTA.
- Include one image prompt line:
  - [IMAGE BRIEF: ...]

2. Twitter/X Reactive Thread
- Length: 3-5 tweets.
- Structure:
  - Tweet 1: standalone market observation.
  - Tweets 2-3: thesis and implications.
  - Final tweet: CTA.

## Quality Gate Before Return

- Does not mention competitor names.
- Uses direct and non-hedged language.
- Contains category-defining thesis (not feature listing).
- Passes base QA policy.

## Performance Notes
<!-- Auto-updated by self_improve.py — do not edit manually -->
Last updated: 2026-05-15
Average score (last 7 runs): pending
Common violations fixed in this version:
- Added signal triage layer before content generation
- Added explicit quality gate and market-reframing workflow
- Strengthened no-name and no-attack competitor rules
