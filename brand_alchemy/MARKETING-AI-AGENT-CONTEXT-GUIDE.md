# Marketing AI Agent: Context Reference Guide

**Purpose:** Help the marketing AI agent know which documents to reference for different task types.

**Use this guide:** When you receive a task, find the task type below and follow the context hierarchy.

---

## Task Type Reference Matrix

### Task: Write Social Media Content (LinkedIn, Instagram, Twitter)

**Step 1 — Understand the brand**

1. Read [brand_alchemy/brand-bible/\_context/brand-bible.md](brand_alchemy/brand-bible/_context/brand-bible.md) — 5-min read on brand essence, promise, personality
2. Read [brand_alchemy/brand-bible/\_strategy/05-voice-and-tone.md](brand_alchemy/brand-bible/_strategy/05-voice-and-tone.md) — Voice rules + do/don't examples

**Step 2 — Pick your angle**

1. Read [brand_alchemy/brand-bible/\_strategy/04-content-system.md](brand_alchemy/brand-bible/_strategy/04-content-system.md) — 5 content pillars (35% Education, 25% Social Proof, etc.)
2. Identify pillar: Is this education (explaining rendering AI)? Social proof (case study)? Inspiration? Behind-product? CTA?

**Step 3 — Know your audience**

1. Read [brand_alchemy/brand-bible/\_context/customer-context.md](brand_alchemy/brand-bible/_context/customer-context.md) — 5 audience segments with pain points, language, buying triggers

**Step 4 — Verify claims**

1. Use [brand_alchemy/brand-bible/\_context/claims-and-proof.md](brand_alchemy/brand-bible/_context/claims-and-proof.md) — Check every numeric claim (speed, pricing, etc.) before including
2. Rule: If status is "Needs proof" → DO NOT USE publicly

**Step 5 — Use the template**

1. Open [brand_alchemy/templates/social-post-template.md](brand_alchemy/templates/social-post-template.md)
2. Follow structure for your platform (LinkedIn format ≠ Instagram ≠ Twitter)
3. Use rkitect examples provided in template

**Step 6 — Verify tone and approval**

1. Check against [brand_alchemy/brand-bible/\_strategy/05-voice-and-tone.md](brand_alchemy/brand-bible/_strategy/05-voice-and-tone.md) — Does it sound confident, direct, helpful? Not hype?
2. Use [brand_alchemy/templates/brand-review-checklist.md](brand_alchemy/templates/brand-review-checklist.md) before sending for approval

**REFERENCE STACK:**

```
brand-bible.md (foundation)
  ↓
voice-and-tone.md (how to sound)
  ↓
customer-context.md (who we're talking to)
  ↓
content-system.md (what pillar?)
  ↓
claims-and-proof.md (verify facts)
  ↓
social-post-template.md (structure)
  ↓
brand-review-checklist.md (quality gate)
```

---

### Task: Launch a Campaign (Email, Ads, Landing Page)

**Step 1 — Understand campaign fit**

1. Read [brand_alchemy/brand-bible/\_strategy/06-segmentation-messaging.md](brand_alchemy/brand-bible/_strategy/06-segmentation-messaging.md) — If it's about post-render segmentation
2. OR read [brand_alchemy/brand-bible/\_strategy/05-go-to-market.md](brand_alchemy/brand-bible/_strategy/05-go-to-market.md) — 90-day GTM phases (Awareness, Acquisition, Monetization)

**Step 2 — Understand positioning**

1. Read [brand_alchemy/brand-bible/\_strategy/02-positioning.md](brand_alchemy/brand-bible/_strategy/02-positioning.md) — Category, wedge, competitor frame
2. Read [brand_alchemy/brand-bible/\_strategy/04-messaging.md](brand_alchemy/brand-bible/_strategy/04-messaging.md) — One-liner, elevator pitch, proof narrative

**Step 3 — Know the audience for this campaign**

1. Read [brand_alchemy/research/competitor-landscape.md](brand_alchemy/research/competitor-landscape.md) — Who are they competing against?
2. Read [brand_alchemy/research/social-community-intelligence-report.md](brand_alchemy/research/social-community-intelligence-report.md) — Where do they hang out?

**Step 4 — Use campaign template**

1. Open [brand_alchemy/templates/campaign-brief-template.md](brand_alchemy/templates/campaign-brief-template.md)
2. Follow structure with rkitect example provided

