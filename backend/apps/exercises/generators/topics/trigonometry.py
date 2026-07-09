"""Trigonometry — single-item class (spec §7.3; Subiectul I pos 6, info-on-sub1 §6).

Subiectul I position 6 draws from a broad tier-1 pool so successive mock exams
look genuinely different (the previous version only had remarkable-value items):

- right-triangle tasks — trig ratio (``sin C = 3/5``), perimeter, side from
  ``tg B``, the 30/60 "double angle" side (§6.1 T6.a–e);
- remarkable-value expressions — combinations and ``E(x)=a\\sin x+b\\cos x`` at
  ``π/k`` (§6.2 T6.id3);
- identity / area items, some with radical answers (§6.1 T6.f/h);
- a simple equation on ``[0, 2π)``.

D2/D3 keep the harder equations. M3 stays on remarkable values only (§5.2).
Every value is computed and checked with sympy; radical answers are allowed but
kept short.
"""
from __future__ import annotations

from math import gcd

import sympy as sp

from ..base import TieredExerciseGenerator
from .._utils import latex, make, pick

# Remarkable angles with clean sin/cos.
_SPECIAL = [
    (sp.pi / 6, r"\frac{\pi}{6}"), (sp.pi / 4, r"\frac{\pi}{4}"),
    (sp.pi / 3, r"\frac{\pi}{3}"), (sp.pi / 2, r"\frac{\pi}{2}"),
    (2 * sp.pi / 3, r"\frac{2\pi}{3}"), (3 * sp.pi / 4, r"\frac{3\pi}{4}"),
    (5 * sp.pi / 6, r"\frac{5\pi}{6}"), (sp.pi, r"\pi"),
]
# Angles usable for tangent (drop π/2 where tg is undefined).
_SPECIAL_TG = [a for a in _SPECIAL if a[0] != sp.pi / 2]
# Right-triangle leg/leg/hypotenuse triples → clean ratios & sides.
_TRIPLES = [(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17),
            (7, 24, 25), (9, 12, 15), (20, 21, 29), (10, 24, 26)]


# --- remarkable values -------------------------------------------------------
def _t_value(rng):
    fn_name, fn, pool = pick(rng, [
        ("sin", sp.sin, _SPECIAL), ("cos", sp.cos, _SPECIAL),
        ("tg", sp.tan, _SPECIAL_TG),
    ])
    angle, angle_tex = pick(rng, pool)
    val = sp.simplify(fn(angle))
    assert val.is_finite
    fn_tex = r"\operatorname{tg}" if fn_name == "tg" else rf"\{fn_name}"
    return make("trigonometry",
                rf"Calculați ${fn_tex}\left({angle_tex}\right)$.",
                rf"${latex(val)}$", hint_latex=r"Folosiți tabelul valorilor remarcabile.")


def _t_value_expr(rng):
    # p·f(α) ± q·g(β) with clean remarkable values; keep the result short.
    clean = [(sp.pi / 6, r"\frac{\pi}{6}"), (sp.pi / 3, r"\frac{\pi}{3}"),
             (sp.pi / 4, r"\frac{\pi}{4}"), (sp.pi / 2, r"\frac{\pi}{2}"), (sp.pi, r"\pi")]
    (a1, t1), (a2, t2) = pick(rng, clean), pick(rng, clean)
    f1n, f1 = pick(rng, [("sin", sp.sin), ("cos", sp.cos)])
    f2n, f2 = pick(rng, [("sin", sp.sin), ("cos", sp.cos)])
    p, q = rng.randint(1, 4), rng.randint(1, 4)
    op = pick(rng, ["+", "-"])
    expr = p * f1(a1) + (q * f2(a2) if op == "+" else -q * f2(a2))
    val = sp.simplify(expr)
    assert val.is_finite and len(latex(val)) < 30
    pc = "" if p == 1 else str(p)
    qc = "" if q == 1 else str(q)
    return make("trigonometry",
                rf"Calculați ${pc}\{f1n}\left({t1}\right) {op} {qc}\{f2n}\left({t2}\right)$.",
                rf"${latex(val)}$",
                hint_latex=r"Înlocuiți cu valorile remarcabile și efectuați calculul.")


