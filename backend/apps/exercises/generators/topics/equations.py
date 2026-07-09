"""Equations in ℝ — single-item class (Subiectul I, position 3; ``info-on-sub1.md`` §3).

The invariant wrapper "Rezolvați în mulțimea numerelor reale ecuația $…$" over a
rotating equation body — exponential, logarithmic, irrational, or modulus
(``info-on-sub1.md`` §3). Roots are constructed by design (clean) and re-verified
with sympy; the domain (positive log argument, non-negative radicand, RHS ≥ 0) is
enforced and extraneous roots discarded.

M3 is restricted to single-step equations with base ∈ {2, 3, 10}
(``info-on-sub1.md`` §3: ``E3.exp4, E3.log1, E3.log2, E3.irr2, E3.abs1``).
"""
from __future__ import annotations

import sympy as sp

from ..base import TieredExerciseGenerator
from .._utils import make

X = sp.Symbol("x", real=True)
WRAP = r"Rezolvați în mulțimea numerelor reale ecuația ${}$."


def _l(expr) -> str:
    return sp.latex(expr)


def _axs(a: int) -> str:
    return "x" if a == 1 else f"{a}x"


# --- exponential -------------------------------------------------------------
def _exp_simple(rng):                         # base^x = base^k        (single step)
    base = rng.choice([2, 3, 10])
    k = rng.randint(1, 3)
    val = base ** k
    assert base ** k == val
    return make(
        "equations",
        WRAP.format(rf"{base}^{{x}} = {val}"),
        rf"$x = {k}$",
        hint_latex=rf"Scrieți ${val} = {base}^{{{k}}}$ și egalați exponenții.",
        steps_latex=[rf"${base}^{{x}} = {base}^{{{k}}} \Rightarrow x = {k}$"],
    )


def _exp_prod(rng):                           # base^x · base^a = val  (single step)
    base = rng.choice([2, 3])
    a = rng.randint(1, 3)
    x0 = rng.randint(1, 3)
    m = x0 + a
    val = base ** m
    return make(
        "equations",
        WRAP.format(rf"{base}^{{x}} \cdot {base}^{{{a}}} = {val}"),
        rf"$x = {x0}$",
        hint_latex=rf"${base}^{{x}} \cdot {base}^{{{a}}} = {base}^{{x + {a}}}$ și "
                   rf"${val} = {base}^{{{m}}}$.",
        steps_latex=[rf"${base}^{{x + {a}}} = {base}^{{{m}}} \Rightarrow x + {a} = {m} "
                     rf"\Rightarrow x = {x0}$"],
    )


def _exp_quadratic(rng):                      # base^{2x} - S·base^x + P = 0  (M1/M2)
    base = rng.choice([2, 3])
    x1, x2 = sorted(rng.sample([0, 1, 2, 3], 2))
    t1, t2 = base ** x1, base ** x2
    S, P = t1 + t2, t1 * t2
    t = sp.Symbol("t", positive=True)
    troots = sorted(int(r) for r in sp.solve(sp.Eq(t ** 2 - S * t + P, 0), t))
    assert troots == sorted([t1, t2])
    sol = ",\\ ".join(str(s) for s in (x1, x2))
    return make(
        "equations",
        WRAP.format(rf"{base}^{{2x}} - {S}\cdot {base}^{{x}} + {P} = 0"),
        rf"$x \in \{{{sol}\}}$",
        hint_latex=rf"Notați $t = {base}^{{x}}$, $t > 0$: $t^2 - {S}t + {P} = 0$.",
        steps_latex=[rf"$t = {base}^{{x}} \Rightarrow t^2 - {S}t + {P} = 0$",
                     rf"$t \in \{{{t1},\ {t2}\}} \Rightarrow x \in \{{{sol}\}}$"],
    )


# --- logarithmic -------------------------------------------------------------
def _log_simple(rng):                         # log_b(x²+px) = log_b(C)   (single step)
    b = rng.choice([2, 3, 10])
    r1 = rng.choice([-2, -3, -4, -5])
    r2 = rng.choice([1, 2, 3])
    p = -(r1 + r2)
    C = -r1 * r2                              # > 0
    arg = X ** 2 + p * X
    sols = sorted((s for s in sp.solve(sp.Eq(arg, C), X)
                   if s.is_real and arg.subs(X, s) > 0), key=float)
    assert sols == sorted([r1, r2])
    sol = ",\\ ".join(_l(s) for s in sols)
    return make(
        "equations",
        WRAP.format(rf"\log_{{{b}}}\left({_l(arg)}\right) = \log_{{{b}}} {C}"),
        rf"$x \in \{{{sol}\}}$",
        hint_latex=r"Egalitatea logaritmilor în aceeași bază $\Rightarrow$ egalitatea "
                   r"argumentelor (cu condiția de existență).",
        steps_latex=[rf"${_l(arg)} = {C}$", rf"$x \in \{{{sol}\}}$"],
    )


def _log_linear(rng):                         # log_b(ax + c) = k   (single step)
    b = rng.choice([2, 3, 10])
    k = rng.randint(1, 2)
    a = rng.randint(1, 4)
    x0 = rng.randint(1, 4)
    rhs = b ** k
    c = rhs - a * x0
    arg = a * X + c
    assert arg.subs(X, x0) == rhs and rhs > 0
    return make(
        "equations",
        WRAP.format(rf"\log_{{{b}}}\left({_l(arg)}\right) = {k}"),
        rf"$x = {x0}$",
        hint_latex=rf"$\log_{{{b}}}(\,\cdot\,) = {k} \Rightarrow {_l(arg)} = {b}^{{{k}}} = {rhs}$.",
        steps_latex=[rf"${_l(arg)} = {rhs} \Rightarrow x = {x0}$"],
    )


