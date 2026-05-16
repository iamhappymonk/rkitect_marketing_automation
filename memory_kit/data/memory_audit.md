# rkitect.ai · memory audit + B/M/O matrix

Source: buyer-persona interview (Aanya Mehta — Bengaluru boutique principal, architect + interior designer) pressure-testing the 167 facts in the `rkitect-marketing` mem0 namespace.

Lens key: **B** = business case (ROI, deals, time/cost) · **M** = marketing perception (credible/desirable) · **O** = operations (fits daily workflow). Verdict: **KEEP** / **FIX** / **KILL** / **RECLASSIFY**.

---

## A. Decision matrix — claims under review

| # | Claim (as stored) | Lens | Verdict | Corrected / action | Buyer rationale |
|---|---|---|---|---|---|
| 1 | "Edit after render — move a lamp without re-rendering" | O + B | **KEEP — promote to hero** | Make this the lead benefit, above the fold | "The only thing here that solves my actual pain… that changes my business." |
| 2 | "Locks to the client's actual floor plan" (currently implied, buried) | O + B | **KEEP — promote, make explicit** | New top-3 claim + a recognisability guarantee | "This should be your entire headline. Every AI tool moves the sofa." |
| 3 | "Studio of specialist agents (Chief Architect, Interior Designer, …)" | (internal) | **KILL from buyer-facing** | Keep in /how-it-works only; strip from facts used for buyer copy | "Engineering theatre. I don't care if five agents or a monkey." |
| 4 | "42-point design rubric" | (internal) | **KILL from buyer-facing** | Remove from buyer copy; keep as internal QA note | "Means nothing. Whose 42 points? It'll fight my taste." |
| 5 | "6 render engines" | (internal) | **KILL** | Drop entirely; pick one good result | "Tells me you haven't decided which one works." |
| 6 | "Segmentation accuracy 92%" vs "94%" (stated both ways) | M | **FIX — single number + method** | Pick ONE (recommend 92%, matches landing); add how it's measured; purge the 94% facts | "You stated your own core number two ways. Sloppy. Why trust it in front of a ₹2Cr client?" |
| 7 | "$0.20 per render" | B | **FIX — reframe as per-project / per-seat** | Replace with ₹ per-project or ₹ per-seat/mo unlimited. Keep $0.20 as internal unit-cost only | "Per render of what? 30 renders for one living room. Confusion = assume real price extracted later." |
| 8 | "$199/mo unlimited" + "free first 100" + "free students" + "free first render" | B + M | **FIX — collapse to ONE price + ONE free offer** | One pilot price (₹) + one free trigger (first render free). Kill the other 3 | "Four prices. I cannot tell what I'd pay in a year." |
| 9 | "3 hours → 60s" vs "3 days → 60s" vs "7-day → 5-min" | M + B | **FIX — pick ONE real baseline** | Interview 3 real studios; state the true revision-cycle number once | "Three baselines = whatever made the slide look good. You don't know my process." |
| 10 | "Cut rendering costs up to 70%" | B | **FIX — show arithmetic, not %** | Replace with: "₹15k–60k/cycle → ₹X" worked example on a real project | "'Up to 70%' = best case once. Show me the actual arithmetic." |
| 11 | "200+ materials" | O | **FIX — prove India coverage** | Add explicit Indian finishes: Kota, Jaisalmer, terrazzo, teak, IPS, Kadappa, handmade tile | "Meaningless if I can't get a proper Kadappa floor." |
| 12 | "14 NYC studios beta" | M | **KILL / RECLASSIFY** | Replace with real Indian beta proof (Bengaluru/Mumbai studio, ₹ project) | "Built for someone else, India an afterthought. Trust goes down." |
| 13 | "Targets architects + interior designers in India" / IST / ₹ project | M + B | **KEEP — make it THE positioning** | Commit to India-first. Drop NYC framing everywhere | "Proof has to be Indian or it does nothing with my clients." |
| 14 | "One beta user closed a ₹2.5 Cr interior project" | B + M | **KEEP — but substantiate** | Get the studio name + 1-line quote + permission; else mark unverified | "Business case IF substantiated, marketing fluff if not." |
| 15 | "Integrates with SketchUp / 3ds Max / Revit" | O | **FIX — clarify import vs round-trip** | State exactly: import-only today, round-trip on roadmap. Don't imply round-trip | "I need round-trip, not just import." |
| 16 | "60 seconds per render" | B | **KEEP — qualify** | "~60s on your own model" not on a demo file; show on messy real SketchUp | "I'll believe it on my own messy model, not your demo file." |
| 17 | "Remembers your studio's voice across projects" | B | **KEEP — needs proof** | Hold claim until a 2-project before/after demo exists | "Interesting IF real. Today it's noise." |
| 18 | repo/automation facts (HappyMonk dump, posts-final.json, manifest.json schemas, marketing automation layer, Meta/Google Ads) | (internal) | **KILL from brand namespace** | These are project-build facts, not buyer/brand facts. Purge `project:claude-md` + `project:references-readme` from the brand graph | Not buyer-relevant; pollutes brand recall |
| 19 | "Generate future architectural concepts for 2030" / "visualization studios might be replaced by AI" | M | **RECLASSIFY → content-angle, not product fact** | Tag as carousel/contrarian content, not product capability | Speculative carousel hook, not a feature |
| 20 | "Free renders for architecture students" / "weekly rendering challenges" | M | **RECLASSIFY → top-of-funnel tactic** | Move to growth-tactics, not core product/pricing facts | Distribution tactic, not a buyer-pricing fact |

