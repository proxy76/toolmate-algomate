"""Matrices & determinants — tiered to the BAC.

D1 (Subiectul I/II) : addition, subtraction, scalar multiple (2x2).
D2 (Subiectul II)   : product A·B (2x2), determinant (2x2 and 3x3).
D3 (Subiectul III)  : A^2, inverse of an invertible 2x2, a 2x2 system (Cramer).

Matrices live mostly in Subiectul II on the real exam; the D3 tier covers the
multi-step items (inverse, systems) that appear in the harder problems.
"""
from __future__ import annotations

import random

import sympy as sp

from ._utils import latex, make, nonzero, pick


def _mat(rng, n, lo=-5, hi=5):
    return sp.Matrix(n, n, lambda i, j: nonzero(rng, lo, hi))


# ---------------------------------------------------------------- D1 ----------
def _d1_addsub(rng):
    A, B = _mat(rng, 2), _mat(rng, 2)
    op = pick(rng, ["+", "-"])
    C = A + B if op == "+" else A - B
    return make(
        "matrices",
        rf"Calculează $A {op} B$, unde $A = {latex(A)}$, $B = {latex(B)}$.",
        rf"${latex(C)}$",
        hint_latex=r"Operează element cu element.",
    )


def _d1_scalar(rng):
    A = _mat(rng, 2)
    k = nonzero(rng, -4, 4)
    return make(
        "matrices",
        rf"Calculează ${k} \cdot A$, unde $A = {latex(A)}$.",
        rf"${latex(k * A)}$",
        hint_latex=r"Înmulțește fiecare element cu scalarul.",
    )


# ---------------------------------------------------------------- D2 ----------
def _d2_product(rng):
    A, B = _mat(rng, 2), _mat(rng, 2)
    return make(
        "matrices",
        rf"Calculează $A \cdot B$, unde $A = {latex(A)}$, $B = {latex(B)}$.",
        rf"${latex(A * B)}$",
        hint_latex=r"$(AB)_{ij} = \sum_k A_{ik} B_{kj}$.",
    )


def _d2_det2(rng):
    A = _mat(rng, 2)
    return make(
        "matrices",
        rf"Calculează $\det(A)$ pentru $A = {latex(A)}$.",
        rf"$\det(A) = {latex(A.det())}$",
        hint_latex=r"$\det\begin{pmatrix}a&b\\c&d\end{pmatrix} = ad - bc$.",
    )


def _d2_det3(rng):
    A = _mat(rng, 3, -3, 3)
    return make(
        "matrices",
        rf"Calculează $\det(A)$ pentru $A = {latex(A)}$.",
        rf"$\det(A) = {latex(A.det())}$",
        hint_latex=r"Regula lui Sarrus sau dezvoltarea după o linie/coloană.",
    )


# ---------------------------------------------------------------- D3 ----------
def _d3_square(rng):
    A = _mat(rng, 2, -3, 3)
    return make(
        "matrices",
        rf"Calculează $A^2$ pentru $A = {latex(A)}$.",
        rf"${latex(A * A)}$",
        hint_latex=r"$A^2 = A\cdot A$ (înmulțire de matrice, nu pe elemente).",
    )


def _d3_inverse(rng):
    # Find a 2x2 with small integer entries and det = +-1 (clean integer inverse).
    for _ in range(80):
        A = _mat(rng, 2, -3, 3)
        if A.det() in (1, -1):
            return make(
                "matrices",
                rf"Determină inversa matricei $A = {latex(A)}$.",
                rf"$A^{{-1}} = {latex(A.inv())}$",
                hint_latex=r"$A^{-1} = \dfrac{1}{\det A}\begin{pmatrix}d&-b\\-c&a\end{pmatrix}$.",
                steps_latex=[
                    rf"$\det(A) = {latex(A.det())}$",
                    rf"$A^{{-1}} = {latex(A.inv())}$",
                ],
            )
    return _d3_square(rng)


def _d3_system(rng):
    x0, y0 = nonzero(rng, -4, 4), nonzero(rng, -4, 4)
    for _ in range(80):
        a, b, c, d = (nonzero(rng, -4, 4) for _ in range(4))
        if a * d - b * c != 0:
            break
    e = a * x0 + b * y0
    f = c * x0 + d * y0
    return make(
        "matrices",
        r"Rezolvă sistemul $\begin{cases}"
        rf"{a}x + {b}y = {e}\\ {c}x + {d}y = {f}"
        r"\end{cases}$",
        rf"$x = {x0},\ y = {y0}$",
        hint_latex=r"Regula lui Cramer: $x = \dfrac{\Delta_x}{\Delta}$, $y = \dfrac{\Delta_y}{\Delta}$.",
        steps_latex=[
            rf"$\Delta = {a*d - b*c}$",
            rf"$x = {x0},\ y = {y0}$",
        ],
    )


TIERS = {
    1: [_d1_addsub, _d1_scalar],
    2: [_d2_product, _d2_det2, _d2_det3],
    3: [_d3_square, _d3_inverse, _d3_system],
}


def generate(difficulty: int, rng: random.Random) -> dict:
    from ._utils import choose_subtype

    return choose_subtype(difficulty, rng, TIERS)
