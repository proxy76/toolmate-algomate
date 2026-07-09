"""Sequences — single-item class (spec §7.3 sequences, §4.2). M1/M2.

Distinct from ``progressions`` (basic arithmetic/geometric): this is the
convergence/limit/recurrence flavour.
  d1: limit of a rational sequence; a recurrence term.
  d2: sum of an infinite geometric series (|q|<1); harder rational limit.
  d3 (M1): a Cesàro–Stolz limit.
All limits/sums computed and verified with sympy.
"""
from __future__ import annotations

import sympy as sp

from ..base import ExerciseGenerator

n = sp.Symbol("n", positive=True)


def _l(expr) -> str:
    return sp.latex(expr)


class SequencesGenerator(ExerciseGenerator):
    TOPIC_CODE = "sequences"
    SUPPORTED_PROFILES = ["mate-info", "tehnologic", "stiintele-naturii"]

    def _generate_params(self) -> dict:
        rng = self.rng
        d = self.difficulty
        if d == 1:
            pool = [self._st_limit_rational, self._st_recurrence]
        elif d == 2:
            pool = [self._st_geom_series, self._st_limit_rational]
        else:
            pool = [self._st_cesaro] if self.profile == "mate-info" else [self._st_geom_series]
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
    def _st_limit_rational(self):
        rng = self.rng
        deg = rng.choice([1, 2])
        lead_num = rng.randint(1, 5)
        lead_den = rng.randint(1, 5)
        if deg == 1:
            num = lead_num * n + rng.randint(-4, 4)
            den = lead_den * n + rng.randint(1, 5)
        else:
            num = lead_num * n ** 2 + rng.randint(-4, 4) * n + rng.randint(-4, 4)
            den = lead_den * n ** 2 + rng.randint(1, 5) * n + rng.randint(1, 5)
        expr = num / den
        lim = sp.limit(expr, n, sp.oo)
        assert lim == sp.Rational(lead_num, lead_den)
        return {
            "question": rf"Se consideră șirul $(a_n)_{{n \geq 1}}$, $a_n = {_l(expr)}$. "
                        rf"Calculați $\lim\limits_{{n \to \infty}} a_n$.",
            "answer_latex": rf"$\lim\limits_{{n \to \infty}} a_n = {_l(lim)}$",
            "answer": lim,
            "hint": r"Dați factor comun puterea cea mai mare a lui $n$ la numărător și numitor.",
            "steps": [rf"$\lim_{{n\to\infty}} {_l(expr)} = {_l(lim)}$"],
            "ok": True,
        }

    def _st_recurrence(self):
        rng = self.rng
        a1 = rng.randint(1, 4)
        mul = rng.choice([2, 3])
        add = rng.randint(1, 4)
        k = rng.choice([3, 4])
        terms = [a1]
        for _ in range(k - 1):
            terms.append(mul * terms[-1] + add)
        ak = terms[-1]
        return {
            "question": rf"Se consideră șirul $(a_n)_{{n \geq 1}}$ definit prin $a_1 = {a1}$ și "
                        rf"$a_{{n+1}} = {mul} a_n + {add}$, pentru orice $n \geq 1$. "
                        rf"Calculați $a_{{{k}}}$.",
            "answer_latex": rf"$a_{{{k}}} = {ak}$",
            "answer": sp.Integer(ak),
            "hint": r"Calculați termenii succesiv folosind relația de recurență.",
            "steps": [rf"$a_{{{i + 1}}} = {terms[i]}$" for i in range(k)],
            "ok": True,
        }

    def _st_geom_series(self):
        rng = self.rng
        a1 = rng.choice([1, 2, 3, 4, 6])
        q = rng.choice([sp.Rational(1, 2), sp.Rational(1, 3), sp.Rational(1, 4),
                        sp.Rational(2, 3)])
        S = sp.simplify(a1 / (1 - q))
        k = sp.Symbol("k", integer=True, nonnegative=True)
        assert sp.summation(a1 * q ** k, (k, 0, sp.oo)) == S
        return {
            "question": rf"Calculați suma $S = {a1} + {a1}\cdot{_l(q)} + {a1}\cdot{_l(q)}^2 + "
                        rf"\cdots$, unde termenii formează o progresie geometrică infinită "
                        rf"cu primul termen ${a1}$ și rația ${_l(q)}$.",
            "answer_latex": rf"$S = {_l(S)}$",
            "answer": S,
            "hint": rf"Pentru $|q| < 1$, $S = \dfrac{{a_1}}{{1 - q}}$.",
            "steps": [rf"$S = \dfrac{{{a1}}}{{1 - {_l(q)}}} = {_l(S)}$"],
            "ok": True,
        }

    def _st_cesaro(self):
        rng = self.rng
        c = rng.choice([1, 2, 3])
        # a_n = c(1+2+...+n) = c·n(n+1)/2 ; lim a_n / n² = c/2  (Cesàro–Stolz)
        an = c * n * (n + 1) / 2
        lim = sp.limit(an / n ** 2, n, sp.oo)
        assert lim == sp.Rational(c, 2)
        return {
            "question": rf"Se consideră șirul $(a_n)_{{n \geq 1}}$, "
                        rf"$a_n = {c}\,(1 + 2 + \cdots + n)$. Utilizând criteriul "
                        rf"Cesàro–Stolz, calculați $\lim\limits_{{n \to \infty}} "
                        rf"\dfrac{{a_n}}{{n^2}}$.",
            "answer_latex": rf"$\lim\limits_{{n \to \infty}} \dfrac{{a_n}}{{n^2}} = {_l(lim)}$",
            "answer": lim,
            "hint": r"Cesàro–Stolz: $\lim \dfrac{a_n}{b_n} = "
                    r"\lim \dfrac{a_{n+1}-a_n}{b_{n+1}-b_n}$.",
            "steps": [rf"$a_n = {_l(sp.simplify(an))}$",
                      rf"$\lim \dfrac{{a_n}}{{n^2}} = {_l(lim)}$"],
            "ok": True,
        }
