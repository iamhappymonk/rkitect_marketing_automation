# Team Skills

This folder vendors the curated marketing skills selected for the rkitect.ai marketing workspace so the team can use the same workflows after the repo is pushed.

## How To Use

- Each subfolder is a reusable skill directory with its own `SKILL.md`.
- These are workflow skills, not rkitect.ai-specific brand docs.
- Brand-specific context still lives in `brand_alchemy/brand-bible/_context/`, `brand_alchemy/research/`, and `brand_alchemy/brand-bible/_strategy/`.
- When using a skill, load the relevant brand context at runtime instead of hardcoding brand facts into the skill.

## Installing Locally

To make these available in a teammate's Codex environment, copy the desired skill folders into their Codex skills directory:

```powershell
Copy-Item -Recurse .\skills\marketingskills-content-strategy "$HOME\.codex\skills\marketingskills-content-strategy"
```

Or copy all vendored skills:

```powershell
Get-ChildItem -Directory .\skills | Where-Object { $_.Name -ne 'README.md' } | ForEach-Object {
  Copy-Item -LiteralPath $_.FullName -Destination (Join-Path "$HOME\.codex\skills" $_.Name) -Recurse -Force
}
```

Restart Codex after installing skills.

## Current Skill Groups

- `marketingskills-*`: product marketing, content, SEO, analytics, community, copywriting, launch, sales enablement, directory submissions.
- `digital-marketing-pro-*`: brand setup, audience intelligence, campaign planning, validation, growth planning, SOPs, continuous improvement.
- `affiliate-*`: content research, content atomization, Reddit posts, Twitter/X threads.
- `opendirectory-*`: brand, tone, market mapping, customer discovery, outreach, Reddit, LinkedIn, CLAUDE.md generation.
