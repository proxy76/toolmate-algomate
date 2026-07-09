"""Complex numbers — single-item class (spec §3.2, §7.3). M1 (full) / M2 (algebraic).

D1: sum/difference, modulus, conjugate (algebraic form).
D2: product, square, quotient to algebraic form, powers of i.
D3 (M1 only): De Moivre powers of (1+i), solving z² = a+bi.
M2 = algebraic form only (no trigonometric form / De Moivre), spec §4.2.
"""
from __future__ import annotations

import sympy as sp

from ..base import TieredExerciseGenerator
from .._utils import latex, make, nonzero, pick


def _z(a, b):
    return sp.Integer(a) + sp.Integer(b) * sp.I


def _d1_addsub(rng):
    a, b, c, d = (nonzero(rng, -7, 7) for _ in range(4))
    op = pick(rng, ["+", "-"])
    z1, z2 = _z(a, b), _z(c, d)
    ans = sp.simplify(z1 + z2 if op == "+" else z1 - z2)
    return make("complex", rf"Calculează $({latex(z1)}) {op} ({latex(z2)})$.", rf"${latex(ans)}$",
                hint_latex=r"Adună (scade) separat partea reală și partea imaginară.")


def _d1_modulus(rng):
    a, b = nonzero(rng, -7, 7), nonzero(rng, -7, 7)
    z = _z(a, b)
    mod = sp.sqrt(a * a + b * b)
    return make("complex", rf"Calculează modulul $|z|$ pentru $z = {latex(z)}$.",
                rf"$|z| = {latex(sp.simplify(mod))}$", hint_latex=r"$|a + bi| = \sqrt{a^2 + b^2}$.")


def _d1_conjugate(rng):
    a, b = nonzero(rng, -7, 7), nonzero(rng, -7, 7)
    z = _z(a, b)
    return make("complex", rf"Determină conjugatul $\bar z$ pentru $z = {latex(z)}$.",
                rf"$\bar z = {latex(sp.conjugate(z))}$", hint_latex=r"$\overline{a + bi} = a - bi$.")


def _d2_product(rng):
    a, b, c, d = (nonzero(rng, -5, 5) for _ in range(4))
    z1, z2 = _z(a, b), _z(c, d)
    return make("complex", rf"Calculează $({latex(z1)})({latex(z2)})$.",
                rf"${latex(sp.expand(z1 * z2))}$",
                hint_latex=r"Desfă parantezele și folosește $i^2 = -1$.")


def _d2_square(rng):
    a, b = nonzero(rng, -5, 5), nonzero(rng, -5, 5)
    z = _z(a, b)
    return make("complex", rf"Calculează $z^2$ pentru $z = {latex(z)}$.",
                rf"${latex(sp.expand(z**2))}$", hint_latex=r"$(a+bi)^2 = a^2 - b^2 + 2ab\,i$.")


def _d2_quotient(rng):
    a, b, c, d = (nonzero(rng, -5, 5) for _ in range(4))
    z1, z2 = _z(a, b), _z(c, d)
    return make("complex", rf"Adu la forma algebrică $\dfrac{{{latex(z1)}}}{{{latex(z2)}}}$.",
                rf"${latex(sp.simplify(z1 / z2))}$",
                hint_latex=r"Amplifică cu conjugatul numitorului: "
                           r"$\frac{z_1}{z_2}=\frac{z_1\bar z_2}{|z_2|^2}$.")


def _d2_power_i(rng):
    nval = rng.randint(5, 30)
    return make("complex", rf"Calculează $i^{{{nval}}}$.", rf"${latex(sp.I**nval)}$",
                hint_latex=r"Puterile lui $i$ se repetă cu perioada 4: $i^n = i^{n \bmod 4}$.")


def _d2_show_natural(rng):
    # T1.M1.a — (a−bi)(a+bi) = a²+b² is always a natural number.
    a, b = rng.randint(1, 6), rng.randint(1, 6)
    z1, z2 = _z(a, -b), _z(a, b)
    val = sp.expand(z1 * z2)
    assert sp.im(val) == 0 and val > 0
    return make("complex",
                rf"Arătați că numărul $z = ({latex(z1)})({latex(z2)})$ este natural.",
                rf"$z = {latex(val)}$",
                hint_latex=r"$(a - bi)(a + bi) = a^2 + b^2$.")


def _d2_show_real(rng):
    # Real-mate-info style "2(1−2i)+i(4+i)" — expand, group, show it is an integer.
    m = rng.randint(2, 4)
    a = nonzero(rng, -4, 4)
    b = rng.randint(1, 4)
    d = nonzero(rng, -4, 4)
    c = -m * b                               # makes m·z1 + i·z2 purely real
    z1, z2 = _z(a, b), _z(c, d)
    val = sp.expand(m * z1 + sp.I * z2)
    assert sp.im(val) == 0 and val != 0
    return make("complex",
                rf"Arătați că numărul $z = {m}({latex(z1)}) + i({latex(z2)})$ este real.",
                rf"$z = {latex(val)}$",
                hint_latex=r"Efectuați calculele folosind $i^2 = -1$ și grupați partea reală "
                           r"cu partea imaginară.")


def _d3_de_moivre(rng):
    nval = pick(rng, [2, 4, 6, 8])
    ans = sp.expand((1 + sp.I) ** nval)
    return make("complex", rf"Calculează $(1 + i)^{{{nval}}}$.", rf"${latex(ans)}$",
                hint_latex=r"$1+i = \sqrt2\left(\cos\frac{\pi}{4} + i\sin\frac{\pi}{4}\right)$, "
                           r"apoi De Moivre.",
                steps_latex=[r"$(1+i)^2 = 2i$",
                             rf"$(1+i)^{{{nval}}} = (2i)^{{{nval//2}}} = {latex(ans)}$"])


