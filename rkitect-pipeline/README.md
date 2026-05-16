# rkitect.ai — Daily Content Automation Pipeline v2

> Automated multi-platform content generation for rkitect.ai.
> Built by HappyMonk AI · Bengaluru · May 2026

---

## What This Does

Every day (or on demand), this pipeline:

1. **Researches** trending topics across Reddit, Google Trends, LinkedIn, Twitter/X, and competitor sites
2. **Filters** to select the best topic using pillar weights and deduplication
3. **Generates** platform-native content in parallel for LinkedIn, Instagram Carousel, Twitter/X, and Reddit
4. **Generates image briefs** for each platform's content (text prompts for image generation via OpenRouter)
5. **QA scores** each piece against a 100-point brand rubric (80 = pass threshold)
6. **Retries** failed content up to 3 times with QA critique feedback
7. **Publishes** approved content to Buffer for scheduling
8. **Self-improves** by rewriting underperforming prompts every 7 runs

---

## Quick Start

### 1. Clone and Setup

```bash
cd rkitect-pipeline
cp .env.example .env
# Fill in your API keys in .env
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Required .env Keys

| Key | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes (if using Claude) | Anthropic API key |
| `OPENROUTER_API_KEY` | Yes | OpenRouter API key for model routing |
| `BUFFER_ACCESS_TOKEN` | Yes | Buffer API access token |
| `BUFFER_INSTAGRAM_PROFILE_ID` | Yes | Buffer profile ID for Instagram |
| `BUFFER_LINKEDIN_PROFILE_ID` | Yes | Buffer profile ID for LinkedIn |
| `BUFFER_TWITTER_PROFILE_ID` | Yes | Buffer profile ID for Twitter |
| `DASHBOARD_PORT` | No (default: 5050) | Dashboard server port |
| `DASHBOARD_SECRET_KEY` | No | Flask secret key |
| `DASHBOARD_USERNAME` | No (default: admin) | Dashboard login username |
| `DASHBOARD_PASSWORD` | Yes | Dashboard login password |

### 4. Run the Pipeline

```bash
python main.py
```

### 5. Start the Dashboard

```bash
python dashboard/app.py
# Access at http://your-ip:5050
```

---

## Cron Setup (Mac Mini)

```bash
crontab -e
```

```cron
# Pipeline — runs at 6am daily
0 6 * * * cd /path/to/rkitect-pipeline && python3 main.py >> /tmp/rkitect-pipeline.log 2>&1

# Dashboard — starts on reboot
@reboot cd /path/to/rkitect-pipeline && python3 dashboard/app.py >> /tmp/rkitect-dashboard.log 2>&1
```

---

## Folder Structure

```
rkitect-pipeline/
├── main.py                    # Orchestrator (6 stages)
├── config.py                  # Settings, model routing, paths
├── model_router.py            # Claude + OpenRouter routing
├── requirements.txt
├── .env.example
├── .gitignore
│
├── agents/                    # Pipeline stage implementations
│   ├── research.py
│   ├── filter.py
│   ├── generate.py
│   ├── qa.py
│   ├── publish.py
│   └── self_improve.py
│
├── prompts/                   # Agent system prompts (Markdown)
│   ├── research_agent.md
│   ├── filter_agent.md
│   ├── linkedin_writer.md
│   ├── carousel_writer.md
│   ├── twitter_writer.md
│   ├── reddit_writer.md
│   ├── qa_reviewer.md
│   ├── image_brief_writer.md
│   └── versions/              # Archived prompt versions
│
├── skills/                    # Skill definitions (Markdown)
│   ├── meta-prompt-improver.md
│   ├── performance-log-analyzer.md
│   ├── competitor-signal-responder.md
│   └── image-brief-craft.md
│
├── context/                   # Brand context loaded at runtime
│   ├── brand_bible.md
│   ├── voice_rules.md
│   ├── content_pillars.md
│   ├── competitor_watch.md
│   ├── image_style_guide.md
│   ├── post_history.json
│   └── skill_performance.json
│
├── dashboard/
│   ├── app.py                 # Flask server (auth-protected)
│   ├── templates/index.html
│   └── static/style.css
│
├── output/                    # Daily generated content
│   └── YYYY-MM-DD/
│       ├── linkedin.md
│       ├── carousel.md
│       ├── twitter.md
│       ├── reddit.md
│       ├── *_image_brief.md
│       └── image_briefs.json
│
└── logs/                      # Daily run logs
    └── YYYY-MM-DD.json
```

---

## Model Routing

Currently in **testing mode** (all cheap OpenRouter models). To switch to production:

Edit `config.py` and uncomment the PRODUCTION MODE lines:

```python
# PRODUCTION MODE
"linkedin":    {"provider": "claude",     "model": "claude-sonnet-4-20250514"},
"qa":          {"provider": "claude",     "model": "claude-sonnet-4-20250514"},
"self_improve":{"provider": "claude",     "model": "claude-sonnet-4-20250514"},
```

### Estimated Daily Cost

| Mode | Cost/Day | Cost/Month |
|---|---|---|
| Testing (all OpenRouter) | ~$0.005 | ~$1.50 |
| Production (Claude for LinkedIn/QA) | ~$0.02 | ~$7 |
| All Claude | ~$0.08 | ~$25 |

---

## After First Run

1. Check `output/YYYY-MM-DD/` for generated content
2. Check the dashboard at `http://your-ip:5050`
3. Copy image briefs from the dashboard to your image generator
4. Review Buffer queue for scheduled posts
5. Check `logs/YYYY-MM-DD.json` for run details

---

## Reddit (Placeholder)

Reddit posting is commented out in `publish.py` and `config.py`. To enable:

1. Add Reddit API credentials to `.env`
2. Uncomment Reddit lines in `config.py` PLATFORM_MAP and BUFFER_PROFILES
3. Wire Reddit posting in `publish.py`

---

*rkitect.ai · HappyMonk AI · Bengaluru · May 2026 · v2*
