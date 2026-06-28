"""Powers and radicals — tiered to the BAC.

D1 (Subiectul I)  : a single power law (product / quotient / power of a power).
D2 (Subiectul II) : radical <-> rational exponent, negative exponents, two laws
                    chained in one expression.

Powers sit in Subiectul I/II, so there is no D3 variant; ``choose_subtype``
falls back to D2 when difficulty 3 is requested.
"""
from __future__ import annotations

import random

import sympy as sp

from ._utils import make, pick


# ---------------------------------------------------------------- D1 ----------
def _d1_product(rng):
    base = rng.randint(2, 9)
    e1, e2 = rng.randint(2, 5), rng.randint(2, 5)
    total = e1 + e2
    ans = rf"${base}^{{{total}}}$"
    if total <= 6:
        ans = rf"${base}^{{{total}}} = {base**total}$"
    return make(
        "powers",
        rf"Calculează ${base}^{{{e1}}} \cdot {base}^{{{e2}}}$.",
        ans,
        hint_latex=r"Aceeași bază: adună exponenții, $a^m \cdot a^n = a^{m+n}$.",
    )


def _d1_quotient(rng):
    base = rng.randint(2, 9)
    small = rng.randint(2, 4)
    big = small + rng.randint(2, 4)
    return make(
        "powers",
        rf"Simplifică $\dfrac{{{base}^{{{big}}}}}{{{base}^{{{small}}}}}$.",
        rf"${base}^{{{big - small}}}$",
        hint_latex=r"Aceeași bază la împărțire: scade exponenții, $\frac{a^m}{a^n}=a^{m-n}$.",
    )


def _d1_power_of_power(rng):
    base = rng.randint(2, 6)
    e1, e2 = rng.randint(2, 4), rng.randint(2, 4)
    return make(
        "powers",
        rf"Simplifică $\left({base}^{{{e1}}}\right)^{{{e2}}}$.",
        rf"${base}^{{{e1 * e2}}}$",
        hint_latex=r"$(a^m)^n = a^{m\cdot n}$.",
    )


# ---------------------------------------------------------------- D2 ----------
def _d2_radical(rng):
    base = rng.randint(2, 6)
    root = rng.randint(2, 3)
    e = rng.randint(2, 4)
    m = e * root
    return make(
        "powers",
        rf"Scrie ca putere a lui ${base}$: $\sqrt[{root}]{{{base}^{{{m}}}}}$.",
        rf"${base}^{{{e}}}$",
        hint_latex=r"$\sqrt[n]{a^m} = a^{m/n}$, apoi simplifică exponentul.",
    )


def _d2_negative(rng):
    base = rng.randint(2, 6)
    e = rng.randint(2, 4)
    return make(
        "powers",
        rf"Scrie ca fracție ${base}^{{-{e}}}$.",
        rf"$\dfrac{{1}}{{{base}^{{{e}}}}} = \dfrac{{1}}{{{base**e}}}$",
        hint_latex=r"Exponent negativ: $a^{-n} = \dfrac{1}{a^n}$.",
    )


def _d2_combined(rng):
    base = rng.randint(2, 5)
    a, b = rng.randint(2, 4), rng.randint(2, 4)
    c = a + b - 2  # leaves exponent 2
    return make(
        "powers",
        rf"Simplifică $\dfrac{{{base}^{{{a}}} \cdot {base}^{{{b}}}}}{{{base}^{{{c}}}}}$.",
        rf"${base}^{{2}} = {base**2}$",
        hint_latex=r"Adună exponenții de la numărător, apoi scade-l pe cel de la numitor.",
        steps_latex=[
            rf"$\dfrac{{{base}^{{{a}}}\cdot {base}^{{{b}}}}}{{{base}^{{{c}}}}} = {base}^{{{a}+{b}-{c}}} = {base}^{{2}}$",
        ],
    )


TIERS = {
    1: [_d1_product, _d1_quotient, _d1_power_of_power],
    2: [_d2_radical, _d2_negative, _d2_combined],
}


def generate(difficulty: int, rng: random.Random) -> dict:
    from ._utils import choose_subtype

    return choose_subtype(difficulty, rng, TIERS)


def generate_basic(difficulty: int, rng: random.Random) -> dict:
    """M3 — no radicals, no negative exponents: stay on the D1 laws."""
    from ._utils import choose_subtype

    return choose_subtype(difficulty, rng, {1: TIERS[1]})
