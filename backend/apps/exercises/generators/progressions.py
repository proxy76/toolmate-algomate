"""Arithmetic & geometric progressions — tiered to the BAC.

D1 (Subiectul I)  : the n-th term, or the sum of the first n terms (direct formula).
D2 (Subiectul II) : recover the ratio from two terms, geometric sum.

Progressions are a Subiectul I/II topic; ``choose_subtype`` falls back to D2
when difficulty 3 is requested.
"""
from __future__ import annotations

import random

from ._utils import make, pick


# ---------------------------------------------------------------- D1 ----------
def _d1_arith_term(rng):
    a1 = rng.randint(1, 9)
    r = rng.randint(2, 5)
    n = rng.randint(5, 12)
    an = a1 + (n - 1) * r
    return make(
        "progressions",
        rf"Într-o progresie aritmetică $a_1 = {a1}$ și rația $r = {r}$. Calculează $a_{{{n}}}$.",
        rf"$a_{{{n}}} = {an}$",
        hint_latex=r"$a_n = a_1 + (n-1)\,r$.",
    )


def _d1_arith_sum(rng):
    a1 = rng.randint(1, 9)
    r = rng.randint(2, 5)
    n = rng.randint(5, 10)
    an = a1 + (n - 1) * r
    s = n * (a1 + an) // 2
    return make(
        "progressions",
        rf"Calculează suma primilor ${n}$ termeni ai progresiei aritmetice cu "
        rf"$a_1 = {a1}$ și rația $r = {r}$.",
        rf"$S_{{{n}}} = {s}$",
        hint_latex=r"$S_n = \dfrac{n\,(a_1 + a_n)}{2}$.",
    )


def _d1_geom_term(rng):
    b1 = rng.randint(1, 5)
    q = rng.randint(2, 3)
    n = rng.randint(4, 7)
    bn = b1 * q ** (n - 1)
    return make(
        "progressions",
        rf"Într-o progresie geometrică $b_1 = {b1}$ și rația $q = {q}$. Calculează $b_{{{n}}}$.",
        rf"$b_{{{n}}} = {bn}$",
        hint_latex=r"$b_n = b_1\cdot q^{\,n-1}$.",
    )


# ---------------------------------------------------------------- D2 ----------
def _d2_find_ratio(rng):
    a1 = rng.randint(1, 6)
    r = rng.randint(2, 5)
    k = rng.randint(3, 6)
    ak = a1 + (k - 1) * r
    return make(
        "progressions",
        rf"Într-o progresie aritmetică $a_1 = {a1}$ și $a_{{{k}}} = {ak}$. Determină rația $r$.",
        rf"$r = {r}$",
        hint_latex=rf"$a_{{{k}}} = a_1 + ({k}-1)\,r$, de unde scoți $r$.",
        steps_latex=[rf"${ak} = {a1} + {k-1}\,r \Rightarrow r = {r}$"],
    )


def _d2_geom_sum(rng):
    b1 = rng.randint(1, 4)
    q = rng.randint(2, 3)
    n = rng.randint(4, 6)
    s = b1 * (q**n - 1) // (q - 1)
    return make(
        "progressions",
        rf"Calculează suma primilor ${n}$ termeni ai progresiei geometrice cu "
        rf"$b_1 = {b1}$ și rația $q = {q}$.",
        rf"$S_{{{n}}} = {s}$",
        hint_latex=r"$S_n = b_1\,\dfrac{q^n - 1}{q - 1}$.",
    )


TIERS = {
    1: [_d1_arith_term, _d1_arith_sum, _d1_geom_term],
    2: [_d2_find_ratio, _d2_geom_sum],
}


def generate(difficulty: int, rng: random.Random) -> dict:
    from ._utils import choose_subtype

    return choose_subtype(difficulty, rng, TIERS)