def _t_expr_eval(rng):
    ang, angtex = pick(rng, [(sp.pi / 6, r"\frac{\pi}{6}"), (sp.pi / 3, r"\frac{\pi}{3}"),
                             (sp.pi / 2, r"\frac{\pi}{2}"), (sp.pi, r"\pi")])
    p, q = rng.randint(1, 4), rng.randint(1, 4)
    val = sp.simplify(p * sp.sin(ang) + q * sp.cos(ang))
    assert val.is_finite and len(latex(val)) < 30
    return make("trigonometry",
                rf"Se consideră expresia $E(x) = {p}\sin x + {q}\cos x$. Arătați că "
                rf"$E\left({angtex}\right) = {latex(val)}$.",
                rf"$E\left({angtex}\right) = {latex(val)}$",
                hint_latex=r"Înlocuiți $x$ cu valoarea dată și folosiți valorile remarcabile.")


# --- right triangle ----------------------------------------------------------
def _t_rt_ratio(rng):
    a, b, c = pick(rng, _TRIPLES)          # legs a=AB, b=AC; hyp c=BC (right angle A)
    vertex, fn = pick(rng, ["B", "C"]), pick(rng, ["sin", "cos", "tg"])
    if vertex == "B":                      # opposite AC=b, adjacent AB=a
        num, den = {"sin": (b, c), "cos": (a, c), "tg": (b, a)}[fn]
    else:                                  # angle C: opposite AB=a, adjacent AC=b
        num, den = {"sin": (a, c), "cos": (b, c), "tg": (a, b)}[fn]
    g = gcd(num, den)
    frac = rf"\dfrac{{{num // g}}}{{{den // g}}}"
    fn_tex = r"\operatorname{tg}" if fn == "tg" else rf"\{fn}"
    return make("trigonometry",
                rf"Se consideră triunghiul $ABC$, dreptunghic în $A$, cu $AB = {a}$ și "
                rf"$AC = {b}$. Arătați că ${fn_tex} {vertex} = {frac}$.",
                rf"${fn_tex} {vertex} = {frac}$",
                hint_latex=rf"$BC = \sqrt{{AB^2 + AC^2}} = {c}$, apoi scrieți raportul cerut.",
                steps_latex=[rf"$BC = \sqrt{{{a}^2 + {b}^2}} = {c}$",
                             rf"${fn_tex} {vertex} = \dfrac{{{num}}}{{{den}}} = {frac}$"])


def _t_rt_perimeter(rng):
    a, b, c = pick(rng, _TRIPLES)
    p = a + b + c
    return make("trigonometry",
                rf"Se consideră triunghiul $ABC$, dreptunghic în $A$, cu $AB = {a}$ și "
                rf"$BC = {c}$. Arătați că perimetrul triunghiului $ABC$ este egal cu ${p}$.",
                rf"$P_{{ABC}} = {p}$",
                hint_latex=rf"$AC = \sqrt{{BC^2 - AB^2}} = {b}$, apoi $P = AB + AC + BC$.",
                steps_latex=[rf"$AC = \sqrt{{{c}^2 - {a}^2}} = {b}$",
                             rf"$P = {a} + {b} + {c} = {p}$"])


def _t_rt_tan_side(rng):
    a, b, c = pick(rng, _TRIPLES)          # tg B = AC/AB = b/a
    g = gcd(b, a)
    return make("trigonometry",
                rf"Se consideră triunghiul $ABC$, dreptunghic în $A$, cu $AB = {a}$ și "
                rf"$\operatorname{{tg}} B = \dfrac{{{b // g}}}{{{a // g}}}$. Arătați că $BC = {c}$.",
                rf"$BC = {c}$",
                hint_latex=r"$\operatorname{tg} B = \dfrac{AC}{AB} \Rightarrow AC$, "
                           r"apoi teorema lui Pitagora.",
                steps_latex=[rf"$AC = AB \cdot \operatorname{{tg}} B = {b}$",
                             rf"$BC = \sqrt{{{a}^2 + {b}^2}} = {c}$"])


