"""Complex numbers — tiered to the BAC.

D1 (Subiectul I)  : sum / difference, modulus, conjugate (algebraic form).
D2 (Subiectul II) : product, square, quotient to algebraic form, powers of i.
D3 (Subiectul III): De Moivre powers of (1+i), solving z^2 = a+bi.   [M1 only]

M2 uses ``generate_algebraic`` — algebraic form only, no trigonometric form
(matches the reduced M_st-nat syllabus).
"""
from __future__ import annotations

import random

import sympy as sp

from ._utils import latex, make, nonzero, pick


def _z(a, b):
    return sp.Integer(a) + sp.Integer(b) * sp.I


# ---------------------------------------------------------------- D1 ----------
def _d1_addsub(rng):
    a, b, c, d = (nonzero(rng, -7, 7) for _ in range(4))
    op = pick(rng, ["+", "-"])
    z1, z2 = _z(a, b), _z(c, d)
    ans = sp.simplify(z1 + z2 if op == "+" else z1 - z2)
    return make(
        "complex",
        rf"Calculează $({latex(z1)}) {op} ({latex(z2)})$.",
        rf"${latex(ans)}$",
        hint_latex=r"Adună (scade) separat partea reală și partea imaginară.",
    )


def _d1_modulus(rng):
    a, b = nonzero(rng, -7, 7), nonzero(rng, -7, 7)
    z = _z(a, b)
    mod = sp.sqrt(a * a + b * b)
    return make(
        "complex",
        rf"Calculează modulul $|z|$ pentru $z = {latex(z)}$.",
        rf"$|z| = {latex(sp.simplify(mod))}$",
        hint_latex=r"$|a + bi| = \sqrt{a^2 + b^2}$.",
    )


def _d1_conjugate(rng):
    a, b = nonzero(rng, -7, 7), nonzero(rng, -7, 7)
    z = _z(a, b)
    return make(
        "complex",
        rf"Determină conjugatul $\bar z$ pentru $z = {latex(z)}$.",
        rf"$\bar z = {latex(sp.conjugate(z))}$",
        hint_latex=r"$\overline{a + bi} = a - bi$.",
    )


# ---------------------------------------------------------------- D2 ----------
def _d2_product(rng):
    a, b, c, d = (nonzero(rng, -5, 5) for _ in range(4))
    z1, z2 = _z(a, b), _z(c, d)
    ans = sp.expand(z1 * z2)
    return make(
        "complex",
        rf"Calculează $({latex(z1)})({latex(z2)})$.",
        rf"${latex(ans)}$",
        hint_latex=r"Desfă parantezele și folosește $i^2 = -1$.",
    )


def _d2_square(rng):
    a, b = nonzero(rng, -5, 5), nonzero(rng, -5, 5)
    z = _z(a, b)
    return make(
        "complex",
        rf"Calculează $z^2$ pentru $z = {latex(z)}$.",
        rf"${latex(sp.expand(z**2))}$",
        hint_latex=r"$(a+bi)^2 = a^2 - b^2 + 2ab\,i$.",
    )


def _d2_quotient(rng):
    a, b, c, d = (nonzero(rng, -5, 5) for _ in range(4))
    z1, z2 = _z(a, b), _z(c, d)
    ans = sp.simplify(z1 / z2)
    return make(
        "complex",
        rf"Adu la forma algebrică $\dfrac{{{latex(z1)}}}{{{latex(z2)}}}$.",
        rf"${latex(ans)}$",
        hint_latex=r"Amplifică cu conjugatul numitorului: $\frac{z_1}{z_2}=\frac{z_1\bar z_2}{|z_2|^2}$.",
    )


def _d2_power_i(rng):
    nval = rng.randint(5, 30)
    return make(
        "complex",
        rf"Calculează $i^{{{nval}}}$.",
        rf"${latex(sp.I**nval)}$",
        hint_latex=r"Puterile lui $i$ se repetă cu perioada 4: $i^n = i^{n \bmod 4}$.",
    )


# ---------------------------------------------------------------- D3 ----------
def _d3_de_moivre(rng):
    nval = pick(rng, [2, 4, 6, 8])
    ans = sp.expand((1 + sp.I) ** nval)
    return make(
        "complex",
        rf"Calculează $(1 + i)^{{{nval}}}$.",
        rf"${latex(ans)}$",
        hint_latex=r"$1+i = \sqrt2\left(\cos\frac{\pi}{4} + i\sin\frac{\pi}{4}\right)$, apoi De Moivre.",
        steps_latex=[
            r"$(1+i)^2 = 2i$",
            rf"$(1+i)^{{{nval}}} = (2i)^{{{nval//2}}} = {latex(ans)}$",
        ],
    )


def _d3_solve_square(rng):
    p, q = nonzero(rng, 1, 4), nonzero(rng, 1, 4)
    z0 = _z(p, q)
    target = sp.expand(z0**2)
    return make(
        "complex",
        rf"Rezolvă în $\mathbb{{C}}$: $z^2 = {latex(target)}$.",
        rf"$z \in \{{{latex(z0)},\ {latex(-z0)}\}}$",
        hint_latex=r"Caută $z = x + yi$ cu $x,y\in\mathbb{R}$ și identifică părțile reală și imaginară.",
    )


TIERS_FULL = {
    1: [_d1_addsub, _d1_modulus, _d1_conjugate],
    2: [_d2_product, _d2_square, _d2_quotient, _d2_power_i],
    3: [_d3_de_moivre, _d3_solve_square],
}

TIERS_ALGEBRAIC = {1: TIERS_FULL[1], 2: TIERS_FULL[2]}


def generate(difficulty: int, rng: random.Random) -> dict:
    from ._utils import choose_subtype

    return choose_subtype(difficulty, rng, TIERS_FULL)


def generate_algebraic(difficulty: int, rng: random.Random) -> dict:
    """M2 — algebraic form only (no trigonometric form / De Moivre)."""
    from ._utils import choose_subtype

    return choose_subtype(difficulty, rng, TIERS_ALGEBRAIC)
