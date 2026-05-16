---
name: meta-prompt-improver
version: 2.0.0
description: Rewrite underperforming rkitect prompt files using QA violations and score trends while preserving format contracts and brand rules.
---

# Meta-Prompt Improver

Professional prompt optimization skill for rkitect.ai. This is the execution layer used by `agents/self_improve.py`.

## Core Objective

Improve prompt reliability and QA scores without destroying format fidelity, brand language, or output schema contracts.

## Optimization Workflow

1. Observe
- Load current prompt text.
- Load last 7 run scores and violations for the target format.
- Identify repeated failures, not one-off noise.

2. Analyze
- Classify failures into buckets:
   - Format: missing sections, wrong structure, wrong length, missing hooks, missing [VISUAL:] blocks.
   - Voice: hedging, generic copy, weak founder conviction, non-technical fluff.
   - Brand: forbidden terms, category dilution, naming violations.
   - CTA: missing or weak close, incorrect action style.

3. Diagnose
- Find root-cause instruction gaps in the current prompt:
   - Missing hard constraints.
   - Vague quality definitions.
   - No strong positive/negative examples.
   - Conflicting guidance across sections.

4. Rewrite
- Tighten the prompt with minimal necessary changes.
- Preserve all required format logic.
- Add targeted guidance where failures cluster.

5. Validate
- Confirm rewritten prompt still enforces expected output type and structure.
- Confirm required terminology and brand constraints are explicit.

6. Record
- Keep and update the `## Performance Notes` section.

## Hard Constraints

1. Never remove format-specific instructions. Only add, tighten, clarify, or exemplify.
2. Always preserve and update the `## Performance Notes` section.
3. Rewritten prompt length must be greater than or equal to original prompt length.
4. Add 2-3 concrete DO/DO NOT examples derived from observed violations.
5. Keep JSON output schemas and section formatting unchanged when present.
6. Do not add tool-specific dependencies or external workflow assumptions.

## rkitect Brand Safety Rules

- Never allow "AI render tool" wording.
- Never allow "credits". Use "Design Units".
- Keep product naming as "rkitect.ai".
- Keep segmentation naming as "Sektura".
- Reinforce category language: "Agentic Spatial Intelligence".
- Remove hedging terms such as: might, perhaps, could potentially, we believe, we think, can help.

## Rewrite Patterns To Apply

- Replace vague requests with measurable constraints.
- Add examples exactly where the model fails.
- Convert soft language into explicit pass/fail instructions.
- Add dedicated section for the dominant failure cluster if violations exceed 60% in one bucket.

## DO / DO NOT Examples

DO:
- "Write a 1-line hook under 15 words that names a concrete workflow pain."

DO NOT:
- "Write a compelling opening."

DO:
- "Hard fail if the phrase 'AI render tool' appears anywhere in the output."

DO NOT:
- "Avoid generic product descriptions when possible."

DO:
- "Include one explicit founder thesis line in the close."

DO NOT:
- "End strongly."

## Output Contract

Return the full rewritten prompt text only.

No preamble.
No explanation.
No notes.

## Performance Notes
<!-- Auto-updated by self_improve.py — do not edit manually -->
Last updated: 2026-05-15
Average score (last 7 runs): pending
Common violations fixed in this version:
- Added root-cause diagnosis workflow before rewrite
- Added explicit brand-safety rule block for rkitect terms
- Added mandatory DO/DO NOT examples and measurable constraints
