# Templates Audit Report — 2026-05-13

**Objective:** Evaluate all templates in `brand_alchemy/templates/` for rkitect-readiness, clarity, completeness, and agent usability.

**Evaluation Criteria:**

1. Generic vs. rkitect-specific (content pillar mapping, brand voice alignment)
2. Working examples (at least 1 complete rkitect-specific example)
3. Approval checklist (claim verification, brand compliance)
4. Content pillar mapping (35-25-20-10-10 framework)
5. Brand voice and claims-and-proof alignment
6. Agent clarity (can a new agent execute without asking questions?)

**Content Pillar Framework (rkitect.ai):**

- **35% Education & Insight** — Feature explanations, technical deep-dives, workflow guides
- **25% Social Proof & Transformation** — Before/after comparisons, case studies, testimonials
- **20% Inspiration & Trend** — Design aesthetics, emerging styles, design philosophy
- **10% Behind-the-Product** — Build journey, team stories, product decisions
- **10% CTA & Conversion** — Free trial offers, comparisons, plan explainers

---

## Template Audit Results

### 1. Content Brief Template ⚠️ Partial

**File:** [brand_alchemy/templates/content-brief-template.md](brand_alchemy/templates/content-brief-template.md)

**Quality Level:** Generic / Partial  
**Generic Fields:** 10/13 (77%)  
**Rkitect Fields:** 0

**Current Structure:**

```
- Working title
- Owner
- Audience
- Funnel stage
- Content type
- Channel
- Primary pain point
- Primary message
- CTA
- Keywords
- Source notes
- Claims to verify
- Draft deadline
- Reviewers
- Distribution plan
- Success metric
```

**What's Working:**
✅ Has `Claims to verify` field (good reminder for claims-and-proof.md)  
✅ Includes audience and funnel stage  
✅ Has success metric field

**Critical Gaps:**
❌ No rkitect-specific pain points or audience segments  
❌ No content pillar indicator (35-25-20-10-10)  
❌ No brand voice or compliance guidance  
❌ No example of a completed rkitect brief  
❌ No link to claims-and-proof.md  
❌ Missing tone/style guidelines for rkitect  
❌ No editorial constraints (e.g., "avoid hype language")  
❌ Unclear what "Success metric" means for content (traffic? leads? shares?)

**What an Agent Needs:**

- Example of a completed brief for "Post-render segmentation explained" (35% pillar)
- Example of a completed brief for "Before/after render comparison" (25% pillar)
- Mapping table: Audience segment → Content type → Funnel stage
- Explicit reminder: Check claim against claims-and-proof.md before draft deadline
- Brand voice checklist: "Avoid: industry-leading, magical, just type. Use: practical, workflow-focused, controlled."

**Priority:** 🔴 **HIGH** — This is the first step in content creation. Agents need immediate rkitect context.

**Recommendation:**

```
Add to template:
1. Rkitect-specific audiences (independent architects, small studios, students, developers)
2. Content pillar selector (Radio: 35 | 25 | 20 | 10 | 10)
3. 2 worked examples (architecture + education + before/after)
4. Claim verification reminder with link to claims-and-proof.md
5. Brand voice guardrails section
6. Typical success metrics by funnel stage (Awareness: top 10 ranking + 500+ views | Consideration: 20+ inbound | Decision: 5+ trial signups)
```

---

### 2. Campaign Brief Template ⚠️ Partial

**File:** [brand_alchemy/templates/campaign-brief-template.md](brand_alchemy/templates/campaign-brief-template.md)

**Quality Level:** Generic / Partial  
**Generic Fields:** 17/17 (100%)  
**Rkitect Fields:** 0

**Current Structure:**

```
- Campaign name
- Owner
- Objective
- Audience
- Insight/problem
- Core message
- Offer
- CTA
- Channels
- Required assets
- Timeline
- Budget/resources
- KPI
- Risks
- Launch checklist
- Retrospective notes
```

**What's Working:**
✅ Has "Insight/problem" field (foundation for positioning)  
✅ Includes launch checklist (process rigor)  
✅ Has retrospective notes (learning loop)  
✅ Complete field coverage for campaign planning