---

## B. Three-lens clean briefs (what survives, by buyer lens)

### Business case (the facts that decide a pilot)
- Locks to the client's actual floor plan; client recognises THEIR room. *(promote)*
- Edit after render — change one element without re-rendering. *(promote)*
- ~60s per render on the user's own model.
- Real worked cost example: ₹15k–60k outsourced cycle → ₹X with rkitect (TBD, must derive).
- One ₹2.5 Cr project closed in beta *(substantiate or mark unverified)*.
- One clear price: per-project ₹ OR per-seat/mo unlimited *(decision needed)*.

### Marketing perception (the facts that must be credible + desirable)
- India-first: Indian studios, ₹ pricing, Indian materials, Indian proof. *(commit)*
- One segmentation number with a method (recommend 92%).
- One traditional baseline, sourced from real studios.
- Headline candidate still works: "Five interior options before your next pitch."
- Kill: NYC framing, contradictory free offers, "up to 70%".

### Operations (the facts that decide if it fits the daily workflow)
- SketchUp/Revit: import today, round-trip on roadmap *(state honestly)*.
- Indian finish library explicit (Kota, Jaisalmer, terrazzo, teak, IPS, Kadappa).
- Editable post-render elements.
- Support availability in IST when it breaks mid-pitch *(currently MISSING — must add)*.
- Client floor-plan privacy / not used for training *(currently MISSING — dealbreaker)*.
- IP: user owns render, portfolio + deck use, no watermark/clawback *(currently MISSING)*.

---

## C. The "$0.20 per render" problem (the costing the user asked about)

**Where the value came from:** `$0.20` appears in `brand:sample-posts`, `brand:posts-final`, `brand:brief-synthesis` — all trace back to the original `sample-content/posts.md` marketing copy. It is a **marketing-stated unit price, not a derived unit economic.** No source document derives it from API costs (Gemini/FLUX/Ideogram inference + storage). It is unverified.

**Why it fails as a buyer number:** a single room at 5 styles × 6 revisions = ~30 renders. A villa = 8 rooms = ~240 renders/project. At "$0.20" that's ~$48/project — but the user is also quoted "$199/mo" and "free". The buyer cannot reconcile four numbers and defaults to distrust.

**Recommended presentation (pick one — decision needed):**
1. **Per project, ₹, unlimited revisions** — e.g. "₹X per project, render until the client signs off." Maps to how Indian studios bill. Strongest per buyer.
2. **Per seat / month, unlimited** — e.g. "₹Y / designer / month" for the 7-person studio. Predictable, fits SaaS.
3. Keep `$0.20` strictly as an INTERNAL unit-cost ceiling for margin math — never buyer-facing.

To make any of these defensible we must derive true unit cost: render-model inference $ + storage + overhead per render → margin at ₹X project price. That model does not exist yet.

---

## D. mem0 cleanup actions (proposed — needs approval before write)

KILL from `user_id=rkitect-marketing` (junk / internal / not buyer-brand):
- All `project:claude-md` facts (14) — repo build facts
- All `project:references-readme` facts (15) — knowledge-bank meta
- `brand:*` facts asserting "94% accuracy" (conflicts with 92%)
- Facts asserting NYC beta (conflicts with India positioning)
- "2030 concepts" / "visualization studios replaced" speculative facts

FIX (delete wrong + re-add corrected):
- Accuracy → single 92% w/ method
- Pricing → one model (post-decision)
- Baseline → one sourced number (post-interview)

RECLASSIFY (retag agent_id, keep content):
- Student-free / weekly-challenges → `growth:tactic`
- 2030 / contrarian → `content:angle`

Net: ~29 junk facts removed, ~5 fixed, ~3 reclassified. Brand namespace shrinks from 167 → ~130 high-signal buyer facts.

---

## E. Open decisions for the user

1. **Pricing model** — per-project ₹ / per-seat ₹ / keep $0.20 internal-only?
2. **Geography** — commit India-first and purge NYC, or keep a global story?
3. **Apply mem0 deletions now** — yes (auto-clean junk) / propose-each / hold?
4. **Substantiate the ₹2.5 Cr claim** — can you get the studio name + quote, or mark unverified?
5. Continue the buyer interview (persona agent still live) on the 3 MISSING items — IP, privacy, mid-pitch support?
