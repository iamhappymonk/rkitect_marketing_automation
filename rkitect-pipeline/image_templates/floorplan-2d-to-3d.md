---
id: floorplan-2d-to-3d
name: Floor Plan 2D to 3D Reveal
slide_count: 2
image_size: "1080x1350"
compatible_platforms: ["instagram", "linkedin", "twitter"]
compatible_pillars: ["proof", "product", "workflow"]
transition_direction: top-to-bottom
video_transition: zoom
video_duration_hint: 3
video_generation_mode: ai
---

## Spatial Anchor (filled once per run — same value injected into both slides)

**Layout spec:** {floor_plan_spec}
> Pipeline note: {floor_plan_spec} must be set ONCE per run and passed identically to both Slide 1 and Slide 2 image generation calls. Never generate the two slides with different layout specs — this breaks the video transition.

---

## Slide 1 — 2D Floor Plan

**Scene:** {floorplan_2d_drawing}
**Layout:** Use {floor_plan_spec} exactly. Room count, wall positions, orientations, and proportions as specified.
**Mood:** Precise, technical, clean. A flat architectural drawing — black lines on white. The stillness before the build.
**Color palette:** white (#FFFFFF), light gray (#E8E4DF), charcoal (#3D3D3D)
**Camera:** 90° directly overhead, portrait 4:5. Full plan visible edge to edge. Orientation locked to {floor_plan_spec}. No text in frame.
**Transition note:** Hold 1.5 seconds. Camera begins a slow arc from 90° toward 45° isometric. Wall positions from this frame must persist exactly into Slide 2.

## Slide 2 — 3D Isometric Render

**Scene:** {apartment_3d_render}
**Layout:** Same {floor_plan_spec} as Slide 1 — identical room count, wall positions, and orientation. No rooms added, removed, or shifted.
**Mood:** Warm, inviting, complete. Same plan — now alive with cream, wood, and soft greenery.
**Color palette:** cream (#F5F1ED), warm gray (#A89A8D), wood amber (#C8A96E), sage green (#9CAF88)
**Camera:** 45° isometric overhead. Same footprint and orientation as Slide 1 — derived from {floor_plan_spec}. No text in frame.
**Transition note:** Camera arrives at 45° as walls and furniture fully materialized. Hold 2.5 seconds. No further movement.

## Video Direction

**Sequence type:** 2D to 3D
**Transition:** zoom / top-to-bottom
**Total duration:** 5.5 seconds (video_duration_hint: 3s x 2 slides - 0.5s overlap)

### Shot Breakdown

| Time      | Shot           | Description                                                                                        |
|-----------|----------------|----------------------------------------------------------------------------------------------------|
| 0:00-0:02 | Slide 1 Hold   | 90 deg overhead. Flat plan matching {floor_plan_spec}. Static. No movement.                        |
| 0:02-0:05 | Arc Transition | Camera arcs from 90 deg to 45 deg. Walls extrude from exact plan lines. No drift.                  |
| 0:05-0:08 | Slide 2 Hold   | 45 deg isometric. Same footprint. Fully furnished, warm tones. Hold 2.5s.                          |

### AI Video Prompts (generated per-model by video_prompt_writer agent)

> The pipeline generates model-specific prompts at runtime using `agents/video_prompt_writer.py`.
> Prompts are saved to `ai_video_prompts.json` alongside the images.
> Use the prompts below as reference only — they are overwritten each run.

**Template type for prompt writer:** `2d_to_3d`

**Kling (i2v):**
Top-down aerial view. Flat architectural floor plan — {floor_plan_spec}. Walls extrude upward, roof materialises, surfaces resolve with concrete and timber texture. Camera arcs from 90 deg overhead to 45 deg isometric. Soft overcast light. Photorealistic architectural visualisation. 5 seconds.

**Wan 2.5 (i2v):**
Top-down aerial shot. Camera slowly tilts from 90 deg top-down to 45 deg isometric angle. Walls extrude upward from flat plan matching {floor_plan_spec}. Surfaces materialise. Soft even light. 5 seconds.

**Veo 3:**
Cinematic top-down aerial. Flat architectural floor plan — {floor_plan_spec}. Walls extrude upward, structure builds, roof materialises, surfaces resolve. Camera arcs from 90 deg overhead to 45 deg isometric. Soft overcast architectural light, even and shadowless. Photorealistic. Subtle site ambience. 5 seconds.

**Runway (i2v):**
Starting from a flat 2D architectural floor plan viewed from above, walls extrude upward, structure builds, camera arcs to 45 deg isometric as surfaces materialise. {floor_plan_spec} layout maintained. Soft overcast light. 5 seconds.

### Instagram Reels Hook

> Start mid-arc — camera already 40% through its descent, walls half-extruded. First frame = the apartment building itself. Skip the static plan hold entirely.

## Feedback Log

- **2026-05-25 10:17 UTC** — the image generated is good just that make sure that the 3d being made uses the exact some lauout of the 2d plan cuz it feels broken at a few palces

- **2026-05-25 10:25 UTC** — the image generated is good just a few fixed, make sure that the 3d image generated is made using the exact same 2d floor plan cuz the 3d and 2d donsent look a little the same

- **2026-05-25 11:06 UTC** — make sure the 3d image is made using the exact same 2d floor plan
