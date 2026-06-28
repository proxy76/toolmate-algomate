"""Derivatives — tiered to the BAC.

D1 (Subiectul I)   : direct power rule, derivative of a polynomial, f'(x0).
D2 (Subiectul II)  : product / quotient / chain rule, tangent line at a point.
D3 (Subiectul III) : function study — monotonicity & extrema, convexity, asymptote.

Every answer is produced (and therefore verified) by ``sympy``; difficulty
selects the *technique*, never the size of the coefficients.
"""
from __future__ import annotations

import random

import sympy as sp

from ._utils import latex, make, nonzero, pick, small_coef, small_pos, x


def _diff(expr):
    return sp.simplify(sp.diff(expr, x))


# ---------------------------------------------------------------- D1 ----------
def _d1_power(rng):
    a = small_coef(rng)
    e = small_pos(rng, 2, 5)
    expr = a * x**e
    return make(
        "derivatives",
        rf"Calculează derivata funcției $f:\mathbb{{R}}\to\mathbb{{R}}$, $f(x) = {latex(expr)}$.",
        rf"$f'(x) = {latex(_diff(expr))}$",
        hint_latex=r"Regula puterii: $(c\,x^n)' = c\cdot n\cdot x^{n-1}$.",
    )


def _d1_polynomial(rng):
    a = nonzero(rng, 1, 4)
    b = small_coef(rng)
    c = small_coef(rng)
    d = small_coef(rng)
    expr = a * x**3 + b * x**2 + c * x + d
    return make(
        "derivatives",
        rf"Calculează derivata funcției $f:\mathbb{{R}}\to\mathbb{{R}}$, $f(x) = {latex(expr)}$.",
        rf"$f'(x) = {latex(_diff(expr))}$",
        hint_latex=r"Derivează termen cu termen; derivata unei constante este $0$.",
    )


def _d1_value_at_point(rng):
    a = nonzero(rng, 1, 3)
    b = small_coef(rng)
    c = small_coef(rng)
    x0 = rng.randint(-2, 2)
    expr = a * x**2 + b * x + c
    fp = sp.diff(expr, x)
    val = int(fp.subs(x, x0))
    return make(
        "derivatives",
        rf"Fie $f:\mathbb{{R}}\to\mathbb{{R}}$, $f(x) = {latex(expr)}$. Calculează $f'({x0})$.",
        rf"$f'({x0}) = {val}$",
        hint_latex=rf"Calculează întâi $f'(x)$, apoi înlocuiește $x = {x0}$.",
        steps_latex=[rf"$f'(x) = {latex(fp)}$", rf"$f'({x0}) = {val}$"],
    )


# ---------------------------------------------------------------- D2 ----------
def _d2_product(rng):
    e = small_pos(rng, 2, 4)
    expr = x**e * sp.exp(x)
    return make(
        "derivatives",
        rf"Calculează derivata funcției $f:\mathbb{{R}}\to\mathbb{{R}}$, $f(x) = {latex(expr)}$.",
        rf"$f'(x) = {latex(_diff(expr))}$",
        hint_latex=r"Regula produsului: $(u\cdot v)' = u'v + uv'$.",
    )


def _d2_quotient(rng):
    a = nonzero(rng, 1, 4)
    b = small_coef(rng)
    c = nonzero(rng, 1, 4)
    expr = (a * x + b) / (x + c)
    return make(
        "derivatives",
        rf"Calculează derivata funcției $f(x) = {latex(expr)}$, $x \neq {-c}$.",
        rf"$f'(x) = {latex(_diff(expr))}$",
        hint_latex=r"Regula câtului: $\left(\dfrac{u}{v}\right)' = \dfrac{u'v - uv'}{v^2}$.",
    )


def _d2_chain(rng):
    kind = pick(rng, ["power", "sin", "cos", "exp", "ln"])
    a = nonzero(rng, 2, 4)
    b = small_coef(rng)
    if kind == "power":
        e = small_pos(rng, 2, 4)
        expr = (a * x + b) ** e
        hint = r"Regula lanțului: $(u^n)' = n\,u^{n-1}\cdot u'$."
    elif kind == "sin":
        expr = sp.sin(a * x + b)
        hint = r"$(\sin u)' = \cos(u)\cdot u'$."
    elif kind == "cos":
        expr = sp.cos(a * x + b)
        hint = r"$(\cos u)' = -\sin(u)\cdot u'$."
    elif kind == "exp":
        expr = sp.exp(a * x + b)
        hint = r"$(e^u)' = e^u\cdot u'$."
    else:
        c = nonzero(rng, 1, 4)
        expr = sp.log(a * x + c)
        hint = r"$(\ln u)' = \dfrac{u'}{u}$."
    return make(
        "derivatives",
        rf"Calculează derivata funcției $f(x) = {latex(expr)}$.",
        rf"$f'(x) = {latex(_diff(expr))}$",
        hint_latex=hint,
    )


def _d2_tangent(rng):
    b = small_coef(rng)
    c = small_coef(rng)
    x0 = rng.randint(-2, 2)
    expr = x**2 + b * x + c
    fp = sp.diff(expr, x)
    m = int(fp.subs(x, x0))
    y0 = int(expr.subs(x, x0))
    q = y0 - m * x0
    tangent = m * x + q
    return make(
        "derivatives",
        rf"Fie $f:\mathbb{{R}}\to\mathbb{{R}}$, $f(x) = {latex(expr)}$. "
        rf"Determină ecuația tangentei la graficul lui $f$ în punctul de abscisă $x_0 = {x0}$.",
        rf"$y = {latex(tangent)}$",
        hint_latex=r"Tangenta în $x_0$: $y = f'(x_0)\,(x - x_0) + f(x_0)$.",
        steps_latex=[
            rf"$f'(x) = {latex(fp)}$, deci $f'({x0}) = {m}$",
            rf"$f({x0}) = {y0}$",
            rf"$y = {m}\,(x - ({x0})) + ({y0}) = {latex(tangent)}$",
        ],
    )


