"""Numeric computation — single-item class (M2/M3 Subiectul I position 1).

The real M_tehnologic papers open with a numeric identity ``Arătați că <expr> = <int>``:
a **fraction** computation, a **radical** simplification, or (occasionally) a Viète
identity on a quadratic with integer roots. Every expression is built by design and
re-verified with sympy to a small integer. No complex numbers (that is M1's opener).
"""
from __future__ import annotations

import sympy as sp

from ..base import TieredExerciseGenerator
from .._utils import make, pick

WRAP = r"Arătați că ${}$ = ${}$."


def _show(expr_tex: str, value) -> dict:
    return make("arithmetic", rf"Arătați că ${expr_tex} = {sp.latex(value)}$.",
                rf"${sp.latex(value)}$",
                hint_latex=r"Efectuați calculele respectând ordinea operațiilor.")


def _frac(num: int, den: int) -> str:
    return rf"\dfrac{{{num}}}{{{den}}}" if den != 1 else f"{num}"


# --- fraction arithmetic -----------------------------------------------------
def _a_frac_sum(rng):
    # A·(1/p ± 1/q) = int   (choose A a multiple of the combined denominator).
    p, q = rng.sample([2, 3, 4, 5, 6], 2)
    op = pick(rng, ["+", "-"])
    inner = sp.Rational(1, p) + (sp.Rational(1, q) if op == "+" else -sp.Rational(1, q))
    if inner == 0:
        raise ValueError("degenerate")
    mult = rng.randint(1, 4) * inner.q          # A a multiple of the denominator
    val = sp.nsimplify(mult * inner)
    if not (val.is_integer and 1 <= abs(val) <= 12):
        raise ValueError("not clean")
    return _show(rf"{mult}\left({_frac(1, p)} {op} {_frac(1, q)}\right)", val)


def _a_frac_mixed(rng):
    # A − B·(1 + 1/p) = int   or   1/p + A·(1/q − 1/r) = int.
    if rng.random() < 0.5:
        p = rng.choice([2, 3, 4])
        B = rng.randint(1, 4) * p               # B·(1+1/p) = B + B/p integer
        A = B + B // p + rng.randint(0, 4)
        val = sp.nsimplify(A - B * (1 + sp.Rational(1, p)))
        if not (val.is_integer and 0 <= abs(val) <= 12):
            raise ValueError("not clean")
        return _show(rf"{A} - {B}\left(1 + {_frac(1, p)}\right)", val)
    p, q, r = rng.sample([2, 3, 4, 6], 3)
    inner = sp.Rational(1, q) - sp.Rational(1, r)
    if inner == 0:
        raise ValueError("degenerate")
    A = rng.randint(1, 5) * inner.q
    val = sp.nsimplify(sp.Rational(1, p) + A * inner)
    if not (val.is_integer and 1 <= abs(val) <= 12):
        raise ValueError("not clean")
    return _show(rf"{_frac(1, p)} + {A}\left({_frac(1, q)} - {_frac(1, r)}\right)", val)


def _a_frac_div(rng):
    # A·(B − p/q : r/s) = int, using the "împărțire de fracții" step. Both fractions
    # are proper and reduced (no degenerate 1/1 or 2/2).
    f1 = sp.Rational(rng.randint(1, 3), rng.choice([2, 3, 4]))
    f2 = sp.Rational(rng.randint(1, 3), rng.choice([2, 3, 4]))
    if f1.q == 1 or f2.q == 1 or f2 == 1:
        raise ValueError("not proper")
    quot = f1 / f2
    B = rng.randint(1, 4)
    inner = B - quot
    if inner == 0:
        raise ValueError("degenerate")
    A = rng.randint(1, 4) * inner.q
    val = sp.nsimplify(A * inner)
    if not (val.is_integer and 1 <= abs(val) <= 12):
        raise ValueError("not clean")
    return _show(rf"{A}\left({B} - {_frac(f1.p, f1.q)} : {_frac(f2.p, f2.q)}\right)", val)


# --- radical simplification --------------------------------------------------
def _a_radical(rng):
    # k(a − √(m·b²)) + √(m·c²) = int, arranged so the √m terms cancel.
    m = rng.choice([2, 3, 5])
    k = rng.randint(1, 3)
    b, c = rng.randint(1, 3), rng.randint(1, 4)
    if k * b != c:                              # need k·b√m to cancel c√m
        c = k * b
    a = rng.randint(1, 4)
    A, C = m * b * b, m * c * c
    val = sp.nsimplify(k * (a - sp.sqrt(A)) + sp.sqrt(C))
    assert val.is_integer
    kc = "" if k == 1 else str(k)
    return _show(rf"{kc}\left({a} - \sqrt{{{A}}}\right) + \sqrt{{{C}}}", sp.Integer(val))


def _a_radical_conj(rng):
    # (n − k√m)(n + k√m) = n² − k²m  (integer), authentic pos-1 conjugate product.
    m = rng.choice([2, 3, 5, 6])
    n = rng.randint(2, 6)
    k = rng.randint(1, 2)
    val = n * n - k * k * m
    kc = "" if k == 1 else str(k)
    return _show(rf"\left({n} - {kc}\sqrt{{{m}}}\right)\left({n} + {kc}\sqrt{{{m}}}\right)",
                 sp.Integer(val))