**Critical Gaps:**
❌ No rkitect-specific campaigns as examples  
❌ No product/feature positioning guidance  
❌ No audience mapping (which segments? which buyer types?)  
❌ No content pillar alignment  
❌ No messaging hierarchy reference (one-liner, elevator pitch, deep dive)  
❌ No regulatory/compliance notes (DPDP, Startup India claims)  
❌ "KPI" undefined — traffic? leads? signups?  
❌ No target audience definition table  
❌ Unclear what "Launch checklist" should contain

**What an Agent Needs:**

- Example campaign: "Post-render Segmentation Education Push" across LinkedIn + blog
- Example campaign: "Student Free Tier Acquisition" across Reddit + Instagram
- Audience mapping: Studio Principal | Working Architect | Student → Preferred channels
- Launch checklist template (pre-flight: brand review, claim verification, legal check, design QA)
- Risk registry: "AI claims without evidence" → "Mitigation: check claims-and-proof.md"

**Priority:** 🔴 **HIGH** — Campaigns require strategic alignment. Agents need rkitect context upfront.

**Recommendation:**

```
Add to template:
1. Rkitect audience selector (with buyer type, decision trigger, preferred channel)
2. Messaging hierarchy reference (link to brand-bible level 1-4 messaging)
3. 2 complete worked examples (feature education + audience acquisition)
4. Content pillar breakdown (what % of assets in each pillar?)
5. Pre-launch compliance checklist (brand review, claim verification, legal, design)
6. KPI definition by objective (awareness: reach/impressions | consideration: engagement | decision: conversion rate)
7. Regulatory checklist: DPDP, DPIIT claims, pricing accuracy
```

---

### 3. Social Post Template ⚠️ Partial

**File:** [brand_alchemy/templates/social-post-template.md](brand_alchemy/templates/social-post-template.md)

**Quality Level:** Generic / Partial  
**Generic Fields:** 12/12 (100%)  
**Rkitect Fields:** 0

**Current Structure:**

```
- Campaign/theme
- Channel
- Audience
- Pain point
- Post copy
- Creative direction
- CTA/link
- Hashtags
- Claims to verify
- Approval status
- Scheduled date
- Performance notes
```

**What's Working:**
✅ Has `Claims to verify` field (good)  
✅ Includes creative direction (visual guidance)  
✅ Has performance notes (learning loop)  
✅ Approval status field (process checkpoint)