**Step 5 — Verify no unvalidated claims**

1. Reference [brand_alchemy/brand-bible/\_context/claims-and-proof.md](brand_alchemy/brand-bible/_context/claims-and-proof.md)
2. Flag anything marked "Needs proof" or "Draft claim" — escalate to Aman/Bhavish

**Step 6 — Get approval**

1. Use [brand_alchemy/brand-bible/\_sop/approval-workflow.md](brand_alchemy/brand-bible/_sop/approval-workflow.md) — WHO approves campaigns and timeline
2. Provide draft to [approval authority] with claims verification attached

**REFERENCE STACK:**

```
positioning.md (what category are we in?)
  ↓
messaging.md (what are we saying?)
  ↓
go-to-market.md (what phase of GTM is this?)
  ↓
competitor-landscape.md (who are we positioning against?)
  ↓
social-community-intelligence-report.md (where do audiences hang out?)
  ↓
campaign-brief-template.md (structure)
  ↓
claims-and-proof.md (verify all facts)
  ↓
approval-workflow.md (get approval)
```

---

### Task: Create Outreach Sequence (Email, LinkedIn, DM)

**Step 1 — Know your target**

1. Read [brand_alchemy/brand-bible/\_strategy/03-audience-personas.md](brand_alchemy/brand-bible/_strategy/03-audience-personas.md) — 3 main personas + decision-makers
2. Read [brand_alchemy/brand-bible/\_context/customer-context.md](brand_alchemy/brand-bible/_context/customer-context.md) — Pain points, objections, buying triggers

**Step 2 — Understand competitive positioning**

1. Read [brand_alchemy/research/competitor-landscape.md](brand_alchemy/research/competitor-landscape.md) — How do we position vs their current tools?

**Step 3 — Know what they value**

1. Read [brand_alchemy/brand-bible/\_strategy/02-positioning.md](brand_alchemy/brand-bible/_strategy/02-positioning.md) — Why should they care about rkitect vs alternatives?

**Step 4 — Use outreach template**

1. Open [brand_alchemy/templates/outreach-sequence-template.md](brand_alchemy/templates/outreach-sequence-template.md)
2. Follow multi-touch sequence (email 1, 2, 3; or LinkedIn touch 1, 2; etc.)
3. Use rkitect Studio Principal example provided

**Step 5 — Verify tone and offers**

1. Check tone against [brand_alchemy/brand-bible/\_strategy/05-voice-and-tone.md](brand_alchemy/brand-bible/_strategy/05-voice-and-tone.md)
2. Verify offers/claims against [claims-and-proof.md](brand_alchemy/brand-bible/_context/claims-and-proof.md)

**REFERENCE STACK:**

```
audience-personas.md (who am I reaching?)
  ↓
customer-context.md (what do they care about?)
  ↓
competitor-landscape.md (how do we compare?)
  ↓
positioning.md (why rkitect over alternatives?)
  ↓
voice-and-tone.md (how to sound in personal outreach)
  ↓
outreach-sequence-template.md (structure)
  ↓
claims-and-proof.md (verify every claim)
```

---

### Task: Create Content Brief for Designer/Writer

**Step 1 — Define what we're communicating**

1. Read [brand_alchemy/brand-bible/\_strategy/04-messaging.md](brand_alchemy/brand-bible/_strategy/04-messaging.md) — Core message + pillars
2. Read [brand_alchemy/brand-bible/\_strategy/04-content-system.md](brand_alchemy/brand-bible/_strategy/04-content-system.md) — Content pillars (which one is this?)

**Step 2 — Know the audience**

1. Read [brand_alchemy/brand-bible/\_context/customer-context.md](brand_alchemy/brand-bible/_context/customer-context.md) — Personas, pain points, language

**Step 3 — Understand what makes rkitect different**

1. Read [brand_alchemy/brand-bible/\_strategy/06-segmentation-messaging.md](brand_alchemy/brand-bible/_strategy/06-segmentation-messaging.md) — Post-render segmentation positioning (Sektura)
2. Read [brand_alchemy/brand-bible/\_context/company-profile.md](brand_alchemy/brand-bible/_context/company-profile.md) — Unique moat + competitive analysis

**Step 4 — Use content brief template**

