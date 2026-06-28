"""Polynomials — tiered to the BAC.

D1 (Subiectul I)  : solve a quadratic with integer roots; evaluate P(a).
D2 (Subiectul II) : Horner / Bézout remainder, Viète on a quadratic.
D3 (Subiectul III): a cubic with integer roots — full root set and Viète sums.

Values are checked with ``sympy``.
"""
from __future__ import annotations

import random

import sympy as sp

from ._utils import latex, make, nonzero, pick, x


# ---------------------------------------------------------------- D1 ----------
def _d1_quadratic(rng):
    r1, r2 = nonzero(rng, -5, 5), nonzero(rng, -5, 5)
    poly = sp.expand((x - r1) * (x - r2))
    roots = sorted({int(r1), int(r2)})
    return make(
        "polynomials",
        rf"Rezolvă în $\mathbb{{R}}$: ${latex(poly)} = 0$.",
        rf"$x \in \{{{', '.join(map(str, roots))}\}}$",
        hint_latex=r"Factorizează sau aplică relațiile lui Viète.",
    )


def _d1_evaluate(rng):
    a, b, c, d = (nonzero(rng, -4, 4) for _ in range(4))
    P = a * x**3 + b * x**2 + c * x + d
    pt = rng.randint(-2, 2)
    val = int(P.subs(x, pt))
    return make(
        "polynomials",
        rf"Fie $P(x) = {latex(P)}$. Calculează $P({pt})$.",
        rf"$P({pt}) = {val}$",
        hint_latex=r"Înlocuiește direct valoarea în polinom.",
    )


# ---------------------------------------------------------------- D2 ----------
def _d2_horner(rng):
    a, b, c, d = (nonzero(rng, -4, 4) for _ in range(4))
    P = a * x**3 + b * x**2 + c * x + d
    root = nonzero(rng, -3, 3)
    val = int(P.subs(x, root))
    return make(
        "polynomials",
        rf"Determină restul împărțirii lui $P(x) = {latex(P)}$ la $x - ({root})$.",
        rf"$P({root}) = {val}$",
        hint_latex=r"Teorema lui Bézout: restul împărțirii la $x-a$ este $P(a)$.",
    )


def _d2_viete(rng):
    r1, r2 = nonzero(rng, -5, 5), nonzero(rng, -5, 5)
    s, p = r1 + r2, r1 * r2
    return make(
        "polynomials",
        rf"Fie $x_1, x_2$ rădăcinile ecuației $x^2 - ({s})x + ({p}) = 0$. "
        r"Calculează $x_1^2 + x_2^2$.",
        rf"${s*s - 2*p}$",
        hint_latex=r"$x_1^2 + x_2^2 = (x_1+x_2)^2 - 2x_1 x_2 = S^2 - 2P$.",
        steps_latex=[rf"$S = {s},\ P = {p}$", rf"$S^2 - 2P = {s*s} - {2*p} = {s*s - 2*p}$"],
    )


# ---------------------------------------------------------------- D3 ----------
def _d3_cubic_roots(rng):
    roots = rng.sample([-3, -2, -1, 1, 2, 3], 3)
    poly = sp.expand((x - roots[0]) * (x - roots[1]) * (x - roots[2]))
    rs = sorted(roots)
    return make(
        "polynomials",
        rf"Rezolvă în $\mathbb{{R}}$: ${latex(poly)} = 0$.",
        rf"$x \in \{{{', '.join(map(str, rs))}\}}$",
        hint_latex=r"Caută o rădăcină întreagă printre divizorii termenului liber, apoi "
        r"factorizează (Horner).",
    )


def _d3_viete_cubic(rng):
    roots = rng.sample([-3, -2, -1, 1, 2, 3], 3)
    poly = sp.expand((x - roots[0]) * (x - roots[1]) * (x - roots[2]))
    s1 = sum(roots)
    ssq = sum(r * r for r in roots)
    return make(
        "polynomials",
        rf"Fie $x_1, x_2, x_3$ rădăcinile ecuației ${latex(poly)} = 0$. "
        r"Calculează $x_1^2 + x_2^2 + x_3^2$.",
        rf"${ssq}$",
        hint_latex=r"$\sum x_i^2 = \left(\sum x_i\right)^2 - 2\sum_{i<j} x_i x_j = S_1^2 - 2S_2$.",
        steps_latex=[
            rf"$S_1 = x_1+x_2+x_3 = {s1}$",
            rf"$\sum x_i^2 = S_1^2 - 2S_2 = {ssq}$",
        ],
    )


TIERS = {
    1: [_d1_quadratic, _d1_evaluate],
    2: [_d2_horner, _d2_viete],
    3: [_d3_cubic_roots, _d3_viete_cubic],
}


def generate(difficulty: int, rng: random.Random) -> dict:
    from ._utils import choose_subtype

    return choose_subtype(difficulty, rng, TIERS)