def _d3_solve_square(rng):
    p, q = nonzero(rng, 1, 4), nonzero(rng, 1, 4)
    z0 = _z(p, q)
    target = sp.expand(z0**2)
    return make("complex", rf"Rezolvă în $\mathbb{{C}}$: $z^2 = {latex(target)}$.",
                rf"$z \in \{{{latex(z0)},\ {latex(-z0)}\}}$",
                hint_latex=r"Caută $z = x + yi$ cu $x,y\in\mathbb{R}$ și identifică "
                           r"părțile reală și imaginară.")


# --- authentic Subiectul I pos-1 "Arătați că"/modulus/find-(a,b) items --------
# The real papers overwhelmingly phrase pos-1 complex items as "Se consideră
# numerele complexe … Arătați că <expr> = <val>", "Calculați modulul …", or
# "Determinați numerele reale a și b pentru care …" — not "Calculează (z1)(z2)".

def _p1_show_expand_real(rng):
    # (a+bi)² + i(c+di) = a²−b²−d  (c = −2ab so the imaginary parts cancel).
    a, b = nonzero(rng, -3, 3), nonzero(rng, -3, 3)
    d = nonzero(rng, -4, 4)
    c = -2 * a * b
    z1, z2 = _z(a, b), _z(c, d)
    val = sp.expand(z1**2 + sp.I * z2)
    assert sp.im(val) == 0
    return make("complex",
                rf"Arătați că $({latex(z1)})^2 + i({latex(z2)}) = {latex(val)}$, unde $i^2 = -1$.",
                rf"${latex(val)}$",
                hint_latex=r"Dezvoltați pătratul, efectuați înmulțirea cu $i$ și folosiți "
                           r"$i^2 = -1$; părțile imaginare se reduc.")


def _p1_show_product_two(rng):
    # Two complex numbers declared; show their product equals a computed value.
    a, b, c, d = (nonzero(rng, -4, 4) for _ in range(4))
    z1, z2 = _z(a, b), _z(c, d)
    val = sp.expand(z1 * z2)
    return make("complex",
                rf"Se consideră numerele complexe $z_1 = {latex(z1)}$ și $z_2 = {latex(z2)}$. "
                rf"Arătați că $z_1\cdot z_2 = {latex(val)}$.",
                rf"$z_1\cdot z_2 = {latex(val)}$",
                hint_latex=r"Desfaceți parantezele și folosiți $i^2 = -1$.")


def _p1_modulus_of_expr(rng):
    # z = (a+bi)(a−bi) − (p+qi) = (a²+b²−p) − qi ; choose a Pythagorean (re, im).
    re0, im0, mod = pick(rng, [(3, 4, 5), (4, 3, 5), (5, 12, 13), (8, 6, 10),
                               (6, 8, 10), (12, 5, 13)])
    a = pick(rng, [1, 2, 3])
    b = pick(rng, [1, 2, 3])
    p = a * a + b * b - re0          # so real part = re0
    q = -im0                          # imaginary part = im0 (from −(p+qi))
    z1, z2 = _z(a, b), _z(a, -b)
    sub = _z(p, q)
    z = sp.expand(z1 * z2 - sub)
    assert sp.Abs(z) == mod
    return make("complex",
                rf"Calculați modulul numărului complex $z = ({latex(z1)})({latex(z2)}) - "
                rf"({latex(sub)})$.",
                rf"$|z| = {mod}$",
                hint_latex=r"Aduceți $z$ la forma algebrică, apoi $|a + bi| = \sqrt{a^2 + b^2}$.",
                steps_latex=[rf"$z = {latex(z)}$", rf"$|z| = {mod}$"])


def _p1_find_ab(rng):
    # (a+bi)(c+di) = val ; recover the reals a, b.
    a0, b0 = nonzero(rng, -4, 4), nonzero(rng, -4, 4)
    c, d = pick(rng, [(1, 1), (1, -1), (2, 1), (1, 2)])
    mult = _z(c, d)
    val = sp.expand(_z(a0, b0) * mult)
    return make("complex",
                rf"Determinați numerele reale $a$ și $b$ pentru care "
                rf"$(a + bi)({latex(mult)}) = {latex(val)}$, unde $i^2 = -1$.",
                rf"$a = {a0},\ b = {b0}$",
                hint_latex=r"Desfaceți parantezele, grupați partea reală și partea imaginară, "
                           r"apoi identificați-le cu cele ale membrului drept.")


_P1_SHOW = [_p1_show_expand_real, _p1_show_product_two, _p1_modulus_of_expr, _p1_find_ab]

_TIERS_FULL = {
    1: [_d1_addsub, _d1_modulus, _d1_conjugate] + _P1_SHOW,
    # Tier 2 is what M1 Subiectul I pos-1 draws — the authentic "show/modulus/
    # find (a,b)" items dominate (weighted ×2), with a lighter presence of the
    # algebraic-form computations.
    2: 2 * _P1_SHOW + [_d2_product, _d2_square, _d2_quotient, _d2_power_i,
                       _d2_show_natural, _d2_show_real],
    3: [_d3_de_moivre, _d3_solve_square] + _P1_SHOW,
}


class ComplexNumbersGenerator(TieredExerciseGenerator):
    TOPIC_CODE = "complex"
    SUPPORTED_PROFILES = ["mate-info", "tehnologic", "stiintele-naturii"]

    def _tiers(self):
        if self.profile in ("tehnologic", "stiintele-naturii"):   # algebraic form only
            return {1: _TIERS_FULL[1], 2: _TIERS_FULL[2]}
        return _TIERS_FULL
