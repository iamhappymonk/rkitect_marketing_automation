---
id: room-style-variants-carousel
name: Same Room / Four Interior Styles Carousel
slide_count: 6
image_size: "1080x1440"
compatible_platforms: ["instagram", "linkedin"]
compatible_pillars: ["inspiration", "product", "cta"]
transition_direction: left-to-right
video_transition: wipe
video_duration_hint: 3
video_generation_mode: python
style_pool:
  - Japanese Wabi-Sabi
  - Indian Traditional
  - Scandinavian Minimal
  - American Contemporary
  - Chinese Imperial
  - Brutalist Concrete
  - Mediterranean Villa
  - Mid-Century Modern
  - Moroccan Riad
  - Korean Modern Hanok
  - Art Deco Luxury
  - Tropical Balinese
style_pick_count: 4
style_pick_method: random_each_run

text_overlay_policy: CODE_ONLY
# All text overlays (style labels, CTA copy, collage tags) are applied
# by the automation pipeline via image compositing — NOT prompted into
# any image generation model. Image generation prompts must never
# include text, labels, watermarks, or typography instructions.
---

## Slide 1 — Collage Cover (2×2 Grid)

**Assembly:** Post-composited from the four renders produced for Slides 2–5.
Do NOT generate this image separately — build it in code after all four renders complete.

**Layout spec:**
- 2×2 equal quadrants at 1080×1350px total
- Divider: 3px solid #1A1A1A between quadrants (horizontal and vertical)
- Top-left = {style_a} render
- Top-right = {style_b} render
- Bottom-left = {style_c} render
- Bottom-right = {style_d} render

**Tag overlay (applied by pipeline, not image gen):**
- Position: top-left corner of each quadrant
- Style: bold all-caps sans-serif, white text (#FFFFFF), 14–16px, on a semi-transparent dark pill/rectangle (#1A1A1A at 80% opacity), 8px padding, 4px border-radius
- Content per quadrant: {style_a_label} / {style_b_label} / {style_c_label} / {style_d_label}

**Mood:** Immediate visual contrast between four styles. This is the scroll-stopper. Viewer sees the variety in one frame.
**Color palette:** No palette applied — the four renders supply all color. Divider lines and tag overlays only.
**Transition note:** Cover slide. No inbound transition. Hold until swipe.

---

## Slide 2 — Style Variant A (Full Image)

**Generation prompt base:** {room_base_scene}, rendered in {style_a} interior design style. Photorealistic architectural render, natural light, no people, no text, no watermarks.
**Mood:** Fully immersive in {style_a}. Materials, lighting temperature, decor, and atmosphere should feel native to the style — not applied on top of a generic room.
**Color palette:** Derived from {style_a} — let the style dictate the palette entirely.
**Camera:** 28mm equivalent, portrait 3:4, eye-level, wide enough to show staircase and main seating zone together. No text in frame, no labels, no overlays.

**Tag overlay (applied by pipeline, not image gen):**
- Position: top-left corner
- Style: bold all-caps sans-serif, white (#FFFFFF) on dark pill (#1A1A1A at 80% opacity), 16–18px, 10px padding, 6px border-radius
- Content: {style_a_label}

**Transition note:** Hold 1 second. Camera static. Wipe left-to-right on swipe.

---

## Slide 3 — Style Variant B (Full Image)

**Generation prompt base:** {room_base_scene}, rendered in {style_b} interior design style. Photorealistic architectural render, natural light, no people, no text, no watermarks.
**Mood:** Distinct from Slide 2. Same room geometry, entirely different material world. The contrast with the previous style should be immediately readable.
**Color palette:** Derived from {style_b} — contrast with Slide 2 palette.
**Camera:** Same framing as Slide 2 — 28mm equivalent, portrait 3:4, eye-level. No text in frame, no labels, no overlays.

**Tag overlay (applied by pipeline, not image gen):**
- Position: top-left corner
- Style: same spec as Slide 2
- Content: {style_b_label}

**Transition note:** Hold 1 second. Wipe left-to-right on swipe.

---

## Slide 4 — Style Variant C (Full Image)

**Generation prompt base:** {room_base_scene}, rendered in {style_c} interior design style. Photorealistic architectural render, natural light, no people, no text, no watermarks.
**Mood:** Third style read — lighter or more dramatic than Slides 2–3 to maintain visual variety through the sequence.
**Color palette:** Derived from {style_c}.
**Camera:** Same framing — 28mm equivalent, portrait 3:4, eye-level. No text in frame, no labels, no overlays.

**Tag overlay (applied by pipeline, not image gen):**
- Position: top-left corner
- Style: same spec as Slides 2–3
- Content: {style_c_label}

**Transition note:** Hold 1 second. Wipe left-to-right on swipe.

---

## Slide 5 — Style Variant D (Full Image)

**Generation prompt base:** {room_base_scene}, rendered in {style_d} interior design style. Photorealistic architectural render, natural light, no people, no text, no watermarks.
**Mood:** Final style — most aspirational or unexpected of the four. Strong visual impact. This is the last render the viewer sees before the CTA.
**Color palette:** Derived from {style_d}.
**Camera:** Same framing — 28mm equivalent, portrait 3:4, eye-level. No text in frame, no labels, no overlays.

**Tag overlay (applied by pipeline, not image gen):**
- Position: top-left corner
- Style: same spec as Slides 2–4
- Content: {style_d_label}

**Transition note:** Hold 1 second. Wipe to Slide 6.

---

## Slide 6 — CTA

**Assembly:** Reuse the highest-contrast render from Slides 2–5 as the background (pipeline selects — no new generation). Apply a 40% black overlay (#000000 at 40% opacity) in post.

**Generation:** No new image generated. Reuse existing render.

**CTA overlay (applied by pipeline, not image gen):**
- Headline: "ONE ROOM. INFINITE STYLES."
  - Font: bold all-caps, white (#F5F1ED), 36–40px, centered
- Subline (pick one per run based on campaign):
  - "Follow for weekly architecture drops."
  - "Join the architect.ai beta — link in bio."
  - Subline font: regular weight, cream (#F5F1ED), 18px, centered
- Handle/URL: "architect.ai" or "@architect.ai"
  - Color: gold (#C8A96E), 16px, centered, bottom third of frame

**Mood:** Bold architectural authority. The world-class render under the overlay does the visual work. The copy just closes.
**Color palette:** Render tones + #000000 overlay + #F5F1ED text + #C8A96E accent.
**Transition note:** Terminal slide. No outbound transition.