1. Open [brand_alchemy/templates/content-brief-template.md](brand_alchemy/templates/content-brief-template.md)
2. Follow structure: Objective, Audience, Message, Pillar, Tone, Success Metric
3. Use rkitect Education Pillar example provided

**Step 5 — Verify no unproven claims**

1. Check [claims-and-proof.md](brand_alchemy/brand-bible/_context/claims-and-proof.md) — Any numeric claims must be verified
2. Include verification status in brief ("VERIFIED" / "DRAFT CLAIM" / "DO NOT USE")

**REFERENCE STACK:**

```
messaging.md (what's the core message?)
  ↓
content-system.md (which pillar? 35% education, etc)
  ↓
customer-context.md (who's this for?)
  ↓
company-profile.md (what's our unique advantage?)
  ↓
segmentation-messaging.md (if feature-focused: post-render AI)
  ↓
content-brief-template.md (structure for writer/designer)
  ↓
claims-and-proof.md (verify all facts)
```

---

### Task: Make a Decision (Strategy, Positioning, Channel)

**Step 1 — Review existing decisions**

1. Read [brand_alchemy/company-os/decision-log.md](brand_alchemy/company-os/decision-log.md) — What decisions have already been made? What can/can't change?

**Step 2 — Understand decision authority**

1. Read [brand_alchemy/company-os/roles-and-ownership.md](brand_alchemy/company-os/roles-and-ownership.md) — Who decides on strategy? Channels? Positioning?
2. Contact decision owner before proposing change

**Step 3 — Gather supporting context**

- For positioning decisions: [brand-bible.md](brand_alchemy/brand-bible/_context/brand-bible.md), [positioning.md](brand_alchemy/brand-bible/_strategy/02-positioning.md)
- For audience decisions: [customer-context.md](brand_alchemy/brand-bible/_context/customer-context.md), [audience-research.md](brand_alchemy/research/audience-research.md)
- For channel decisions: [channel-research.md](brand_alchemy/research/channel-research.md), [social-community-intelligence-report.md](brand_alchemy/research/social-community-intelligence-report.md)
- For competitor decisions: [competitor-landscape.md](brand_alchemy/research/competitor-landscape.md), [claims-and-proof.md](brand_alchemy/brand-bible/_context/claims-and-proof.md)

**Step 4 — Document the decision**

1. Use [brand_alchemy/company-os/decision-log.md](brand_alchemy/company-os/decision-log.md) template
2. Include: What decision? Why? Who approved? When? Reversal conditions?

**REFERENCE STACK:**

```
decision-log.md (what's already decided?)
  ↓
roles-and-ownership.md (who decides this?)
  ↓
[Relevant context for decision type]
  ↓
decision-log.md (document it)
```

---

## Emergency Reference: When You Don't Know

**"I need to write about rkitect.ai but don't know where to start."**
→ Start here: [brand_alchemy/brand-bible/\_context/brand-bible.md](brand_alchemy/brand-bible/_context/brand-bible.md) + [brand_alchemy/00-start-here.md](brand_alchemy/00-start-here.md)

**"I need to verify a claim before using it."**
→ Go here: [brand_alchemy/brand-bible/\_context/claims-and-proof.md](brand_alchemy/brand-bible/_context/claims-and-proof.md)

