"""Logarithms — tiered to the BAC.

D1 (Subiectul I)  : definition and direct evaluation ($\\log_a a^k$, $\\log_a x = k$).
D2 (Subiectul II) : the operational properties (product / quotient / power).
D3 (Subiectul III): a logarithmic equation (quadratic-in-log), worked in steps.

Difficulty now genuinely drives the problem — the old version ignored it and
repeated a single hard-coded equation.
"""
from __future__ import annotations

import random

import sympy as sp

from ._utils import make, pick


# ---------------------------------------------------------------- D1 ----------
def _d1_identity(rng):
    base = pick(rng, [2, 3, 5, 10])
    k = rng.randint(2, 6)
    return make(
        "logarithms",
        rf"Calculează $\log_{{{base}}} {base}^{{{k}}}$.",
        rf"${k}$",
        hint_latex=r"$\log_a a^k = k$.",
    )


def _d1_evaluate(rng):
    base = pick(rng, [2, 3, 5])
    k = rng.randint(2, 4)
    val = base**k
    return make(
        "logarithms",
        rf"Calculează $\log_{{{base}}} {val}$.",
        rf"${k}$",
        hint_latex=rf"Scrie ${val}$ ca putere a lui ${base}$.",
    )


def _d1_equation(rng):
    base = pick(rng, [2, 3, 5])
    k = rng.randint(2, 4)
    return make(
        "logarithms",
        rf"Rezolvă în $\mathbb{{R}}$: $\log_{{{base}}} x = {k}$.",
        rf"$x = {base**k}$",
        hint_latex=r"Definiția: $\log_a x = y \iff x = a^y$.",
    )


# ---------------------------------------------------------------- D2 ----------
def _d2_sum(rng):
    base = pick(rng, [2, 3, 5, 10])
    a, b = rng.randint(2, 6), rng.randint(2, 6)
    return make(
        "logarithms",
        rf"Calculează $\log_{{{base}}} {a} + \log_{{{base}}} {b} - \log_{{{base}}} {a*b}$.",
        r"$0$",
        hint_latex=r"$\log_a M + \log_a N - \log_a P = \log_a \dfrac{MN}{P}$.",
        steps_latex=[
            rf"$= \log_{{{base}}} \dfrac{{{a}\cdot {b}}}{{{a*b}}} = \log_{{{base}}} 1 = 0$",
        ],
    )


def _d2_power_property(rng):
    base = pick(rng, [2, 3, 5])
    k = rng.randint(2, 4)
    return make(
        "logarithms",
        rf"Calculează $\log_{{{base}}} {base}^{{{k}}} + \log_{{{base}}} {base}$.",
        rf"${k + 1}$",
        hint_latex=r"$\log_a a^k = k$ și $\log_a a = 1$.",
    )


def _d2_collapse(rng):
    base = pick(rng, [2, 3])
    a = rng.randint(2, 4)
    return make(
        "logarithms",
        rf"Scrie ca un singur logaritm: $2\log_{{{base}}} {a} + \log_{{{base}}} {a}$.",
        rf"$\log_{{{base}}} {a**3}$",
        hint_latex=r"$k\log_a M = \log_a M^k$, apoi adună logaritmii.",
    )


# ---------------------------------------------------------------- D3 ----------
def _d3_quadratic_in_log(rng):
    base = pick(rng, [2, 3])
    r1, r2 = sorted(rng.sample([1, 2, 3, 4], 2))
    s = r1 + r2
    p = r1 * r2
    sols = sorted([base**r1, base**r2])
    return make(
        "logarithms",
        rf"Rezolvă în $\mathbb{{R}}$: $\left(\log_{{{base}}} x\right)^2 - {s}\log_{{{base}}} x + {p} = 0$.",
        rf"$x \in \{{{sols[0]}, {sols[1]}\}}$",
        hint_latex=r"Notează $t = \log_a x$ și rezolvă ecuația de gradul II în $t$.",
        steps_latex=[
            rf"$t = \log_{{{base}}} x:\quad t^2 - {s}t + {p} = 0$",
            rf"$t \in \{{{r1}, {r2}\}}$",
            rf"$\log_{{{base}}} x = {r1} \Rightarrow x = {base**r1}$; "
            rf"$\log_{{{base}}} x = {r2} \Rightarrow x = {base**r2}$",
        ],
    )


def _d3_exponential(rng):
    base = pick(rng, [2, 3])
    k1, k2 = sorted(rng.sample([0, 1, 2], 2))
    t1, t2 = base**k1, base**k2
    s = t1 + t2
    p = t1 * t2
    return make(
        "logarithms",
        rf"Rezolvă în $\mathbb{{R}}$: ${base}^{{2x}} - {s}\cdot {base}^{{x}} + {p} = 0$.",
        rf"$x \in \{{{k1}, {k2}\}}$",
        hint_latex=rf"Notează $t = {base}^x > 0$ și rezolvă ecuația de gradul II în $t$.",
        steps_latex=[
            rf"$t = {base}^x:\quad t^2 - {s}t + {p} = 0 \Rightarrow t \in \{{{t1}, {t2}\}}$",
            rf"${base}^x = {t1} \Rightarrow x = {k1}$; ${base}^x = {t2} \Rightarrow x = {k2}$",
        ],
    )


TIERS = {
    1: [_d1_identity, _d1_evaluate, _d1_equation],
    2: [_d2_sum, _d2_power_property, _d2_collapse],
    3: [_d3_quadratic_in_log, _d3_exponential],
}


def generate(difficulty: int, rng: random.Random) -> dict:
    from ._utils import choose_subtype

    return choose_subtype(difficulty, rng, TIERS)