def _t_rt_two_angles(rng):
    bc = rng.choice([4, 6, 8, 10, 12])     # C = 2B, right angle A ⇒ B=30°, C=60°
    ac = sp.Rational(bc, 2)                 # AC = BC·sin 30° = BC/2
    return make("trigonometry",
                rf"Se consideră triunghiul $ABC$, dreptunghic în $A$, cu $BC = {bc}$ și "
                rf"măsura unghiului $C$ de două ori mai mare decât măsura unghiului $B$. "
                rf"Determinați lungimea laturii $AC$.",
                rf"$AC = {latex(ac)}$",
                hint_latex=r"Din $C = 2B$ și $B + C = 90^\circ$ rezultă $B = 30^\circ$; "
                           r"$AC = BC \cdot \sin B$.",
                steps_latex=[r"$B = 30^\circ,\ C = 60^\circ$",
                             rf"$AC = {bc} \cdot \sin 30^\circ = {latex(ac)}$"])


# --- area / identity (may be radical) ----------------------------------------
def _t_area_angle(rng):
    ab, ac = rng.randint(2, 8), rng.randint(2, 8)
    ang_tex, sinv = pick(rng, [
        (r"\frac{\pi}{6}", sp.Rational(1, 2)), (r"\frac{\pi}{2}", sp.Integer(1)),
        (r"\frac{5\pi}{6}", sp.Rational(1, 2)), (r"\frac{\pi}{3}", sp.sqrt(3) / 2),
        (r"\frac{2\pi}{3}", sp.sqrt(3) / 2),
    ])
    area = sp.simplify(sp.Rational(1, 2) * ab * ac * sinv)
    assert area.is_finite and len(latex(area)) < 30
    return make("trigonometry",
                rf"Se consideră triunghiul $ABC$ cu $AB = {ab}$, $AC = {ac}$ și "
                rf"$\widehat{{A}} = {ang_tex}$. Arătați că aria triunghiului $ABC$ este "
                rf"egală cu ${latex(area)}$.",
                rf"$\mathcal{{A}}_{{ABC}} = {latex(area)}$",
                hint_latex=r"$\mathcal{A} = \dfrac{1}{2}\cdot AB \cdot AC \cdot \sin A$.",
                steps_latex=[rf"$\mathcal{{A}} = \dfrac{{1}}{{2}} \cdot {ab} \cdot {ac} "
                             rf"\cdot {latex(sinv)} = {latex(area)}$"])


def _t_id_complementary(rng):
    # The two acute angles of a right triangle are complementary (u + v = 90°),
    # so pick the right-angle vertex, the acute pair order, and the identity form.
    verts = ["A", "B", "C"]
    r = pick(rng, verts)                       # right-angle vertex
    u, v = [w for w in verts if w != r]
    if rng.random() < 0.5:
        u, v = v, u
    kind = pick(rng, ["tg_inv", "tg_prod", "sin_cos", "cos_sin", "sin2"])
    if kind == "tg_inv":
        body = rf"\operatorname{{tg}} {u} = \dfrac{{1}}{{\operatorname{{tg}} {v}}}"
        hint = (rf"${u} + {v} = 90^\circ \Rightarrow \operatorname{{tg}} {u} = "
                rf"\operatorname{{ctg}} {v} = \dfrac{{1}}{{\operatorname{{tg}} {v}}}$.")
    elif kind == "tg_prod":
        body = rf"\operatorname{{tg}} {u} \cdot \operatorname{{tg}} {v} = 1"
        hint = (rf"${u} + {v} = 90^\circ \Rightarrow \operatorname{{tg}} {u} = "
                rf"\operatorname{{ctg}} {v}$, deci produsul este $1$.")
    elif kind == "sin_cos":
        body = rf"\sin {u} = \cos {v}"
        hint = rf"Unghiurile ${u}$ și ${v}$ sunt complementare: ${u} + {v} = 90^\circ$."
    elif kind == "cos_sin":
        body = rf"\cos {u} = \sin {v}"
        hint = rf"Unghiurile ${u}$ și ${v}$ sunt complementare: ${u} + {v} = 90^\circ$."
    else:  # sin2
        body = rf"\sin^2 {u} + \sin^2 {v} = 1"
        hint = (rf"$\sin {v} = \cos {u}$ (unghiuri complementare), apoi "
                rf"$\sin^2 {u} + \cos^2 {u} = 1$.")
    # Numeric sympy check with a concrete acute angle θ and its complement.
    th, comp = sp.pi / 5, sp.pi / 2 - sp.pi / 5
    checks = {
        "tg_inv": sp.tan(th) - 1 / sp.tan(comp),
        "tg_prod": sp.tan(th) * sp.tan(comp) - 1,
        "sin_cos": sp.sin(th) - sp.cos(comp),
        "cos_sin": sp.cos(th) - sp.sin(comp),
        "sin2": sp.sin(th) ** 2 + sp.sin(comp) ** 2 - 1,
    }
    assert sp.simplify(checks[kind]) == 0
    return make("trigonometry",
                rf"Se consideră triunghiul $ABC$, dreptunghic în ${r}$. Arătați că ${body}$.",
                rf"${body}$", hint_latex=hint)