# ---------------------------------------------------------------- D3 ----------
def _d3_monotonicity(rng):
    r1 = rng.randint(-3, 0)
    r1, r2 = r1, r1 + pick(rng, [2, 4])  # distinct integer roots, even sum
    fp = sp.expand(3 * (x - r1) * (x - r2))
    f = sp.integrate(fp, x)  # constant of integration 0 -> clean polynomial
    f_r1, f_r2 = int(f.subs(x, r1)), int(f.subs(x, r2))
    return make(
        "derivatives",
        rf"Se consideră funcția $f:\mathbb{{R}}\to\mathbb{{R}}$, $f(x) = {latex(f)}$. "
        r"Determină intervalele de monotonie și punctele de extrem ale lui $f$.",
        (
            rf"$f$ este crescătoare pe $(-\infty, {r1}]$ și pe $[{r2}, \infty)$, "
            rf"descrescătoare pe $[{r1}, {r2}]$. "
            rf"Maxim local $f({r1}) = {f_r1}$, minim local $f({r2}) = {f_r2}$."
        ),
        hint_latex=r"Studiază semnul lui $f'(x)$: rezolvă $f'(x)=0$ și fă tabelul de semn.",
        steps_latex=[
            rf"$f'(x) = {latex(fp)} = 3\,(x - {r1})(x - {r2})$",
            rf"$f'(x) = 0 \iff x \in \{{{r1}, {r2}\}}$",
            rf"$f' > 0$ pe $(-\infty,{r1})\cup({r2},\infty)$, $f' < 0$ pe $({r1},{r2})$",
            rf"max local în $x={r1}$, min local în $x={r2}$",
        ],
    )


def _d3_convexity(rng):
    b = pick(rng, [-6, -3, 3, 6])  # inflection at integer x = -b/3
    c = small_coef(rng)
    f = x**3 + b * x**2 + c * x
    fpp = sp.diff(f, x, 2)
    infl = sp.Rational(-b, 3)
    return make(
        "derivatives",
        rf"Se consideră funcția $f:\mathbb{{R}}\to\mathbb{{R}}$, $f(x) = {latex(f)}$. "
        r"Determină intervalele de convexitate/concavitate și punctul de inflexiune.",
        (
            rf"$f$ este concavă pe $(-\infty, {latex(infl)})$, convexă pe "
            rf"$({latex(infl)}, \infty)$; punct de inflexiune în $x = {latex(infl)}$."
        ),
        hint_latex=r"Studiază semnul derivatei a doua $f''(x)$.",
        steps_latex=[
            rf"$f''(x) = {latex(fpp)}$",
            rf"$f''(x) = 0 \iff x = {latex(infl)}$",
            rf"$f'' < 0$ înainte, $f'' > 0$ după $\Rightarrow$ inflexiune în $x={latex(infl)}$",
        ],
    )


def _d3_asymptote(rng):
    c = nonzero(rng, 1, 4)
    b = small_coef(rng)
    f = (x**2 + b) / (x + c)
    # f = x - c + (c^2 + b)/(x + c)  -> oblique asymptote y = x - c
    oblique = x - c
    return make(
        "derivatives",
        rf"Determină asimptotele funcției $f(x) = {latex(f)}$, $x \neq {-c}$.",
        rf"Asimptotă verticală $x = {-c}$; asimptotă oblică $y = {latex(oblique)}$.",
        hint_latex=r"Împarte cu rest: $\frac{P(x)}{Q(x)} = C(x) + \frac{R(x)}{Q(x)}$, "
        r"apoi $\lim_{x\to\pm\infty}\frac{R}{Q}=0$.",
        steps_latex=[
            rf"$f(x) = x - {c} + \dfrac{{{c**2 + b}}}{{x + {c}}}$",
            rf"$\lim_{{x\to -{c}}} f = \pm\infty \Rightarrow$ asimptotă verticală $x={-c}$",
            rf"partea întreagă $\Rightarrow$ asimptotă oblică $y = {latex(oblique)}$",
        ],
    )


TIERS = {
    1: [_d1_power, _d1_polynomial, _d1_value_at_point],
    2: [_d2_product, _d2_quotient, _d2_chain, _d2_tangent],
    3: [_d3_monotonicity, _d3_convexity, _d3_asymptote],
}


def generate(difficulty: int, rng: random.Random) -> dict:
    from ._utils import choose_subtype

    return choose_subtype(difficulty, rng, TIERS)


# ---- M3: polynomials only, capped at direct technique (D1 / light D2) --------
def _m3_power(rng):
    a = nonzero(rng, 2, 5)
    b = nonzero(rng, 2, 5)
    c = small_coef(rng)
    expr = a * x**3 + b * x**2 + c * x
    return make(
        "derivatives",
        rf"Calculează derivata funcției $f(x) = {latex(expr)}$.",
        rf"$f'(x) = {latex(_diff(expr))}$",
        hint_latex=r"Derivează fiecare termen: $(c\,x^n)' = c\cdot n\cdot x^{n-1}$.",
    )


def generate_basic(difficulty: int, rng: random.Random) -> dict:
    from ._utils import choose_subtype

    tiers = {1: [_m3_power, _d1_value_at_point], 2: [_d2_tangent, _m3_power]}
    return choose_subtype(difficulty, rng, tiers)
