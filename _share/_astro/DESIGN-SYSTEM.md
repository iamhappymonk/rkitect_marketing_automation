# rkitect.ai · v2 Design System

> Extracted from `_share/landing.{css,html,js}` via `/impeccable:impeccable extract`. The Astro pages (`/v2/*`) inherit this 1:1. Studio-print register, hand-drafted feel, restraint over flash.

## 1. Foundations

### 1.1 Typography

| Token | Family | Use |
|---|---|---|
| `--font-display` | **Spectral** (300, 400, 500; italic 300, 400) | h1, h2, italic-display flourishes |
| `--font-sans` | **Switzer** (400, 500, 600) | Body, h3, h4, buttons, nav |
| `--font-mono` | **Inconsolata** (400, 500, 600) | Eyebrows, labels, code, stamps |

Loaded via Google Fonts (Spectral + Inconsolata) + Fontshare (Switzer). Preconnect both at `<head>`.

**Banned font picks** (per impeccable): Inter, Roboto, Open Sans, Fraunces, Newsreader, Cormorant, IBM Plex, Space Grotesk, Outfit, Plus Jakarta, DM Sans/Serif, Instrument, Crimson, Lora, Playfair, Syne. None of these. Spectral + Inconsolata + Switzer = the locked stack.

### 1.2 Type scale

Fixed + fluid hybrid. **App pages use fixed `rem`. Marketing headings use fluid `clamp()`.**

```css
--text-2xs: 0.6875rem;
--text-xs:  0.75rem;
--text-sm:  0.8125rem;
--text-base:0.9375rem;
--text-md:  1rem;
--text-lg:  1.1875rem;
--text-xl:  1.5rem;
--text-2xl: 1.875rem;
--text-3xl: 2.375rem;
--text-4xl: 3rem;
--text-fluid-xl:  clamp(2rem, 1.4rem + 2.4vw, 3.5rem);
--text-fluid-2xl: clamp(2.75rem, 1.8rem + 4.6vw, 5.5rem);
--text-fluid-3xl: clamp(3.5rem, 2.2rem + 6vw, 7rem);
```

Ratio ≥1.25 between steps (impeccable rule). Hero h1 uses `--text-fluid-3xl`.

### 1.3 Heading rules

- `h1`, `h2`: font-display, weight 400, line-height **1.02** (tight), letter-spacing **-0.022em**
- `h3`, `h4`: font-sans, weight 500, line-height 1.25
- Display italic on accent words: `.italic-display { font-family: var(--font-display); font-style: italic; font-weight: 300; }`
- Body: line-height **1.55**, `font-feature-settings: "ss01", "cv11"` (Switzer stylistic sets — small caps numerals + alternate g)

### 1.4 Color (OKLCH, perceptually uniform)

Per impeccable: **always OKLCH, never HSL/hex for working tokens.** Hex only in HTML `meta[name="theme-color"]`.

```css
--color-bg:           oklch(0.985 0.003 70);   /* paper */
--color-bg-elevated:  oklch(0.995 0.003 70);
--color-bg-muted:     oklch(0.965 0.004 70);

--color-text-primary: oklch(0.22 0.01 70);     /* ink */
--color-text-secondary:oklch(0.42 0.01 70);
--color-text-muted:   oklch(0.55 0.01 70);

--color-border:       oklch(0.9 0.005 70);
--color-border-hover: oklch(0.82 0.006 70);

--color-accent:       oklch(0.55 0.18 25);     /* redline-red */
--color-accent-hover: oklch(0.49 0.18 25);
--color-accent-light: oklch(0.95 0.04 25);

--color-ink:          oklch(0.32 0.07 240);    /* blueprint blue */
--color-ink-hover:    oklch(0.27 0.07 240);
--color-ink-light:    oklch(0.94 0.03 240);
```

**Hue tinting:** all neutrals tinted toward warm cream (hue 70). Even at 0.003-0.005 chroma it's perceptible — gives subconscious cohesion with the redline-red brand hue (hue 25) without competing.

