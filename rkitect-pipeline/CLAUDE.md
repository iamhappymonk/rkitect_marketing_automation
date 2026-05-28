# rkitect-pipeline — CLAUDE.md

Sub-workspace context for the content automation pipeline.
**Load this file** when working inside `rkitect-pipeline/`.

---

## Architecture Overview

6-stage daily pipeline orchestrated by `main.py`:

```
1. Research   → agents/research.py     — find trending topics
2. Filter     → agents/filter.py       — pick today's best topic
3. Generate   → agents/generate.py     — parallel content for all formats
3.25          → agents/template_engine.py — override carousel brief w/ template
3.5           → agents/image_generator.py — generate carousel + LinkedIn images
3.6           → agents/video_assembler.py — assemble slide video (FFmpeg xfade)
3.6alt        → agents/ai_video_generator.py — AI video via OpenRouter (Veo/Kling) — triggered on-demand from review page for ai-mode templates
3.7           → agents/video_prompt_writer.py — AI video prompts (Kling/Veo/etc)
4. QA         → agents/qa.py           — score + retry loop (max 3 retries)
5. Publish    → agents/publish.py      — Buffer GraphQL + Zernio REST
6. Self-Improve → agents/self_improve.py — update perf log, rewrite prompts
```

---

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | Orchestrator — runs full pipeline end to end |
| `config.py` | All settings: model routing, API keys, paths, thresholds |
| `model_router.py` | Route calls to Claude or OpenRouter based on `MODEL_ROUTING` |
| `agents/generate.py` | Parallel generation + image brief writer |
| `agents/publish.py` | Buffer GraphQL + Zernio REST + review queue fallback |
| `agents/image_generator.py` | FLUX image generation via OpenRouter |
| `agents/template_engine.py` | Template-driven image brief override |
| `dashboard/app.py` | Flask review dashboard (port 5050) |
| `context/publish_queue.json` | Manual review queue (pending_review items) |
| `context/skill_performance.json` | Per-format QA score history |
| `context/post_history.json` | Last 7 days topics (deduplication) |
| `context/publish_settings.json` | `auto_publish` flag |
| `prompts/*.md` | LLM system prompts per format |
| `prompts/versions/` | Versioned prompt history |
| `image_templates/*.md` | Markdown templates for image slides |

---

## Active Formats

`FORMATS = ["linkedin", "carousel", "twitter", "reddit"]`

Platform mapping:
- `linkedin` → LinkedIn
- `carousel` → Instagram (1080×1350)
- `twitter` → Twitter/X (1600×900)
- `reddit` → Reddit (no images)

---

## Model Routing (config.py)

Currently in **TESTING MODE** (cheap models):
- Most formats → `openai/gpt-4o-mini` via OpenRouter
- Filter/Twitter → `mistralai/mistral-7b-instruct-v0.1`
- Production mode lines commented in `config.py` — use Claude Sonnet for LinkedIn/QA

---

## Output Structure

```
output/
  YYYY-MM-DD/
    run_HHMMSS/         ← each pipeline run gets own folder
      linkedin.md
      twitter.md
      carousel.md
      reddit.md
      *_image_brief.md
      image_briefs.json
      carousel_images/
        slide_01.jpg ... slide_07.jpg
      linkedin_images/
        linkedin_01.jpg
```

---

## Key Invariants

