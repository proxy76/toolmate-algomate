"""Derivatives — reference class generator (spec §9.1).

This is the canonical example the spec calls out as the model for every other
topic. Difficulty selects the *technique*; the derivative is always computed and
verified with ``sympy.diff`` (spec §11). M3 is polynomials-only (§5.2, §13.1).
"""
from __future__ import annotations

import sympy as sp

from ..base import ExerciseGenerator, ProblemGenerator

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


class DerivativesStudyProblem(ProblemGenerator):
    """Subiectul III, problema 1 — studiu de funcție (spec §3.3, §10.4). M1/M2.

    One shared ``f`` with linked a/b/c:
      cubic mode      — (a) f'(x), (b) strict monotonicity, (c) f(x)=0 has exactly
                        one real solution (guaranteed by f'>0 + limits ±∞).
      rational mode   — (a) f'(x), (b) oblique asymptote, (c) vertical asymptote.
    All facts are verified with sympy.
    """

    TOPIC_CODE = "derivatives"
    SUPPORTED_PROFILES = ["M1", "M2"]

    def _generate_context(self) -> dict:
        rng = self.rng
        if rng.choice(["cubic", "rational"]) == "cubic":
            a = rng.choice([1, 2, 3, 4, 5])      # a>0 ⇒ f'(x)=3x²+a>0 ⇒ strictly ↑
            b = rng.choice([-3, -2, -1, 1, 2, 3])
            f = x ** 3 + a * x + b
            return {"mode": "cubic", "f": f, "a": a, "b": b, "fp": sp.diff(f, x)}
        c = rng.choice([1, 2, 3, -1, -2])
        b = rng.choice([-3, -2, -1, 1, 2, 3])
        if c * c + b == 0:
            b += 1
        f = (x ** 2 + b) / (x + c)
        return {"mode": "rational", "f": sp.together(f), "b": b, "c": c,
                "fp": sp.simplify(sp.diff(f, x))}

    def _validate_context(self, ctx) -> bool:
        if ctx["mode"] == "cubic":
            return ctx["a"] > 0 and len(sp.real_roots(sp.Poly(ctx["f"], x))) == 1
        return ctx["c"] ** 2 + ctx["b"] != 0

    def _build_statement(self, ctx) -> str:
        f = ctx["f"]
        if ctx["mode"] == "cubic":
            return rf"Se consideră funcția $f:\mathbb{{R}}\to\mathbb{{R}}$, $f(x) = {_latex(f)}$."
        c = ctx["c"]
        return (rf"Se consideră funcția $f:\mathbb{{R}}\setminus\{{{-c}\}}\to\mathbb{{R}}$, "
                rf"$f(x) = {_latex(f)}$.")

    def _build_sub_item(self, ctx, label, difficulty) -> dict:
        idx = ("a", "b", "c").index(label)
        if ctx["mode"] == "cubic":
            return (self._cub_a, self._cub_b, self._cub_c)[idx](ctx)
        return (self._rat_a, self._rat_b, self._rat_c)[idx](ctx)

    # cubic mode ------------------------------------------------------------
    def _cub_a(self, ctx):
        fp = ctx["fp"]
        assert sp.simplify(sp.diff(ctx["f"], x) - fp) == 0
        return {"question_latex": rf"Arătați că $f'(x) = {_latex(fp)}$, $x \in \mathbb{{R}}$.",
                "answer_latex": rf"$f'(x) = {_latex(fp)}$",
                "hint_latex": r"Derivați termen cu termen."}

    def _cub_b(self, ctx):
        return {"question_latex": r"Arătați că funcția $f$ este strict crescătoare pe "
                                  r"$\mathbb{R}$.",
                "answer_latex": rf"$f'(x) = {_latex(ctx['fp'])} > 0$, deci $f$ este strict "
                                r"crescătoare pe $\mathbb{R}$",
                "hint_latex": r"Studiați semnul derivatei $f'$."}

    def _cub_c(self, ctx):
        return {"question_latex": r"Arătați că ecuația $f(x) = 0$ are exact o soluție reală.",
                "answer_latex": r"$f$ strict crescătoare și continuă, cu "
                                r"$\lim_{x\to-\infty}f=-\infty$, $\lim_{x\to+\infty}f=+\infty$ "
                                r"$\Rightarrow$ exact o soluție reală",
                "hint_latex": r"O funcție continuă și strict monotonă cu limite de semne "
                              r"contrare are exact o rădăcină."}

    # rational mode ---------------------------------------------------------
    def _rat_a(self, ctx):
        fp = ctx["fp"]
        assert sp.simplify(sp.diff(ctx["f"], x) - fp) == 0
        return {"question_latex": rf"Arătați că $f'(x) = {_latex(fp)}$, $x \neq {-ctx['c']}$.",
                "answer_latex": rf"$f'(x) = {_latex(fp)}$",
                "hint_latex": r"Regula câtului: $\left(\dfrac{u}{v}\right)' = \dfrac{u'v-uv'}{v^2}$."}

    def _rat_b(self, ctx):
        f, c = ctx["f"], ctx["c"]
        m = sp.limit(f / x, x, sp.oo)
        n = sp.limit(f - m * x, x, sp.oo)
        asy = m * x + n
        assert m == 1 and sp.simplify(n - (-c)) == 0
        return {"question_latex": r"Determinați ecuația asimptotei oblice către $+\infty$ a "
                                  r"graficului funcției $f$.",
                "answer_latex": rf"$y = {_latex(asy)}$",
                "hint_latex": r"$m = \lim_{x\to\infty}\dfrac{f(x)}{x}$, "
                              r"$n = \lim_{x\to\infty}\big(f(x)-mx\big)$.",
                "steps_latex": [rf"$m = {_latex(m)}$, $n = {_latex(n)}$",
                                rf"$y = {_latex(asy)}$"]}

    def _rat_c(self, ctx):
        c = ctx["c"]
        assert sp.limit(ctx["f"], x, -c) in (sp.oo, -sp.oo, sp.zoo)
        return {"question_latex": r"Determinați ecuația asimptotei verticale a graficului "
                                  r"funcției $f$.",
                "answer_latex": rf"$x = {-c}$",
                "hint_latex": rf"Studiați $\lim_{{x\to {-c}}} f(x)$."}
