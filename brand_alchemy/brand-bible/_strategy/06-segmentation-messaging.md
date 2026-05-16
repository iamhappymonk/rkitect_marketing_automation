# Segmentation Feature: Messaging & Campaigns

_Source: rkitect_segmentation_competitive_report.docx | Last updated: 2026-05-13_

## Feature Overview

**Feature Name:** Sektura (Post-Render Material & Object Segmentation)

**What it does:**

- AI reads and analyzes the rendered output
- Automatically identifies and labels every major object: walls, windows, doors, flooring, furniture, lighting, materials
- User clicks any labeled object and modifies it instantly without re-rendering
- Changes apply in seconds (vs. 45-90 seconds per object on competitor tools)

## Why This Is Defensible

### Moat Duration Estimates

- **ArchiVinci, mnml.ai, MyArchitectAI:** 12-18 months to copy (have rendering pipeline, need segmentation layer)
- **Veras, LookX:** 9-15 months (have 3D model integration advantage)
- **New competitors:** 18-24 months (must build from scratch)

### What Competitors Would Need

1. Post-render image segmentation pipeline (3-6 months)
2. Real-time object labeling and semantic understanding (4-8 months)
3. Non-destructive editing engine respecting spatial relationships (4-6 months)
4. Full integration with render engine for instant material/color swaps (2-3 months)
5. Testing and reliability across diverse architectural inputs (2-4 months)

**Total effort: 15-27 months minimum**

## Core Messaging Headline

**"The AI that reads your render and segments every element for instant editing."**

Alternative headlines:

- "Every surface is labeled. Click any one. Change it in 5 seconds."
- "Your render. Your rules. Every element, instantly editable."
- "No re-rendering. No masking. Just click, change, done."

## Content Campaigns

### Campaign 1: "Before vs After" (60-second Reel/Short)

**Visual:** Split screen showing same room render being edited in two ways:

- _Left side (Competitor Tool):_ User manually brushes over sofa for 30 seconds, types prompt, waits for result (shows spinning loader)
- _Right side (rkitect.ai):_ AI shows labeled segments, user clicks "sofa," selects velvet material from dropdown, done in 5 seconds

**Caption:** "45-90 seconds per object vs. 5 seconds. That's not an improvement. That's a different category."

**Goal:** Viral comparison that doesn't attack competitors by name, just shows time difference as the story.

---

### Campaign 2: "The Object Map" Content Series (LinkedIn + Instagram)

**Visual:** Screenshot of beautifully complex room render with rkitect.ai segmentation overlay showing all labeled objects visible.

**Example layout:**

- Walls labeled "Wall_Accent" (orange), "Wall_Main" (cream)
- Flooring: "Marble_Floor", "Wood_Accent"
- Furniture: "Sofa", "Coffee_Table", "Wall_Art"
- Lighting: "Pendant_1", "Pendant_2", "Floor_Lamp"

**Caption:** "rkitect.ai just read this render and identified every object. Click any label. Change any material. No brushing. No masking. Just click."

**Goal:** Visually distinctive format — no competitor can produce equivalent screenshot. Creates SEO/social proof momentum.

---

### Campaign 3: "Material Explorer" Client Workflow (LinkedIn)

**Visual:** Time-lapse showing same room with 8 different floor materials — marble, timber, concrete, terrazzo, porcelain, engineered wood, stone, and hybrid.

**Workflow shown:**

1. Render complete (5 seconds)
2. User clicks "Floor" label
3. Each material swaps in (5 seconds each)
4. Total time: Under 2 minutes

**Caption:** "Your client wants to see marble, timber, concrete, and terrazzo options. Other tools make you re-render the whole room each time. rkitect.ai lets you click the floor and switch materials in seconds."

**Target:** Senior architects managing client revision rounds.

---

### Campaign 4: "The Manual Masking Tax" (Education Post)

**Content:** Quantify the time cost of manual masking on competitor tools.

**Post copy:**

> Every time you use [competitor] to change a material, you spend 45–90 seconds carefully painting a mask around the object.
>
> On a 10-material client exploration: 7–15 minutes of masking work.
> On rkitect.ai: 0 minutes. We mask it for you.
>
> This is the hidden cost of competitor tools that architects haven't named yet. Introducing Sektura: AI segmentation that reads your render and labels every surface.

**Goal:** Position as a "named pain" that architects recognize but haven't articulated. OwnThe conversation about time cost.

---

### Campaign 5: "Architect Testimonial" (Short Video)

**Format:** 30-second architect reaction to first segmentation experience.

**Script:**

> _[Architect sees labeled render]_
> "Wait, it labeled everything automatically?"
>
> _[Clicks sofa, changes material]_
> "That's... it? That was 3 seconds. On our old tool that was... 5 minutes."
>
> _[Changes wall color]_
> "No re-render?"
>
> _[Smiles]_
> "This is the feature we've been waiting for."

**Goal:** Authentic emotional reaction. No marketing speak. Raw discovery moment.

---

## Feature Gap Closure

While rkitect.ai's segmentation is uniquely superior, consider matching two competitor features to ensure no weakness in head-to-head comparisons:

### Gap 1: Style Variation Control

- **Competitor advantage:** LookX, mnml.ai let users select/train specific architectural styles
- **rkitect.ai consideration:** Develop style profile system or style-locking within Sektura labels
- **Timeline:** Roadmap for Month 3-4

### Gap 2: Export & Presentation Board Features

- **Competitor advantage:** ArchiVinci has built-in presentation export (PDF with multiple renders)
- **rkitect.ai consideration:** Add multi-render export → presentation board template system
- **Timeline:** Roadmap for Month 2-3

---

## Competitive Counter-Positioning

| When Prospect Says                                    | Counter Position                                                                                                                                       |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "We use [Competitor]'s API for our proptech platform" | "rkitect.ai's B2B API launches Month 4. You'll get segmentation built-in — your clients get instant material changes."                                 |
| "We need BIM integration"                             | "Sektura works from CAD exports, floor plans, photos. No BIM requirement. Your existing team workflow + our segmentation = 3x faster."                 |
| "Credit costs are fine for us"                        | "Credit costs scale unpredictably. At ₹16.50/render, a 10-option exploration = ₹165. On competitor credit tiers = ₹2,000+. That's your actual margin." |
| "[Competitor] has better render quality"              | "Render quality is subjective. Editing speed and control are measurable. Spend 2 minutes changing materials or 15 minutes re-rendering?"               |
| "We already trained on our firm's style"              | "Great. Sektura works with any style. Upload your reference aesthetic, get Sektura labels on every surface. Best of both."                             |

---

## Verification Needed (Before Public Use)

- [ ] Product demo showing Sektura in action (labeled objects, instant edits)
- [ ] Timing verification: confirm 45-90 sec masking on competitors, <5 sec on Sektura
- [ ] Test Sektura reliability across: hand sketches, photos, CAD exports, 3D models
- [ ] Screenshot examples showing labeled render for each input type
- [ ] Case study: real architect using Sektura for client revision workflow (with metrics)
- [ ] Competitor pricing screenshot (dated) for cost comparison claims
- [ ] Technical documentation: Sektura segmentation accuracy, error cases, limitations