- **Never overwrite runs** — each run creates timestamped subfolder.
- **Image briefs** keys end with `_image_brief` — QA/Publish strip them before scoring.
- **Carousel publish** = extract `caption` from JSON, NOT slide text.
- **Twitter publish** = extract `tweets` array from JSON, join with `\n\n`.
- **`_template_meta`** must be `.pop()`ed from generated dict before QA (it's a dict, QA expects strings).
- **Buffer image attach** = prefer public URL (`PUBLIC_BASE_URL/output/...`) → fall back to direct upload.
- **`auto_publish: false`** (default) → all passed content goes to review queue, not live.
- `_iter_json_candidates()` pattern used in both `generate.py` and `publish.py` — do not replace with greedy regex.

---

## Environment Variables (.env)

```
ANTHROPIC_API_KEY=
OPENROUTER_API_KEY=
BUFFER_ACCESS_TOKEN=
BUFFER_ORGANIZATION_ID=
BUFFER_LINKEDIN_PROFILE_ID=
BUFFER_INSTAGRAM_PROFILE_ID=
BUFFER_TWITTER_PROFILE_ID=
ZERNIO_API_KEY=
PUBLIC_BASE_URL=          # needed for image URL attachment to Buffer
IMAGE_GENERATION_ENABLED=true
IMAGE_TEMPLATE_ENABLED=true
DASHBOARD_PORT=5050
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=changeme
```

---

## QA Settings

- Pass threshold: `80/100`
- Max retries: `3`
- Self-improve triggers every `2` runs if avg score < `75`

---

## Image Generation Rules (enforced in code)

- **Template-only mode** — `IMAGE_TEMPLATE_ENABLED=true` disables all free-form LLM image briefs
- `generate.py` skips `*_image_brief` generation for ALL formats when template mode is on
- `image_generator.py` skips standalone LinkedIn/Twitter image generation in template mode
- `template_engine.py` `build_platform_image_paths()` always shares carousel slides → LinkedIn (all slides) + Twitter (slide 1)
- **NO TEXT in any image** — enforced at 3 layers: style lock block, per-slide prompt builder, platform guards
- Templates must NOT contain text overlay slots (`**Overlay rule:**`, `{location} · brand` etc) — these leak into prompts and cause FLUX to render broken text

## Known Issues / Active Work

- Reddit not yet wired to Buffer (profile ID commented out in config)
- Zernio integration is best-effort; failures don't block pipeline
- `ai_video_generator.py` — Veo generation via OpenRouter (in progress)
- Image i2i disabled — model unavailable on OpenRouter, all slides use t2i

---

## Dashboard Pages

| URL | Purpose |
|-----|---------|
| `/` | Main dashboard |
| `/review` | Manual review queue (approve/reject → Buffer) |
| `/templates` | Template Launcher — pick template → start pipeline run |

## On-Demand Generation API (Review Page)

| Endpoint | Purpose |
|----------|---------|
| `POST /api/review-queue/<id>/generate-image` | Generate images for item from `image_briefs.json` in run folder |
| `POST /api/review-queue/<id>/generate-video` | Build video — FFmpeg (python mode) or AI/Veo (ai mode) based on `template_meta.video_generation_mode` |

Queue items now store: `source_file`, `run_folder`, `template_meta` (subset: id, video_transition, video_generation_mode, etc.).
`video_generation_mode: python` → `video_assembler.py` (FFmpeg xfade). `video_generation_mode: ai` → `ai_video_generator.py` (Veo via OpenRouter).

## Template Launcher Flow

1. `GET /api/templates` — reads `image_templates/*.md`, returns metadata
2. User clicks "Start Pipeline →" on a card
3. `POST /api/run-template {"template_id": "..."}` — validates template exists, spawns `main.py --template-id <id>` as background process
4. `main.py` passes `forced_template_id` → `run_template_selection()` bypasses random selection
5. Pipeline runs all 6 stages; QA-passed content lands in `context/publish_queue.json`
6. User sees new items in `/review` queue

## Working Rules

- Run pipeline: `cd rkitect-pipeline && python main.py`
- Run dashboard: `cd rkitect-pipeline && python dashboard/app.py`
- All prompt edits → also save version copy to `prompts/versions/`
- Model routing changes → update `config.py MODEL_ROUTING` only
- Do not hardcode brand facts into agent code — pull from `context/` files
- Update this file when architecture changes (new stages, new agents, new output paths)