# --- Pythagorean identity & equations ----------------------------------------
def _t_pyth_ratio(rng):
    a, b, c = pick(rng, [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)])
    given, gnum = pick(rng, [("sin", a), ("cos", b)])
    other, onum = ("cos", b) if given == "sin" else ("sin", a)
    return make("trigonometry",
                rf"Știind că $\{given} x = \dfrac{{{gnum}}}{{{c}}}$ și "
                rf"$x \in \left(0, \dfrac{{\pi}}{{2}}\right)$, calculați $\{other} x$.",
                rf"$\{other} x = \dfrac{{{onum}}}{{{c}}}$",
                hint_latex=r"$\sin^2 x + \cos^2 x = 1$; pe $\left(0,\frac{\pi}{2}\right)$ "
                           r"ambele funcții sunt pozitive.",
                steps_latex=[rf"$\{other}^2 x = 1 - \dfrac{{{gnum**2}}}{{{c*c}}} "
                             rf"= \dfrac{{{onum**2}}}{{{c*c}}}$",
                             rf"$\{other} x = \dfrac{{{onum}}}{{{c}}}$"])


def _t_simple_equation(rng):
    eq, sols = pick(rng, [
        (r"2\sin x = 1", r"\frac{\pi}{6},\ \frac{5\pi}{6}"),
        (r"2\cos x = 1", r"\frac{\pi}{3},\ \frac{5\pi}{3}"),
        (r"\sqrt2\,\sin x = 1", r"\frac{\pi}{4},\ \frac{3\pi}{4}"),
        (r"2\cos x = -1", r"\frac{2\pi}{3},\ \frac{4\pi}{3}"),
        (r"2\sin x = -1", r"\frac{7\pi}{6},\ \frac{11\pi}{6}"),
    ])
    return make("trigonometry", rf"Rezolvați în $[0, 2\pi)$ ecuația ${eq}$.",
                rf"$x \in \left\{{{sols}\right\}}$",
                hint_latex=r"Aduceți la forma $\sin x = a$ / $\cos x = a$ și "
                           r"identificați unghiurile din cerc.")


def _t_trig_from_ratio(rng):
    a, b, c = pick(rng, [(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17), (20, 21, 29)])
    g = gcd(a, b)
    return make("trigonometry",
                rf"Știind că $\sin x = \dfrac{{{a}}}{{{c}}}$ și "
                rf"$x \in \left(0, \dfrac{{\pi}}{{2}}\right)$, calculați $\operatorname{{tg}} x$.",
                rf"$\operatorname{{tg}} x = \dfrac{{{a // g}}}{{{b // g}}}$",
                hint_latex=r"$\cos x = \sqrt{1 - \sin^2 x}$, apoi "
                           r"$\operatorname{tg} x = \dfrac{\sin x}{\cos x}$.",
                steps_latex=[rf"$\cos x = \dfrac{{{b}}}{{{c}}}$",
                             rf"$\operatorname{{tg}} x = \dfrac{{{a}}}{{{b}}} "
                             rf"= \dfrac{{{a // g}}}{{{b // g}}}$"])


