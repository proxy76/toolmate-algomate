---
name: Algomate
description: Romanian Baccalaureate math practice — verified, exam-faithful, calm under pressure.
colors:
  ink: "#2b2622"
  ink-strong: "#1c1815"
  ink-muted: "#61584f"
  ink-faint: "#9a8f86"
  paper: "#fdfbfb"
  sunken: "#f7f1f0"
  edge: "#e8dcd9"
  oxblood: "#8f3128"
  oxblood-deep: "#79271f"
  oxblood-tint: "#f4e0dc"
  math-ink: "#261f1b"
  ochre: "#bd8431"
  ochre-tint: "#f8efdd"
  ochre-ink: "#79561f"
  verified: "#2f8d5d"
  verified-tint: "#e4f3ea"
  verified-edge: "#b9e0c8"
  verified-ink: "#1d5e3c"
  danger: "#c0322c"
  danger-tint: "#fbeae8"
  danger-edge: "#f3c9c5"
  danger-ink: "#8f211c"
typography:
  display:
    fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif"
    fontSize: "2.25rem"
    fontWeight: 800
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "normal"
  body:
    fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "normal"
  label:
    fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "0.05em"
rounded:
  lg: "8px"
  xl: "12px"
  "2xl": "16px"
  full: "9999px"
spacing:
  xs: "8px"
  sm: "12px"
  md: "16px"
  lg: "24px"
  xl: "40px"
components:
  button-primary:
    backgroundColor: "{colors.oxblood}"
    textColor: "{colors.paper}"
    rounded: "{rounded.xl}"
    padding: "12px 20px"
  button-primary-hover:
    backgroundColor: "{colors.oxblood-deep}"
    textColor: "{colors.paper}"
  button-secondary:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: "8px 16px"
  chip-selected:
    backgroundColor: "{colors.oxblood}"
    textColor: "{colors.paper}"
    rounded: "{rounded.full}"
    padding: "6px 12px"
  chip-unselected:
    backgroundColor: "{colors.sunken}"
    textColor: "{colors.ink-muted}"
    rounded: "{rounded.full}"
    padding: "6px 12px"
  card:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.2xl}"
    padding: "24px"
  input:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: "8px 12px"
  badge:
    backgroundColor: "{colors.oxblood-tint}"
    textColor: "{colors.oxblood-deep}"
    rounded: "{rounded.full}"
    padding: "4px 12px"
---

# Design System: Algomate

## 1. Overview

**Creative North Star: "The Problem Book"**

Algomate feels like a well-set Romanian math problem book made interactive —
generous margins, a confident typographic hierarchy, and warm ink-on-paper
calm. Authority comes from restraint and correctness, not decoration. Every
screen is, at heart, a page a tired 18-year-old reads at night: the math is
the figure, everything else is ground. Because each answer is symbolically
verified, the interface earns trust by *looking* composed and deliberate,
never busy or hawkish.

This is a **product** system: design serves the task of generating and working
problems. Earned familiarity beats novelty. The same control means the same
thing on every screen; the math renders flawlessly at any zoom; nothing
competes with the equation for attention. Warmth lives in the **oxblood**
action color, the warm-paper neutrals, and generous spacing — not in loud
gradients.

**Migration note.** The system was originally a *cool indigo SaaS* look
(indigo→blue gradient masthead, indigo-600 buttons, slate surfaces). The warm
Problem-Book palette below is the canonical system and has landed on the
**shared frame (`Layout`)** and the **`/practice`** surface. The remaining
pages (Home, Login, Register, Dashboard, Blog, Contact, Simulate) still carry
the legacy indigo utilities and are pending migration to these tokens — treat
any indigo on those pages as debt, not direction.

**Key Characteristics:**
- Math is the protagonist; chrome recedes to hairlines.
- Warm paper surfaces; depth only as a response to state.
- One typeface (Inter), worked hard across weights — no display/body pairing.
- Semantic color is rationed: oxblood = action, ochre = difficulty/hints,
  green = verified answers, red = errors. Color carries meaning, never mood.
- Calm density: generous whitespace, never a wall of controls.

## 2. Colors

A committed **oxblood** action color over warm near-white paper, with ochre and
green reserved as semantic signals for difficulty/hints and verified answers.
Neutrals are tinted toward oxblood's own hue (~28°), never toward generic
warm-cream.

