# rkitect.ai — Image Style Guide

> Visual direction for image brief generation. Loaded by the image_brief_writer agent.

## Brand Visual Identity

- **Style:** Minimal, modern architectural visualization. Clean compositions.
- **Mood:** Professional confidence. Not futuristic sci-fi, not generic stock.
- **Lighting:** Generous natural light, soft shadows, warm tones for interiors. Cool directional light for exteriors.

## Color Palette

- **Primary:** Restrained, high-contrast, modern.
- **Avoid:** Generic purple AI gradients, neon tech colors, oversaturated fantasy tones.
- **Preferred tones:** Warm neutrals (concrete, wood, linen), accent greens (biophilic), muted blues (sky, glass), warm whites.
- **Text overlays:** White or off-white on dark backgrounds. Black on light backgrounds. Always legible.

## Typography Direction

- Clear, technical, legible.
- Professional confidence over decoration.
- Sans-serif preferred for overlays (Inter, DM Sans, or equivalent).

## Sektura Visual Identity (Segment Reveal)

The signature visual: a flat architectural render that gradually "lights up" as Sektura labels each surface — walls, floors, windows pulse into labeled, editable segments.
- Labels should look like clean UI annotations (subtle, not cluttered).
- Color-coded segment highlights: walls (blue tint), floors (warm amber), furniture (green), windows (cyan).

## Image Types Per Platform

| Platform | Dimensions | Style Notes |
|---|---|---|
| LinkedIn | 1200×627 | Hero image, professional, generous text overlay space, Sektura segments if product-focused |
| Twitter/X | 1200×675 | Bold typography, high contrast, dark mode optimized, stat callouts |
| Instagram | 1080×1080 or 1080×1350 | Slide-by-slide visuals, clean data viz, before/after splits, minimal UI chrome |

## Approved Visual Subjects

- Real interiors (living rooms, offices, lobbies, bedrooms)
- Building facades and exteriors
- Floor plans with 3D render overlays
- SketchUp/Revit-style inputs alongside rendered output
- Before/after render comparisons
- Indian architectural context when relevant (compact apartments, Vastu, monsoon-aware design)

## Anti-Patterns (Hard Reject)

- Abstract AI blobs or neural network visualizations
- Fantasy/impossible architecture without buildability
- Dark blurred stock photography
- Unsupported quality claim graphics
- Device frames (laptops, phones) unless specifically requested

## Composition Rules

- Preferred: centered composition, split composition, before-vs-after, single strong focal point, floating architectural panels, and large negative space.
- Avoid: crowded dashboards, too many labels, excessive UI, dense paragraphs, glowing cyberpunk, and random futuristic elements.

## Typography Rules

- Use bold, oversized, minimal, high-contrast typography for on-image hooks. Keep text short (5–12 words preferred). Examples: "STOP WAITING.", "START CREATING." Use Inter, DM Sans, or similar clean sans-serif.

## Color System

- Primary palette: warm ivory, sand, clay, concrete beige, muted stone, soft white.
- Accent colors: muted architectural green, soft olive, subtle neon-lime (sparingly).
- Avoid saturated SaaS blues, rainbow neons, bright purples, and harsh reds.

## Rendering Style

- Ultra-realistic cinematic architectural renders are preferred for product imagery: soft shadows, clean geometry, premium materials (concrete, oak, travertine, glass, brushed metal).
- Lighting: calm daylight or soft dusk depending on mood; avoid hyper-stylized neon lighting.

## Sektura Guidance

- Use Sektura visuals only when the content explicitly focuses on product functionality, segmentation, or editability. Label segments subtly ("Powered by Sektura" caption allowed). Keep Sektura secondary to the rkitect.ai brand.

## Quality Control Checklist

- Is the message understandable in 1 second?
- Is there sufficient negative space?
- Does the image feel premium and editorial?
- Is the architecture the hero of the composition?
- Is on-image text concise (5–12 words) and legible at mobile sizes?
- Are accent colors used sparingly and purposefully?

## Example Prompts

- See `prompts/image_brief_writer.md` for practical prompt templates and platform-specific examples.

