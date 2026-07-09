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
    # Romanian BAC writes the natural log as ``ln`` (sympy emits ``\log``).
    return sp.latex(expr, mul_symbol="dot").replace(r"\log", r"\ln")


class DerivativesGenerator(ExerciseGenerator):
    TOPIC_CODE = "derivatives"
    SUPPORTED_PROFILES = ["mate-info", "tehnologic", "stiintele-naturii", "pedagogic"]

    # (key, description, builder(params, x)) per profile/difficulty (spec §9.1).
    FUNC_TEMPLATES = {
        "mate-info": {
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
        "tehnologic": {
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
        "pedagogic": {  # polynomials only — no exp/log (§5.2)
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
        # șt-nat has no own single-item template set — it shares mate-info's
        # (poly / exp / log / rational), matching its analytic character.
        templates = self.FUNC_TEMPLATES.get(self.profile, self.FUNC_TEMPLATES["mate-info"])[d]
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
    SUPPORTED_PROFILES = ["mate-info", "tehnologic", "stiintele-naturii"]

    def _generate_context(self) -> dict:
        rng = self.rng
        # M1 (mate-info) uses the harder function-study modes of the real papers:
        # exp/rational with a *bijectivity* proof, and ln with extremum analysis.
        # M2 keeps the cubic/rational study unchanged.
        if self.profile == "mate-info":
            mode = rng.choice(["exp_bijective", "ln_extrem", "rational", "cubic"])
        elif self.profile == "stiintele-naturii":
            # M_șt-nat Subiect III prob-1 is a real-analysis study of a rational /
            # ln function (asymptote + monotonicity/extremum) — harder than the
            # tehnologic poly-dominant study, lighter than mate-info's bijectivity.
            mode = rng.choice(["rational", "rational", "ln_extrem", "cubic"])
        else:
            # M_tehnologic Subiect III prob-1 is dominated by polynomial function
            # study with a tangent-at-a-point cerință.
            mode = rng.choice(["poly", "poly", "cubic", "rational"])

        if mode == "poly":
            return self._context_poly()
        if mode == "cubic":
            a = rng.choice([1, 2, 3, 4, 5])      # a>0 ⇒ f'(x)=3x²+a>0 ⇒ strictly ↑
            b = rng.choice([-3, -2, -1, 1, 2, 3])
            f = x ** 3 + a * x + b
            return {"mode": "cubic", "f": f, "a": a, "b": b, "fp": sp.diff(f, x)}
        if mode == "rational":
            c = rng.choice([1, 2, 3, -1, -2])
            b = rng.choice([-3, -2, -1, 1, 2, 3])
            if c * c + b == 0:
                b += 1
            f = (x ** 2 + b) / (x + c)
            return {"mode": "rational", "f": sp.together(f), "b": b, "c": c,
                    "fp": sp.simplify(sp.diff(f, x))}
        if mode == "exp_bijective":
            k = rng.choice([1, 2])                # f'(x)=1+k·e^{kx}>0 ⇒ bijective ℝ→ℝ
            f = x + sp.exp(k * x)
            return {"mode": "exp_bijective", "f": f, "k": k, "fp": sp.simplify(sp.diff(f, x))}
        a = rng.choice([1, 2, 3])                 # f(x)=x−a·ln x on (0,∞); min at x=a
        f = x - a * sp.ln(x)
        return {"mode": "ln_extrem", "f": f, "a": a, "fp": sp.simplify(sp.diff(f, x))}

    def _context_poly(self) -> dict:
        """Cubic polynomial with a factorable derivative (M_tehnologic)."""
        rng = self.rng
        for _ in range(200):
            B = rng.choice([-6, -3, 3, 6, -4, 4])       # even keeps f' roots integer-friendly
            C = rng.choice([-15, -12, -9, -5, -3, 3, 9, 12])
            D = rng.choice([-3, -1, 1, 3, 9])
            f = x ** 3 + B * x ** 2 + C * x + D
            fp = sp.diff(f, x)
            rts = sp.roots(sp.Poly(fp, x))
            if sum(rts.values()) != 2 or not all(r.is_integer for r in rts):
                continue
            if len(set(rts)) != 2:
                continue
            x0 = rng.choice([0, 1, -1])
            return {"mode": "poly", "f": f, "fp": sp.factor(fp),
                    "roots": sorted(int(r) for r in rts), "x0": x0}
        raise ValueError("no poly context")

    def _validate_context(self, ctx) -> bool:
        mode = ctx["mode"]
        if mode == "poly":
            return sp.simplify(sp.diff(ctx["f"], x) - sp.expand(ctx["fp"])) == 0
        if mode == "cubic":
            return ctx["a"] > 0 and len(sp.real_roots(sp.Poly(ctx["f"], x))) == 1
        if mode == "rational":
            return ctx["c"] ** 2 + ctx["b"] != 0
        if mode == "exp_bijective":
            return ctx["k"] > 0
        return ctx["a"] > 0                        # ln_extrem

    def _build_statement(self, ctx) -> str:
        f, mode = ctx["f"], ctx["mode"]
        if mode in ("cubic", "exp_bijective", "poly"):
            return rf"Se consideră funcția $f:\mathbb{{R}}\to\mathbb{{R}}$, $f(x) = {_latex(f)}$."
        if mode == "ln_extrem":
            return (rf"Se consideră funcția $f:(0,\infty)\to\mathbb{{R}}$, "
                    rf"$f(x) = {_latex(f)}$.")
        c = ctx["c"]
        return (rf"Se consideră funcția $f:\mathbb{{R}}\setminus\{{{-c}\}}\to\mathbb{{R}}$, "
                rf"$f(x) = {_latex(f)}$.")

    def _build_sub_item(self, ctx, label, difficulty) -> dict:
        idx = ("a", "b", "c").index(label)
        builders = {
            "poly": (self._poly_a, self._poly_b, self._poly_c),
            "cubic": (self._cub_a, self._cub_b, self._cub_c),
            "rational": (self._rat_a, self._rat_b, self._rat_c),
            "exp_bijective": (self._exp_a, self._exp_b, self._exp_c),
            "ln_extrem": (self._ln_a, self._ln_b, self._ln_c),
        }[ctx["mode"]]
        return builders[idx](ctx)

    # poly mode (M_tehnologic) ----------------------------------------------
    def _poly_a(self, ctx):
        fp = ctx["fp"]
        assert sp.simplify(sp.diff(ctx["f"], x) - sp.expand(fp)) == 0
        return {"question_latex": rf"Arătați că $f'(x) = {_latex(fp)}$, $x \in \mathbb{{R}}$.",
                "answer_latex": rf"$f'(x) = {_latex(fp)}$",
                "hint_latex": r"Derivați termen cu termen, apoi dați factor comun."}

    def _poly_b(self, ctx):
        f, x0 = ctx["f"], ctx["x0"]
        y0 = f.subs(x, x0)
        slope = sp.diff(f, x).subs(x, x0)
        tang = sp.expand(slope * (x - x0) + y0)
        return {"question_latex": rf"Determinați ecuația tangentei la graficul funcției $f$ în "
                                  rf"punctul de abscisă $x = {x0}$, situat pe graficul funcției $f$.",
                "answer_latex": rf"$y = {_latex(tang)}$",
                "hint_latex": rf"Tangenta în $x_0$: $y = f'({x0})(x - {x0}) + f({x0})$.",
                "steps_latex": [rf"$f({x0}) = {_latex(y0)}$, $f'({x0}) = {_latex(slope)}$",
                                rf"$y = {_latex(tang)}$"]}

    def _poly_c(self, ctx):
        r1, r2 = ctx["roots"]
        return {"question_latex": r"Determinați intervalele de monotonie ale funcției $f$.",
                "answer_latex": rf"$f$ este strict crescătoare pe $(-\infty, {r1}]$ și pe "
                                rf"$[{r2}, \infty)$, strict descrescătoare pe $[{r1}, {r2}]$",
                "hint_latex": r"Studiați semnul lui $f'$ folosind rădăcinile derivatei.",
                "steps_latex": [rf"$f'(x) = 0 \Rightarrow x \in \{{{r1}, {r2}\}}$",
                                rf"$f' > 0$ în afara $[{r1}, {r2}]$, $f' < 0$ pe $({r1}, {r2})$"]}

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

    # exp-bijective mode (M1) ----------------------------------------------
    def _exp_a(self, ctx):
        fp = ctx["fp"]
        assert sp.simplify(sp.diff(ctx["f"], x) - fp) == 0
        return {"question_latex": rf"Arătați că $f'(x) = {_latex(fp)}$, $x \in \mathbb{{R}}$.",
                "answer_latex": rf"$f'(x) = {_latex(fp)}$",
                "hint_latex": r"$(e^{u})' = e^{u}\cdot u'$; derivați termen cu termen."}

    def _exp_b(self, ctx):
        return {"question_latex": r"Arătați că funcția $f$ este strict crescătoare pe "
                                  r"$\mathbb{R}$.",
                "answer_latex": rf"$f'(x) = {_latex(ctx['fp'])} > 0$ pentru orice "
                                r"$x \in \mathbb{R}$, deci $f$ este strict crescătoare",
                "hint_latex": r"$e^{kx} > 0$, deci $f'(x) > 0$ pe tot $\mathbb{R}$."}

    def _exp_c(self, ctx):
        f = ctx["f"]
        assert sp.limit(f, x, -sp.oo) == -sp.oo and sp.limit(f, x, sp.oo) == sp.oo
        return {"question_latex": r"Arătați că funcția $f$ este bijectivă.",
                "answer_latex": r"$f$ strict crescătoare și continuă $\Rightarrow$ injectivă; "
                                r"$\lim_{x\to-\infty}f=-\infty$, $\lim_{x\to+\infty}f=+\infty$ "
                                r"$\Rightarrow$ surjectivă, deci $f$ este bijectivă",
                "hint_latex": r"O funcție continuă, strict monotonă, cu limite $\pm\infty$ "
                              r"la capete este bijectivă."}

    # ln-extremum mode (M1) ------------------------------------------------
    def _ln_a(self, ctx):
        fp = sp.together(ctx["fp"])
        assert sp.simplify(sp.diff(ctx["f"], x) - fp) == 0
        return {"question_latex": rf"Arătați că $f'(x) = {_latex(fp)}$, $x \in (0, \infty)$.",
                "answer_latex": rf"$f'(x) = {_latex(fp)}$",
                "hint_latex": r"$(\ln x)' = \dfrac{1}{x}$; derivați termen cu termen."}

    def _ln_b(self, ctx):
        a = ctx["a"]
        return {"question_latex": r"Determinați intervalele de monotonie ale funcției $f$.",
                "answer_latex": rf"$f$ este strict descrescătoare pe $(0, {a})$ și strict "
                                rf"crescătoare pe $({a}, \infty)$",
                "hint_latex": rf"$f'(x) = \dfrac{{x - {a}}}{{x}}$; studiați semnul pe $(0,\infty)$.",
                "steps_latex": [rf"$f'(x) < 0$ pe $(0, {a})$, $f'(x) > 0$ pe $({a}, \infty)$"]}

    def _ln_c(self, ctx):
        a = ctx["a"]
        assert sp.simplify(ctx["fp"].subs(x, a)) == 0
        return {"question_latex": r"Determinați punctul de minim al funcției $f$.",
                "answer_latex": rf"$x = {a}$",
                "hint_latex": rf"Punctul de minim este soluția ecuației $f'(x) = 0$ din "
                              rf"$(0,\infty)$.",
                "steps_latex": [rf"$f'(x) = 0 \Rightarrow x = {a}$ (minim, căci $f'$ schimbă "
                                rf"semnul din $-$ în $+$)"]}
