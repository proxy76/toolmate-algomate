"""Functions — single-item class (Subiectul I, position 2; ``info-on-sub1.md`` §2).

Authentic BAC position-2 phrasings over affine/linear functions ``f(x)=ax+b``:
solve ``f(x0)=val``, point on graph (find ``b``), composition ``(f∘g)(x0)``,
``f(x0)=g(x0)``, the linearity identity ``f(kx)-k·f(x)``, the self-composition
``(f∘f)(x0)=val``, and (M1/M2 only) the parabola-vertex-on-Ox item.

M3 is restricted to the linear/affine tasks only (no parabola, no
self-composition), per ``info-on-sub1.md`` §2 ("use only T2.a, T2.b, T2.d, T2.e").

Every answer is an integer, constructed by design and re-verified with sympy.
"""
from __future__ import annotations

import sympy as sp

from ..base import TieredExerciseGenerator
from .._utils import make, nonzero

X = sp.Symbol("x")
A = sp.Symbol("a")
B = sp.Symbol("b")


def _ax(a: int) -> str:
    """`ax` in BAC style (drops the coefficient 1)."""
    if a == 1:
        return "x"
    if a == -1:
        return "-x"
    return f"{a}x"


def _lin(a: int, b: int) -> str:
    """`ax + b` in BAC style, with the sign of ``b`` folded into the printout."""
    s = _ax(a)
    if b == 0:
        return s
    return f"{s} + {b}" if b > 0 else f"{s} - {-b}"


def _decl(expr_str: str, name: str = "f") -> str:
    return (rf"Se consideră funcția ${name}:\mathbb{{R}}\to\mathbb{{R}}$, "
            rf"${name}(x) = {expr_str}$")


# --- T2.a — solve f(x0) = val ------------------------------------------------
def _d1_solve_value(rng):
    a = nonzero(rng, -4, 4)
    b = rng.randint(-6, 6)
    x0 = rng.randint(-4, 4)
    val = a * x0 + b
    assert sp.solve(sp.Eq(a * X + b, val), X) == [x0]
    return make(
        "functions",
        _decl(_lin(a, b)) + rf". Determinați numărul real $x_0$ pentru care $f(x_0) = {val}$.",
        rf"$x_0 = {x0}$",
        hint_latex=rf"Rezolvați ecuația ${_lin(a, b)} = {val}$.",
        steps_latex=[rf"${_lin(a, b)} = {val} \Rightarrow x_0 = {x0}$"],
    )


# --- T2.b — point on graph, determine b --------------------------------------
def _d1_point_find_b(rng):
    a = nonzero(rng, -4, 4)
    xv = nonzero(rng, -4, 4)
    b = rng.randint(-6, 6)
    yv = a * xv + b
    prod = a * xv
    assert sp.solve(sp.Eq(prod + B, yv), B) == [b]
    return make(
        "functions",
        rf"Se consideră funcția $f:\mathbb{{R}}\to\mathbb{{R}}$, $f(x) = {_ax(a)} + b$, unde $b$ "
        rf"este număr real. Determinați numărul real $b$ pentru care punctul $M({xv}, {yv})$ "
        rf"aparține graficului funcției $f$.",
        rf"$b = {b}$",
        hint_latex=rf"Punctul aparține graficului dacă $f({xv}) = {yv}$.",
        steps_latex=[rf"$f({xv}) = {prod} + b = {yv} \Rightarrow b = {b}$"],
    )


# --- T2.d — compute (f∘g)(x0) ------------------------------------------------
def _d1_compose_value(rng):
    a = nonzero(rng, -3, 3)
    b = rng.randint(-5, 5)
    c = nonzero(rng, -3, 3)
    d = rng.randint(-5, 5)
    xv = rng.randint(-3, 3)
    inner = c * xv + d
    val = a * inner + b
    return make(
        "functions",
        rf"Se consideră funcțiile $f, g:\mathbb{{R}}\to\mathbb{{R}}$, $f(x) = {_lin(a, b)}$ și "
        rf"$g(x) = {_lin(c, d)}$. Calculați $(f\circ g)({xv})$.",
        rf"$(f\circ g)({xv}) = {val}$",
        hint_latex=r"$(f\circ g)(x) = f(g(x))$.",
        steps_latex=[rf"$g({xv}) = {inner}$", rf"$f({inner}) = {val}$"],
    )