**60-30-10:** paper 60%, ink 30%, redline 10%. Redline is RARE. Reserved for hairlines, dot pulses, hover states, eyebrow underlines, single-word emphasis. Never for body text.

### 1.5 Spacing (4pt scale)

```css
--space-xs:  8px;
--space-sm:  12px;
--space-md:  16px;
--space-lg:  24px;
--space-xl:  32px;
--space-2xl: 48px;
--space-3xl: 64px;
--space-4xl: 96px;
--space-5xl: 128px;
```

Use `gap` not margins (impeccable). Sibling spacing via grid/flex `gap`.

### 1.6 Easing

```css
--ease-out-quint: cubic-bezier(0.22, 1, 0.36, 1);   /* hero reveals, line draws */
--ease-out-back:  cubic-bezier(0.16, 1, 0.3, 1);    /* card lifts */
--ease-out-soft:  cubic-bezier(0.2, 0.7, 0.2, 1);   /* default everywhere else */
```

No bounce. No elastic. Exponential ease-outs only.

### 1.7 Radii + shadows

```css
--card-radius: 8px;
--card-shadow:          0 1px 0 oklch(0 0 0 / 0.04);
--card-shadow-hover:    0 1px 2px oklch(0 0 0 / 0.06), 0 1px 0 oklch(0 0 0 / 0.04);
--card-shadow-elevated: 0 4px 16px oklch(0 0 0 / 0.08), 0 1px 0 oklch(0 0 0 / 0.04);
```

Restrained. No glassmorphism. No glowing accents. No drop shadows over 16px blur radius.

### 1.8 Measure

`--measure-prose: 60ch;` — wrap body text in `max-w-prose`. Hard cap 75ch (impeccable).

---

## 2. Components (atoms → patterns)

### 2.1 `.eyebrow` — section label with animated hairline

```css
.eyebrow {
  font-family: var(--font-mono);
  font-size: var(--text-2xs);
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: var(--color-text-muted);
  font-weight: 500;
  display: inline-flex; align-items: center; gap: 8px;
}
.eyebrow::before {
  content: ""; width: 28px; height: 1px;
  background: var(--color-accent);
  display: inline-block;
  transform-origin: left; transform: scaleX(0);
  animation: drawX 0.8s var(--ease-out-quint) forwards;
}
```

Hairline draws in on mount/scroll-into-view. Restraint: 1px high, redline accent only here.

### 2.2 `.italic-display` — Spectral italic flourish on single words

Use SPARINGLY — never more than one per heading. Currently in landing's H1 "Pin-up-ready by *Friday*".

### 2.3 `.mono` — Inconsolata with tabular numerals

`font-feature-settings: "tnum" 1;` for stamp/spec callouts.

### 2.4 `.btn-primary` — single-CTA button

Inherits from landing. Solid ink fill, paper text, redline dot indicator, hover darkens. Reserved for the ONE primary action per surface.

### 2.5 Card patterns

- **flow-card** (5-stage flow on home): paper-elevated bg, 2px top accent (uses `var(--accent)` CSS custom property per card for color variance), restrained shadow, hover lift
- **roster-card** (6-agent roster): same family, but chief variant inverts (ink bg, paper text, redline pulse dot)
- **NEVER:** side-stripe borders (per impeccable `BAN 1` — border-left/right > 1px is BANNED)
- **NEVER:** gradient text (per impeccable `BAN 2`)

### 2.6 Drafting-stamp motifs

The Atelier 01 badge SVG (`01-Projects/2026-Cohort-01/_assets/atelier-01-badge.svg`) defines the visual vernacular:

- Hairline frames (double-rule outer + inner)
- North-arrow tick (corner motif)
- Scale-bar (corner motif)
- Hairline dividers under labels
- Inconsolata for `ATELIER` label + `01` numeral

**Reuse these motifs** as section dividers, card corners, page footers. Architects know these symbols.

### 2.7 Section structure

```astro
<section class="section">
  <header class="section-head">
    <p class="eyebrow">For practices &amp; offices · pre-launch</p>
    <h2>One brief in. <span class="italic-display">The studio runs the project.</span></h2>
  </header>
  <div class="section-body"><!-- content --></div>
</section>
```