### Primary
- **Oxblood** (#8f3128): The single action color — primary buttons, selected
  profile/topic chips, active nav, links, the focus ring. On ≤10% of any
  screen. Carries white (`paper`) text at ≥6:1.
- **Oxblood Deep** (#79271f): Hover/pressed state of every primary action.
- **Oxblood Tint** (#f4e0dc, plus `oxblood/10` washes): The "Exercițiul N"
  badge, the masthead logo tile, active-nav background — oxblood at a whisper.

### Secondary
- **Ochre** (#bd8431): The think-don't-warn accent. Marks the active difficulty
  and anchors hints. Harmonized with oxblood (both warm), never competing
  with it for "action".
- **Ochre Tint / Ink** (#f8efdd · washes / #79561f): Hint callout and its text.

### Tertiary
- **Verified Green** (#2f8d5d / tint #e4f3ea / edge #b9e0c8 / ink #1d5e3c):
  Reserved exclusively for revealed, sympy-verified answers. Green here means
  "this is provably correct" — the emotional core of the product. Never
  decorative.
- **Error Red** (#c0322c / tint #fbeae8 / edge #f3c9c5 / ink #8f211c): Form and
  request errors only. Kept **more vivid** than the muted oxblood and always
  paired with an alert role, so the two reds never read as the same signal.

### Neutral (warm)
- **Ink** (#2b2622): Default body text. ≥4.5:1 on paper and sunken.
- **Ink Strong** (#1c1815): Page/section headings, wordmark.
- **Ink Muted** (#61584f): Secondary prose, labels, helper text. Still ≥4.5:1.
- **Ink Faint** (#9a8f86): Disabled and placeholder only — never body copy.
- **Paper** (#fdfbfb): Cards, forms, masthead, inputs — the sheet.
- **Sunken** (#f7f1f0): App background and unselected chips.
- **Edge** (#e8dcd9): Hairline 1px borders and dividers.

### Named Rules
**The One Voice Rule.** Oxblood is the only action color and appears on ≤10%
of any screen. Its rarity is what makes a primary button read as *the* next
step. Ochre and green are signals, not second and third action colors.

**The Verified-Green Rule.** Green is reserved for verified answers. It never
appears as decoration, a hover, or a generic "success" flourish elsewhere.
When a student sees green, the engine has proven the result.

**The Warm-Paper Rule.** Neutrals tint toward oxblood's hue (~28°), never
toward yellow-cream. If a surface reads as beige/parchment, the chroma is on
the wrong hue.

## 3. Typography

**Display Font:** Inter (with ui-sans-serif, system-ui, sans-serif fallback)
**Body Font:** Inter — same family, worked across weights
**Label/Mono Font:** none distinct; inline `code` uses the monospace fallback

**Character:** One humanist-geometric sans doing all the work, from 800-weight
page titles down to 400-weight prose. No second face — a problem book speaks in
one confident voice. Inter is chosen partly because it renders Romanian
diacritics (ă, â, î, ș, ț) cleanly at every weight, which is non-negotiable.

### Hierarchy
- **Display** (800, 1.875–2.25rem `text-3xl`/`text-4xl`, lh 1.1, -0.02em,
  `text-balance`): Page titles ("Generator de exerciții"). Fixed rem, not fluid.
- **Headline** (700, 1.25rem `text-xl`, lh 1.3): Section headers ("N exerciții
  generate").
- **Title** (600, 1.125rem `text-lg`, lh 1.4): The exercise question — the
  densest, most-read string, set in Math Ink.
- **Body** (400–500, 1rem, lh 1.6, `text-pretty`): Prose and helper text;
  cap at 65–75ch (the Practice intro is capped at `max-w-2xl`).
- **Label** (700, 0.75rem `text-xs`, +0.05em, often UPPERCASE): The
  "Exercițiul N" badge and field labels.

### Named Rules
**The Single-Voice Rule.** One family only (Inter). Hierarchy comes from
weight and size, never from introducing a second typeface into UI.

**The Diacritics Rule.** Any font change must render ă/â/î/ș/ț correctly at
400–800 weight before it ships. Romanian copy is the product.

## 4. Elevation

Flat by default. Surfaces sit at rest on the page like sheets of paper —
depth is conveyed through the 1px `edge` (#e8dcd9) border and tonal layering
(sunken #f7f1f0 background vs. paper #fdfbfb surface), not through ambient
shadow. Shadow is a **response to state**, not a resting decoration. The
masthead uses a translucent paper background with `backdrop-blur` and a single
hairline bottom border instead of a drop shadow.

### Shadow Vocabulary
- **Resting card** (`shadow-sm` — `0 1px 2px rgba(28,24,21,0.05)`): Barely-there
  edge definition on paper cards; reads as a sheet, not a float.
- **Hover lift** (`shadow-md`): Exercise cards gain depth only on hover,
  signalling interactivity.

### Named Rules
**The Flat-By-Default Rule.** Surfaces are flat at rest. If a card has a heavy
shadow before you touch it, the shadow is wrong. Depth answers interaction —
hover, focus, stickiness — and nothing else.

## 5. Components

### Buttons
- **Shape:** Primary actions use 12px (`rounded-xl`); secondary and segmented
  controls use 8px (`rounded-lg`).
- **Primary:** Oxblood (#8f3128) on paper text, `12px 20px`, bold, with a
  leading icon (Sparkles on "Generează"). Hover → Oxblood Deep (#79271f).
  Disabled drops to 50% opacity + `not-allowed`; loading swaps the icon for a
  spinner and the label to "Se generează…".
- **Secondary:** "Salvează sesiunea" is a quiet bordered paper button
  (`border-edge`, `hover:bg-sunken`) — an archival action, not a primary one.
- **Focus:** Every control shows the shared 2px oxblood `:focus-visible` ring
  (outline-offset 2px); mouse users don't see it.

### Chips
- **Style:** Topic chips are pills (`rounded-full`); profile/difficulty are
  square-cornered (`rounded-lg`) segmented buttons. All 1px `edge`-bordered.
- **State:** *Selected* = Oxblood fill, paper text, matching border (difficulty
  selects in **Ochre** instead). *Unselected* = Sunken fill, Ink Muted text,
  hover warms the border toward oxblood/ochre and lifts to paper.

### Cards / Containers
- **Corner Style:** 16px (`rounded-2xl`) — softest radius, for content
  containers (exercise cards, the generator form).
- **Background:** Paper on the sunken app background.
- **Shadow Strategy:** `shadow-sm` at rest → `shadow-md` on hover. Flat-by-default.
- **Border:** 1px Edge (#e8dcd9) always — the primary depth cue.
- **Internal Padding:** 24px (`p-6`), 32px (`p-8`) on the generator form at `md`.

### Inputs / Fields
- **Style:** Paper, 1px Edge border, `rounded-lg`, `8px 12px`. Labels are
  0.875rem semibold Ink, 8px above the control.
- **Focus:** Border shifts to Oxblood plus the shared focus-visible ring; **no
  glow**. The range slider uses `accent-oxblood`. Placeholders use Ink Faint.
- **Error:** Surfaces in a Danger-tint callout (`role="alert"`) below the form.

### Navigation
- **Style:** Sticky translucent **paper** masthead with `backdrop-blur` and a
  hairline bottom border — the calm Problem-Book bar that replaced the indigo
  gradient. Wordmark is Ink Strong with an oxblood-tint logo tile.
- **States:** Active link = Oxblood text, semibold, on an `oxblood/10` wash.
  Inactive = Ink Muted, hover warms to Ink on Sunken.
- **Mobile:** Collapses to a bordered hamburger (`md:`) revealing a stacked
  paper panel under a hairline divider.

### Exercise Card (signature component)
The product's defining surface. A flex column: a badge row ("Exercițiul N" in
oxblood-tint + topic + ochre difficulty pills) → the question in Title type,
**Math Ink (#261f1b)**, the heaviest mark on the card → two
progressive-disclosure reveals pinned to the bottom. The **Hint** reveal is
Ochre (Lightbulb, ochre wash callout); the **Answer** reveal is Verified Green
(CheckCircle, green callout, larger type). Both animate in with `fadeIn`
(translateY -4px → 0, 0.25s ease-out-quart) and collapse to a positionless
crossfade under `prefers-reduced-motion`. The ochre→green progression *is* the
learning loop made visible: think, then confirm.

## 6. Do's and Don'ts

### Do:
- **Do** treat the equation as the figure on the page. Math (Math Ink #261f1b)
  is the most prominent, most legible element of any card — readable and
  zoomable on a phone (`.katex-display` scrolls horizontally, never overflows).
- **Do** ration oxblood to ≤10% of a screen (The One Voice Rule). One obvious
  primary action per view.
- **Do** keep green exclusively for verified answers (The Verified-Green Rule).
- **Do** keep surfaces flat at rest; let shadow answer hover/focus only.
- **Do** verify body text hits ≥4.5:1 — use Ink (#2b2622) / Ink Muted
  (#61584f), never Ink Faint (#9a8f86), which is placeholder-only.
- **Do** keep neutrals tinted toward oxblood's hue, not toward warm-cream
  (The Warm-Paper Rule).
- **Do** confirm Romanian diacritics (ă/â/î/ș/ț) render at every weight.
- **Do** give every control the shared oxblood `:focus-visible` ring and a
  `prefers-reduced-motion` fallback for any reveal.

### Don't:
- **Don't** reintroduce the generic-SaaS template look: no `indigo-800 →
  blue-700` gradient masthead, no hero-metric blocks, no identical
  icon-heading-text feature-card grids, no tiny uppercase tracked eyebrow above
  every section. (PRODUCT.md anti-reference: *generic SaaS template*.) The
  legacy indigo on un-migrated pages is debt to remove, not a pattern to copy.
- **Don't** drift toward cluttered ed-tech: no badge-everywhere, multi-color,
  ad-heavy Romanian-portal density. Trust comes from calm. (PRODUCT.md
  anti-reference: *cluttered ed-tech*.)
- **Don't** gamify. No mascots, confetti, cartoon palette, or badge-grinding —
  the BAC is high-stakes. (PRODUCT.md anti-reference: *childish gamified app*.)
- **Don't** use `border-left`/`border-right` greater than 1px as a colored
  accent stripe on cards or callouts. Use full borders and background tints.
- **Don't** use gradient text (`background-clip: text`) for emphasis. Weight
  and size only.
- **Don't** introduce a second UI typeface. Inter carries everything.
- **Don't** let error-red and oxblood read as the same signal — keep red more
  vivid and always icon/role-paired.
- **Don't** let a card float with a heavy resting shadow — if it looks lifted
  before you hover it, the shadow is too strong.
