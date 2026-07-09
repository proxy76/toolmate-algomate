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
        c0 = self.rng.choice([2, -2, 3, 1, -1])
        f = X ** 3 + a * X ** 2 - a * X + c0
        return {"f": f, "c0": c0}

    def _validate_context(self, ctx) -> bool:
        return sp.simplify(ctx["f"].subs(X, 1) - (1 + ctx["c0"])) == 0

    def _build_statement(self, ctx) -> str:
        return rf"Se consideră polinomul $f = {_l(ctx['f'])}$, unde $a$ este număr real."

    def _build_sub_item(self, ctx, label, difficulty) -> dict:
        return {"a": self._a, "b": self._b, "c": self._c}[label](ctx)

    def _a(self, ctx):
        val = 1 + ctx["c0"]
        assert sp.simplify(ctx["f"].subs(X, 1) - val) == 0
        return {
            "question_latex": rf"Arătați că $f(1) = {val}$, pentru orice număr real $a$.",
            "answer_latex": rf"$f(1) = {val}$",
            "hint_latex": r"Înlocuiți $X$ cu $1$; termenii care conțin $a$ se reduc.",
            "steps_latex": [rf"$f(1) = 1 + a - a + ({ctx['c0']}) = {val}$"],
        }

    def _b(self, ctx):
        f = ctx["f"]
        quo, rem = sp.div(f, X + 1, X)
        quo, rem = sp.expand(quo), sp.expand(rem)
        assert sp.expand(f - ((X + 1) * quo + rem)) == 0
        return {
            "question_latex": r"Determinați câtul și restul împărțirii polinomului $f$ la $X + 1$.",
            "answer_latex": rf"$C(X) = {_l(quo)}$, $\quad R = {_l(rem)}$",
            "hint_latex": r"Folosiți schema lui Horner sau împărțirea polinoamelor.",
            "steps_latex": [rf"$f = (X + 1)\left({_l(quo)}\right) + \left({_l(rem)}\right)$"],
        }

    def _c(self, ctx):
        target = self.rng.choice([1, 2, 3])
        K = target ** 2 + 2 * target
        coeffs = sp.Poly(ctx["f"], X).all_coeffs()      # [1, a, -a, c0]
        sum_sq = sp.expand(coeffs[1] ** 2 - 2 * coeffs[2])   # (Σx)² − 2Σxᵢxⱼ = a² + 2a
        sols = sorted((s for s in sp.solve(sp.Eq(sum_sq, K), a) if s.is_real), key=float)
        assert sols
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
