"""Algebraic structures — law of composition problem (spec §9.3, §5.4).

A law ``x ∗ y = f(x, y)`` is fixed and linked cerinte explore it: direct value,
commutativity, neutral element, symmetric element, equations. For M3 this is the
**Subiectul II 6-item** format; for M1/M2 it is a 3-item Subiectul II problem.

Every law here has the canonical "translate-and-shift" shape
``x ∗ y = (x − e)(y − e) + e`` (associative, commutative, neutral element ``e``,
symmetric ``x' = e + 1/(x−e)``) or an additive variant — all easy to verify by
hand and with sympy, per §9.3 rules.
"""
from __future__ import annotations

import sympy as sp

from ..base import ProblemGenerator

x, y = sp.symbols("x y", real=True)


def _l(expr) -> str:
    return sp.latex(expr, mul_symbol="dot")


class AlgebraicStructuresProblem(ProblemGenerator):
    TOPIC_CODE = "algebraic_structures"
    SUPPORTED_PROFILES = ["M1", "M2", "M3"]

    def __init__(self, profile, rng, *, six_items: bool = False):
        super().__init__(profile, rng)
        self.six = six_items
        if six_items:
            self.SUB_LABELS = ("a", "b", "c", "d", "e", "f")
            self.SUB_DIFFICULTIES = (1, 1, 2, 2, 3, 3)

    # --- law construction ----------------------------------------------------
    def _law_family(self):
        """Return (f(x,y), neutral e). Both laws are commutative & associative;
        the neutral is the *true* one (verified in ``_validate_context``).

        - mult-shift  f = (x−c)(y−c)+c   →  neutral e = c+1
        - additive    f = x+y−c          →  neutral e = c
        """
        rng = self.rng
        c = rng.choice([1, 2, 3, -1])
        fams = [
            (lambda u, v, c=c: (u - c) * (v - c) + c, c + 1),
            (lambda u, v, c=c: u + v - c, c),
        ]
        if self.profile == "M3":
            # M3: keep the additive law (simplest to verify by hand, §5.4).
            return fams[1]
        return rng.choice(fams)

    def _generate_context(self) -> dict:
        f, e = self._law_family()
        rng = self.rng
        # y0 distinct from the neutral to avoid a degenerate equation in cerinte.
        y_choices = [v for v in [0, 1, 2, 3] if v != e] or [e + 1]
        return {
            "f": f,
            "e": e,
            "x0": rng.choice([0, 1, 2, 3]),
            "y0": rng.choice(y_choices),
            "target": rng.choice([e + 1, e + 2, e - 2]),
        }

    def _validate_context(self, ctx) -> bool:
        f, e = ctx["f"], ctx["e"]
        z = sp.symbols("z", real=True)
        comm = sp.simplify(f(x, y) - f(y, x)) == 0
        assoc = sp.simplify(f(f(x, y), z) - f(x, f(y, z))) == 0
        neutral = sp.simplify(f(x, e) - x) == 0 and sp.simplify(f(e, x) - x) == 0
        return bool(comm and assoc and neutral)

    def _build_statement(self, ctx) -> str:
        f = ctx["f"]
        dom = r"\mathbb{R}"
        return (
            rf"Pe mulțimea ${dom}$ se definește legea de compoziție "
            rf"$x \ast y = {_l(sp.expand(f(x, y)))}$."
        )

    # --- cerinte (sympy-verified) --------------------------------------------
    def _c_value(self, ctx, label, tier):
        f, x0, y0 = ctx["f"], ctx["x0"], ctx["y0"]
        val = sp.nsimplify(f(x0, y0))
        return {
            "question_latex": rf"Arătați că ${x0} \ast {y0} = {_l(val)}$.",
            "answer_latex": rf"${x0} \ast {y0} = {_l(val)}$",
            "hint_latex": r"Înlocuiți $x$ și $y$ cu valorile date în formula legii.",
            "steps_latex": [rf"${x0} \ast {y0} = {_l(sp.expand(f(x0, y0)))} = {_l(val)}$"],
        }

    def _c_commutativity(self, ctx, label, tier):
        f = ctx["f"]
        return {
            "question_latex": r"Arătați că legea $\ast$ este comutativă.",
            "answer_latex": r"$x \ast y = y \ast x$, pentru orice $x, y \in \mathbb{R}$",
            "hint_latex": r"Comparați $x \ast y$ cu $y \ast x$ după formula legii.",
            "steps_latex": [rf"$x \ast y = {_l(sp.expand(f(x, y)))} = y \ast x$"],
        }

    def _c_neutral(self, ctx, label, tier):
        f, e = ctx["f"], ctx["e"]
        assert sp.simplify(f(x, e) - x) == 0
        return {
            "question_latex": rf"Arătați că $e = {e}$ este elementul neutru al legii $\ast$.",
            "answer_latex": rf"$e = {e}$",
            "hint_latex": r"Rezolvați $x \ast e = x$ pentru orice $x$.",
            "steps_latex": [rf"$x \ast {e} = {_l(sp.expand(f(x, e)))} = x$, "
                            rf"deci $e = {e}$ este element neutru."],
        }

    def _c_equation(self, ctx, label, tier):
        f, e = ctx["f"], ctx["e"]
        target = ctx["target"]
        sols = sp.solve(sp.Eq(f(x, x), f(x, x).subs(x, target)), x)
        sols = sorted({s for s in sols if s.is_real}, key=lambda s: float(s))
        if not sols:
            raise ValueError("no real solution")
        rhs = sp.expand(f(target, target))
        sol_l = ",\\ ".join(_l(s) for s in sols)
        return {
            "question_latex": rf"Determinați numerele reale $x$ pentru care "
                              rf"$x \ast x = {_l(rhs)}$.",
            "answer_latex": rf"$x \in \{{{sol_l}\}}$",
            "hint_latex": r"Scrieți $x \ast x$ după formula legii și rezolvați ecuația.",
            "steps_latex": [rf"$x \ast x = {_l(sp.expand(f(x, x)))} = {_l(rhs)}$",
                            rf"$\Rightarrow x \in \{{{sol_l}\}}$"],
        }

    def _c_symmetric(self, ctx, label, tier):
        f, e = ctx["f"], ctx["e"]
        xp = sp.symbols("x'", real=True)
        sym = sp.solve(sp.Eq(f(x, xp), e), xp)
        if not sym:
            raise ValueError("no symmetric")
        sx = sp.simplify(sym[0])
        assert sp.simplify(f(x, sx) - e) == 0
        return {
            "question_latex": rf"Determinați elementul simetric al lui $x$ față de legea "
                              rf"$\ast$ (cu element neutru $e = {e}$), pentru $x$ cu "
                              rf"$x \neq {e}$ când este cazul.",
            "answer_latex": rf"$x' = {_l(sx)}$",
            "hint_latex": rf"Rezolvați $x \ast x' = {e}$ în raport cu $x'$.",
            "steps_latex": [rf"$x \ast x' = {e} \Rightarrow x' = {_l(sx)}$"],
        }

    def _c_eq_with_value(self, ctx, label, tier):
        f, y0, e = ctx["f"], ctx["y0"], ctx["e"]
        rhs = sp.expand(f(ctx["target"], y0))
        sol = sp.solve(sp.Eq(f(x, y0), rhs), x)
        sol = [s for s in sol if s.is_real]
        if not sol:
            raise ValueError("no solution")
        sol_l = ",\\ ".join(_l(sp.simplify(s)) for s in sol)
        return {
            "question_latex": rf"Determinați numerele reale $x$ pentru care "
                              rf"$x \ast {y0} = {_l(rhs)}$.",
            "answer_latex": rf"$x \in \{{{sol_l}\}}$",
            "hint_latex": r"Înlocuiți $y$ cu valoarea dată și rezolvați ecuația în $x$.",
            "steps_latex": [rf"$x \ast {y0} = {_l(sp.expand(f(x, y0)))} = {_l(rhs)}$",
                            rf"$\Rightarrow x \in \{{{sol_l}\}}$"],
        }

    def _plan(self):
        if self.six:  # M3 Subiectul II — six items
            return [self._c_value, self._c_equation, self._c_commutativity,
                    self._c_neutral, self._c_eq_with_value, self._c_symmetric]
        return [self._c_value, self._c_neutral, self._c_symmetric]

    def _build_sub_item(self, ctx, label, difficulty) -> dict:
        idx = self.SUB_LABELS.index(label)
        return self._plan()[idx](ctx, label, difficulty)
