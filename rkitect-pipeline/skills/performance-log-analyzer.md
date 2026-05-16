---
name: performance-log-analyzer
version: 2.0.0
description: Analyze skill_performance.json with week-over-week scoring and violation clustering to drive targeted prompt rewrites.
---

# Performance Log Analyzer

Professional analytics skill used by `agents/self_improve.py` and intended for dashboard reporting.

## Core Objective

Turn QA logs into clear weekly decisions:

- What is stable and should not be touched.
- What is degrading and needs immediate intervention.
- What failed, why it failed, and what to fix first.

## Data Source

- Primary input: `context/skill_performance.json`
- Each format should include: `date`, `score`, `passed`, `violations`

## Analysis Workflow

1. Observe

- Load full performance log.
- Validate each format has enough history for week-over-week analysis.

2. Compute

- For each format:
  - Current 7-day average.
  - Previous 7-day average (days 8-14).
  - Week-over-week delta.
  - Pass-rate trend for current week.

3. Classify

- Apply label and action rules from the matrix below.

4. Diagnose

- Normalize and bucket violations:
  - Voice: hedging, weak conviction, generic tone.
  - Format: structure misses, length misses, hook/CTA misses.
  - Brand: forbidden terms, naming violations, missing category reinforcement.
- Flag dominant bucket when one category exceeds 60% of total violations.

5. Recommend

- Prioritize one primary rewrite target and one secondary target maximum.
- Explicitly protect stable formats from unnecessary rewrites.

## Classification Matrix

| Condition                  | Label           | Required Action                                  |
| -------------------------- | --------------- | ------------------------------------------------ |
| Current avg >= 88          | Stable          | Do not rewrite. Keep monitoring only.            |
| Current avg >= 80 and < 88 | Acceptable      | Monitor trend; rewrite only if degrading.        |
| Current avg < 80           | Underperforming | Queue for rewrite.                               |
| WoW drop > 5               | Degrading       | Immediate priority regardless of absolute score. |
| WoW gain > 5               | Improving       | Protect current prompt; avoid over-editing.      |

## Prioritization Rules

1. Degrading beats all other states.
2. Underperforming with brand violations outranks underperforming format-only issues.
3. Stable formats are lock-protected unless there is a critical brand compliance failure.

## Output Contract

Write a 5-8 bullet markdown summary to:

- `logs/weekly-insight-YYYY-MM-DD.md`

Required sections in that file:

1. Per-format status bullets with avg and WoW delta.
2. Top violation cluster this week.
3. Rewrite recommendation (primary target + fix theme).
4. Stability protection note for high-performing formats.

## Output Example

```markdown
# Weekly Insight - YYYY-MM-DD

- LinkedIn: 84.2 avg (+2.1 WoW) - Acceptable. Voice compliance improving.
- Carousel: 72.5 avg (-6.3 WoW) - Degrading. Primary failure cluster: format.
- Twitter: 88.1 avg (+0.5 WoW) - Stable. Protect from rewrite.
- Reddit: 79.0 avg (new) - Underperforming. Brand violations dominate.
- Top violation cluster: "AI render tool" and weak category language.
- Recommendation: Rewrite carousel_writer first, then reddit_writer if brand failures persist.
- Protection: Keep twitter prompt unchanged this week.
```

## Performance Notes

<!-- Auto-updated by self_improve.py — do not edit manually -->

Last updated: 2026-05-15
Average score (last 7 runs): pending
Common violations fixed in this version:

- Added explicit prioritization and protection rules
- Added pass-rate trend requirement
- Standardized output contract for weekly insight file
