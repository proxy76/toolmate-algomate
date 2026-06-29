"""Trigonometry — single-item class (spec §7.3). M1/M2/M3.

D1: remarkable-angle values. D2: Pythagorean identity, simple equation.
D3: an equation on [0, 2π). M3 = remarkable values only (§5.2).
"""
from __future__ import annotations

import sympy as sp

from ..base import TieredExerciseGenerator
from .._utils import latex, make, pick

_SPECIAL = [
    (sp.pi / 6, r"\frac{\pi}{6}"), (sp.pi / 4, r"\frac{\pi}{4}"),
    (sp.pi / 3, r"\frac{\pi}{3}"), (sp.pi / 2, r"\frac{\pi}{2}"),
    (2 * sp.pi / 3, r"\frac{2\pi}{3}"), (3 * sp.pi / 4, r"\frac{3\pi}{4}"),
    (5 * sp.pi / 6, r"\frac{5\pi}{6}"), (sp.pi, r"\pi"),
]


def _d1_value(rng):
    angle, angle_tex = pick(rng, _SPECIAL)
    fn_name, fn = pick(rng, [("sin", sp.sin), ("cos", sp.cos)])
    val = sp.simplify(fn(angle))
    return make("trigonometry", rf"Calculează $\{fn_name}\left({angle_tex}\right)$.",
                rf"${latex(val)}$", hint_latex=r"Folosește tabelul valorilor remarcabile.")


def _d2_pythagorean(rng):
    a, b, c = pick(rng, [(3, 4, 5), (5, 12, 13), (8, 15, 17)])
    return make("trigonometry",
                rf"Știind că $\sin x = \dfrac{{{a}}}{{{c}}}$ și "
                rf"$x \in \left(0, \dfrac{{\pi}}{{2}}\right)$, calculează $\cos x$.",
                rf"$\cos x = \dfrac{{{b}}}{{{c}}}$",
                hint_latex=r"$\sin^2 x + \cos^2 x = 1$ și "
                           r"$\cos x > 0$ pe $\left(0,\frac{\pi}{2}\right)$.",
                steps_latex=[rf"$\cos^2 x = 1 - \dfrac{{{a*a}}}{{{c*c}}} = \dfrac{{{b*b}}}{{{c*c}}}$",
                             rf"$\cos x = \dfrac{{{b}}}{{{c}}}$"])


def _d2_simple_equation(rng):
    eq, sols = pick(rng, [
        (r"2\sin x = 1", r"\frac{\pi}{6},\ \frac{5\pi}{6}"),
        (r"2\cos x = 1", r"\frac{\pi}{3},\ \frac{5\pi}{3}"),
        (r"\sqrt2\,\sin x = 1", r"\frac{\pi}{4},\ \frac{3\pi}{4}"),
        (r"2\cos x = -1", r"\frac{2\pi}{3},\ \frac{4\pi}{3}"),
    ])
    return make("trigonometry", rf"Rezolvă în $[0, 2\pi)$: ${eq}$.",
                rf"$x \in \left\{{{sols}\right\}}$",
                hint_latex=r"Adu la forma $\sin x = a$ / $\cos x = a$ și "
                           r"identifică unghiurile din cerc.")


def _d3_double_angle(rng):
    return make("trigonometry", r"Rezolvă în $[0, 2\pi)$: $\sin 2x = \sin x$.",
                r"$x \in \left\{0,\ \pi,\ \dfrac{\pi}{3},\ \dfrac{5\pi}{3}\right\}$",
                hint_latex=r"$\sin 2x = 2\sin x\cos x$; dă factor comun $\sin x$.",
                steps_latex=[
                    r"$2\sin x\cos x - \sin x = 0 \Rightarrow \sin x\,(2\cos x - 1) = 0$",
                    r"$\sin x = 0 \Rightarrow x\in\{0,\pi\}$; "
                    r"$\cos x = \tfrac12 \Rightarrow x\in\{\tfrac{\pi}{3},\tfrac{5\pi}{3}\}$"])


_TIERS = {1: [_d1_value], 2: [_d2_pythagorean, _d2_simple_equation], 3: [_d3_double_angle]}


class TrigonometryGenerator(TieredExerciseGenerator):
    TOPIC_CODE = "trigonometry"
    SUPPORTED_PROFILES = ["M1", "M2", "M3"]

    def _tiers(self):
        return {1: _TIERS[1]} if self.profile == "M3" else _TIERS
