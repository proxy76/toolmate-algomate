# M2 (M_tehnologic) — observed exam distribution

Source: 135 official M_tehnologic papers, 2020–2026 (`files/exam_corpus/M2/`, raw PDFs).
Read directly with the Read tool (PDFs render cleanly). **M2 tehnologic is structurally
like M1 (Subiect I = 6×5p; II & III = 2 problems × a/b/c × 5p, 90+10, 3h, no calculator)
but markedly EASIER and with a different topic mix.** This file records what the real
papers show, so the generator can stay inside that distribution.

## Subiectul I — 6 items, fixed roles

1. **Numeric computation** — `Arătați că <expr> = <small int>`. Two flavours:
   - **fraction arithmetic**: `12/5·(1/2+1/3)=2`, `3·(1+1/2)−1/2=4`, `1/10+3·(1/2−1/5)=1`,
     `2·(2−3/4:1/2)=1`, `5−3·(1+1/3)=1`.
   - **radical simplification**: `3(2−√20)+√180=6`, `(10−2·3)(10+2·3)=64`.
   - occasionally an **arithmetic-progression term** (`a₁=10, a₂=18 → a₃`) or a
     **Viète-on-quadratic** identity (`x²−7x+10=0 → 2(x₁+x₂)−x₁x₂=4`).
   **No complex numbers** (the biggest difference from M1).
2. **Linear function** `f(x)=ax+b`: find `a` for `f(a)=v`, `f(2)=a+f(0)`, `(f∘f)(1)`,
   `f(1)+g(1)`. Affine only — **no parabola** (unlike M1).
3. **Equation in ℝ** (single step): exponential `5^{2x}=5^{3−x}`, log `log_7(2x+1)=log_7 9`
   / `lg(5x−1)=lg2+lg7`, irrational `√(4x+1)=3`.
4. **Probability over a small EXPLICIT set** OR **practical percentage**:
   - `A={10,20,…,90}, divizibil cu 20`; `A={1,…,23}, n≥10`; `A={0,…,9}, 6n>25` → P = fav/|A|.
   - `Un produs costă 90 lei; preț după scumpire cu 10%` / `…costă 5200 după +30%, preț inițial`.
   **Not** 2-/3-digit number counting, **not** urns, **not** Aₙᵏ/Cₙᵏ evaluation.
5. **Analytic geometry**: midpoint, distance/perimeter, `AB=2BC`, `BC=a·AB` find a,
   distance point→line. Small integer coordinates.
6. **Trigonometry/triangle**: remarkable-value identity (`1+sin30°=2sin60°cos30°`,
   `2cos30°/(2tg45°+1)=tg30°`), right triangle (side / area / `sin B`). Simple.

## Subiectul al II-lea

- **Problem 1 — 2×2 matrices** (never 3×3, never a linear system):
  - **concrete**: A, B, C integer 2×2 given → (a) `det A`, (b) a linear-combination identity
    (`A+2B=3C`, `2B−A=3C`, `2B+I₂=3A`), (c) solve a matrix equation for X
    (`2X·A=B+2C`, `A·X−B·X=I₂−X`) or a det condition.
  - **parametrized**: `A(x)=xM+N` (affine) → (a) `det(A(x₀))`, (b) an affine identity
    (`A(2)+A(0)=2A(1)`, `2A(1)+A(4)=3A(2)`), (c) find x (from `A(x)=…` / `A(−x)·A(x)=A(y)`
    / a det condition).
- **Problem 2 — law of composition** (dominant) OR **polynomials**:
  laws `x∗y=(x−c)(y−c)+c`, `x∘y=2(x+y)−xy−4`, `x∘y=(x²+y²)/(xy)`, …: value, commutative,
  neutral, symmetric, natural-`n` condition, inequality. Polynomials: `f(1)=0`, Viète,
  divisibility/remainder.

## Subiectul al III-lea

- **Problem 1 — function study (derivatives)**: functions are mostly **polynomials**
  (`3x⁴−4x³−12x²−1`, `2x⁵+5x⁴−10x³+1`, `x³+6x²−15x+9`, `x(x²−12)+3`) plus some rational
  (`(2x−1)/x²`) / exp (`(x−2)/eˣ`) / ln (`4/x+ln x−5`). Cerinte: (a) `f'(x)` in a factored
  form, (b) **equation of the tangent at a given abscissa** (very common) OR monotonicity OR
  a limit, (c) an inequality / bounds on an interval. No bijectivity / no integral-sequences.
- **Problem 2 — integrals**: definite integrals (often with a helper factor that cancels the
  denominator), `∫f=ln k`, area, a volume of revolution, or an integral equation to find `a`.
  Functions: `(2x+1)/(x²+x+1)`, `8x/(x+9)`, `x²+4x+8`, `eˣ+3x²+3`, `x+1+xeˣ`.

## Generator implications (Session 8)
Add: `arithmetic` topic (pos-1 fraction/radical) · `Matrix2x2Problem` (Subiect II P1) ·
explicit-set probability (pos-4) · tangent-at-point + polynomial mode in `DerivativesStudyProblem`
for M2. Remove `matrices_system` from M2 (it's an M1-only 3×3 form). Keep M2 Subiectul I at d1.