def _t_sin_double(rng):
    a, b, c = pick(rng, [(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17), (20, 21, 29)])
    num, den = 2 * a * b, c * c                # sin 2x = 2·sin x·cos x = 2ab/c²
    g = gcd(num, den)
    return make("trigonometry",
                rf"Știind că $\sin x = \dfrac{{{a}}}{{{c}}}$ și "
                rf"$x \in \left(0, \dfrac{{\pi}}{{2}}\right)$, calculați $\sin 2x$.",
                rf"$\sin 2x = \dfrac{{{num // g}}}{{{den // g}}}$",
                hint_latex=r"$\sin 2x = 2\sin x\cos x$, iar $\cos x = \sqrt{1 - \sin^2 x}$.",
                steps_latex=[rf"$\cos x = \dfrac{{{b}}}{{{c}}}$",
                             rf"$\sin 2x = 2\cdot\dfrac{{{a}}}{{{c}}}\cdot\dfrac{{{b}}}{{{c}}} "
                             rf"= \dfrac{{{num // g}}}{{{den // g}}}$"])


_X = sp.Symbol("x")


def _t_double_angle(rng):
    # Factorable equations on [0, 2π); every listed root is checked with sympy.
    variants = [
        (sp.sin(2 * _X), sp.sin(_X), r"\sin 2x = \sin x",
         [0, sp.pi / 3, sp.pi, 5 * sp.pi / 3],
         r"$2\sin x\cos x - \sin x = 0 \Rightarrow \sin x\,(2\cos x - 1) = 0$"),
        (sp.sin(2 * _X), sp.cos(_X), r"\sin 2x = \cos x",
         [sp.pi / 6, sp.pi / 2, 5 * sp.pi / 6, 3 * sp.pi / 2],
         r"$2\sin x\cos x - \cos x = 0 \Rightarrow \cos x\,(2\sin x - 1) = 0$"),
        (sp.cos(2 * _X), sp.cos(_X), r"\cos 2x = \cos x",
         [0, 2 * sp.pi / 3, 4 * sp.pi / 3],
         r"$2\cos^2 x - \cos x - 1 = 0 \Rightarrow (\cos x - 1)(2\cos x + 1) = 0$"),
        (sp.cos(2 * _X), sp.sin(_X), r"\cos 2x = \sin x",
         [sp.pi / 6, 5 * sp.pi / 6, 3 * sp.pi / 2],
         r"$\cos 2x = 1 - 2\sin^2 x$; $2\sin^2 x + \sin x - 1 = 0 "
         r"\Rightarrow (2\sin x - 1)(\sin x + 1) = 0$"),
    ]
    lhs, rhs, eqtex, sols, fact = pick(rng, variants)
    for s in sols:
        assert sp.simplify(lhs.subs(_X, s) - rhs.subs(_X, s)) == 0
    sol_l = ",\\ ".join(latex(s) for s in sorted(sols, key=lambda z: float(z)))
    return make("trigonometry", rf"Rezolvați în $[0, 2\pi)$ ecuația ${eqtex}$.",
                rf"$x \in \left\{{{sol_l}\right\}}$", hint_latex=fact,
                steps_latex=[fact, rf"$x \in \left\{{{sol_l}\right\}}$"])