# --- T2.e — solve f(x0) = g(x0) ----------------------------------------------
def _d1_f_eq_g(rng):
    par = rng.randint(-4, 4)
    a = nonzero(rng, -4, 4)
    c = nonzero(rng, -4, 4)
    while c == a:
        c = nonzero(rng, -4, 4)
    b = rng.randint(-5, 5)
    d = (a - c) * par + b           # so that a·par + b = c·par + d
    assert sp.solve(sp.Eq(a * X + b, c * X + d), X) == [par]
    return make(
        "functions",
        rf"Se consideră funcțiile $f, g:\mathbb{{R}}\to\mathbb{{R}}$, $f(x) = {_lin(a, b)}$ și "
        rf"$g(x) = {_lin(c, d)}$. Determinați numărul real $x_0$ pentru care "
        rf"$f(x_0) = g(x_0)$.",
        rf"$x_0 = {par}$",
        hint_latex=r"Rezolvați ecuația $f(x) = g(x)$.",
    )


# --- T2.c — self-composition (f∘f)(x0) = val, determine a --------------------
def _d2_compose_self(rng):
    a = nonzero(rng, -3, 3)
    b = rng.randint(-4, 4)
    xv = nonzero(rng, -3, 3)
    val = a * (a * xv + b) + b
    ints = sorted({s for s in sp.solve(sp.Eq(A * (A * xv + b) + b, val), A) if s.is_integer})
    assert ints == [a]              # a must be the unique integer solution
    bs = "" if b == 0 else (f" + {b}" if b > 0 else f" - {-b}")
    return make(
        "functions",
        rf"Se consideră funcția $f:\mathbb{{R}}\to\mathbb{{R}}$, $f(x) = ax{bs}$, unde $a$ este "
        rf"număr real. Determinați numărul real $a$ pentru care $(f\circ f)({xv}) = {val}$.",
        rf"$a = {a}$",
        hint_latex=r"$(f\circ f)(x) = a(ax + b) + b = a^2 x + ab + b$.",
    )


# --- T2.f — linearity identity f(kx) - k·f(x) = const ------------------------
def _d2_identity(rng):
    a = nonzero(rng, -4, 4)
    b = nonzero(rng, -5, 5)
    k = rng.randint(2, 4)
    val = sp.simplify(a * k * X + b - k * (a * X + b))
    assert val == b * (1 - k)       # constant in x (the x-terms cancel)
    return make(
        "functions",
        rf"Se consideră funcția $f:\mathbb{{R}}\to\mathbb{{R}}$, $f(x) = {_lin(a, b)}$. "
        rf"Arătați că $f({k}x) - {k}f(x) = {val}$, pentru orice număr real $x$.",
        rf"${val}$",
        hint_latex=rf"$f({k}x) = {_ax(a * k)} + {b}$ și ${k}f(x) = {k}\left({_lin(a, b)}\right)$; "
                   rf"termenii în $x$ se reduc.",
    )


# --- T2.h — solve f(x0) + f(k·x0) = val --------------------------------------
def _d2_sum_arg(rng):
    par = rng.randint(-3, 3)
    a = nonzero(rng, -3, 3)
    b = rng.randint(-4, 4)
    k = rng.randint(2, 3)
    val = (a * par + b) + (a * k * par + b)
    assert sp.solve(sp.Eq((a * X + b) + (a * k * X + b), val), X) == [par]
    return make(
        "functions",
        rf"Se consideră funcția $f:\mathbb{{R}}\to\mathbb{{R}}$, $f(x) = {_lin(a, b)}$. "
        rf"Determinați numărul real $x_0$ pentru care $f(x_0) + f({k}x_0) = {val}$.",
        rf"$x_0 = {par}$",
        hint_latex=rf"$f(x_0) + f({k}x_0) = \left({_lin(a, b)}\right) + "
                   rf"\left({_lin(a * k, b)}\right)$.",
    )


# --- T2.g — parabola vertex on Ox (M1/M2 only) -------------------------------
def _d3_parabola_vertex(rng):
    t = rng.randint(1, 4)
    a = 2 * t
    b = t * t                       # Δ = a² - 4b = 0
    assert set(sp.solve(sp.Eq(A ** 2 - 4 * b, 0), A)) == {-a, a}
    return make(
        "functions",
        rf"Se consideră funcția $f:\mathbb{{R}}\to\mathbb{{R}}$, $f(x) = x^2 + ax + {b}$, unde "
        rf"$a$ este număr real. Determinați numerele reale $a$ pentru care vârful parabolei "
        rf"asociate funcției $f$ se află pe axa $Ox$.",
        rf"$a \in \{{-{a}, {a}\}}$",
        hint_latex=r"Vârful este pe axa $Ox$ când discriminantul este nul: $a^2 - 4c = 0$.",
        steps_latex=[rf"$\Delta = a^2 - 4\cdot{b} = 0 \Rightarrow a^2 = {4 * b} "
                     rf"\Rightarrow a = \pm{a}$"],
    )


