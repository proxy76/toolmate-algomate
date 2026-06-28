"""Integrals — tiered to the BAC.

D1 (Subiectul I)   : direct table primitives (power, polynomial, e^x).
D2 (Subiectul II)  : linearity / substitution, a clean definite integral.
D3 (Subiectul III) : applications — area under a curve, integration by parts,
                     volume of a body of revolution.

Primitives and definite values are computed by ``sympy``.
"""
from __future__ import annotations

import random

import sympy as sp

from ._utils import latex, make, nonzero, pick, small_coef, small_pos, x


# ---------------------------------------------------------------- D1 ----------
def _d1_power(rng):
    a = nonzero(rng, 1, 5)
    e = small_pos(rng, 2, 5)
    expr = a * x**e
    prim = sp.integrate(expr, x)
    return make(
        "integrals",
        rf"Calculează $\displaystyle\int {latex(expr)} \, dx$.",
        rf"${latex(prim)} + \mathcal{{C}}$",
        hint_latex=r"$\int x^n \, dx = \dfrac{x^{n+1}}{n+1} + \mathcal{C}$.",
    )


def _d1_polynomial(rng):
    a = nonzero(rng, 1, 4)
    b = small_coef(rng)
    c = small_coef(rng)
    expr = a * x**2 + b * x + c
    prim = sp.integrate(expr, x)
    return make(
        "integrals",
        rf"Calculează $\displaystyle\int \left({latex(expr)}\right) dx$.",
        rf"${latex(prim)} + \mathcal{{C}}$",
        hint_latex=r"Integrează termen cu termen.",
    )


def _d1_exp(rng):
    a = small_coef(rng)
    expr = sp.exp(x) + a
    prim = sp.integrate(expr, x)
    return make(
        "integrals",
        rf"Calculează $\displaystyle\int \left({latex(expr)}\right) dx$.",
        rf"${latex(prim)} + \mathcal{{C}}$",
        hint_latex=r"$\int e^x \, dx = e^x + \mathcal{C}$.",
    )


# ---------------------------------------------------------------- D2 ----------
def _d2_exp_linear(rng):
    a = nonzero(rng, 2, 4)
    expr = sp.exp(a * x)
    prim = sp.integrate(expr, x)
    return make(
        "integrals",
        rf"Calculează $\displaystyle\int {latex(expr)} \, dx$.",
        rf"${latex(prim)} + \mathcal{{C}}$",
        hint_latex=r"$\int e^{ax} \, dx = \dfrac{1}{a} e^{ax} + \mathcal{C}$.",
    )


def _d2_reciprocal(rng):
    a = nonzero(rng, 1, 5)
    return make(
        "integrals",
        rf"Calculează $\displaystyle\int \dfrac{{1}}{{x + {a}}} \, dx$, $x > {-a}$.",
        rf"$\ln(x + {a}) + \mathcal{{C}}$",
        hint_latex=r"$\int \dfrac{1}{x+a} \, dx = \ln|x+a| + \mathcal{C}$.",
    )


def _d2_substitution(rng):
    a = nonzero(rng, 2, 4)
    b = small_coef(rng)
    e = small_pos(rng, 2, 4)
    expr = (a * x + b) ** e
    prim = sp.integrate(expr, x)
    return make(
        "integrals",
        rf"Calculează $\displaystyle\int {latex(expr)} \, dx$.",
        rf"${latex(sp.expand(prim))} + \mathcal{{C}}$",
        hint_latex=r"Substituție $u = ax+b$, $du = a\,dx$.",
    )


def _d2_definite(rng):
    a = nonzero(rng, 1, 3)
    b = small_coef(rng)
    lo = rng.randint(0, 1)
    hi = lo + rng.randint(1, 3)
    expr = a * x**2 + b
    val = sp.integrate(expr, (x, lo, hi))
    F = sp.integrate(expr, x)
    return make(
        "integrals",
        rf"Calculează $\displaystyle\int_{{{lo}}}^{{{hi}}} \left({latex(expr)}\right) dx$.",
        rf"${latex(val)}$",
        hint_latex=r"Leibniz–Newton: $\int_a^b f = F(b) - F(a)$.",
        steps_latex=[
            rf"$F(x) = {latex(F)}$",
            rf"$F({hi}) - F({lo}) = {latex(val)}$",
        ],
    )


# ---------------------------------------------------------------- D3 ----------
def _d3_area(rng):
    a = nonzero(rng, 1, 3)
    b = rng.randint(0, 2)
    f = a * x**2 + b  # f > 0 on [0, t]
    t = rng.randint(1, 3)
    area = sp.integrate(f, (x, 0, t))
    return make(
        "integrals",
        rf"Se consideră $f:[0,{t}]\to\mathbb{{R}}$, $f(x) = {latex(f)}$. "
        rf"Calculează aria suprafeței plane delimitate de graficul lui $f$, "
        rf"axa $Ox$ și dreptele $x = 0$, $x = {t}$.",
        rf"$\mathcal{{A}} = {latex(area)}$",
        hint_latex=r"$\mathcal{A} = \displaystyle\int_a^b f(x)\,dx$ (deoarece $f \ge 0$).",
        steps_latex=[
            rf"$\mathcal{{A}} = \int_0^{t} \left({latex(f)}\right) dx$",
            rf"$\mathcal{{A}} = {latex(area)}$",
        ],
    )


def _d3_by_parts(rng):
    kind = pick(rng, ["exp", "sin", "cos"])
    if kind == "exp":
        expr = x * sp.exp(x)
        hint = r"$u = x$, $dv = e^x dx$."
    elif kind == "sin":
        expr = x * sp.sin(x)
        hint = r"$u = x$, $dv = \sin x\,dx$."
    else:
        expr = x * sp.cos(x)
        hint = r"$u = x$, $dv = \cos x\,dx$."
    prim = sp.integrate(expr, x)
    return make(
        "integrals",
        rf"Calculează $\displaystyle\int {latex(expr)} \, dx$.",
        rf"${latex(prim)} + \mathcal{{C}}$",
        hint_latex=r"Integrare prin părți: $\int u\,dv = uv - \int v\,du$. " + hint,
    )


def _d3_volume(rng):
    t = rng.randint(1, 3)
    f = x  # body of revolution of the line y = x
    vol = sp.integrate(sp.pi * f**2, (x, 0, t))
    return make(
        "integrals",
        rf"Se consideră $f:[0,{t}]\to\mathbb{{R}}$, $f(x) = x$. Calculează volumul "
        rf"corpului obținut prin rotația graficului lui $f$ în jurul axei $Ox$.",
        rf"$V = {latex(vol)}$",
        hint_latex=r"$V = \pi\displaystyle\int_a^b f^2(x)\,dx$.",
        steps_latex=[
            rf"$V = \pi\int_0^{t} x^2 \, dx$",
            rf"$V = {latex(vol)}$",
        ],
    )


TIERS = {
    1: [_d1_power, _d1_polynomial, _d1_exp],
    2: [_d2_exp_linear, _d2_reciprocal, _d2_substitution, _d2_definite],
    3: [_d3_area, _d3_by_parts, _d3_volume],
}


def generate(difficulty: int, rng: random.Random) -> dict:
    from ._utils import choose_subtype

    return choose_subtype(difficulty, rng, TIERS)
