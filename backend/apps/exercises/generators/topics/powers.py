"""Powers and radicals — single-item class (spec §7.3). M1/M2/M3.

D1: a single power law (product / quotient / power of a power).
D2: radical ↔ rational exponent, negative exponents, two chained laws.
M3 stays on the D1 laws (no radicals / negative exponents, §5.2).
"""
from __future__ import annotations

from ..base import TieredExerciseGenerator
from .._utils import make


def _d1_product(rng):
    base = rng.randint(2, 9)
    e1, e2 = rng.randint(2, 5), rng.randint(2, 5)
    total = e1 + e2
    ans = rf"${base}^{{{total}}}$" if total > 6 else rf"${base}^{{{total}}} = {base**total}$"
    return make("powers", rf"Calculează ${base}^{{{e1}}} \cdot {base}^{{{e2}}}$.", ans,
                hint_latex=r"Aceeași bază: adună exponenții, $a^m \cdot a^n = a^{m+n}$.")


def _d1_quotient(rng):
    base = rng.randint(2, 9)
    small = rng.randint(2, 4)
    big = small + rng.randint(2, 4)
    return make("powers", rf"Simplifică $\dfrac{{{base}^{{{big}}}}}{{{base}^{{{small}}}}}$.",
                rf"${base}^{{{big - small}}}$",
                hint_latex=r"Aceeași bază la împărțire: scade exponenții, $\frac{a^m}{a^n}=a^{m-n}$.")


def _d1_power_of_power(rng):
    base = rng.randint(2, 6)
    e1, e2 = rng.randint(2, 4), rng.randint(2, 4)
    return make("powers", rf"Simplifică $\left({base}^{{{e1}}}\right)^{{{e2}}}$.",
                rf"${base}^{{{e1 * e2}}}$", hint_latex=r"$(a^m)^n = a^{m\cdot n}$.")


def _d2_radical(rng):
    base = rng.randint(2, 6)
    root = rng.randint(2, 3)
    e = rng.randint(2, 4)
    m = e * root
    return make("powers", rf"Scrie ca putere a lui ${base}$: $\sqrt[{root}]{{{base}^{{{m}}}}}$.",
                rf"${base}^{{{e}}}$",
                hint_latex=r"$\sqrt[n]{a^m} = a^{m/n}$, apoi simplifică exponentul.")


def _d2_negative(rng):
    base = rng.randint(2, 6)
    e = rng.randint(2, 4)
    return make("powers", rf"Scrie ca fracție ${base}^{{-{e}}}$.",
                rf"$\dfrac{{1}}{{{base}^{{{e}}}}} = \dfrac{{1}}{{{base**e}}}$",
                hint_latex=r"Exponent negativ: $a^{-n} = \dfrac{1}{a^n}$.")


def _d2_combined(rng):
    base = rng.randint(2, 5)
    a, b = rng.randint(2, 4), rng.randint(2, 4)
    c = a + b - 2
    return make("powers",
                rf"Simplifică $\dfrac{{{base}^{{{a}}} \cdot {base}^{{{b}}}}}{{{base}^{{{c}}}}}$.",
                rf"${base}^{{2}} = {base**2}$",
                hint_latex=r"Adună exponenții de la numărător, apoi scade-l pe cel de la numitor.",
                steps_latex=[rf"$\dfrac{{{base}^{{{a}}}\cdot {base}^{{{b}}}}}"
                             rf"{{{base}^{{{c}}}}} = {base}^{{{a}+{b}-{c}}} = {base}^{{2}}$"])


def _d2_radical_simplify(rng):
    # Arătați că √A − √B = (p−q)√m, with A=p²m, B=q²m (authentic pos-1 radical).
    m = rng.choice([2, 3, 5])
    p, q = sorted(rng.sample([2, 3, 4, 5], 2), reverse=True)
    A, B = p * p * m, q * q * m
    k = p - q
    kc = "" if k == 1 else str(k)
    return make("powers",
                rf"Arătați că $\sqrt{{{A}}} - \sqrt{{{B}}} = {kc}\sqrt{{{m}}}$.",
                rf"${kc}\sqrt{{{m}}}$",
                hint_latex=rf"Scoateți factorii de sub radical: $\sqrt{{{A}}} = {p}\sqrt{{{m}}}$ și "
                           rf"$\sqrt{{{B}}} = {q}\sqrt{{{m}}}$.",
                steps_latex=[rf"$\sqrt{{{A}}} - \sqrt{{{B}}} = {p}\sqrt{{{m}}} - {q}\sqrt{{{m}}} "
                             rf"= {kc}\sqrt{{{m}}}$"])


def _d2_radical_conjugate(rng):
    # Arătați că (√a + √b)(√a − √b) = a − b (an integer).
    a, b = rng.sample([2, 3, 5, 6, 7, 10], 2)
    val = a - b
    return make("powers",
                rf"Arătați că $\left(\sqrt{{{a}}} + \sqrt{{{b}}}\right)"
                rf"\left(\sqrt{{{a}}} - \sqrt{{{b}}}\right) = {val}$.",
                rf"${val}$",
                hint_latex=r"$(\sqrt{a} + \sqrt{b})(\sqrt{a} - \sqrt{b}) = a - b$.")


_TIERS = {
    1: [_d1_product, _d1_quotient, _d1_power_of_power],
    2: [_d2_radical, _d2_negative, _d2_combined,
        _d2_radical_simplify, _d2_radical_conjugate],
}


class PowersGenerator(TieredExerciseGenerator):
    TOPIC_CODE = "powers"
    SUPPORTED_PROFILES = ["M1", "M2", "M3"]

    def _tiers(self):
        return {1: _TIERS[1]} if self.profile == "M3" else _TIERS