# --- Parabola / quadratic family (Subiectul I pos 2 — the dominant real form) --
# Real M1 pos-2 items are overwhelmingly quadratic f(x)=x²+bx+c with a
# discriminant / vertex / intersection condition. Every answer is a clean integer,
# an integer bound, or ±integer, built by design and re-verified with sympy.

def _bx(b: int) -> str:
    """`+ bx` / `- |b|x` fragment (empty when b == 0)."""
    if b == 0:
        return ""
    return f" + {b}x" if b > 0 else f" - {-b}x"


def _p_vertex_ordinate_pos(rng):
    """f(x)=x²+bx+m, vertex ordinate strictly > 0  ⇔  Δ<0  ⇔  m > b²/4."""
    t = rng.randint(1, 4)
    b = rng.choice([2 * t, -2 * t])   # b even ⇒ b²/4 integer
    k = t * t
    return make(
        "functions",
        rf"Se consideră funcția $f:\mathbb{{R}}\to\mathbb{{R}}$, $f(x) = x^2{_bx(b)} + m$, unde "
        rf"$m$ este număr real. Determinați valorile reale ale lui $m$ pentru care vârful "
        rf"parabolei asociate funcției $f$ are ordonata strict mai mare decât $0$.",
        rf"$m > {k}$",
        hint_latex=r"Ordonata vârfului este $-\dfrac{\Delta}{4}$; cerința devine $\Delta < 0$.",
        steps_latex=[rf"$\Delta = {b**2} - 4m < 0 \Rightarrow m > {k}$"],
    )


def _p_vertex_on_ox(rng):
    """f(x)=x²+bx+m, vertex on Ox / Ox tangent  ⇔  Δ=0  ⇔  m = b²/4."""
    t = rng.randint(1, 4)
    b = rng.choice([2 * t, -2 * t])
    k = t * t
    assert sp.solve(sp.Eq(b ** 2 - 4 * X, 0), X) == [k]
    ask = rng.choice([
        "vârful parabolei asociate funcției $f$ este situat pe axa $Ox$",
        "axa $Ox$ este tangentă graficului funcției $f$",
    ])
    return make(
        "functions",
        rf"Se consideră funcția $f:\mathbb{{R}}\to\mathbb{{R}}$, $f(x) = x^2{_bx(b)} + m$, unde "
        rf"$m$ este număr real. Determinați numărul real $m$ pentru care {ask}.",
        rf"$m = {k}$",
        hint_latex=r"Contactul cu axa $Ox$ înseamnă discriminant nul: $\Delta = 0$.",
        steps_latex=[rf"$\Delta = {b**2} - 4m = 0 \Rightarrow m = {k}$"],
    )


def _p_positive_all(rng):
    """f(x)=x²+bx+m, f(x)>0 for all real x  ⇔  Δ<0  ⇔  m > b²/4."""
    t = rng.randint(1, 4)
    b = rng.choice([2 * t, -2 * t])
    k = t * t
    return make(
        "functions",
        rf"Se consideră funcția $f:\mathbb{{R}}\to\mathbb{{R}}$, $f(x) = x^2{_bx(b)} + m$, unde "
        rf"$m$ este număr real. Determinați valorile reale ale lui $m$ pentru care "
        rf"$f(x) > 0$, pentru orice număr real $x$.",
        rf"$m > {k}$",
        hint_latex=r"O parabolă cu $a>0$ este strict pozitivă pe $\mathbb{R}$ când $\Delta < 0$.",
        steps_latex=[rf"$\Delta = {b**2} - 4m < 0 \Rightarrow m > {k}$"],
    )


def _p_two_roots(rng):
    """f(x)=x²+bx+m, graph meets Ox in two distinct points  ⇔  Δ>0  ⇔  m < b²/4."""
    t = rng.randint(1, 4)
    b = rng.choice([2 * t, -2 * t])
    k = t * t
    return make(
        "functions",
        rf"Se consideră funcția $f:\mathbb{{R}}\to\mathbb{{R}}$, $f(x) = x^2{_bx(b)} + m$, unde "
        rf"$m$ este număr real. Determinați valorile reale ale lui $m$ pentru care graficul "
        rf"funcției $f$ intersectează axa $Ox$ în două puncte distincte.",
        rf"$m < {k}$",
        hint_latex=r"Două intersecții distincte cu axa $Ox$ înseamnă $\Delta > 0$.",
        steps_latex=[rf"$\Delta = {b**2} - 4m > 0 \Rightarrow m < {k}$"],
    )


