# great-web-copy

A Claude Code plugin that writes high-converting website copy using proven copywriting frameworks.

Stop shipping "innovative, cutting-edge solutions" that nobody clicks on. This plugin enforces the rules that separate copy that converts from copy that just fills space.

## Install

```md
/plugin install makash/great-web-copy
```

## What You Get

**Two slash commands:**

- `/great-web-copy:write-copy` — Write new copy for any page or section
- `/great-web-copy:audit-copy` — Score existing copy out of 100 on 8 conversion criteria

**One auto-activating skill:**

The `write-copy` skill activates automatically when Claude detects you're working on landing pages, hero sections, CTAs, marketing copy, or README intros. No slash command needed — it just kicks in.

## Usage

### Write new copy

```md
/great-web-copy:write-copy Landing page for an open-source cloud security scanner targeting DevOps teams at mid-size SaaS companies
```

### Audit existing copy

```md
/great-web-copy:audit-copy [paste your current copy here, or provide a file path]
```

### Let the skill auto-activate

Just ask Claude to help with your website copy in natural language. The skill triggers when it detects copywriting context:

```md
> Help me rewrite the hero section of our landing page. We sell API monitoring to backend engineers.
```

## What It Enforces

| Rule | Why It Matters |
|---|---|
| Headlines lead with outcomes, not product names | "Your API uptime — monitored in 3 minutes" beats "Acme Monitor" |
| "You" outnumbers "we" at least 3:1 | Your copy is about the reader, not about you |
| Banned words are killed on sight | No "innovative", "cutting-edge", "leverage", "synergy", "seamless", "robust" |
| CTAs start with verbs and say what you get | "Start your free scan" not "Get started" |
| Every section needs a specific number | "340 teams" beats "many companies" |
| Copy follows proven section flow | Hero → Problem → Solution → How It Works → Proof → Objections → Final CTA |
| 7th-grade reading level | Short sentences. Short paragraphs. No jargon walls. |

## Frameworks

The plugin picks the best framework based on your context:

- **PAS** (Problem → Agitation → Solution) — landing pages, cold audiences
- **AIDA** (Attention → Interest → Desire → Action) — home pages, broad audiences
- **BAB** (Before → After → Bridge) — SaaS, transformation stories
- **StoryBrand** — full website narrative, brand messaging

## Output Format

Every run produces:

1. **The copy** — section-labeled and ready to paste
2. **3 headline alternatives** — clarity-first, curiosity-first, urgency-first
3. **2-3 CTA options** — different commitment levels
4. **Copy notes** — rationale for key choices, what to A/B test

## Example Audit Score

Here's what an audit looks like on weak vs strong copy:

| Criterion | Weak Copy | After Plugin |
|---|---|---|
| Headline impact | 3/10 | 10/10 |
| CTA clarity | 2/10 | 9/10 |
| You vs We ratio | 2/10 | 10/10 |
| Banned words | 9/10 | 10/10 |
| Specificity | 6/10 | 9/10 |
| Narrative | 5/10 | 9/10 |
| Reading level | 7/10 | 9/10 |
| Social proof | 2/10 | 7/10 |
| **Total** | **52/100** | **91/100** |

## License

MIT. See [LICENSE](LICENSE).

## Author

[Akash Mahajan](https://akashm.com) · [@makash](https://x.com/makash)

Built with frustration at AI-generated copy that says "leverage our innovative, cutting-edge platform" and expects anyone to click.