**Critical Gaps:**
❌ No rkitect-specific examples (Instagram, Twitter, LinkedIn)  
❌ No channel-specific guidance (LinkedIn isn't Twitter)  
❌ No character limit guidance by platform  
❌ No hashtag strategy (which hashtags for architects? students? developers?)  
❌ No content pillar indicator  
❌ No brand voice checklist  
❌ Undefined "Campaign/theme" — what are rkitect themes?  
❌ No approval workflow (who approves? legal review needed?)  
❌ No link to claims-and-proof.md

**What an Agent Needs:**

- Platform-specific templates (LinkedIn 1000-char thought leadership post vs. Instagram Story vs. Twitter thread)
- Rkitect audience personas with preferred hashtags
- 3 worked examples: LinkedIn post (Education), Instagram post (Inspiration), Twitter thread (Social Proof)
- Brand voice reminders: "Avoid: 'revolutionary.' Use: 'practical,' 'tested,' 'built for real architects.'"
- Approval checklist: Legal flag for claims, brand review flag for voice
- Performance baseline by channel (LinkedIn engagement rate, Instagram reach, Twitter impressions)

**Priority:** 🟠 **HIGH-MEDIUM** — Social is high-volume content. Templates must speed up creation while maintaining quality.

**Recommendation:**

```
Add to template:
1. Platform selector (LinkedIn | Instagram | Twitter | Reddit | TikTok) with platform-specific guidance
2. Character limits and format requirements by platform
3. 3 worked examples (one per major platform)
4. Content pillar indicator (which pillar does this post serve?)
5. Target audience for this post (Studio Principal | Architect | Student | Developer)
6. Hashtag strategy section with 5–10 recommended hashtags for rkitect audience
7. Brand voice checklist: "Did I avoid hype language? Did I lead with workflow value?"
8. Claims verification flag with link to claims-and-proof.md
9. Approval workflow: Brand > Legal (if claims) > Post
```

---

### 4. Brand Review Checklist Template ✅ Good

**File:** [brand_alchemy/templates/brand-review-checklist-template.md](brand_alchemy/templates/brand-review-checklist-template.md)

**Quality Level:** Generic / Solid  
**Generic Fields:** 10/10 (100%)  
**Rkitect Fields:** 0 (not needed for generic checklist)

**Current Structure:**

```
- Asset name
- Reviewer
- Brand voice pass/fail
- Message clarity pass/fail
- Positioning alignment pass/fail
- Visual consistency pass/fail
- Claims verified
- Legal/compliance needed
- Required edits
- Approval decision
```

**What's Working:**
✅ Complete brand review process built in  
✅ Clear pass/fail structure  
✅ Includes claims verification gate  
✅ Legal/compliance checkpoint  
✅ Required edits tracking  
✅ Clear approval decision field  
✅ Can be used across any brand/context

**Gaps (Minor):**
⚠️ No rkitect brand voice guidelines embedded (agents must reference brand-bible)  
⚠️ No link to brand-bible or claims-and-proof.md  
⚠️ No definition of "Brand voice pass/fail" criteria  
⚠️ Could benefit from scoring (e.g., "2 edits needed" vs vague "Required edits")

**What Works Well:**

- Process is brand-agnostic, which allows reuse across projects
- Includes gate for claims verification (critical for rkitect)
- Clear approval decision path
- Can be used as-is or enhanced with rkitect brand context

**Priority:** 🟢 **LOW** — This template is already solid. Minor guidance improvements only.

**Recommendation:**

```
Add optional rkitect-specific guidance (not required, but helpful):
1. Link to brand-bible for voice definition
2. Link to claims-and-proof.md in "Claims verified" section
3. Brand voice checklist reminders: "Practical? Respectful of expertise? Controlled, not magical?"
4. Visual consistency reference: Design guidelines location
5. Optional scoring system: "Pass" | "2 edits needed" | "Fail / rewrite required"
```

---

### 5. Publishing Checklist Template ✅ Good

**File:** [brand_alchemy/templates/publishing-checklist-template.md](brand_alchemy/templates/publishing-checklist-template.md)

**Quality Level:** Generic / Solid  
**Generic Fields:** 11/11 (100%)  
**Rkitect Fields:** 0 (not needed for generic checklist)

**Current Structure:**

```
- Asset URL/location
- Owner
- Final approver
- SEO title/meta
- Links tested
- UTM added
- Images/alt text checked
- Mobile preview checked
- Published URL
- Post-publish QA notes
```

**What's Working:**
✅ Complete pre-publish QA process  
✅ SEO best practices included (title, meta)  
✅ UTM tracking built in  
✅ Mobile responsiveness check  
✅ Post-publish QA checkpoint  
✅ Generic enough to work across any brand

**Gaps (Minor):**
⚠️ No rkitect-specific considerations (e.g., claim verification gate before publishing)  
⚠️ No link to claims-and-proof.md  
⚠️ "Links tested" unclear — internal, external, or both?  
⚠️ No redirect or canonical URL guidance  
⚠️ No social media sharing optimization field  
⚠️ No tracking setup verification (GA, event tracking)

**What Works Well:**

- Comprehensive coverage of technical publishing requirements
- UTM strategy built in (good for tracking campaigns)
- Mobile preview check (critical for rkitect user base)
- Post-publish QA ensures quality

**Priority:** 🟢 **LOW** — Template is solid. Enhancement is optional.

**Recommendation:**

```
Add optional guidance:
1. Pre-publish claims gate: "Have all claims been verified in claims-and-proof.md?"
2. Define "Links tested": "Internal links point to live pages | External links open in new tab | No broken 404s"
3. Social media preview (check how post appears in LinkedIn, Twitter, etc.)
4. Event tracking setup verification (goals, conversions in analytics)
5. Email preview (if applicable)
6. Mobile app/email client preview (if content goes via email)
```

---

### 6. Outreach Sequence Template ⚠️ Partial

**File:** [brand_alchemy/templates/outreach-sequence-template.md](brand_alchemy/templates/outreach-sequence-template.md)

**Quality Level:** Generic / Partial  
**Generic Fields:** 10/10 (100%)  
**Rkitect Fields:** 0

**Current Structure:**

```
- Target segment
- Offer
- Reason for outreach
- Personalization fields
- Email/message 1
- Follow-up 1
- Follow-up 2
- Breakup message
- Objection handling notes
- Compliance notes
```

**What's Working:**
✅ Includes compliance notes (important for cold email)  
✅ Has objection handling (sales preparation)  
✅ Personalization fields defined  
✅ Follow-up sequence built in  
✅ Breakup message included (list hygiene)

**Critical Gaps:**
❌ No rkitect-specific target segments (Studio Principal? Student? Developer?)  
❌ No rkitect offers (Free trial? Feature walkthrough? Student discount?)  
❌ No examples of email copy (agents need scaffolding)  
❌ No timing guidance (how many days between follow-ups?)  
❌ No A/B testing fields (subject line variants, copy variants)  
❌ Unclear what "Compliance notes" means (GDPR? CAN-SPAM? India email laws?)  
❌ No success metrics (open rate target? response rate target?)  
❌ No link to claims-and-proof.md (for outreach claim verification)

**What an Agent Needs:**

- Rkitect target segments (Studio Principal, Independent Architect, Student, Developer, Architecture Firm)
- Sample offers per segment (30-min product demo, free 50 renders, student discount)
- 1 complete worked sequence (3 emails, timing, objection handling)
- Email copy templates with tone guidelines
- Timing recommendations (day 0, day 3, day 7, day 14 breakup)
- Compliance reference (CAN-SPAM, India IT Act, GDPR)
- A/B testing guidance (vary subject line or copy or offer)

**Priority:** 🔴 **HIGH** — Outreach is high-volume. Agents need concrete rkitect examples.

**Recommendation:**

```
Add to template:
1. Rkitect target segment selector (with buyer type, buying trigger, preferred channel)
2. Offer examples by segment (Studio: demo | Student: free credits | Developer: API access)
3. 1 complete worked sequence (3-email series with timing, copy, objections)
4. Timing field: "Days between follow-ups" (e.g., "Day 0: initial | Day 3: follow-up 1 | Day 7: follow-up 2")
5. Subject line variants (A/B testing)
6. Brand voice guidelines: "Avoid: 'revolutionary.' Use: 'built for real architects,' 'practical help.'"
7. Compliance checklist: "Is this CAN-SPAM compliant? GDPR? India IT Act?"
8. Claims verification: Link to claims-and-proof.md for outreach claims
9. Success metrics: Target open rate, click rate, response rate by segment
```

---

### 7. Research Note Template ✅ Good

**File:** [brand_alchemy/templates/research-note-template.md](brand_alchemy/templates/research-note-template.md)

**Quality Level:** Generic / Solid  
**Generic Fields:** 10/10 (100%)  
**Rkitect Fields:** 0 (not needed for generic research)

**Current Structure:**

```
- Source
- Date captured
- Source type
- Summary
- Relevant audience
- Relevant pain
- Useful quote or insight
- Confidence
- Actionability
- Related docs
```

**What's Working:**
✅ Complete research capture process  
✅ Includes confidence rating (quality signal)  
✅ Actionability field (turns research into strategy)  
✅ Related docs linking (knowledge management)  
✅ Captures audience relevance immediately  
✅ Pain point mapping built in

**Gaps (Minor):**
⚠️ "Source type" undefined (blog post? competitor? customer interview? Reddit?)  
⚠️ No guidance on confidence scale (1-5? Certain/Likely/Possible?)  
⚠️ No guidance on actionability scale  
⚠️ Could benefit from competitor labeling field  
⚠️ No "Conflicting with" field (if research contradicts existing assumption)

**What Works Well:**

- Researchers can use this immediately without rkitect context
- Forces structured capture (quality improves retention)
- Links to related docs enable knowledge graph
- Confidence and actionability fields drive prioritization

**Priority:** 🟢 **LOW** — Template is solid. Minimal guidance needed.

**Recommendation:**

```
Add optional guidance:
1. Source type examples: Blog post, Competitor website, Reddit/community, Customer interview, Tweet/LinkedIn, News article, Survey, Analyst report
2. Confidence scale definition: "1 = Rumor/speculation | 3 = Likely based on evidence | 5 = Certain/verified"
3. Actionability scale: "1 = Nice-to-know | 3 = Could inform strategy | 5 = Must act on this"
4. Optional: Competitor label (if research is about competitors)
5. Optional: Conflicting with field (e.g., "Conflicts with: earlier assumption about pricing")
```

---

### 8. SOP Template ✅ Good

**File:** [brand_alchemy/templates/sop-template.md](brand_alchemy/templates/sop-template.md)

**Quality Level:** Generic / Solid  
**Generic Fields:** 9/9 (100%)  
**Rkitect Fields:** 0 (not needed for generic SOP)

**Current Structure:**

```
- SOP name
- Purpose
- Owner
- Inputs
- Workflow steps
- Outputs
- Review checklist
- Escalation path
- Update cadence
```

**What's Working:**
✅ Complete SOP structure  
✅ Clear inputs/outputs definition  
✅ Review checklist built in  
✅ Escalation path included (process rigor)  
✅ Update cadence field (keeps SOPs current)  
✅ Generic enough to apply anywhere

**Gaps (Minor):**
⚠️ "Workflow steps" not structured (list? numbered? flowchart?)  
⚠️ No template for "Review checklist" content  
⚠️ No guidance on escalation criteria  
⚠️ Could benefit from "Exceptions" or "When not to use" field  
⚠️ No role/permissions field (who can execute this SOP?)

**What Works Well:**

- Clear ownership (accountability)
- Review checklist ensures quality
- Update cadence prevents drift
- Escalation path prevents bottlenecks

**Priority:** 🟢 **LOW** — Template is solid.

**Recommendation:**

```
Add optional guidance:
1. Workflow steps format guidance: "Use numbered steps with decision points"
2. Review checklist template: "Does output match specification? Has quality been checked?"
3. Escalation criteria example: "Escalate to owner if [X condition]"
4. Optional: Exceptions field (when this SOP should NOT be used)
5. Optional: Roles/permissions (who can execute this SOP?)
6. Optional: Dependencies (what other SOPs or systems does this depend on?)
```

---

### 9. Task Template ✅ Good

**File:** [brand_alchemy/templates/task-template.md](brand_alchemy/templates/task-template.md)

**Quality Level:** Generic / Solid  
**Generic Fields:** 8/8 (100%)  
**Rkitect Fields:** 0 (not needed for generic task)

**Current Structure:**

```
- Task
- Owner
- Status
- Source doc
- Acceptance criteria
- Dependencies
- Due date
- Notes
```

**What's Working:**
✅ Clear ownership (accountability)  
✅ Acceptance criteria defined upfront (prevents rework)  
✅ Dependencies tracked  
✅ Source doc reference (context linking)  
✅ Simple and unambiguous

**Gaps (Minor):**
⚠️ "Status" not enumerated (should be: Backlog | In Progress | Review | Done?)  
⚠️ No priority field (critical? high? normal? low?)  
⚠️ No blockers field (what's preventing progress?)  
⚠️ No "Assignee" field (who should do this?)  
⚠️ No "Started date" field (helps with duration tracking)  
⚠️ No "Subtasks" structure

**What Works Well:**

- Lightweight, doesn't add friction
- Acceptance criteria prevents scope creep
- Source doc links to context
- Simple enough for daily use

**Priority:** 🟢 **LOW** — Template is adequate.

**Recommendation:**

```
Add optional guidance:
1. Status enum: "Backlog | In Progress | In Review | Done | Blocked"
2. Priority field: "🔴 Critical | 🟠 High | 🟡 Normal | 🟢 Low"
3. Blockers field: "What's preventing progress?"
4. Assignee field: (separate from Owner; Owner = accountability, Assignee = current executor)
5. Subtasks structure (for large tasks that need breakdown)
6. Started date field (helps with duration tracking)
```

---

### 10. AI Agent Task Template ⚠️ Partial

**File:** [brand_alchemy/templates/ai-agent-task-template.md](brand_alchemy/templates/ai-agent-task-template.md)

**Quality Level:** Generic / Partial  
**Generic Fields:** 10/10 (100%)  
**Rkitect Fields:** 0

**Current Structure:**

```
- Task name
- Agent/tool used
- Input provided
- Required context files
- Expected output
- Constraints
- Sources required
- Human reviewer
- Final decision
- Notes/issues
```

**What's Working:**
✅ Clear agent/tool specification  
✅ Required context files listed (good for agent clarity)  
✅ Constraints defined (prevents hallucination)  
✅ Sources required (good governance)  
✅ Human review gate built in  
✅ Final decision field (audit trail)

**Critical Gaps:**
❌ No rkitect-specific agent roles or examples  
❌ No context file locations (where are context files?)  
❌ No examples of good/bad inputs  
❌ No examples of expected output  
❌ No guidance on constraint examples  
❌ Unclear what "Sources required" means (primary? secondary? verified?)  
❌ No approval workflow (who reviews? timeline?)

**What an Agent Needs:**

- Rkitect agent examples (Content Strategist, Brand Reviewer, Social Curator)
- Context file locations (brand_alchemy/brand-bible/\_context/, brand_alchemy/research/, brand_alchemy/sops/)
- Example task: "Content strategist: Generate 5 blog topics for Q2 2026"
- Constraint examples: "Must avoid unverified claims," "Must reference 35-25-20-10-10 pillar distribution"
- Source requirements: "Must check claims-and-proof.md," "Must reference 2+ competitor analysis points"
- Approval workflow: Brand review > Legal (if claims) > Publish

**Priority:** 🟡 **MEDIUM** — Useful for agent governance, but not blocking.

**Recommendation:**

```
Add to template:
1. Rkitect agent selector (Content Strategist | Brand Reviewer | Social Curator | Research Analyst)
2. Context files location guide: "Load from brand_alchemy/brand-bible/_context/, brand_alchemy/research/"
3. 1 worked example: Task name, agent, input, context, expected output, constraints, sources, review, decision
4. Constraint examples: "Must use brand voice," "Must verify claims in claims-and-proof.md," "Must map to 35-25-20-10-10"
5. Sources required guidance: "Primary sources preferred (product data, customer interviews) | Secondary (analyst reports) | Tertiary (news)"
6. Approval workflow: "Brand review > Legal (if claims) > Publish"
7. Timeline: "Expected review time: 24-48 hours"
```

---

## Summary Table

| Template                   | Quality | Generic | Rkitect Ready | Priority  | Key Issue                                      |
| -------------------------- | ------- | ------- | ------------- | --------- | ---------------------------------------------- |
| **Content Brief**          | Partial | ⚠️ 77%  | ❌ 0%         | 🔴 HIGH   | No pillar mapping, no rkitect examples         |
| **Campaign Brief**         | Partial | ⚠️ 100% | ❌ 0%         | 🔴 HIGH   | No audience mapping, no rkitect examples       |
| **Social Post**            | Partial | ⚠️ 100% | ❌ 0%         | 🟠 HIGH   | No platform guidance, no brand voice checklist |
| **Brand Review Checklist** | Good    | ✅ 100% | ✅ Solid      | 🟢 LOW    | Minor: link brand-bible                        |
| **Publishing Checklist**   | Good    | ✅ 100% | ✅ Solid      | 🟢 LOW    | Minor: add claims gate                         |
| **Outreach Sequence**      | Partial | ⚠️ 100% | ❌ 0%         | 🔴 HIGH   | No rkitect segments, no worked examples        |
| **Research Note**          | Good    | ✅ 100% | ✅ Solid      | 🟢 LOW    | Minor: define source types                     |
| **SOP**                    | Good    | ✅ 100% | ✅ Solid      | 🟢 LOW    | Minor: clarify steps structure                 |
| **Task**                   | Good    | ✅ 100% | ✅ Solid      | 🟢 LOW    | Minor: add status enum                         |
| **AI Agent Task**          | Partial | ⚠️ 100% | ❌ 0%         | 🟡 MEDIUM | No rkitect agents, no examples                 |

---

## Critical Findings

### 🔴 Red Flags (Blocking Agent Productivity)

1. **No rkitect examples in creation templates** — Content Brief, Campaign Brief, Social Post, Outreach Sequence lack worked examples. Agents must ask clarifying questions instead of executing.

2. **No content pillar mapping** — Templates don't guide 35-25-20-10-10 distribution. Agents won't know if content serves the right strategic purpose.

3. **Missing claims verification gates** — Social Post and Outreach Sequence templates don't reference claims-and-proof.md. Risk of unverified public claims.

4. **No brand voice checklist in content creation** — Agents have no quick reference for rkitect voice guidelines (practical, controlled, architect-respectful, no hype).

5. **Undefined approval workflows** — Campaign Brief and Social Post have "approval status" but no approval path, timeline, or who approves.

### 🟠 Yellow Flags (Slowing Agent Execution)

1. **Platform-specific guidance missing** — Social Post template treats LinkedIn, Instagram, and Twitter equally. Requires agent research.

2. **No audience segment table** — Content Brief, Campaign Brief, Outreach Sequence don't map to rkitect personas (Studio Principal, Architect, Student, Developer).

3. **Compliance notes undefined** — Outreach Sequence says "compliance notes" but doesn't explain what (CAN-SPAM? GDPR? India laws?).

4. **Vague success metrics** — Templates use "KPI," "Success metric," "Performance" without definition. Agents must infer meaning.

### 🟢 Green Flags (Working Well)

- Brand Review Checklist: Complete process, clear gates ✅
- Publishing Checklist: Technical completeness ✅
- Research Note: Good capture structure ✅
- SOP Template: Clear ownership and update cadence ✅
- Task Template: Lightweight, acceptance criteria clear ✅

---

## Recommendations by Priority

### Priority 1: Add Rkitect Examples (HIGH — Weeks 1–2)

**Action:** Create rkitect-specific worked examples for:

- Content Brief (2 examples: 35% pillar article + 25% pillar article)
- Campaign Brief (1 example: "Segmentation feature education campaign")
- Social Post (3 examples: LinkedIn + Instagram + Twitter)
- Outreach Sequence (1 example: "Studio Principal outreach sequence")

**Effort:** 4–6 hours  
**Impact:** Enables agents to create content without asking clarifying questions  
**Who:** Content strategist with rkitect brand knowledge

### Priority 2: Add Content Pillar Mapping (HIGH — Weeks 1–2)

**Action:** Add pillar selector/indicator to:

- Content Brief (dropdown: 35 | 25 | 20 | 10 | 10)
- Campaign Brief (breakdown: e.g., "65% Education, 25% Social Proof, 10% CTA")
- Social Post (indicator: which pillar does this serve?)

**Effort:** 2–3 hours  
**Impact:** Ensures content aligns with strategic distribution  
**Who:** Marketing strategist + template maintainer

### Priority 3: Add Approval Workflows & Claims Gates (HIGH — Weeks 2–3)

**Action:** Define and add:

- Pre-publish claims verification gate (reference claims-and-proof.md)
- Approval workflow diagram (Brand > Legal > Publish)
- Who approves what (brand voice: content strategist | claims: legal)
- Timeline SLA (e.g., "Brand review within 24 hours")

**Effort:** 3–4 hours  
**Impact:** Prevents unverified claims and brand voice errors  
**Who:** Legal + marketing ops

### Priority 4: Add Brand Voice Checklists (MEDIUM — Week 3)

**Action:** Add quick reference checklists to content templates:

- "Did I avoid hype language? (magical, revolutionary, game-changing)"
- "Did I focus on workflow value? (not aspirational fantasy)"
- "Did I respect architect expertise? (not positioning AI as replacement)"
- "Did I use practical tone? (specific, technical, helpful, not fluff)"

**Effort:** 2 hours  
**Impact:** Catches voice misalignment early, reduces revisions  
**Who:** Brand strategist + content strategist

### Priority 5: Platform-Specific Social Post Guidance (MEDIUM — Week 4)

**Action:** Create platform-specific social post sub-templates:

- LinkedIn (character limits, format, voice, hashtag strategy)
- Instagram (character limits, visual requirements, caption style)
- Twitter/X (thread structure, hashtag strategy, reply engagement)
- Reddit (voice style, community norms, self-promotion rules)

**Effort:** 4–5 hours  
**Impact:** Reduces need for agent research, speeds execution  
**Who:** Social media strategist

### Priority 6: Define Success Metrics (MEDIUM — Week 4)

**Action:** Define baseline metrics for each template type:

- Content Brief: "Success metrics: Rank top 10 for keyword | 500+ organic views | 10+ qualified leads"
- Campaign Brief: "KPI examples by objective: Awareness (50k+ impressions) | Consideration (500+ engagements) | Decision (5% conversion)"
- Outreach Sequence: "Target metrics: 30%+ open rate | 10%+ click rate | 3%+ response rate"

**Effort:** 2–3 hours  
**Impact:** Aligns expectations, enables measurement  
**Who:** Analytics owner + campaign manager

---

## Next Steps

1. **Create working document:** Update each template with Priority 1 improvements (rkitect examples).
2. **Build template companion:** Create [brand_alchemy/templates/TEMPLATE-GUIDANCE.md](brand_alchemy/templates/TEMPLATE-GUIDANCE.md) with rkitect context, checklists, and worked examples.
3. **Test with agent:** Assign a template to an AI agent and measure whether clarifying questions are eliminated.
4. **Measure adoption:** Track which templates agents use and which they skip; iterate based on usage.

---

**Report Completed:** 2026-05-13 | **Status:** Ready for Implementation
