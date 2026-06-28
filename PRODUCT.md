# Product

## Register

product

## Users

Romanian high-school students (16–19) preparing for the **Bacalaureat** math
exam, across all three profiles: M_mate-info (M1), M_șt-nat (M2), and
M_pedagogic/tehnologic (M3). They arrive stressed and time-pressured, often
studying late, frequently on a phone. Their job-to-be-done is concrete: get
*large volumes of varied, correctly-solved practice* at the exact topic and
difficulty mix of the real exam — either targeted drilling on one weak topic,
or full 3-part simulated subiecte (SUBIECTUL I / II / III).

Secondary users: a self-driven student browsing the public landing, blog, and
try-it-now demo before deciding to make an account. Teachers/tutors are an
explicit non-goal for the baseline.

The interface is **entirely in Romanian** and must render KaTeX math correctly
on every page, mobile and desktop.

## Product Purpose

Algomate procedurally generates BAC-calibrated math exercises from a
deterministic `sympy`-backed engine — every question ships with a verified
answer, hint, and (optionally) worked steps, never a guessed result. It mirrors
the official MEN curriculum so generated sets stay inside what the student is
actually examined on, and it persists accounts so students can save sessions,
track mastered topics, and resume.

Success looks like: a student opens `/practice`, picks profile + topics +
difficulty, and within seconds is working through trustworthy problems they
can check themselves — or runs a full `/simulate` paper that feels like the
real exam. The product wins when it becomes the default place to grind reps,
because the material is *endless, varied, and correct*.

## Brand Personality

**Warm, academic, trustworthy.** Algomate is the great teacher made available
at 1 a.m. — textbook authority, but never cold or intimidating. Voice is
calm, precise, and encouraging; it lowers exam anxiety rather than amplifying
it. Correctness is the emotional core: because every answer is symbolically
verified, the interface should *feel* credible and structured, like a
well-set problem book, while staying approachable for a tired teenager.

Tone in Romanian copy: clear, supportive, exam-literate (uses the real
vocabulary — *subiect*, *profil*, *barem*) without being stuffy.

## Anti-references

- **Generic SaaS template.** No indigo/violet gradient heroes, no
  hero-metric blocks, no identical icon-heading-text feature-card grids, no
  tracked-uppercase eyebrows above every section. The current default-Tailwind
  `slate-50` look is the thing to grow out of, not preserve.
- **Cluttered ed-tech / Romanian school portals.** No noisy, ad-heavy,
  badge-everywhere, multi-color dated portal feel. Trust comes from calm and
  restraint, not density of decoration.
- **Childish gamified app.** No Duolingo mascots, confetti, cartoon palette, or
  badge-grinding. The BAC is high-stakes; the tool stays exam-grade serious.
  Encouragement is in tone and clarity, not in mascots.

## Design Principles

1. **Correctness made visible.** The defining feature is verified math; the
   design should make trust legible — clear answer/hint/steps hierarchy,
   flawless KaTeX, nothing that undercuts the "this is right" feeling.
2. **The tool disappears into the task.** Generating and working problems is the
   job. Earned familiarity over novelty; standard affordances, consistent
   component vocabulary, low cognitive overhead so the student spends attention
   on math, not on the UI.
3. **Calm under pressure.** Stressed users, often at night, often on mobile.
   Reduce anxiety: generous whitespace, quiet color, legible math at any zoom,
   no urgency theatrics.
4. **Exam-faithful structure.** Mirror the real BAC mental model — profiles,
   topics, difficulty, the 3-subiect paper. The interface teaches the exam's
   own shape, so practice transfers.
5. **Mobile-real, math-first.** Romanian students study on phones; equations
   must stay readable, scrollable, and zoomable. Math rendering is a
   first-class layout constraint, not an afterthought.

## Accessibility & Inclusion

Target **WCAG 2.1 AA**. Body text ≥4.5:1, large text ≥3:1, visible keyboard
focus on every interactive element, full keyboard navigation of the
generate/practice flow, and `prefers-reduced-motion` honored on all motion.
Because math is on every page, KaTeX must render with `throwOnError: false`
and `trust: false`, and equations must remain legible and zoomable on small
screens. Romanian diacritics (ă, â, î, ș, ț) must render correctly in every
font and weight chosen.