# --- irrational --------------------------------------------------------------
def _irr_simple(rng):                         # sqrt(a + bx) = c   (single step)
    bcoef = rng.choice([-3, -2, 2, 3])
    c = rng.randint(1, 5)
    x0 = rng.randint(-3, 4)
    a = c * c - bcoef * x0
    rad = a + bcoef * X
    assert rad.subs(X, x0) == c * c
    return make(
        "equations",
        WRAP.format(rf"\sqrt{{{_l(rad)}}} = {c}"),
        rf"$x = {x0}$",
        hint_latex=rf"Ridicați la pătrat: ${_l(rad)} = {c * c}$.",
        steps_latex=[rf"${_l(rad)} = {c ** 2}$", rf"$x = {x0}$"],
    )


def _irr_extraneous(rng):                     # sqrt(ax + b) = x - c   (M1/M2)
    a = rng.randint(1, 3)
    c = rng.randint(0, 3)
    x0 = rng.randint(c + 1, c + 5)
    b = (x0 - c) ** 2 - a * x0
    rad = a * X + b
    quad = X ** 2 - (2 * c + a) * X + (c * c - b)   # (x - c)² = ax + b
    valid = sorted({s for s in sp.solve(quad, X)
                    if s.is_real and (s - c) >= 0 and (a * s + b) >= 0}, key=float)
    assert x0 in valid
    sol = ",\\ ".join(_l(s) for s in valid)
    ans = rf"$x \in \{{{sol}\}}$" if len(valid) > 1 else rf"$x = {_l(valid[0])}$"
    return make(
        "equations",
        WRAP.format(rf"\sqrt{{{_l(rad)}}} = x - {c}"),
        ans,
        hint_latex=rf"Condiția de existență: $x \geq {c}$. Ridicați la pătrat și verificați "
                   rf"soluțiile.",
        steps_latex=[rf"${_l(rad)} = (x - {c})^2$", ans.strip("$")],
    )


# --- modulus -----------------------------------------------------------------
def _abs_eq(rng):                             # |ax - b| = c   (single step)
    a = rng.randint(1, 3)
    x0 = rng.randint(-3, 3)
    t = rng.randint(1, 3)
    c = a * t
    b = a * x0 + c
    x1, x2 = sorted([x0, x0 + 2 * t])
    got = sorted(int(s) for s in sp.solve(sp.Eq(sp.Abs(a * X - b), c), X))
    assert got == [x1, x2]
    if b == 0:
        inner = _axs(a)
    elif b > 0:
        inner = f"{_axs(a)} - {b}"
    else:
        inner = f"{_axs(a)} + {-b}"
    sol = ",\\ ".join(str(s) for s in (x1, x2))
    return make(
        "equations",
        WRAP.format(rf"\left|{inner}\right| = {c}"),
        rf"$x \in \{{{sol}\}}$",
        hint_latex=rf"$\left|{inner}\right| = {c} \Rightarrow {inner} = \pm{c}$.",
        steps_latex=[rf"${inner} = {c}$ sau ${inner} = -{c}$", rf"$x \in \{{{sol}\}}$"],
    )


def _log_sum(rng):                            # log_b(x+p) + log_b(x+q) = log_b(C)  (M1/M2)
    b = rng.choice([2, 3, 10])
    p, q = rng.sample([1, 2, 3, 4, 5], 2)     # distinct offsets → distinct log arguments
    x0 = rng.randint(1, 3)
    C = (x0 + p) * (x0 + q)
    arg1, arg2 = X + p, X + q
    sols = [s for s in sp.solve(sp.Eq(arg1 * arg2, C), X)
            if s.is_real and arg1.subs(X, s) > 0 and arg2.subs(X, s) > 0]
    assert sols == [x0]                       # the other root is out of the domain
    return make(
        "equations",
        WRAP.format(rf"\log_{{{b}}}({_l(arg1)}) + \log_{{{b}}}({_l(arg2)}) = \log_{{{b}}} {C}"),
        rf"$x = {x0}$",
        hint_latex=r"$\log_b A + \log_b B = \log_b(AB)$; impuneți condițiile de existență "
                   r"($A > 0$, $B > 0$).",
        steps_latex=[rf"$({_l(arg1)})({_l(arg2)}) = {C}$", rf"$x = {x0}$"],
    )


_TIERS = {
    1: [_exp_simple, _exp_prod, _log_simple, _irr_simple, _abs_eq],
    2: [_exp_quadratic, _log_linear, _log_sum, _irr_extraneous],
    3: [_exp_quadratic, _log_linear, _log_sum, _irr_extraneous],
}
# M3: single-step only, base ∈ {2,3,10} (info-on-sub1 §3 restriction).
_TIERS_M3 = {1: [_exp_simple, _exp_prod, _log_simple, _log_linear, _irr_simple, _abs_eq]}


class EquationsGenerator(TieredExerciseGenerator):
    TOPIC_CODE = "equations"
    SUPPORTED_PROFILES = ["mate-info", "tehnologic", "stiintele-naturii", "pedagogic"]

    def _tiers(self):
        return _TIERS_M3 if self.profile == "pedagogic" else _TIERS
