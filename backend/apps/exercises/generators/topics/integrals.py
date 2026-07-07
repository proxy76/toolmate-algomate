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


def _lln(expr) -> str:
    # Romanian BAC writes the natural log as ``ln`` (sympy emits ``\log``).
    return sp.latex(expr).replace(r"\log", r"\ln")


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
        # M1 (mate-info): the sequence-of-integrals problem (recurrence + limit) is
        # a *signature* form but only ~1/4 of real M1 integral problems — the rest
        # are direct integrals / areas / substitutions. Match that frequency.
        if self.profile == "M1" and self.rng.random() < 0.3:
            return self._context_sequence()
        f, lo, hi, dom = self._families()
        F = sp.simplify(sp.integrate(f, x))
        value = sp.simplify(sp.integrate(f, (x, lo, hi)))
        area = self._area(f, lo, hi)
        return {"f": f, "F": F, "lo": lo, "hi": hi, "dom": dom,
                "value": value, "area": area}

    def _validate_context(self, ctx) -> bool:
        if ctx.get("kind") == "sequence":
            return True                       # pre-verified in _context_sequence
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
        if ctx.get("kind") == "sequence":
            return (rf"Se consideră șirul $(I_n)_{{n \geq 1}}$, definit prin "
                    rf"$I_n = \displaystyle\int_0^1 \dfrac{{x^n}}{{{ctx['denom_tex']}}}\,dx$, "
                    rf"unde $n$ este număr natural nenul.")
        return rf"Se consideră funcția ${ctx['dom']}$, $f(x) = {_l(ctx['f'])}$."

    def _build_sub_item(self, ctx, label, difficulty) -> dict:
        if ctx.get("kind") == "sequence":
            return {"a": self._seq_a, "b": self._seq_b, "c": self._seq_c}[label](ctx)
        return {"a": self._a, "b": self._b, "c": self._c}[label](ctx)

    # --- M1 sequence-of-integrals mode ---------------------------------------
    def _context_sequence(self) -> dict:
        rng = self.rng
        if rng.choice(["p1", "p2"]) == "p1":
            integrand = lambda k: x ** k / (x + 1)
            denom_tex, rec_tex = "x + 1", r"I_n + I_{n-1} = \dfrac{1}{n}"
            rec_hint = r"$\dfrac{x^n + x^{n-1}}{x + 1} = x^{n-1}$"
            n_min, shift = 2, 1
            check = lambda n: sp.integrate(integrand(n), (x, 0, 1)) + \
                sp.integrate(integrand(n - 1), (x, 0, 1)) - sp.Rational(1, n)
        else:
            integrand = lambda k: x ** k / (x ** 2 + 1)
            denom_tex, rec_tex = "x^2 + 1", r"I_n + I_{n-2} = \dfrac{1}{n-1}"
            rec_hint = r"$\dfrac{x^n + x^{n-2}}{x^2 + 1} = x^{n-2}$"
            n_min, shift = 3, 2
            check = lambda n: sp.integrate(integrand(n), (x, 0, 1)) + \
                sp.integrate(integrand(n - 2), (x, 0, 1)) - sp.Rational(1, n - 1)
        for n in (n_min, n_min + 1, n_min + 2):
            assert sp.simplify(check(n)) == 0
        I1 = sp.simplify(sp.integrate(integrand(1), (x, 0, 1)))
        return {"kind": "sequence", "integrand": integrand, "denom_tex": denom_tex,
                "rec_tex": rec_tex, "rec_hint": rec_hint, "n_min": n_min,
                "shift": shift, "I1": I1}

    def _seq_a(self, ctx):
        I1 = ctx["I1"]
        return {"question_latex": r"Calculați $I_1$.",
                "answer_latex": rf"$I_1 = {_lln(I1)}$",
                "hint_latex": rf"$I_1 = \displaystyle\int_0^1 \dfrac{{x}}{{{ctx['denom_tex']}}}"
                              rf"\,dx$; rescrieți numărătorul folosind numitorul.",
                "steps_latex": [rf"$I_1 = {_lln(I1)}$"]}

    def _seq_b(self, ctx):
        return {"question_latex": rf"Arătați că ${ctx['rec_tex']}$, pentru orice număr "
                                  rf"natural $n \geq {ctx['n_min']}$.",
                "answer_latex": rf"${ctx['rec_tex']}$",
                "hint_latex": rf"Adunați cele două integrale: {ctx['rec_hint']}.",
                "steps_latex": [rf"{ctx['rec_hint']}",
                                rf"$\Rightarrow {ctx['rec_tex']}$"]}

    def _seq_c(self, ctx):
        return {"question_latex": r"Arătați că $\displaystyle\lim_{n\to\infty} I_n = 0$.",
                "answer_latex": r"$\displaystyle\lim_{n\to\infty} I_n = 0$",
                "hint_latex": r"$0 \leq I_n \leq \displaystyle\int_0^1 x^n\,dx = "
                              r"\dfrac{1}{n+1} \to 0$ (criteriul cleștelui).",
                "steps_latex": [rf"$0 \leq \dfrac{{x^n}}{{{ctx['denom_tex']}}} \leq x^n$ pe $[0,1]$",
                                r"$0 \leq I_n \leq \dfrac{1}{n+1} \to 0 \Rightarrow "
                                r"\lim_{n\to\infty} I_n = 0$"]}

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
