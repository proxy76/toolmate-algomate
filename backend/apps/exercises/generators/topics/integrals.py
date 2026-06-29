"""Integrals — Subiectul III problem-form (spec §3.3, §10.4). M1/M2.

One shared ``f`` on an interval ``[lo, hi]`` with linked a/b/c:
  (a) show ``F`` is a primitive of ``f``         (verify ``F' = f``)
  (b) compute ``∫[lo,hi] f dx = value``          (Leibniz–Newton)
  (c) area between the graph and ``Ox`` on ``[lo,hi]`` = ``∫|f|``

Functions are chosen from a small set with clean integrals (logarithms / e
allowed); everything is computed and verified with sympy.
"""
from __future__ import annotations

import sympy as sp

from ..base import ProblemGenerator

x = sp.Symbol("x", positive=True)


def _l(expr) -> str:
    return sp.latex(expr)


class IntegralsProblem(ProblemGenerator):
    TOPIC_CODE = "integrals"
    SUPPORTED_PROFILES = ["M1", "M2"]

    def _families(self):
        rng = self.rng
        k = rng.choice([1, 2, 3])
        return rng.choice([
            (sp.log(x), 1, sp.E, r"f:(0,\infty)\to\mathbb{R}"),          # ∫=1
            (x * sp.exp(x), 0, 1, r"f:\mathbb{R}\to\mathbb{R}"),          # ∫=1
            (2 * x - 2, 0, 3, r"f:\mathbb{R}\to\mathbb{R}"),              # sign-changing
            (sp.Integer(1) / (x + 1), 0, k, r"f:(-1,\infty)\to\mathbb{R}"),  # ∫=ln(k+1)
            (3 * x ** 2 + 1, 0, 2, r"f:\mathbb{R}\to\mathbb{R}"),         # ∫=10
        ])

    def _area(self, f, lo, hi):
        """Exact area |∫f| split at the sign changes of f inside (lo, hi)."""
        roots = sorted(
            (r for r in sp.solve(sp.Eq(f, 0), x) if r.is_real and lo < r < hi),
            key=float,
        )
        pts = [lo, *roots, hi]
        total = sum(sp.Abs(sp.integrate(f, (x, a, b))) for a, b in zip(pts, pts[1:]))
        return sp.simplify(total)

    def _generate_context(self) -> dict:
        f, lo, hi, dom = self._families()
        F = sp.simplify(sp.integrate(f, x))
        value = sp.simplify(sp.integrate(f, (x, lo, hi)))
        area = self._area(f, lo, hi)
        return {"f": f, "F": F, "lo": lo, "hi": hi, "dom": dom,
                "value": value, "area": area}

    def _validate_context(self, ctx) -> bool:
        if sp.simplify(sp.diff(ctx["F"], x) - ctx["f"]) != 0:
            return False
        for key in ("value", "area"):
            v = ctx[key]
            if v in (sp.nan, sp.zoo, sp.oo, -sp.oo) or not v.is_finite:
                return False
            if len(sp.latex(v)) > 60:
                return False
        return True

    def _build_statement(self, ctx) -> str:
        return rf"Se consideră funcția ${ctx['dom']}$, $f(x) = {_l(ctx['f'])}$."

    def _build_sub_item(self, ctx, label, difficulty) -> dict:
        return {"a": self._a, "b": self._b, "c": self._c}[label](ctx)

    def _a(self, ctx):
        F = ctx["F"]
        assert sp.simplify(sp.diff(F, x) - ctx["f"]) == 0
        return {"question_latex": rf"Arătați că funcția $F(x) = {_l(F)}$ este o primitivă a "
                                  rf"funcției $f$.",
                "answer_latex": rf"$F'(x) = {_l(sp.simplify(sp.diff(F, x)))} = f(x)$",
                "hint_latex": r"O primitivă verifică $F'(x) = f(x)$."}

    def _b(self, ctx):
        lo, hi, val = ctx["lo"], ctx["hi"], ctx["value"]
        assert sp.simplify(sp.integrate(ctx["f"], (x, lo, hi)) - val) == 0
        return {"question_latex": rf"Arătați că $\displaystyle\int_{{{_l(lo)}}}^{{{_l(hi)}}} "
                                  rf"f(x)\,dx = {_l(val)}$.",
                "answer_latex": rf"$\displaystyle\int_{{{_l(lo)}}}^{{{_l(hi)}}} f(x)\,dx = {_l(val)}$",
                "hint_latex": r"Folosiți formula Leibniz–Newton: "
                              r"$\int_a^b f = F(b) - F(a)$.",
                "steps_latex": [rf"$\int_{{{_l(lo)}}}^{{{_l(hi)}}} f(x)\,dx = "
                                rf"F({_l(hi)}) - F({_l(lo)}) = {_l(val)}$"]}

    def _c(self, ctx):
        lo, hi, area = ctx["lo"], ctx["hi"], ctx["area"]
        return {"question_latex": rf"Calculați aria suprafeței plane delimitate de graficul "
                                  rf"funcției $f$, axa $Ox$ și dreptele $x = {_l(lo)}$ și "
                                  rf"$x = {_l(hi)}$.",
                "answer_latex": rf"$\mathcal{{A}} = {_l(area)}$",
                "hint_latex": r"Aria este $\int_{a}^{b} |f(x)|\,dx$; atenție la semnul lui $f$."}
