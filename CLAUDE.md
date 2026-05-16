# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

Greenfield repo. No code yet. Intent: marketing automation layer for **rkitect.ai** covering the full suite — content generation + scheduling, lead gen + outreach, and ad campaign automation — under one orchestration layer.

User preference: start simple, grow incrementally. Do NOT scaffold a monorepo / multi-package layout up front. Add the minimum needed for the next concrete task.

## Architecture intent (to be revisited as code lands)

- **rkitect.ai** is the parent product. This repo is the marketing-automation sidecar — not part of the rkitect.ai app itself. Keep boundaries clean: no cross-imports back into rkitect.ai's editor/canvas code.
- Likely future shape: Next.js App Router surface (dashboards, approval queues, manual triggers) + a Python/agno or TS worker tier for long-running pipelines (content gen, outreach drips, ad-spend optimization). Decide per feature when the time comes — don't pre-commit.
- Outbound integrations expected: X/LinkedIn/Instagram (content), email (outreach), Meta Ads + Google Ads (campaigns), plus an LLM provider (Vercel AI Gateway preferred).

## Conventions in effect from day one

- Edits happen on a worktree branch, never `main` (see global CLAUDE.md). Use the `worktree-create` skill before touching code.
- Caveman mode is default-on for chat. Code, commit bodies, and security warnings stay normal.
- Commits via `caveman:caveman-commit` (Conventional Commits, subject ≤50 chars). PRs via `superpowers:finishing-a-development-branch` (Option 2).
- Before writing the first real module, run `superpowers:brainstorming` to lock the feature shape, then `superpowers:writing-plans`.
- File-size caps from global CLAUDE.md apply (`small-files` skill). Don't grow god-files.

## Build / test / lint

None yet — no toolchain present. Update this section when `package.json` / `pyproject.toml` / `Makefile` is added. Common commands (build, test, lint, run-single-test, dev server) belong here.

## Knowledge bank — `references/`

Pre-existing rkitect.ai marketing work is stored under `references/drive_dump/HappyMonk/` (pulled from Drive folder `1cLY2iovNpgFq7ZIHwkfLj64s0MPh7O4B`). Treat this as ground truth before generating anything new — strategy docs, post examples, asset schemas, target-account lists, and finished sample outputs are all there. See `references/README.md` for the full index and gaps. Grep `marketing/_extracted/*.txt` for searchable text of the docx/xlsx files.

Key shapes to reuse, not redesign:
- `references/drive_dump/HappyMonk/sample-content/posts-final.json` — finished post record shape
- `references/drive_dump/HappyMonk/before-after/manifest.json` and `posts/manifest.json` — asset metadata schema
- `references/drive_dump/HappyMonk/reels/manifest.json` — reel + model selection record

## Open questions for next session

- Which surface ships first — content scheduler, outreach sequencer, or ad-campaign console?
- TS-only, Python-only, or both? Decide when feature #1 is chosen, not before.
- Deployment target — Vercel (default for rkitect.ai stack) vs. dedicated worker host for long-running automation jobs.