`section-pad`: `padding: var(--space-4xl) var(--space-lg);` — generous vertical rhythm.

---

## 3. Layout

### 3.1 Page width

`max-w-page` = 1200px. Centered. `padding-inline: var(--space-lg)` on mobile, `var(--space-xl)` desktop.

### 3.2 Grid patterns

- **Flow-cards (5-stage):** `repeat(5, minmax(0, 1fr))` desktop · 3-cols (3+2 centered) tablet · 1-col mobile
- **Roster-cards (6-agent):** `repeat(3, minmax(0, 1fr))` desktop · 2-cols tablet · 1-col mobile
- **Card grids generic:** `repeat(auto-fit, minmax(280px, 1fr))` for content where exact count doesn't matter

### 3.3 Breakpoints

```css
@media (max-width: 1100px) { /* tablet */ }
@media (max-width: 880px)  { /* large mobile / small tablet */ }
@media (max-width: 720px)  { /* mobile */ }
@media (max-width: 600px)  { /* small mobile */ }
```

Container queries (`@container`) for component-level responsiveness (impeccable rule).

---

## 4. Motion (via `motion` lib)

### 4.1 Principles

- Use Motion's `animate()` + `inView()` for scroll-triggered reveals
- Hero h1: staggered word reveal on mount (60-80ms stagger, 0.6s duration each, `ease-out-quint`)
- Roster + flow cards: fade-up + slight scale (0.97→1) on scroll-into-view, 80ms stagger between cards
- Section eyebrows: hairline draw animation (already CSS-driven via `.eyebrow::before`)
- ALL animations respect `prefers-reduced-motion: reduce` — gate with `if (!matchMedia('(prefers-reduced-motion: reduce)').matches)`

### 4.2 What NOT to animate

- No bounce/elastic easing
- No `width`/`height`/`padding`/`margin` animations (transform + opacity only)
- No parallax on text — backgrounds only (rare)
- No "page-load curtain" — preloader already exists in landing; Astro can use simpler `inView` for sections

### 4.3 Bundle discipline

Motion is tree-shakeable. Import only `animate`, `inView`, `stagger`. Target: total motion bundle <30KB gzipped.

---

## 5. Voice in copy (cross-ref vault `00-Brand/Voice.md`)

- Architect dictionary mandatory: studio, practice, office, brief, scheme, schematic, design development, plan, section, axo, finish, palette, pin-up, principal, charrette, redline, sign-off, revision round, set, deliverable
- Banned in customer copy: platform, workflow OS, pipeline, AI agent, prompt, user, customer, feature, dashboard, copilot, AI render tool, image generator
- Canonical roster: Principal Architect (chief) + Plan Drafter + Space Planner + Renderer + Materials Specialist + Lighting Designer
- Sektura: STRUCK — use Auto-Segment or generic Segmentation
- No public pricing
- No Atelier / cohort mentions on public site

---

## 6. Page registers (per surface)

| Page | Register | One-line voice |
|---|---|---|
| Home | Studio's own front door | "A studio on your desk." |
| Product | A studio principal walking a visiting architect through the office | "Six on your desk. One brief at a time." |
| About | First-person founder + parent context + manifesto | "Built by people who know what 11pm at the studio feels like." |
| Contact | Direct line to the founder | "Get in touch. Founder call within 48h." |

---

## 7. The AI Slop Test (impeccable mandate)

If someone said "AI made this," would they believe you immediately? **No.** Distinctive markers:

- Spectral italic flourish on accent words (Cormorant would be the AI default — we use Spectral)
- Inconsolata for stamps + eyebrows (Space Mono is the AI default — we use Inconsolata)
- OKLCH-tinted warm cream paper (the cyan-on-dark default is rejected)
- Drafting-stamp motifs (north arrow, scale bar, hairline frames)
- 5-stage flow card (custom grid, never side-stripe borders)
- No glassmorphism, no glowing accents, no gradient text, no purple-blue gradients, no rounded-rectangle-with-shadow card laundry

This is studio-print register, not SaaS-marketing register.
