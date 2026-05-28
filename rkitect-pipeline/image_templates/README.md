# Image Templates

Each `.md` file in this folder defines a visual sequence template. The pipeline selects a compatible template at runtime (Stage 3.25), calls an LLM to fill content-specific `{slots}`, then passes the rendered briefs to the image generator (Stage 3.5).

---

## Frontmatter Fields

```yaml
---
id: unique-kebab-case-id          # Required. Used in template_manifest.json.
name: Human Readable Name         # Required. Shown in pipeline logs.
slide_count: 2                    # Required. Number of slides the LLM must produce.
image_size: "1080x1350"           # Required. Pixel dimensions (see sizes below).
compatible_platforms: ["instagram", "linkedin", "twitter"]   # Required.
compatible_pillars: ["workflow", "product", "proof"]         # Optional. Omit to match all.
transition_direction: left-to-right   # Optional. For future video assembly.
video_transition: wipe                 # Optional. Transition type for video.
video_duration_hint: 3                 # Optional. Seconds per slide in video.
video_generation_mode: python          # Optional. "python" (FFmpeg xfade) or "ai" (Veo/Kling via OpenRouter).
---
```

### Image Sizes

| Size      | Platform      | Aspect Ratio     |
|-----------|---------------|------------------|
| 1080x1350 | Instagram     | 4:5 portrait     |
| 1200x627  | LinkedIn hero | 1.91:1 landscape |
| 1600x900  | Twitter card  | 16:9 landscape   |
| 1024x1024 | Square (any)  | 1:1              |

---

## Template Body

After the frontmatter, write one section per slide using `## Slide N — Title` headings.

Use `{slot_name}` for content-specific details the LLM will fill at runtime. Everything else (color palettes, moods, camera notes) is fixed and copied verbatim into the rendered brief.

### Slot Rules

- Slot names must be descriptive: `{before_scene}`, `{after_scene}`, `{room_type}`.
- One or two slots per slide is ideal; more than three makes the template too loose.
- Color palettes, mood, and camera angle should stay hardcoded — not slotted.

---

## Example Template

```markdown
---
id: before-after-room
name: Before / After Room Transformation
slide_count: 2
image_size: "1080x1350"
compatible_platforms: ["instagram", "linkedin", "twitter"]
compatible_pillars: ["workflow", "product", "proof"]
transition_direction: left-to-right
video_transition: wipe
video_duration_hint: 3
---

## Slide 1 — Before

**Scene:** {before_scene}
**Mood:** Cluttered, unresolved, warm amber tones.
**Color palette:** warm gray (#A89A8D), amber (#C8A96E)
**Camera:** 35mm equivalent, portrait 4:5, eye-level, no text in frame.

## Slide 2 — After

**Scene:** {after_scene}
**Mood:** Clean, resolved, calm and productive.
**Color palette:** sage green (#9CAF88), cream (#F5F1ED)
**Camera:** Same framing as Slide 1. No text in frame.
```

---

## Naming Convention

File name = `id` + `.md`: `before-after-room.md`. Use lowercase kebab-case.

---

## Platform Reuse

If `compatible_platforms` includes `linkedin` or `twitter` and those platforms produce no separate images, the pipeline attaches the carousel images to those platforms automatically. Each platform still gets its own caption written in platform-native style.

For single-image templates (`slide_count: 1`), use a landscape size (`1200x627` or `1600x900`) so the image works well on LinkedIn and Twitter.
