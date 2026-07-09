# Științele Naturii (M_șt-nat) — corpus analysis & generation spec

Derived from `files/exam_corpus/stiintele-naturii/` (226 papers, 2013–2026;
representative modern papers 2019–2026 read directly). This is the authority for
the `stiintele-naturii` profile. **One-line identity:** structurally between
tehnologic and mate-info — Subiect I & II ≈ tehnologic (easy, **2×2** matrices),
but **Subiect III is real analysis** (rational/ln derivative studies + genuine
definite integrals) like mate-info. Harder than tehnologic, easier than mate-info.

## Subiectul I — 6 items × 5p (difficulty ~1)

| Pos | Topic | Observed forms (all sympy-verifiable to clean answers) |
|----|-------|--------|
| 1 | **progressions** (dominant) / occasional numeric **arithmetic** | arithmetic-progression term from two given terms (`a2,a3 → a1`; `a1,a2 → a3`); sometimes a decimal/fraction numeric identity (`(4,9−3,4):3+2,5=3`) |
| 2 | **functions** (linear/affine) | `f(x)=ax+b`; find param from `f(a)+f(2a)=2`, `f(a)+f(2)=2a`, or point-on-graph `A(−3a,a)∈G_f` |
| 3 | **equations** in ℝ | exponential (`5ˣ·(1/5)=25`) and **logarithmic** (`log_b(x²−3x+2)=log_b(2+x)`, `log_b(1+2x−x²)=log_b(3−x)`) — log-of-quadratic = linear, domain-checked |
| 4 | **combinatorics / probability** | probability over 2-digit naturals (multiple of 16 / odd multiple of 11); counting even 2-digit distinct-digit numbers from a set. Digit-condition family, simpler than mate-info |
| 5 | **geometry** (analytic) | points A,B,C; midpoint, distance; show right / isosceles triangle, `AO=AC` |
| 6 | **trigonometry** | identity `E(x)=val` (sum of sin/cos of `x, x/2, 3x/2`); right-triangle `cos B=2/3 → BC`, `tg B=1/3` + area `→ AC` |

## Subiectul II — 2 problems × (a,b,c) × 5p

- **Problem 1 — matrices, always 2×2.** `I₂`, a concrete `A`, and an affine
  `A(x)=xM+N` / `B(x)`. Cerinte: `det`; affine identity (`B(x)−B(0)=xA`,
  `A(0)·(6I₂−A(2)−A(−2))=xI₂`); inverse / non-invertibility for integer param;
  **solve for X ∈ M₂(ℝ)** (`(A−I₂)·X=2A`, `A(1)·X·A(1)=4I₂`). Never 3×3.
- **Problem 2 — law of composition OR polynomials** (rotates, like mate-info/
  tehnologic prob-2):
  - law `x∘y=(2x−1)(2y−1)+1`, `x∘y=x+y−xy` on `M=[0,∞)`: fixed value, solve, integer-param.
  - polynomial `f=X³−aX+2+a`: `f(1)` invariant, divisibility by `X+2`, Viète
    (`Σxᵢ³ = Σxᵢxⱼ`).

## Subiectul III — 2 problems × (a,b,c) × 5p  ← the distinguishing section

- **Problem 1 — derivative study of a rational / ln function** (NOT poly-only like
  tehnologic): `f=5+4x−4/x²`, `f=(x²−2x+2)/(x+…)`, `f=3x²+4ln x`. Cerinte:
  (a) compute/verify `f'`; (b) **horizontal asymptote** toward +∞; (c) an
  **inequality** `f(x)−f(y)≤1 ∀x,y∈[1,∞)` or **tangent parallel to Ox**.
- **Problem 2 — genuine definite integrals** (Leibniz–Newton), often with `ln`:
  `∫(f−4ln x)dx=7`, `∫(x·f−3x²)dx`, primitive `F''` identities. Real integral
  computation — **not** tehnologic's primitive/area only, and **not** mate-info's
  sequence-`Iₙ` recurrence.

## Profile wiring (proposed)

- **PROFILE_TOPICS**: same set as tehnologic (arithmetic, powers, logarithms,
  functions, equations, complex[algebraic], polynomials, matrices, systems,
  algebraic_structures, sequences, limits, derivatives, integrals, geometry,
  trigonometry, combinatorics, progressions).
- **PROFILE_CAPS**: `{"matrix_size": (2,), "complex": "algebraic_only",
  "derivatives": "full"}` — 2×2 matrices; complex available in /generate but **not**
  in the simulare Subiect I rotation (modern papers open with progressions, not
  complex — 18/113 older subiecte mention complex).
- **SIMULATION_RULES**:
  - I: 1 `(progressions, progressions, arithmetic)` · 2 `functions` · 3 `equations`
    · 4 `combinatorics` · 5 `geometry` · 6 `trigonometry` — difficulty 1.
  - II: prob1 `matrices_2x2` · prob2 `(algebraic_structures, polynomials)`.
  - III: prob1 `derivatives` · prob2 `integrals` — with a st-nat derivative mode
    (rational/ln study) and a st-nat integral mode (genuine ∫, no sequence-Iₙ).
- **Reuse:** Subiect I & II reuse the tehnologic code paths (add `stiintele-naturii`
  to the relevant `SUPPORTED_PROFILES` / tehnologic-equivalent branches). Only
  **derivatives** and **integrals** need a new st-nat branch for the harder Subiect
  III (rational+ln derivative study; genuine definite ∫).
