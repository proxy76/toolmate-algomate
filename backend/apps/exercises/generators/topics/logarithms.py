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
    SUPPORTED_PROFILES = ["mate-info", "tehnologic", "stiintele-naturii", "pedagogic"]

    def _generate_params(self) -> dict:
        rng = self.rng
        # ``logarithms`` is the numeric-identity / inequality flavour (Subiectul I
        # position 1 — "algebra on numbers"). Log *equations* are the ``equations``
        # topic (position 3), so they are intentionally not produced here — keeping
        # the pos-1 exam slot a genuine identity, as in the real papers.
        if self.profile == "pedagogic":
            pool = [self._st_identity, self._st_identity_sub]
        elif self.difficulty == 1:
            pool = [self._st_identity, self._st_identity_sub]
        else:
            pool = [self._st_identity, self._st_identity_sub, self._st_inequality]
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
    @staticmethod
    def _lg(b: int, arg) -> str:
        """Base-10 logs print as ``lg`` (BAC convention); others as ``\\log_b``."""
        return rf"\lg {arg}" if b == 10 else rf"\log_{{{b}}} {arg}"

    def _st_identity(self):
        # Authentic pos-1 form: c·log_b(b^p) + log_b(m) + log_b(n) = c·p + q,
        # with m·n = b^q and m, n not necessarily powers of b
        # (e.g. "2\lg 100 + \lg 2 + \lg 5 = 5").
        rng = self.rng
        b = rng.choice([2, 3, 10])
        c, p = rng.randint(1, 3), rng.randint(1, 2)
        q = rng.choice([1, 2]) if b == 10 else 2   # ensure b^q has a proper factor pair
        bq = b ** q
        divs = [d for d in range(2, bq) if bq % d == 0]
        m = rng.choice(divs)                        # m, n ≥ 2 (no degenerate log 1)
        n = bq // m
        val = sp.simplify(c * sp.log(b ** p, b) + sp.log(m, b) + sp.log(n, b))
        assert val == c * p + q
        cc = "" if c == 1 else str(c)
        term1 = self._lg(b, b ** p)
        return {
            "question": rf"Arătați că ${cc}{term1} + {self._lg(b, m)} + {self._lg(b, n)} "
                        rf"= {c * p + q}$.",
            "answer_latex": rf"${c * p + q}$",
            "answer": sp.Integer(c * p + q),
            "hint": r"Folosiți $\log_b(b^p) = p$ și $\log_b m + \log_b n = \log_b(mn)$.",
            "steps": [rf"${cc}{term1} = {c * p}$, $\ {self._lg(b, m)} + {self._lg(b, n)} "
                      rf"= {self._lg(b, m * n)} = {q}$"],
            "ok": True,
        }

    def _st_identity_sub(self):
        # Subtraction form: log_b(M) − log_b(N) = q, with M/N = b^q
        # (e.g. "\lg 40 − \lg 4 = 1", "\log_2 40 − \log_2 5 = 3").
        rng = self.rng
        b = rng.choice([2, 3, 10])
        q = rng.randint(1, 2) if b == 10 else rng.randint(1, 3)
        n = rng.choice([2, 4, 5]) if b == 10 else rng.randint(2, 5)
        m = n * b ** q
        val = sp.simplify(sp.log(m, b) - sp.log(n, b))
        assert val == q
        return {
            "question": rf"Arătați că ${self._lg(b, m)} - {self._lg(b, n)} = {q}$.",
            "answer_latex": rf"${q}$",
            "answer": sp.Integer(q),
            "hint": r"Folosiți $\log_b m - \log_b n = \log_b\dfrac{m}{n}$.",
            "steps": [rf"${self._lg(b, m)} - {self._lg(b, n)} = "
                      rf"{self._lg(b, sp.Rational(m, n))} = {q}$"],
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
