"""Logarithms — single-item class (spec §7.3 logarithms, §5.2 M3 restriction).

d1: a log identity that collapses to an integer, or a simple equation
    ``log_b(x²+px) = log_b(C)``.
d2: ``log_b(x) − log_b(x−a) = 1`` and a logarithmic inequality.
M3: only the d1 simple equations / identities with base 2, 3, 10 (spec §5.2).

Solutions are produced/verified with sympy and filtered to the domain where the
log arguments are positive (spec §11.4).
"""
from __future__ import annotations

import sympy as sp

from ..base import ExerciseGenerator

x = sp.Symbol("x", real=True)


def _l(expr) -> str:
    return sp.latex(expr)


class LogarithmsGenerator(ExerciseGenerator):
    TOPIC_CODE = "logarithms"
    SUPPORTED_PROFILES = ["M1", "M2", "M3"]

    def _generate_params(self) -> dict:
        rng = self.rng
        if self.profile == "M3":
            pool = [self._st_identity, self._st_eq_simple]
        elif self.difficulty == 1:
            pool = [self._st_identity, self._st_eq_simple]
        elif self.difficulty == 2:
            pool = [self._st_eq_linear, self._st_inequality, self._st_eq_simple]
        else:
            pool = [self._st_inequality, self._st_eq_linear]
        return rng.choice(pool)()

    def _compute_answer(self, params):
        return params.get("answer")

    def _validate(self, params, answer) -> bool:
        return params.get("ok", True) and len(params["answer_latex"]) < 200

    def _build_question(self, params):
        return params["question"]

    def _build_answer_latex(self, params, answer):
        return params["answer_latex"]

    def _build_hint(self, params):
        return params.get("hint", "")

    def _build_steps(self, params):
        return params.get("steps", [])

    # --- subtypes ------------------------------------------------------------
    def _st_identity(self):
        rng = self.rng
        b = rng.choice([2, 3, 10])
        k = rng.randint(2, 4)
        e1 = rng.randint(1, k - 1)
        m, n = b ** e1, b ** (k - e1)
        val = sp.simplify(sp.log(m, b) + sp.log(n, b))
        assert val == k
        return {
            "question": rf"Arătați că $\log_{{{b}}} {m} + \log_{{{b}}} {n} = {k}$.",
            "answer_latex": rf"${k}$",
            "answer": sp.Integer(k),
            "hint": r"Folosiți $\log_b m + \log_b n = \log_b(mn)$.",
            "steps": [rf"$\log_{{{b}}} {m} + \log_{{{b}}} {n} = "
                      rf"\log_{{{b}}} {m * n} = {k}$"],
            "ok": True,
        }

    def _st_eq_simple(self):
        rng = self.rng
        b = rng.choice([2, 3, 10])
        r1 = rng.choice([-2, -3, -4, -5])
        r2 = rng.choice([1, 2, 3])
        p = -(r1 + r2)
        C = -r1 * r2                       # > 0
        arg = x ** 2 + p * x
        sols = sorted((s for s in sp.solve(sp.Eq(arg, C), x)
                       if s.is_real and (arg.subs(x, s)) > 0), key=float)
        assert sols == sorted([r1, r2])
        sol_l = ",\\ ".join(_l(s) for s in sols)
        return {
            "question": rf"Rezolvați în mulțimea numerelor reale ecuația "
                        rf"$\log_{{{b}}}\left({_l(arg)}\right) = \log_{{{b}}} {C}$.",
            "answer_latex": rf"$x \in \{{{sol_l}\}}$",
            "answer": tuple(sols),
            "hint": r"Egalitatea logaritmilor în aceeași bază $\Rightarrow$ "
                    r"egalitatea argumentelor (cu condiția de existență).",
            "steps": [rf"${_l(arg)} = {C}$", rf"$x \in \{{{sol_l}\}}$"],
            "ok": True,
        }

    def _st_eq_linear(self):
        rng = self.rng
        b = rng.choice([2, 3])
        a = rng.choice([1, 2, 3])
        sol = sp.solve(sp.Eq(sp.log(x, b) - sp.log(x - a, b), 1), x)
        sol = [s for s in sol if s.is_real and s > 0 and s - a > 0]
        assert len(sol) == 1
        s = sp.nsimplify(sol[0])
        return {
            "question": rf"Rezolvați în mulțimea numerelor reale ecuația "
                        rf"$\log_{{{b}}} x - \log_{{{b}}}(x - {a}) = 1$.",
            "answer_latex": rf"$x = {_l(s)}$",
            "answer": s,
            "hint": rf"$\log_b x - \log_b(x-{a}) = \log_b\dfrac{{x}}{{x-{a}}}$, "
                    rf"apoi $\dfrac{{x}}{{x-{a}}} = {b}$.",
            "steps": [rf"$\dfrac{{x}}{{x-{a}}} = {b}$", rf"$x = {_l(s)}$"],
            "ok": True,
        }

    def _st_inequality(self):
        rng = self.rng
        b = rng.choice([2, 3])
        k = rng.randint(1, 4)
        C = k ** 2 + 1                     # log_b(x²+1) ≤ log_b(C) ⇔ x² ≤ k²
        return {
            "question": rf"Determinați numerele reale $x$ pentru care "
                        rf"$\log_{{{b}}}(x^2 + 1) \leq \log_{{{b}}} {C}$.",
            "answer_latex": rf"$x \in [{-k}, {k}]$",
            "answer": (sp.Integer(-k), sp.Integer(k)),
            "hint": rf"Baza ${b} > 1$, deci logaritmul este crescător: "
                    rf"$x^2 + 1 \leq {C}$.",
            "steps": [rf"$x^2 + 1 \leq {C} \iff x^2 \leq {k**2}$",
                      rf"$x \in [{-k}, {k}]$"],
            "ok": True,
        }
