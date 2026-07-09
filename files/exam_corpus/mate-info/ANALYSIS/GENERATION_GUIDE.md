# M1 Generation Guide — from corpus observation to correct generator

This guide tells you how to convert what you observe in `ANALYSIS/` and `M1/extracted/` into a
generator that produces exercises indistinguishable from the 24 real M1 papers. **It assumes you have
already completed the mandatory reading procedure in `README.md`.**

The corpus is the authority. Where this guide and the corpus disagree, the corpus wins.

---

## 1. The distribution rule restated

A generated M1 item is correct only if a knowledgeable person, shown it next to real items from the
same position, could **not** reliably pick it out. Concretely, the generated item must match the real
papers on all of: topic, phrasing (the wrapper sentence and the ask), number ranges, structural shape,
difficulty, and answer cleanliness.

When in doubt, **make it simpler and more standard**, not fancier. The real exam is conservative and
repetitive by design; that repetition is the target, not a limitation.

---

## 2. Subiectul I — position by position

Each position has a **fixed topic** but genuine phrasing variety. Read the full POSITION section in
`ANALYSIS/subiect_I_by_position.md` and mirror the observed variety — including rotating among the
phrasings, not locking onto one.

### Position 1 — algebra opener
Observed topics across the 24 papers: **complex numbers (algebraic form)**, **progressions**
(arithmetic & geometric term-finding), **logarithms** (`lg`, base-10 identities), **radicals/powers**
simplification, and in the test sets **set cardinality / products of set elements**. Complex numbers
and progressions dominate the official variants; the test sets add the set-based problems.
- Phrasing families: `Arătați că <expr> = <val>` · `Determinați termenul <idx> al progresiei …, cu
  <cond>` · `Se consideră numerele complexe … Arătați că <identity>` · `Calculați modulul/partea
  întreagă …`.
- Numbers: small integers; complex parts in roughly [−4, 4]; progression terms yielding integer
  results; log identities resolving to small integers.

### Position 2 — functions
Observed: **parabola vertex conditions** (vertex on Ox, ordinate sign, Ox tangent to graph),
**composition** `(f∘f)(x0)=val`, **point on graph**, **graph intersections** (with a line or another
graph), **functional identities** `f(2x)−2f(x)=…`.
- Phrasing: `Se consideră funcția f:ℝ→ℝ, f(x)=…, unde m este număr real. Determinați … m pentru care …`.
- Numbers: linear/quadratic coefficients small integers; solutions integer or simple.

### Position 3 — equation in ℝ (invariant wrapper)
Wrapper is fixed: `Rezolvați în mulțimea numerelor reale ecuația <EQ>.` Observed equation types:
**exponential** (incl. quadratic-in-`a^x`), **logarithmic**, **irrational** (`√…` equations).
- Numbers/bases chosen so roots are clean and the domain is valid. Reject rolls with no real root or
  extraneous-only roots.

### Position 4 — combinatorics & probability
Observed: **probability over 2- or 3-digit naturals** with a divisibility / digit / parity condition;
**counting subsets** (with a constraint like "at most 2 elements", "contains element e", digits
distinct/prime). 
- Phrasing: `Calculați probabilitatea ca, alegând un număr din mulțimea numerelor naturale de <k>
  cifre, acesta să <cond>.` · `Determinați numărul submulțimilor … / câte numere … se pot forma …`.
- Answers: probability reduces to a small-denominator fraction; counts are small integers.

### Position 5 — analytic geometry
Observed: **lines through a point** (parallel/perpendicular, or parallels through two points and their
intersection), **vectors** (`AB = k·OA`, find B), **midpoint / collinearity**, **parallelogram**
conditions with vector relations.
- Phrasing: `În reperul cartezian xOy se consideră punctele … . Determinați … / Arătați că …`.
- Coordinates: small integers in about [−6, 6]; answers integer-valued; construct "prove" tasks so the
  property actually holds, then reject degenerate rolls.

### Position 6 — trigonometry / triangle
Observed: **right/acute/isosceles triangles** with given sides/area/angle → find a side, area, or a
trig ratio; **trig identities** to prove; **compute a trig value** given quadrant + one ratio.
- Phrasing: `Se consideră triunghiul ABC, dreptunghic în …, cu … . Arătați că …` · `Arătați că
  <trig identity>, pentru orice …` · `Calculați <ratio>, știind că x∈… și …`.
- Targets: integers, simple fractions, or `k√m` with small k, m. For Pythagoras, draw from known
  triples (3,4,5), (6,8,10), (5,12,13), (8,15,17), (7,24,25).

---

## 3. Subiectul II — mirror `ANALYSIS/subiect_II_problems.md`

Two problems, each with sub-items (a, b, c) worth 5p, difficulty rising a → b → c.

- **Problem 1 — matrices / systems.** Observed shapes: a parametrized matrix `A(x)` (2×2 or 3×3);
  (a) a determinant at a fixed value; (b) a structural property (`A(x)·A(y)=A(x+y)`, inversability,
  a commuting condition); (c) a harder condition (natural-number solutions, an inequality on the
  determinant, an inverse with integer entries).
- **Problem 2 — algebraic structures or polynomials.** For a law of composition `x∗y=…`: (a) a direct
  computation; (b) associativity/neutral element/a rewriting identity; (c) symmetric element or an
  inequality/parametric condition. For polynomials: (a) evaluation independent of the parameter;
  (b) divisibility / quotient-remainder (Horner, Bézout); (c) Viète relations with a parametric target.

Keep coefficients small; keep every sub-item hand-computable. The a→b→c dependency chain in the real
papers is strong — reproduce it.

---

## 4. Subiectul III — mirror `ANALYSIS/subiect_III_problems.md`

Two problems, each (a, b, c), 5p, difficulty rising, with (b)/(c) often depending on (a).

- **Problem 1 — function study (derivatives).** (a) show `f'(x)=…` (verify with `sympy.diff`);
  (b) monotonicity / an asymptote / a tangent / an extremum; (c) an inequality or a
  "exactly k real solutions" argument built from monotonicity.
- **Problem 2 — integrals.** (a) a direct definite integral (verify with `sympy.integrate`);
  (b) a definite integral needing substitution or parts, often resulting in a `ln` value;
  (c) an area, an integral inequality, or a limit of a sequence of integrals.

Functions in the real papers are combinations of polynomial, `e^x`, `ln x`, and simple rationals with
small coefficients — nothing exotic. Match that.

---

## 5. Answer-cleanliness gate (applies everywhere)

No calculator is allowed in the real exam, so every answer must be hand-reachable. Before accepting any
generated item, verify with `sympy` that the answer is one of: a small integer, a simple fraction, a
short radical (`k√m`, small k, m), or a short `ln`/`e` expression. If it is anything else, reject the
roll and regenerate. This single gate removes most unrealistic output.

---

## 6. Final acceptance checklist (run per generated item)

- [ ] Topic matches the fixed topic for that position/problem.
- [ ] Phrasing matches one of the real phrasing families observed in the corpus (wrapper + ask).
- [ ] Every number is within the observed range for that position; nothing larger or uglier than real.
- [ ] Difficulty sits inside the real spread — not above the observed ceiling, not trivially below the floor.
- [ ] Answer passes the cleanliness gate (sympy-verified).
- [ ] For Subiectul II/III: a→b→c difficulty rises and dependencies mirror the corpus.
- [ ] Side-by-side self-check against 5 real items produced **no tells**.

If every box is checked, the item is faithful. If not, regenerate — do not ship a near-miss.
