---
name: image-brief-craft
version: 2.0.0
description: Generate production-ready, platform-aware architectural image briefs for rkitect content with strict brand visual constraints.
---

# Image Brief Craft

Professional visual-brief skill for rkitect.ai image generation workflows.

## Core Objective

Produce clear, reproducible image briefs that create brand-consistent architectural visuals across LinkedIn, Twitter/X, and Instagram formats.

## Visual Principles

1. Architectural first
- Show spatial design work, not generic AI aesthetics.

2. Workflow clarity
- Visuals should communicate transformation, segmentation, iteration, or workflow depth.

3. Brand consistency
- Respect material realism, lighting discipline, and color vocabulary.

## Approved Visual Styles

- Minimal Architectural: clean lines, warm natural light, restrained composition.
- Segment Reveal: Sektura labeling surfaces in progressive visual states.
- Before/After Split: flat or raw render versus editable segmented output.
- Data/Proof Slide: clear stat callouts and process deltas.
- Process Flow: stage-by-stage transformation from render to editable canvas.

## Color and Mood Constraints

Preferred palette:
- Concrete grey: #9CA3AF
- Oak wood: #D2B48C
- Linen white: #FAF0E6
- Sage green: #9CAF88
- Moss: #8B9A46
- Muted blue: #6B8EB8
- Glass cyan: #7EC8E3
- Charcoal: #1F2937

Avoid:
- Neon palettes
- Oversaturated purple dominance
- Futuristic sci-fi glow effects

## Platform Specs

| Platform | Size | Aspect | Composition Notes |
|---|---|---|---|
| LinkedIn | 1200x627 | 1.91:1 | Keep text-safe area top-left. |
| Twitter/X | 1200x675 | 16:9 | Strong center composition, dark-mode resilience. |
| Instagram Square | 1080x1080 | 1:1 | Carousel-friendly framing and margins. |
| Instagram Tall | 1080x1350 | 4:5 | Feed-dominant vertical layout. |

## Pillar-Based Mood Mapping

- Education: precise, labeled, explanatory.
- Social Proof: dramatic transformation, high contrast before/after.
- Inspiration: editorial warmth and aspirational material depth.
- Behind-the-Product: technical, candid, process-authentic.
- CTA: clean, high-contrast, action-centric.

## Brief Structure (Required)

Every generated brief must include:

1. Goal
- What the image should communicate in one sentence.

2. Scene
- Subject, environment, composition angle.

3. Style
- One approved style from this skill.

4. Lighting and Material
- Realistic material cues and lighting direction.

5. Brand Constraints
- Terms to avoid and required visual anchors.

6. Output Spec
- Resolution and aspect ratio per platform.

7. Negative Prompt
- Explicitly list visual anti-patterns to suppress.

## Hard Reject Anti-Patterns

- "futuristic glowing interface"
- "robot AI assistant"
- "abstract data streams with no architecture"
- "stock photo people smiling at laptops"
- "utopian impossible megastructure"

## Output Contract

Return concise image generation prompt blocks that can be copied directly into image tools.

No generic filler.
No contradictory styles.
No banned visual motifs.

## Performance Notes
<!-- Auto-updated by self_improve.py — do not edit manually -->
Last updated: 2026-05-15
Average score (last 7 runs): pending
Common violations fixed in this version:
- Added mandatory brief structure for production consistency
- Added explicit negative prompt section requirement
- Strengthened platform-specific composition constraints