def _p_tangent_linear(rng):
    """f(x)=x²+mx+c, Ox tangent, parameter is the linear coefficient
       ⇔  m² - 4c = 0  ⇔  m = ±2√c   (c a perfect square ⇒ ±integer answer)."""
    t = rng.randint(1, 3)
    c = t * t                       # c ∈ {1,4,9}
    m0 = 2 * t
    assert set(sp.solve(sp.Eq(A ** 2 - 4 * c, 0), A)) == {-m0, m0}
    return make(
        "functions",
        rf"Se consideră funcția $f:\mathbb{{R}}\to\mathbb{{R}}$, $f(x) = x^2 + mx + {c}$, unde "
        rf"$m$ este număr real. Determinați numerele reale $m$ pentru care axa $Ox$ este "
        rf"tangentă graficului funcției $f$.",
        rf"$m \in \{{-{m0}, {m0}\}}$",
        hint_latex=r"Tangența la axa $Ox$ înseamnă $\Delta = 0$.",
        steps_latex=[rf"$\Delta = m^2 - 4\cdot{c} = 0 \Rightarrow m^2 = {4*c} "
                     rf"\Rightarrow m = \pm{m0}$"],
    )


def _p_intersect_line(rng):
    """f(x)=x²+bx+c ∩ line d: y=px+q — find the (integer) abscissas."""
    r1, r2 = sorted(rng.sample([-3, -2, -1, 1, 2, 3], 2))
    p = rng.choice([-2, -1, 1, 2, 3])
    q = rng.randint(-4, 4)
    b = -(r1 + r2) + p              # x²+bx+c = px+q  ⇔  x²-(r1+r2)x+r1r2 = 0
    c = r1 * r2 + q
    roots = sorted(int(s) for s in sp.solve(sp.Eq(X ** 2 + b * X + c, p * X + q), X))
    assert roots == [r1, r2]
    fx = "x^2" + _bx(b) + (f" + {c}" if c > 0 else (f" - {-c}" if c < 0 else ""))
    dline = _lin(p, q)
    sol = ",\\ ".join(str(s) for s in roots)
    return make(
        "functions",
        rf"Se consideră funcția $f:\mathbb{{R}}\to\mathbb{{R}}$, $f(x) = {fx}$. Determinați "
        rf"abscisele punctelor de intersecție a graficului funcției $f$ cu dreapta $d$ de "
        rf"ecuație $y = {dline}$.",
        rf"$x \in \{{{sol}\}}$",
        hint_latex=rf"Rezolvați ecuația $f(x) = {dline}$.",
        steps_latex=[rf"$f(x) = {dline} \Rightarrow x \in \{{{sol}\}}$"],
    )


def _p_point_on_parabola(rng):
    """f(x)=x²+bx+m, point A(x0,y0) on the graph, constant term is the parameter."""
    b = nonzero(rng, -4, 4)
    x0 = nonzero(rng, -3, 3)
    m = rng.randint(-5, 5)
    y0 = x0 * x0 + b * x0 + m
    assert sp.solve(sp.Eq(x0 ** 2 + b * x0 + B, y0), B) == [m]
    return make(
        "functions",
        rf"Se consideră funcția $f:\mathbb{{R}}\to\mathbb{{R}}$, $f(x) = x^2{_bx(b)} + m$, unde "
        rf"$m$ este număr real. Determinați numărul real $m$ pentru care punctul "
        rf"$A({x0}, {y0})$ aparține graficului funcției $f$.",
        rf"$m = {m}$",
        hint_latex=rf"Punctul aparține graficului dacă $f({x0}) = {y0}$.",
        steps_latex=[rf"$f({x0}) = {x0**2 + b*x0} + m = {y0} \Rightarrow m = {m}$"],
    )


_PARABOLA = [
    _p_vertex_ordinate_pos, _p_vertex_on_ox, _p_positive_all, _p_two_roots,
    _p_tangent_linear, _p_intersect_line, _p_point_on_parabola,
]

_TIERS = {
    1: [_d1_solve_value, _d1_point_find_b, _d1_compose_value, _d1_f_eq_g],
    # Tier 2 is what M1 Subiectul I draws — quadratic-dominated, as in the real
    # papers, with the affine d2 items mixed in for variety.
    2: _PARABOLA + [_d2_compose_self, _d2_identity, _d2_sum_arg],
    3: _PARABOLA + [_d3_parabola_vertex],
}
# M3: linear/affine only (info-on-sub1 §2 — no parabola, no self-composition).
_TIERS_M3 = {1: [_d1_solve_value, _d1_point_find_b, _d1_compose_value, _d1_f_eq_g]}


class FunctionsGenerator(TieredExerciseGenerator):
    TOPIC_CODE = "functions"
    SUPPORTED_PROFILES = ["M1", "M2", "M3"]

    def _tiers(self):
        return _TIERS_M3 if self.profile == "M3" else _TIERS