# --- Viète on a quadratic with integer roots ---------------------------------
def _a_viete(rng):
    r1, r2 = sorted(rng.sample([1, 2, 3, 4, 5], 2))
    S, P = r1 + r2, r1 * r2
    p, q = rng.randint(1, 3), rng.randint(1, 2)
    val = p * S - q * P
    body = f"{p if p != 1 else ''}(x_1 + x_2) - {q if q != 1 else ''}x_1 x_2"
    sgn = "-" if val < 0 else ""
    return make("arithmetic",
                rf"Se consideră $x_1$ și $x_2$ soluțiile ecuației $x^2 - {S}x + {P} = 0$. "
                rf"Arătați că ${body} = {sp.latex(sp.Integer(val))}$.",
                rf"${sp.latex(sp.Integer(val))}$",
                hint_latex=r"Relațiile lui Viète: $x_1 + x_2 = S$, $x_1 x_2 = P$.")


# --- logarithmic identity (base 2 / 3 / 10) ----------------------------------
def _a_log_identity(rng):
    # ± log_b(b^e) terms summing to a small integer — e.g. log_2 16 − log_2 8 = 1.
    b = rng.choice([2, 3, 10])
    k = rng.choice([2, 3])
    parts, total, expr = [], 0, sp.Integer(0)
    for i in range(k):
        e = rng.randint(1, 3)
        A = b ** e
        sign = 1 if i == 0 else pick(rng, [1, 1, -1])
        parts.append((rf"\log_{{{b}}} {A}" if i == 0
                      else rf"{'+' if sign > 0 else '-'} \log_{{{b}}} {A}"))
        total += sign * e
        expr += sign * sp.log(A, b)
    if not (1 <= total <= 6):
        raise ValueError("not clean")
    if rng.random() < 0.4:                       # a log_b 1 = 0 term, as in the papers
        parts.append(rf"+ \log_{{{b}}} 1")
        expr += sp.log(1, b)
    if sp.simplify(expr - total) != 0:
        raise ValueError("unverified")
    return _show(" ".join(parts), sp.Integer(total))


# --- radical sum with a radical answer (√18 + √8 = 5√2) -----------------------
def _a_radical_sum(rng):
    m = rng.choice([2, 3, 5])
    a, b = rng.randint(1, 4), rng.randint(1, 4)
    c = rng.randint(1, a + b - 1) if (a + b > 1 and rng.random() < 0.5) else 0
    k = a + b - c
    if k <= 0:
        raise ValueError("degenerate")
    terms = rf"\sqrt{{{m * a * a}}} + \sqrt{{{m * b * b}}}"
    expr = sp.sqrt(m * a * a) + sp.sqrt(m * b * b)
    if c:
        terms += rf" - \sqrt{{{m * c * c}}}"
        expr -= sp.sqrt(m * c * c)
    ans = rf"{k if k != 1 else ''}\sqrt{{{m}}}"
    if sp.simplify(expr - k * sp.sqrt(m)) != 0:
        raise ValueError("unverified")
    return make("arithmetic", rf"Arătați că ${terms} = {ans}$.", rf"${ans}$",
                hint_latex=r"Scoateți factorii de sub radical: $\sqrt{a^2 m} = a\sqrt{m}$.")


# --- sum of conjugate squares (integer) --------------------------------------
def _a_sqrt_squares(rng):
    # (a + √m)² + (a − √m)² = 2a² + 2m — the double-product cancels.
    m = rng.choice([2, 3, 5, 6, 7])
    a = rng.randint(1, 5)
    val = 2 * a * a + 2 * m
    expr = (a + sp.sqrt(m)) ** 2 + (a - sp.sqrt(m)) ** 2
    assert sp.simplify(expr - val) == 0
    return _show(rf"\left({a} + \sqrt{{{m}}}\right)^2 + \left({a} - \sqrt{{{m}}}\right)^2",
                 sp.Integer(val))


# --- power law numeric identity (2³·2² : 2⁴ = 2) -----------------------------
def _a_power(rng):
    a = rng.choice([2, 3])
    m, n, k = rng.randint(1, 3), rng.randint(1, 3), rng.randint(0, 2)
    e = m + n - k
    if not (0 <= e <= 4):
        raise ValueError("not clean")
    ktex = rf" : {a}^{{{k}}}" if k else ""
    return _show(rf"{a}^{{{m}}} \cdot {a}^{{{n}}}{ktex}", sp.Integer(a ** e))


_TIERS = {
    1: [_a_frac_sum, _a_frac_mixed, _a_frac_div, _a_radical, _a_radical_conj, _a_viete,
        _a_log_identity, _a_radical_sum, _a_sqrt_squares, _a_power],
}


class ArithmeticGenerator(TieredExerciseGenerator):
    TOPIC_CODE = "arithmetic"
    SUPPORTED_PROFILES = ["tehnologic", "stiintele-naturii", "pedagogic"]

    def _tiers(self):
        return _TIERS
