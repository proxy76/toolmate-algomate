"""Polynomials — Subiectul II problem-form (spec §3.4, §10.4). M1/M2.

A parametrized cubic ``f = X³ + aX² − aX + c₀`` (so ``f(1) = 1 + c₀`` is
independent of ``a``), with linked sub-items:
  (a) show ``f(1)`` is a fixed value for every ``a``        [evaluate]
  (b) quotient & remainder of ``f`` divided by ``X + 1``    [polynomial division]
  (c) determine ``a`` from a Viète relation on the roots    [§ relațiile lui Viète]

All algebra is computed/verified with sympy.
"""
from __future__ import annotations

import sympy as sp

from ..base import ProblemGenerator

X = sp.Symbol("X")
a = sp.Symbol("a", real=True)


def _l(expr) -> str:
    return sp.latex(expr)


class PolynomialsProblem(ProblemGenerator):
    TOPIC_CODE = "polynomials"
    SUPPORTED_PROFILES = ["mate-info", "tehnologic", "stiintele-naturii"]

    def _generate_context(self) -> dict:
        rng = self.rng
        c0 = rng.choice([2, -2, 3, 1, -1])
        u = rng.choice([1, 2, -1])
        # Two families with an a-independent value at r0: r0=1 needs the aX²/−aX pair,
        # r0=−1 needs aX²/+aX. Both give f(r0) = r0³ + c0.
        r0 = rng.choice([1, -1])
        f = X ** 3 + u * a * X ** 2 + (-u if r0 == 1 else u) * a * X + c0
        inv = r0 ** 3 + c0
        r = rng.choice([v for v in [1, -1, 2, -2] if v != r0])   # divisor X − r for (b)
        return {"f": f, "c0": c0, "r0": r0, "inv": inv, "r": r,
                "kind_c": rng.choice(["sumsq", "divis"])}

    def _validate_context(self, ctx) -> bool:
        return sp.simplify(ctx["f"].subs(X, ctx["r0"]) - ctx["inv"]) == 0

    def _build_statement(self, ctx) -> str:
        return rf"Se consideră polinomul $f = {_l(ctx['f'])}$, unde $a$ este număr real."

    def _build_sub_item(self, ctx, label, difficulty) -> dict:
        return {"a": self._a, "b": self._b, "c": self._c}[label](ctx)

    def _a(self, ctx):
        r0, val = ctx["r0"], ctx["inv"]
        assert sp.simplify(ctx["f"].subs(X, r0) - val) == 0
        r0t = r0 if r0 >= 0 else rf"({r0})"
        return {
            "question_latex": rf"Arătați că $f({r0t}) = {val}$, pentru orice număr real $a$.",
            "answer_latex": rf"$f({r0t}) = {val}$",
            "hint_latex": rf"Înlocuiți $X$ cu ${r0t}$; termenii care conțin $a$ se reduc.",
            "steps_latex": [rf"$f({r0t}) = {val}$"],
        }

    def _b(self, ctx):
        f, r = ctx["f"], ctx["r"]
        dv = X - r
        quo, rem = sp.div(f, dv, X)
        quo, rem = sp.expand(quo), sp.expand(rem)
        assert sp.expand(f - (dv * quo + rem)) == 0
        sign = "+" if r < 0 else "-"
        return {
            "question_latex": rf"Determinați câtul și restul împărțirii polinomului $f$ la "
                              rf"$X {sign} {abs(r)}$.",
            "answer_latex": rf"$C(X) = {_l(quo)}$, $\quad R = {_l(rem)}$",
            "hint_latex": r"Folosiți schema lui Horner sau împărțirea polinoamelor.",
            "steps_latex": [rf"$f = \left(X {sign} {abs(r)}\right)\left({_l(quo)}\right) "
                            rf"+ \left({_l(rem)}\right)$"],
        }

    def _c(self, ctx):
        coeffs = sp.Poly(ctx["f"], X).all_coeffs()          # [1, p, q, c0]
        if ctx["kind_c"] == "sumsq":
            target = self.rng.choice([1, 2, 3])
            K = target ** 2 + 2 * target
            sum_sq = sp.expand(coeffs[1] ** 2 - 2 * coeffs[2])   # (Σx)² − 2Σxᵢxⱼ
            sols = sorted((s for s in sp.solve(sp.Eq(sum_sq, K), a) if s.is_real), key=float)
            if not sols:
                raise ValueError("no real a")
            sol_l = ",\\ ".join(_l(s) for s in sols)
            return {
                "question_latex": rf"Determinați numerele reale $a$ pentru care "
                                  rf"$x_1^2 + x_2^2 + x_3^2 = {K}$, unde $x_1, x_2, x_3$ sunt "
                                  rf"rădăcinile polinomului $f$.",
                "answer_latex": rf"$a \in \{{{sol_l}\}}$",
                "hint_latex": r"Relațiile lui Viète: "
                              r"$x_1^2 + x_2^2 + x_3^2 = \left(\sum x_i\right)^2 - 2\sum_{i<j} x_i x_j$.",
                "steps_latex": [rf"$x_1^2 + x_2^2 + x_3^2 = {_l(sum_sq)} = {K}$",
                                rf"$a \in \{{{sol_l}\}}$"],
            }
        # divisibility: f divisible by (X − s) ⟺ f(s) = 0 (solve for a).
        s = self.rng.choice([v for v in [2, -2, 3, -3] if v not in (ctx["r0"], ctx["r"])])
        fs = sp.expand(ctx["f"].subs(X, s))
        sols = sorted((v for v in sp.solve(sp.Eq(fs, 0), a) if v.is_real), key=float)
        if not sols:
            raise ValueError("no real a")
        sol_l = ",\\ ".join(_l(v) for v in sols)
        sign = "+" if s < 0 else "-"
        return {
            "question_latex": rf"Determinați numerele reale $a$ pentru care polinomul $f$ "
                              rf"este divizibil cu $X {sign} {abs(s)}$.",
            "answer_latex": rf"$a \in \{{{sol_l}\}}$",
            "hint_latex": rf"$f$ divizibil cu $X {sign} {abs(s)} \Leftrightarrow f({s}) = 0$.",
            "steps_latex": [rf"$f({s}) = {_l(fs)} = 0 \Rightarrow a \in \{{{sol_l}\}}$"],
        }
