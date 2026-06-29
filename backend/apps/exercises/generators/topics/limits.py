"""Limits of functions — single-item class (spec §7.3). M1/M2.

D1: limit by direct substitution.
D2: 0/0 by factor-and-cancel, limit at infinity (leading terms).
D3: fundamental limits (sin u / u, (e^u−1)/u), the number e.
All values confirmed with sympy.limit.
"""
from __future__ import annotations

import sympy as sp

from ..base import TieredExerciseGenerator
from .._utils import latex, make, nonzero, small_coef, x


def _d1_substitution(rng):
    a, b, c = nonzero(rng, 1, 3), small_coef(rng), small_coef(rng)
    x0 = rng.randint(-2, 2)
    expr = a * x**2 + b * x + c
    val = sp.limit(expr, x, x0)
    return make("limits", rf"Calculează $\displaystyle\lim_{{x \to {x0}}} \left({latex(expr)}\right)$.",
                rf"${latex(val)}$",
                hint_latex=r"Funcția e continuă: înlocuiește direct $x$ cu valoarea limitei.")


def _d2_factor(rng):
    a = rng.randint(2, 6)
    expr = (x**2 - a * a) / (x - a)
    val = sp.limit(expr, x, a)
    return make("limits", rf"Calculează $\displaystyle\lim_{{x \to {a}}} {latex(expr)}$.",
                rf"${latex(val)}$",
                hint_latex=r"Caz $\frac{0}{0}$: factorizează $x^2 - a^2 = (x-a)(x+a)$ și simplifică.",
                steps_latex=[rf"$\dfrac{{x^2 - {a*a}}}{{x - {a}}} = "
                             rf"\dfrac{{(x-{a})(x+{a})}}{{x-{a}}} = x + {a}$",
                             rf"$\lim_{{x\to {a}}} (x + {a}) = {latex(val)}$"])


def _d2_infinity(rng):
    a, b = nonzero(rng, 2, 5), nonzero(rng, 2, 5)
    expr = (a * x**2 + b * x + 1) / (b * x**2 + 1)
    val = sp.limit(expr, x, sp.oo)
    return make("limits", rf"Calculează $\displaystyle\lim_{{x \to \infty}} {latex(expr)}$.",
                rf"${latex(val)}$",
                hint_latex=r"Raportul coeficienților termenilor de grad maxim (împarte la $x^2$).")


def _d3_sin(rng):
    c = rng.randint(2, 5)
    expr = sp.sin(c * x) / x
    val = sp.limit(expr, x, 0)
    return make("limits", rf"Calculează $\displaystyle\lim_{{x \to 0}} {latex(expr)}$.",
                rf"${latex(val)}$",
                hint_latex=r"Limita fundamentală $\lim_{u \to 0} \dfrac{\sin u}{u} = 1$.",
                steps_latex=[rf"$\dfrac{{\sin({c}x)}}{{x}} = {c}\cdot\dfrac{{\sin({c}x)}}{{{c}x}}$",
                             rf"$\to {c}\cdot 1 = {latex(val)}$"])


def _d3_exp(rng):
    c = rng.randint(2, 5)
    expr = (sp.exp(c * x) - 1) / x
    val = sp.limit(expr, x, 0)
    return make("limits", rf"Calculează $\displaystyle\lim_{{x \to 0}} {latex(expr)}$.",
                rf"${latex(val)}$",
                hint_latex=r"Limita fundamentală $\lim_{u \to 0} \dfrac{e^u - 1}{u} = 1$.")


def _d3_e(rng):
    a = rng.randint(2, 5)
    expr = (1 + a / x) ** x
    val = sp.limit(expr, x, sp.oo)
    return make("limits",
                rf"Calculează $\displaystyle\lim_{{x \to \infty}} "
                rf"\left(1 + \dfrac{{{a}}}{{x}}\right)^{{x}}$.", rf"${latex(val)}$",
                hint_latex=r"Limita lui $e$: $\lim_{x\to\infty}\left(1+\frac{a}{x}\right)^x = e^{a}$.")


_TIERS = {
    1: [_d1_substitution],
    2: [_d2_factor, _d2_infinity],
    3: [_d3_sin, _d3_exp, _d3_e],
}


class LimitsGenerator(TieredExerciseGenerator):
    TOPIC_CODE = "limits"
    SUPPORTED_PROFILES = ["M1", "M2"]

    def _tiers(self):
        return _TIERS
