"""Arithmetic & geometric progressions — single-item class (spec §7.3). M2/M3.

D1: n-th term / sum of first n terms (direct formula).
D2: recover the ratio from two terms, geometric sum.
"""
from __future__ import annotations

from ..base import TieredExerciseGenerator
from .._utils import make


def _d1_arith_term(rng):
    a1, r, n = rng.randint(1, 9), rng.randint(2, 5), rng.randint(5, 12)
    an = a1 + (n - 1) * r
    return make("progressions",
                rf"Într-o progresie aritmetică $a_1 = {a1}$ și rația $r = {r}$. "
                rf"Calculează $a_{{{n}}}$.", rf"$a_{{{n}}} = {an}$",
                hint_latex=r"$a_n = a_1 + (n-1)\,r$.")


def _d1_arith_sum(rng):
    a1, r, n = rng.randint(1, 9), rng.randint(2, 5), rng.randint(5, 10)
    an = a1 + (n - 1) * r
    s = n * (a1 + an) // 2
    return make("progressions",
                rf"Calculează suma primilor ${n}$ termeni ai progresiei aritmetice cu "
                rf"$a_1 = {a1}$ și rația $r = {r}$.", rf"$S_{{{n}}} = {s}$",
                hint_latex=r"$S_n = \dfrac{n\,(a_1 + a_n)}{2}$.")


def _d1_geom_term(rng):
    b1, q, n = rng.randint(1, 5), rng.randint(2, 3), rng.randint(4, 7)
    bn = b1 * q ** (n - 1)
    return make("progressions",
                rf"Într-o progresie geometrică $b_1 = {b1}$ și rația $q = {q}$. "
                rf"Calculează $b_{{{n}}}$.", rf"$b_{{{n}}} = {bn}$",
                hint_latex=r"$b_n = b_1\cdot q^{\,n-1}$.")


def _d2_find_ratio(rng):
    a1, r, k = rng.randint(1, 6), rng.randint(2, 5), rng.randint(3, 6)
    ak = a1 + (k - 1) * r
    return make("progressions",
                rf"Într-o progresie aritmetică $a_1 = {a1}$ și $a_{{{k}}} = {ak}$. "
                rf"Determină rația $r$.", rf"$r = {r}$",
                hint_latex=rf"$a_{{{k}}} = a_1 + ({k}-1)\,r$, de unde scoți $r$.",
                steps_latex=[rf"${ak} = {a1} + {k-1}\,r \Rightarrow r = {r}$"])


def _d2_geom_sum(rng):
    b1, q, n = rng.randint(1, 4), rng.randint(2, 3), rng.randint(4, 6)
    s = b1 * (q**n - 1) // (q - 1)
    return make("progressions",
                rf"Calculează suma primilor ${n}$ termeni ai progresiei geometrice cu "
                rf"$b_1 = {b1}$ și rația $q = {q}$.", rf"$S_{{{n}}} = {s}$",
                hint_latex=r"$S_n = b_1\,\dfrac{q^n - 1}{q - 1}$.")


_TIERS = {
    1: [_d1_arith_term, _d1_arith_sum, _d1_geom_term],
    2: [_d2_find_ratio, _d2_geom_sum],
}


class ProgressionsGenerator(TieredExerciseGenerator):
    TOPIC_CODE = "progressions"
    SUPPORTED_PROFILES = ["M2", "M3"]

    def _tiers(self):
        return _TIERS
