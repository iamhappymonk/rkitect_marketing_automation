# \_context/ — Brand Reference Materials

This is the only brand context folder for the marketing workspace. It holds the core research, insights, and background materials that inform brand strategy and guide all marketing decisions. **Load relevant context files BEFORE creating any marketing content.**

## What Goes Here

This folder contains the "already-researched" foundation that answers "Why do we say what we say?" and "Who are we actually talking to?"

### Company & Business Context

- Company background, founding story, and mission
- Business model and revenue information (pricing tiers, licensing, target revenue)
- Founder/leadership context and strategic priorities
- Current product/service offerings and feature list
- Product roadmap and planned features
- Expansion plans and geographic focus

### Customer & Market Context

- **Detailed customer personas** with demographics, pain points, and workflows
- **Customer research synthesis** — patterns from interviews/surveys
- **Customer success stories** — how current customers use the product
- **Customer acquisition channels** — where customers come from
- **Customer retention data** — what keeps them using the product
- **Willingness to pay** — pricing sensitivity and value perception
- **Geographic context** — India-specific insights, regional differences, local market conditions

### Competitive Context

- **Competitor analysis** — direct competitors (other AI rendering tools, traditional renderers)
- **Competitor positioning** — how they message, their differentiators
- **Competitive advantages** — specific reasons architects choose rkitect over alternatives
- **Market positioning wedge** — where rkitect wins (fast iteration, control, affordability)
- **White space opportunities** — problems competitors aren't solving

### Product & Technical Context

- **Feature documentation** — what rkitect actually does (the honest version)
- **Technical capabilities** — supported file formats, integration points, speed benchmarks
- **Known limitations** — what rkitect can't do (important for honest marketing)
- **Platform integration** — SketchUp, Revit, BIM, workflow compatibility
- **Quality benchmarks** — render quality comparisons, edge cases

### Claims & Verification

- **Approved claims and proof** — verified statements about speed, accuracy, compliance, pricing
- **Claims to avoid** — unverified or misleading statements about competitors
- **Regulatory/compliance context** — data handling, privacy, industry standards

## What Makes Context "Useful" (Not Vague)

❌ Bad context: "We help architects save time"
✓ Good context: "Traditional rendering pipeline (Revit/SketchUp → V-Ray/Lumion → 3-4 hours per render; per-element edit = full re-render). rkitect users report average time per render: 3-5 minutes for concept; material/lighting edits: 30-60 seconds without re-render. ROI calculation: Studio of 5 architects doing 10 concepts/month saves ~40 hours/month vs V-Ray; cost per hour saved: ~$X."

❌ Bad context: "Target audience: architects"
✓ Good context: "PRIMARY: Small-to-mid-size Indian architecture firms (5-20 people) using SketchUp/Revit doing residential and commercial work. Pain point: 40% of billing time goes to render iteration, not design. Secondary: Students using free/discounted licenses, archviz freelancers, interior design studios. Tertiary: Real estate developers needing fast concept visualization."

❌ Bad context: "We're different from competitors"
✓ Good context: "ArchiVinci: AI-generated renders (hallucination risk, less control). Lumion: Real-time, but requires GPU investment, render times 10-30 hours for animations. V-Ray: Hero-quality but $1000+, requires expertise, 4-6 hour render queues. rkitect: Fast concept renders (3-5 min) + non-destructive per-element editing (segmentation), no re-render needed, $X/month entry price, works with existing geometry."

## Context File Structure

Each context doc should include:

### Header Section

- **Last updated:** YYYY-MM-DD
- **Owner/Author:** Who is responsible for this context?
- **Confidence:** Based on what? (survey of N=50, customer calls, public data, internal estimation)
- **Next review date:** When should this be refreshed?

### Data Section (with specificity required)

- Concrete numbers: customer counts, pricing, market size, adoption rates
- Direct quotes from customers or research (in quotes)
- Linked sources: survey documents, interviews, external reports
- Methodologies: "Based on interviews with 10 studio owners" or "Survey of 500 architects"

### What This Means For Marketing (actionable)

- How should this shape our positioning?
- What messaging does this enable?
- What should we avoid saying?
- What content should we create?

### Related Documents

- Which brand documents reference this context? (Link to 01-07 files)
- Which research files support or contradict this? (Link to research/ folder)
- Which marketing outputs use this? (Link to ads/, social/, pages/, etc.)

## Real Examples of Good Context

**EXAMPLE 1: Customer Pain Points Context**

- Document showing specific complaints from r/architecture Reddit threads
- Quotes: "'My V-Ray license stopped working before a deadline'"
- Data: "78% of surveyed architects mention per-element editing as important"
- Implication: "Marketing should emphasize non-destructive editing and subscription reliability"

**EXAMPLE 2: Market Context**

- Real estate developer render requirements: "Decks with 30-50 unit render variations; currently outsourced to archviz studios at $3K-5K per variation"
- Student affordability barrier: "V-Ray student license = $300/year; students asking for free alternatives"
- Implication: "Entry-level product positioning and student program strategy"

**EXAMPLE 3: Competitive Context**

- Direct comparison table: rkitect vs Lumion vs V-Ray vs ArchiVinci (speed, price, learning curve, control)
- Specific competitor quotes from their marketing
- Verification of their claims (e.g., "Lumion: 'Real-time rendering' means interactive viewport, but final animation still 10-20 hours")

## Subfolder Structure (When Needed)

```
_context/
  company-profile/              ← Mission, values, founders, business model
  customer-profiles/            ← Personas, use cases, success metrics
  market-analysis/              ← TAM, competitors, positioning
  product-context/              ← Features, limitations, integrations
  claims-and-proof/             ← Verified statements with evidence
```

## File Naming Convention

- `company-profile.md`
- `customer-personas.md`
- `customer-success-{metric}.md` — e.g., `customer-success-time-saved.md`
- `competitor-{competitor-name}-analysis.md`
- `market-{segment}-analysis.md`
- `product-features-{date}.md`
- `claims-and-proof.md`

## Context Quality Checklist

Before saving context, verify:

- [ ] All claims are specific (numbers, percentages, quotes)
- [ ] Data sources are cited (survey size, interview count, public data link)
- [ ] Customer quotes are direct and representative
- [ ] Competitive claims are fact-checked
- [ ] Limitations and caveats are noted ("This estimate based on N=10, needs validation")
- [ ] File includes owner name and date
- [ ] "Last review" date is noted
- [ ] Actionable implications section exists
- [ ] Links to related strategy documents

## How Agents Should Use This Folder

### Before Writing Any Content:

1. **Load relevant context** — If writing ad copy, read customer-personas.md + product-features.md
2. **Verify claims** — Check claims-and-proof.md before making public statements
3. **Understand competitive position** — Read competitor analysis to inform differentiation messaging
4. **Know your audience** — Load customer personas to understand pain points and language

### Example Usage Chain:

- Agent needs to write LinkedIn post about time savings
- Agent loads: `customer-success-time-saved.md` → finds "architects report saving 40 hours/month"
- Agent loads: `product-features-{date}.md` → understands HOW time is saved (segmentation, no re-render)
- Agent loads: `competitor-analysis.md` → sees that Lumion users report 10-30 hour render times
- Agent writes specific, credible post with data

## Current Context Files

(Add context materials here as they're created/organized)

## Difference Between \_context/ and research/

- **\_context/** — Stable reference materials; foundational answers to "why," "who," "what" (already researched, already incorporated into strategy)
- **research/** — Active findings from ongoing monitoring; community trends, pain points, engagement opportunities (e.g., what Twitter users are saying THIS week)
