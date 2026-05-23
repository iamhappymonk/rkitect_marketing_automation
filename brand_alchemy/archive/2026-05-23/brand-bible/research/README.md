---
archived: 2026-05-23
archived-by: agentic-saas-marketing-expert
reason: Empty shell (research data in `brand_alchemy/research/`)
superseded-by: brand_alchemy/research/README.md
recovery: git mv brand_alchemy/archive/2026-05-23/brand-bible/research/README.md brand_alchemy/brand-bible/research/README.md
---

> **ARCHIVED 2026-05-23** — see frontmatter for context. Do not edit. Recovery instructions in frontmatter.

# research/ — Market & Industry Research

This folder contains detailed community intelligence, platform insights, customer pain points, engagement opportunities, and trend analysis. Research here drives ALL marketing strategy and content planning.

## What Goes Here

### Platform & Community Intelligence

- **Social platform analysis** — Twitter/X accounts to engage, audience types, engagement opportunities (see EXAMPLE: social-community-intelligence-report.md)
- **Hashtag research** — Volume data, audience composition, engagement patterns (min. 40+ hashtags with volume and audience info)
- **Subreddit intelligence** — Community size, activity level, best-performing post types, engagement opportunities
- **Community pain points** — Concrete frustrations, quoted complaints, problems people are trying to solve
- **Conversation gaps** — Opportunities where rkitect can add unique value
- **Content format preferences** — What types of content resonate (threads, images, videos, case studies, etc.)

### Market & Competitive Research

- Market size and growth projections (with sources)
- Industry trend analysis (tech, design style, workflow shifts)
- Competitor positioning and messaging strategy
- Customer comparison: "why they choose X over competitors"
- Pricing sensitivity and willingness to pay research

### Customer & User Research

- Customer behavior research (how they discover tools, decision process, implementation)
- Usage patterns and adoption data (e.g., "60% of users integrate with SketchUp")
- Feature usage statistics
- Churn/retention patterns
- Interview synthesis and patterns from customer calls
- User complaints and feature requests

### Emerging Opportunities

- Emerging design styles (data showing Japandi, biophilic, etc. are trending)
- Technology trend analysis (AI adoption, real-time rendering, etc.)
- Generational adoption patterns (students vs established firms)
- Geographic opportunities (India-specific demands, regional style preferences)

## What Makes Research "Complete" (Not Vague)

❌ Bad: "Architects want faster rendering"
✓ Good: "On r/archviz and Reddit's r/architecture, architects complain 'Lumion render took 30 hours'; users specifically mention GPU constraints and lack of per-element control in AI renders. Survey of 50 professionals shows 78% would pay for tool that allows edits without full re-render."

❌ Bad: "Instagram is good for design content"
✓ Good: "#archviz hashtag has 534K+ posts on IG; audience is 40% students, 35% archviz freelancers, 25% small studios. Posts with 100-200 likes average 30 comments; captions mentioning 'render time' or 'before/after' see 2x engagement. Top posting times: Tuesday-Thursday 8am-2pm."

❌ Bad: "Interior designers need more options"
✓ Good: "r/interiordesign (900K members, 500+ daily active) sees recurring 'how do I show clients multiple styles for same room?' threads. Users mention buying Sketchup plugins ($200-500), outsourcing to archviz studios ($2K-5K per view), or manually recreating scenes. Time from concept to revision: 3-7 days. Designers report 40% of clients request changes after first render."

## Research File Structure

Each research doc should include:

### Header

- **Date conducted:** YYYY-MM-DD
- **Author/Team:** Who collected this data?
- **Confidence level:** High/Medium/Low (based on data quality)
- **Next review date:** When should this be updated?

### Data Section (with sources cited)

- Specific numbers, percentages, quotes from customers/communities
- Links to Reddit threads, social media posts, or survey data
- Screenshot links or direct quotes (verbatim customer language)
- Source methodology: "Monitored 30 Twitter accounts over 60 days" or "Surveyed 50 architects"

### Actionable Insights

- What does this mean for our strategy?
- Which audience segments does this apply to?
- What content angles does this suggest?
- What should we test or validate next?

### Related Documents

- Link to context materials that informed this research
- Link to marketing content created from this research

## Real Examples from Your Research

**EXAMPLE 1: Platform Intelligence**

- File: `social-community-intelligence-report.md`
- Contains: 30+ specific Twitter accounts with follower counts, engagement angles, and audience types
- Contains: 40+ hashtags with volume labels (High/Medium/Low) and specific audience descriptions
- Contains: 20+ Reddit communities with member counts and best-performing post types
- Contains: 18 concrete pain points quoted from Reddit/Twitter with engagement opportunities

**EXAMPLE 2: What To Do With This**
If research shows: "r/architecture users complain 'V-Ray license is $1000+, too expensive,'" then agents should:

1. Create social content answering this specific pain point
2. Target replies to V-Ray pricing complaint posts
3. Develop case study showing ROI vs V-Ray costs
4. Feature affordability in landing page copy

## Subfolder Structure (When Needed)

```
research/
  social-community-intelligence/     ← Twitter/X, Instagram, Reddit data
  customer-research/                 ← Interviews, surveys, user studies
  market-trends/                     ← Market size, TAM, emerging opportunities
  competitive-analysis/              ← Competitor positioning, feature comparison
  customer-pain-points/              ← Aggregated complaints and frustrations
```

## File Naming Convention

- `social-community-intelligence-{platform}-{date}.md` — e.g., `social-community-intelligence-twitter-may2026.md`
- `{topic}-market-research-{date}.md` — e.g., `archviz-market-trends-q1-2026.md`
- `survey-{topic}-{date}.md` — e.g., `survey-architect-rendering-workflow-may2026.md`
- `interview-synthesis-{audience}-{date}.md` — e.g., `interview-synthesis-small-studio-owners-may2026.md`
- `customer-pain-points-{channel}-{date}.md` — e.g., `customer-pain-points-twitter-may2026.md`

## Research Quality Checklist

Before saving research, verify:

- [ ] All claims include specific numbers or quotes
- [ ] Sources are linked or cited (Reddit thread URL, survey size, date collected)
- [ ] Audience composition is described (size, demographics, behavior)
- [ ] Pain points are quoted directly when possible
- [ ] Engagement opportunities are concrete and testable
- [ ] File includes author name and date
- [ ] Research is dated and has a "next review" date
- [ ] Actionable insights section connects findings to marketing strategy

## Current Research

- ✅ `social-community-intelligence-report.md` — Twitter/X, Reddit, community analysis with 30+ accounts, 40+ hashtags, 18 pain points, concrete engagement angles
- (Add more as created)

## Difference Between research/ and \_context/

- **research/** — Actively collected findings, trends, pain points, and opportunities (e.g., "Twitter users are complaining about render time in these specific ways")
- **\_context/** — Stable reference materials already incorporated into brand strategy (e.g., "rkitect positioning is based on speed and control")

Research informs strategy; context documents the strategy.
