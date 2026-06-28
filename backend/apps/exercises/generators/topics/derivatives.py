"""Derivatives — reference class generator (spec §9.1).

This is the canonical example the spec calls out as the model for every other
topic. Difficulty selects the *technique*; the derivative is always computed and
verified with ``sympy.diff`` (spec §11). M3 is polynomials-only (§5.2, §13.1).
"""
from __future__ import annotations

import sympy as sp

from ..base import ExerciseGenerator

x = sp.Symbol("x", real=True)


def _latex(expr) -> str:
    return sp.latex(expr, mul_symbol="dot")


class DerivativesGenerator(ExerciseGenerator):
    TOPIC_CODE = "derivatives"
    SUPPORTED_PROFILES = ["M1", "M2", "M3"]

    # (key, description, builder(params, x)) per profile/difficulty (spec §9.1).
    FUNC_TEMPLATES = {
        "M1": {
            1: [
                ("poly", "polinom",
                 lambda p, x: p["a"] * x ** p["n"] + p["b"] * x ** p["m"] + p["c"]),
                ("exp_lin", "exp×liniar",
                 lambda p, x: sp.exp(p["a"] * x) + p["b"] * x),
                ("log_lin", "logaritm+pătratic",
                 lambda p, x: p["a"] * sp.log(x) + p["b"] * x ** 2),
            ],
            2: [
                ("prod", "produs",
                 lambda p, x: x ** p["n"] * sp.exp(p["a"] * x)),
                ("quot", "cât rațional",
                 lambda p, x: (p["a"] * x + p["b"]) / (x ** 2 + p["c"])),
                ("comp", "compusă exp",
                 lambda p, x: sp.exp(p["a"] * x ** 2 + p["b"] * x)),
                ("comp_log", "compusă log",
                 lambda p, x: sp.log(p["a"] * x ** 2 + p["b"] * x + p["c"])),
            ],
            3: [
                ("mixed1", "exp×polinom−liniar",
                 lambda p, x: (p["a"] * x ** 2 + p["b"] * x) * sp.exp(p["c"] * x) - p["d"] * x),
                ("rational", "rațională",
                 lambda p, x: (p["a"] * x ** 2 + p["b"]) / (x ** 2 + p["c"])),
            ],
        },
        "M2": {
            1: [
                ("poly", "polinom",
                 lambda p, x: p["a"] * x ** p["n"] + p["b"] * x + p["c"]),
                ("exp_lin", "exp×liniar",
                 lambda p, x: sp.exp(p["a"] * x) + p["b"] * x),
            ],
            2: [
                ("prod", "produs",
                 lambda p, x: x ** p["n"] * sp.exp(p["a"] * x)),
                ("quot", "cât",
                 lambda p, x: (p["a"] * x + p["b"]) / (x ** 2 + p["c"])),
            ],
            3: [
                ("comp", "compusă",
                 lambda p, x: sp.exp(p["a"] * x ** 2 + p["b"] * x)),
                ("rational", "rațională",
                 lambda p, x: x ** 2 / (x ** 2 + p["a"] * x + p["b"])),
            ],
        },
        "M3": {  # polynomials only — no exp/log (§5.2)
            1: [
                ("poly2", "polinom grad 2",
                 lambda p, x: p["a"] * x ** 2 + p["b"] * x + p["c"]),
                ("lin", "liniară",
                 lambda p, x: p["a"] * x + p["b"]),
            ],
            2: [
                ("poly3", "polinom grad 3",
                 lambda p, x: p["a"] * x ** 3 + p["b"] * x ** 2 + p["c"] * x + p["d"]),
            ],
            3: [
                ("poly4", "polinom grad 4",
                 lambda p, x: p["a"] * x ** 4 + p["b"] * x ** 2 + p["c"]),
            ],
        },
    }

    def _generate_params(self) -> dict:
        d = self.difficulty
        rng = self.rng
        templates = self.FUNC_TEMPLATES[self.profile][d]
        tmpl = templates[rng.randrange(len(templates))]
        if d == 1:
            coeffs = {
                "a": rng.choice([-3, -2, -1, 1, 2, 3]),
                "b": rng.choice([-4, -3, -2, -1, 1, 2, 3, 4]),
                "c": rng.choice([-5, -3, -1, 0, 1, 3, 5]),
                "n": rng.randint(2, 3), "m": rng.randint(1, 2),
                "d": rng.choice([1, 2, 3, 4]),
            }
        elif d == 2:
            coeffs = {
                "a": rng.choice([-3, -2, -1, 1, 2, 3]),
                "b": rng.choice([-5, -3, -1, 0, 1, 3, 5]),
                "c": rng.randint(1, 5), "d": rng.randint(1, 4),
                "n": rng.randint(2, 4), "m": rng.randint(1, 3),
            }
        else:
            coeffs = {
                "a": rng.choice([-2, -1, 1, 2]),
                "b": rng.choice([-3, -2, -1, 0, 1, 2, 3]),
                "c": rng.randint(1, 4), "d": rng.choice([-2, -1, 1, 2]),
                "n": rng.randint(2, 4), "m": rng.randint(1, 2),
            }
        return {"template": tmpl, "coeffs": coeffs}

    def _expr(self, params):
        return params["template"][2](params["coeffs"], x)

    def _compute_answer(self, params: dict):
        f = self._expr(params)
        f_prime = sp.simplify(sp.diff(f, x))
        return {"f": f, "f_prime": f_prime}

    def _validate(self, params: dict, answer) -> bool:
        fp = answer["f_prime"]
        if fp == 0 or fp in (sp.nan, sp.zoo, sp.oo, -sp.oo):
            return False
        if fp.free_symbols and fp.free_symbols != {x}:
            return False
        return len(sp.latex(fp)) < 200

    def _build_question(self, params: dict) -> str:
        f = self._expr(params)
        d = self.difficulty
        rng = self.rng
        dom = r"\mathbb{R}"
        if d == 1:
            fp = sp.diff(f, x)
            return (
                rf"Se consideră funcția $f : {dom} \to {dom}$, $f(x) = {_latex(f)}$. "
                rf"Arătați că $f'(x) = {_latex(sp.simplify(fp))}$, $x \in {dom}$."
            )
        if d == 2:
            req = rng.choice([
                "Determinați intervalele de monotonie ale funcției $f$.",
                "Determinați punctele de extrem ale funcției $f$.",
            ])
            return rf"Se consideră funcția $f : {dom} \to {dom}$, $f(x) = {_latex(f)}$. {req}"
        req = rng.choice([
            "Arătați că ecuația $f'(x) = 0$ are cel puțin o soluție reală.",
            "Determinați intervalele de monotonie ale funcției $f$.",
        ])
        return rf"Se consideră funcția $f : {dom} \to {dom}$, $f(x) = {_latex(f)}$. {req}"

    def _build_answer_latex(self, params: dict, answer) -> str:
        return rf"$f'(x) = {_latex(answer['f_prime'])}$"

    def _build_hint(self, params: dict) -> str:
        key = params["template"][0]
        hints = {
            "prod": r"Regula produsului: $(u\cdot v)' = u'v + uv'$.",
            "quot": r"Regula câtului: $\left(\dfrac{u}{v}\right)' = \dfrac{u'v - uv'}{v^2}$.",
            "comp": r"Regula lanțului: $(e^{u})' = e^{u}\cdot u'$.",
            "comp_log": r"Regula lanțului: $(\ln u)' = \dfrac{u'}{u}$.",
        }
        return hints.get(key, r"Derivați termen cu termen; derivata unei constante este $0$.")
