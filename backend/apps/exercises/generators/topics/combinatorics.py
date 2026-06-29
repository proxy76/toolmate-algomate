"""Combinatorics & probability — single-item class (spec §7.3). M1/M2/M3.

D1: direct evaluation of n!, C(n,k), A(n,k).
D2: a small combinatorial equation, classical probability.
D3: probability built from combinations. M3 = direct counting only (§5.2).
"""
from __future__ import annotations

from math import comb, factorial, gcd, perm

from ..base import TieredExerciseGenerator
from .._utils import make


def _d1_arrangements(rng):
    n, k = rng.randint(4, 8), rng.randint(2, 3)
    return make("combinatorics", rf"Calculează $A_{{{n}}}^{{{k}}}$.", rf"${perm(n, k)}$",
                hint_latex=r"$A_n^k = \dfrac{n!}{(n-k)!}$.")


def _d1_combinations(rng):
    n, k = rng.randint(4, 8), rng.randint(2, 3)
    return make("combinatorics", rf"Calculează $C_{{{n}}}^{{{k}}}$.", rf"${comb(n, k)}$",
                hint_latex=r"$C_n^k = \dfrac{n!}{k!\,(n-k)!}$.")


def _d1_factorial(rng):
    n = rng.randint(3, 6)
    return make("combinatorics", rf"Calculează ${n}!$.", rf"${factorial(n)}$",
                hint_latex=r"$n! = 1\cdot 2\cdot\ldots\cdot n$.")


def _d2_equation(rng):
    n = rng.randint(4, 8)
    val = comb(n, 2)
    return make("combinatorics", rf"Rezolvă în $\mathbb{{N}}$, $n \ge 2$: $C_n^2 = {val}$.",
                rf"$n = {n}$",
                hint_latex=r"$C_n^2 = \dfrac{n(n-1)}{2}$; rezolvă ecuația de gradul II.",
                steps_latex=[rf"$\dfrac{{n(n-1)}}{{2}} = {val} \Rightarrow "
                             rf"n(n-1) = {2*val} \Rightarrow n = {n}$"])


def _d2_probability(rng):
    total = rng.randint(8, 16)
    favorable = rng.randint(2, total - 2)
    g = gcd(favorable, total)
    return make("combinatorics",
                rf"O urnă conține ${total}$ bile, dintre care ${favorable}$ roșii. Calculează "
                r"probabilitatea ca, extrăgând o bilă, aceasta să fie roșie.",
                rf"$P = \dfrac{{{favorable // g}}}{{{total // g}}}$",
                hint_latex=r"$P = \dfrac{\text{cazuri favorabile}}{\text{cazuri posibile}}$.")


def _d3_probability_comb(rng):
    n = rng.randint(5, 8)
    red = rng.randint(2, n - 2)
    total_ways, fav_ways = comb(n, 2), comb(red, 2)
    g = gcd(fav_ways, total_ways)
    return make("combinatorics",
                rf"Dintr-o urnă cu ${n}$ bile, dintre care ${red}$ roșii, se extrag simultan "
                r"$2$ bile. Calculează probabilitatea ca ambele să fie roșii.",
                rf"$P = \dfrac{{{fav_ways // g}}}{{{total_ways // g}}}$",
                hint_latex=r"$P = \dfrac{C_{red}^2}{C_n^2}$ — alegeri favorabile/posibile, "
                           r"fără ordine.",
                steps_latex=[rf"cazuri posibile $C_{{{n}}}^2 = {total_ways}$, "
                             rf"favorabile $C_{{{red}}}^2 = {fav_ways}$",
                             rf"$P = \dfrac{{{fav_ways}}}{{{total_ways}}} = "
                             rf"\dfrac{{{fav_ways // g}}}{{{total_ways // g}}}$"])


_TIERS = {
    1: [_d1_arrangements, _d1_combinations, _d1_factorial],
    2: [_d2_equation, _d2_probability],
    3: [_d3_probability_comb],
}


class CombinatoricsGenerator(TieredExerciseGenerator):
    TOPIC_CODE = "combinatorics"
    SUPPORTED_PROFILES = ["M1", "M2", "M3"]

    def _tiers(self):
        return {1: _TIERS[1]} if self.profile == "M3" else _TIERS