def _t_trig_quadratic(rng):
    variants = [
        (2 * sp.cos(_X) ** 2 - 3 * sp.cos(_X) + 1, r"2\cos^2 x - 3\cos x + 1 = 0",
         [0, sp.pi / 3, 5 * sp.pi / 3],
         r"Notați $t = \cos x$: $2t^2 - 3t + 1 = 0 \Rightarrow t \in \{1, \tfrac12\}$."),
        (2 * sp.sin(_X) ** 2 - 3 * sp.sin(_X) + 1, r"2\sin^2 x - 3\sin x + 1 = 0",
         [sp.pi / 6, sp.pi / 2, 5 * sp.pi / 6],
         r"Notați $t = \sin x$: $2t^2 - 3t + 1 = 0 \Rightarrow t \in \{1, \tfrac12\}$."),
        (2 * sp.sin(_X) ** 2 + sp.sin(_X) - 1, r"2\sin^2 x + \sin x - 1 = 0",
         [sp.pi / 6, 5 * sp.pi / 6, 3 * sp.pi / 2],
         r"Notați $t = \sin x$: $2t^2 + t - 1 = 0 \Rightarrow t \in \{-1, \tfrac12\}$."),
        (2 * sp.cos(_X) ** 2 - sp.cos(_X) - 1, r"2\cos^2 x - \cos x - 1 = 0",
         [0, 2 * sp.pi / 3, 4 * sp.pi / 3],
         r"Notați $t = \cos x$: $2t^2 - t - 1 = 0 \Rightarrow t \in \{1, -\tfrac12\}$."),
    ]
    expr, eqtex, sols, hint = pick(rng, variants)
    for s in sols:
        assert sp.simplify(expr.subs(_X, s)) == 0
    sol_l = ",\\ ".join(latex(s) for s in sorted(sols, key=lambda z: float(z)))
    return make("trigonometry", rf"Rezolvați în $[0, 2\pi)$ ecuația ${eqtex}$.",
                rf"$x \in \left\{{{sol_l}\right\}}$", hint_latex=hint,
                steps_latex=[hint, rf"$x \in \left\{{{sol_l}\right\}}$"])


def _t_prove_identity(rng):
    variants = [
        (r"(\sin x + \cos x)^2 = 1 + \sin 2x",
         (sp.sin(_X) + sp.cos(_X)) ** 2, 1 + sp.sin(2 * _X),
         r"Dezvoltați pătratul: $\sin^2 x + \cos^2 x = 1$ și $2\sin x\cos x = \sin 2x$."),
        (r"(\sin x - \cos x)^2 = 1 - \sin 2x",
         (sp.sin(_X) - sp.cos(_X)) ** 2, 1 - sp.sin(2 * _X),
         r"Dezvoltați pătratul și folosiți $2\sin x\cos x = \sin 2x$."),
        (r"\cos^4 x - \sin^4 x = \cos 2x",
         sp.cos(_X) ** 4 - sp.sin(_X) ** 4, sp.cos(2 * _X),
         r"$\cos^4 x - \sin^4 x = (\cos^2 x - \sin^2 x)(\cos^2 x + \sin^2 x) = \cos 2x$."),
        (r"\sin^2 x - \cos^2 x = -\cos 2x",
         sp.sin(_X) ** 2 - sp.cos(_X) ** 2, -sp.cos(2 * _X),
         r"$\cos 2x = \cos^2 x - \sin^2 x$."),
    ]
    tex, lhs, rhs, hint = pick(rng, variants)
    assert sp.simplify(lhs - rhs) == 0
    return make("trigonometry",
                rf"Arătați că ${tex}$, pentru orice număr real $x$.",
                rf"${tex}$", hint_latex=hint)


# Subiectul I position 6 pool (rich — all four content families).
_TIER1 = [
    _t_value, _t_value_expr, _t_expr_eval,
    _t_rt_ratio, _t_rt_perimeter, _t_rt_tan_side, _t_rt_two_angles,
    _t_area_angle, _t_id_complementary,
    _t_pyth_ratio, _t_simple_equation,
]
_TIERS = {
    1: _TIER1,
    2: [_t_pyth_ratio, _t_simple_equation, _t_trig_from_ratio, _t_sin_double,
        _t_trig_quadratic],
    3: [_t_double_angle, _t_trig_quadratic, _t_prove_identity],
}
# M3: remarkable values only (spec §5.2), but with a bit more variety than before.
_TIERS_M3 = {1: [_t_value, _t_value_expr]}


class TrigonometryGenerator(TieredExerciseGenerator):
    TOPIC_CODE = "trigonometry"
    SUPPORTED_PROFILES = ["mate-info", "tehnologic", "stiintele-naturii", "pedagogic"]

    def _tiers(self):
        return _TIERS_M3 if self.profile == "pedagogic" else _TIERS