**"I'm writing about what makes rkitect different."**
→ Read: [brand_alchemy/brand-bible/\_context/company-profile.md](brand_alchemy/brand-bible/_context/company-profile.md#unique-competitive-moat) + [brand_alchemy/brand-bible/\_strategy/06-segmentation-messaging.md](brand_alchemy/brand-bible/_strategy/06-segmentation-messaging.md)

**"I need to understand our audience."**
→ Read: [brand_alchemy/brand-bible/\_context/customer-context.md](brand_alchemy/brand-bible/_context/customer-context.md) + [brand_alchemy/brand-bible/\_strategy/03-audience-personas.md](brand_alchemy/brand-bible/_strategy/03-audience-personas.md)

**"I need to know how to sound."**
→ Read: [brand_alchemy/brand-bible/\_strategy/05-voice-and-tone.md](brand_alchemy/brand-bible/_strategy/05-voice-and-tone.md)

**"I need to know what competitors are doing."**
→ Read: [brand_alchemy/research/competitor-landscape.md](brand_alchemy/research/competitor-landscape.md) + [brand_alchemy/brand-bible/\_context/market-context.md](brand_alchemy/brand-bible/_context/market-context.md)

**"I'm not sure if I need approval for this."**
→ Check: [brand_alchemy/company-os/roles-and-ownership.md](brand_alchemy/company-os/roles-and-ownership.md) + [brand_alchemy/brand-bible/\_sop/approval-workflow.md](brand_alchemy/brand-bible/_sop/approval-workflow.md) (when written)

**"I don't know what content pillar this fits into."**
→ Reference: [brand_alchemy/brand-bible/\_strategy/04-content-system.md](brand_alchemy/brand-bible/_strategy/04-content-system.md) — 5 pillars (Education 35%, Social Proof 25%, Inspiration 20%, Behind-Product 10%, CTA 10%)

---

## File Path Quick Reference

**Brand Foundation (Start Here)**

- [brand_alchemy/brand-bible/\_context/brand-bible.md](brand_alchemy/brand-bible/_context/brand-bible.md)
- [brand_alchemy/brand-bible/\_context/company-profile.md](brand_alchemy/brand-bible/_context/company-profile.md)
- [brand_alchemy/brand-bible/\_context/customer-context.md](brand_alchemy/brand-bible/_context/customer-context.md)
- [brand_alchemy/brand-bible/\_context/market-context.md](brand_alchemy/brand-bible/_context/market-context.md)
- [brand_alchemy/brand-bible/\_context/claims-and-proof.md](brand_alchemy/brand-bible/_context/claims-and-proof.md)

**Strategy (How to Execute)**

- [brand_alchemy/brand-bible/\_strategy/02-positioning.md](brand_alchemy/brand-bible/_strategy/02-positioning.md)
- [brand_alchemy/brand-bible/\_strategy/03-audience-personas.md](brand_alchemy/brand-bible/_strategy/03-audience-personas.md)
- [brand_alchemy/brand-bible/\_strategy/04-messaging.md](brand_alchemy/brand-bible/_strategy/04-messaging.md)
- [brand_alchemy/brand-bible/\_strategy/04-content-system.md](brand_alchemy/brand-bible/_strategy/04-content-system.md)
- [brand_alchemy/brand-bible/\_strategy/05-voice-and-tone.md](brand_alchemy/brand-bible/_strategy/05-voice-and-tone.md)
- [brand_alchemy/brand-bible/\_strategy/05-go-to-market.md](brand_alchemy/brand-bible/_strategy/05-go-to-market.md)
- [brand_alchemy/brand-bible/\_strategy/06-segmentation-messaging.md](brand_alchemy/brand-bible/_strategy/06-segmentation-messaging.md)

**Research & Intelligence**

- [brand_alchemy/research/competitor-landscape.md](brand_alchemy/research/competitor-landscape.md)
- [brand_alchemy/research/social-community-intelligence-report.md](brand_alchemy/research/social-community-intelligence-report.md)

**Templates (Use These)**

- [brand_alchemy/templates/social-post-template.md](brand_alchemy/templates/social-post-template.md)
- [brand_alchemy/templates/campaign-brief-template.md](brand_alchemy/templates/campaign-brief-template.md)
- [brand_alchemy/templates/content-brief-template.md](brand_alchemy/templates/content-brief-template.md)
- [brand_alchemy/templates/outreach-sequence-template.md](brand_alchemy/templates/outreach-sequence-template.md)
- [brand_alchemy/templates/brand-review-checklist.md](brand_alchemy/templates/brand-review-checklist.md)

**Operations (When You Need Approval)**

- [brand_alchemy/company-os/decision-log.md](brand_alchemy/company-os/decision-log.md)
- [brand_alchemy/company-os/roles-and-ownership.md](brand_alchemy/company-os/roles-and-ownership.md)

**Tasks & Roadmap**

- [brand_alchemy/tasks/task-board.md](brand_alchemy/tasks/task-board.md)
- [brand_alchemy/tasks/milestones.md](brand_alchemy/tasks/milestones.md)
- [brand_alchemy/tasks/AGENT-AUDIT-CONSOLIDATED-ACTION-PLAN.md](brand_alchemy/tasks/AGENT-AUDIT-CONSOLIDATED-ACTION-PLAN.md)
