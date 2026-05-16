# references/ — knowledge bank

Pulled material from prior rkitect.ai marketing experiments. Read-only. Treat as ground-truth of what's already been generated and what direction has been validated.

Source: Google Drive folder `1cLY2iovNpgFq7ZIHwkfLj64s0MPh7O4B` — downloaded 2026-05-13 via `gdown --folder`.

## Layout

```
references/drive_dump/HappyMonk/
├── before-after/         10 paired renders (P01-P10) + side-by-side
│   └── manifest.json     room, style, caption, fal.media URLs
├── posts/                8 carousels of post imagery
│   ├── bathrooms-carousel/   ba01..ba09.jpg
│   ├── bedroom-trends/       bt01..bt06.jpg
│   ├── exteriors-carousel/   e01..e05.jpg
│   ├── lighting-carousel/    lt1..lt4.jpg
│   ├── material-palettes/    m01..m10.jpg
│   ├── section-c/            c01..c08.jpg
│   ├── styles-carousel/      s03..s05.jpg
│   ├── typography/           t01..t02.jpg
│   └── manifest.json     per-image caption + fal.media URL
├── reels/                R1..R5 mp4 + manifest.json (Kling v2.1 / Seedance 1.5)
├── sample-content/
│   ├── posts.md          10 final platform-ready posts (LinkedIn, X) — 2026-05-01
│   ├── posts-final.json  same as structured JSON
│   └── videos/           per-post mp4 outputs
├── marketing/
│   ├── linkedin-strat.docx       content pillars + posting cadence (IST)
│   ├── social-community-intel-report.docx  30+ X/Twitter target accounts + engagement playbook
│   ├── content-generation.xlsx   content pipeline tracker
│   ├── carousel/c1/              rkitect_slide_01..07.png
│   ├── carousel/carousel-doc-partial.docx  (partial download — re-fetch if needed)
│   └── _extracted/               plain-text dumps of the docx/xlsx for grep
├── problems/             p1..p5.jpg — problem-statement visuals
├── vids/                 1 jpg (incomplete — re-fetch from source)
└── Catalogue/            empty (was empty in source — verify)
```

## How to use this material

- **Don't regenerate what already exists.** Before asking the LLM to write a new LinkedIn pillar plan or a new carousel concept, grep `marketing/_extracted/` first — most of the strategy is already locked in.
- **`posts-final.json` is the golden reference shape** for "what a finished marketing post output looks like" (hook + caption + cta + video prompt + model + file refs). Any new pipeline should produce records that drop into this shape cleanly.
- **`before-after/manifest.json` and `posts/manifest.json`** define the asset metadata schema (id, room/style/section, caption, image_url, local path, status). Reuse the schema for new asset batches — don't reinvent.
- **`reels/manifest.json`** records which fal model was used per reel (Kling v2.1 vs Seedance 1.5) and which failed — useful prior when picking a video model.
- **`social-community-intel-report.docx`** has 30 X accounts to engage, organized by tier (thought leaders, media, communities). This is the seed list for any outreach/community-engagement automation.

## Known gaps in this snapshot

- `Catalogue/` empty — was empty in the source folder, or permissions blocked it. Verify with folder owner before assuming nothing exists.
- `marketing/carousel/carousel-doc-partial.docx` truncated mid-download. Re-fetch.
- `vids/` has one stray jpg — the rest of the videos folder did not come through. Re-fetch.
- All three Office docs (`*.docx`, `*.xlsx`) came down without extensions; renamed locally. Text extracted to `marketing/_extracted/` for searchability.

## Re-sync command

```
cd references/drive_dump
gdown --folder "https://drive.google.com/drive/folders/1cLY2iovNpgFq7ZIHwkfLj64s0MPh7O4B" --remaining-ok
```
