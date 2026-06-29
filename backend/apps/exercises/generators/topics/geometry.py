"""Geometry — analytic plane geometry, single-item (spec §9 geometry, §2.2 slot 5/6).

Subiectul I geometry: point-on-line, midpoint, distance, vector equality, and the
right-triangle/Pythagoras item (all profiles; M3 leans on Pythagoras). Difficulty
2 adds collinearity / parallel conditions. Every value is computed with sympy.

Heterogeneous topic → each subtype precomputes its fully-built (and verified)
payload in ``_generate_params``; the ABC hooks just read it.
"""
from __future__ import annotations

import sympy as sp

from ..base import ExerciseGenerator

X = sp.Symbol("x")


def _l(expr) -> str:
    return sp.latex(expr)


# Pythagorean leg/leg/hyp triples → clean integer distances & hypotenuses.
_PYTHAG = [(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17), (9, 12, 15), (7, 24, 25)]


class GeometryGenerator(ExerciseGenerator):
    TOPIC_CODE = "geometry"
    SUPPORTED_PROFILES = ["M1", "M2", "M3"]

    def _generate_params(self) -> dict:
        rng = self.rng
        d1 = [self._st_point_on_line, self._st_midpoint, self._st_distance,
              self._st_vector_point, self._st_pythagoras]
        d2 = [self._st_collinear, self._st_same_midpoint]
        pool = d1 if self.difficulty == 1 else d2 + d1
        return rng.choice(pool)()

    # ABC hooks just surface the precomputed payload.
    def _compute_answer(self, params):
        return params.get("answer")

    def _validate(self, params, answer) -> bool:
        if not params.get("ok", True):
            return False
        return len(params["answer_latex"]) < 220

    def _build_question(self, params) -> str:
        return params["question"]

    def _build_answer_latex(self, params, answer) -> str:
        return params["answer_latex"]

    def _build_hint(self, params) -> str:
        return params.get("hint", "")

    def _build_steps(self, params) -> list[str]:
        return params.get("steps", [])

    # --- subtypes (each returns a verified payload) --------------------------
    def _st_point_on_line(self):
        rng = self.rng
        m = rng.choice([-3, -2, 2, 3])
        a0 = rng.randint(-3, 3)
        n = rng.randint(-4, 4)
        y0 = m * a0 + n
        line = m * X + n
        a = sp.Symbol("a")
        val = sp.solve(sp.Eq(m * a + n, y0), a)[0]
        return {
            "question": rf"În reperul cartezian $xOy$ se consideră dreapta "
                        rf"$d: y = {_l(line)}$ și punctul $A(a, {y0})$. Determinați "
                        rf"numărul real $a$ pentru care punctul $A$ aparține dreptei $d$.",
            "answer_latex": rf"$a = {_l(val)}$",
            "answer": val,
            "hint": r"Punctul aparține dreptei dacă coordonatele lui verifică ecuația dreptei.",
            "steps": [rf"${y0} = {_l(m * a + n)}$", rf"$a = {_l(val)}$"],
            "ok": True,
        }

    def _st_midpoint(self):
        rng = self.rng
        x1, y1 = rng.randint(-5, 5), rng.randint(-5, 5)
        x2 = x1 + rng.choice([-4, -2, 2, 4])
        y2 = y1 + rng.choice([-4, -2, 2, 4])
        mx, my = sp.Rational(x1 + x2, 2), sp.Rational(y1 + y2, 2)
        return {
            "question": rf"Se consideră punctele $A({x1}, {y1})$ și $B({x2}, {y2})$. "
                        rf"Determinați coordonatele mijlocului segmentului $AB$.",
            "answer_latex": rf"$M\left({_l(mx)},\ {_l(my)}\right)$",
            "answer": (mx, my),
            "hint": r"Mijlocul are coordonatele $\left(\frac{x_A+x_B}{2}, \frac{y_A+y_B}{2}\right)$.",
            "steps": [rf"$x_M = \frac{{{x1}+{x2}}}{{2}} = {_l(mx)}$",
                      rf"$y_M = \frac{{{y1}+{y2}}}{{2}} = {_l(my)}$"],
            "ok": True,
        }

    def _st_distance(self):
        rng = self.rng
        dx, dy, h = rng.choice(_PYTHAG)
        sx, sy = rng.choice([1, -1]), rng.choice([1, -1])
        x1, y1 = rng.randint(-4, 4), rng.randint(-4, 4)
        x2, y2 = x1 + sx * dx, y1 + sy * dy
        dist = sp.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        assert sp.simplify(dist - h) == 0
        return {
            "question": rf"Se consideră punctele $A({x1}, {y1})$ și $B({x2}, {y2})$. "
                        rf"Calculați distanța $AB$.",
            "answer_latex": rf"$AB = {h}$",
            "answer": sp.Integer(h),
            "hint": r"$AB = \sqrt{(x_B-x_A)^2 + (y_B-y_A)^2}$.",
            "steps": [rf"$AB = \sqrt{{({x2}-({x1}))^2 + ({y2}-({y1}))^2}} = \sqrt{{{dx**2 + dy**2}}} = {h}$"],
            "ok": True,
        }

    def _st_vector_point(self):
        rng = self.rng
        ax, ay = rng.randint(-4, 4), rng.randint(-4, 4)
        bx, by = rng.randint(-4, 4), rng.randint(-4, 4)
        cx, cy = ax + bx, ay + by
        return {
            "question": rf"În reperul cartezian $xOy$ se consideră punctele $A({ax}, {ay})$ "
                        rf"și $B({bx}, {by})$, iar $O$ este originea. Determinați coordonatele "
                        rf"punctului $C$ pentru care $\vec{{AC}} = \vec{{OB}}$.",
            "answer_latex": rf"$C({cx}, {cy})$",
            "answer": (cx, cy),
            "hint": r"$\vec{AC} = \vec{OB} \Rightarrow C - A = B$, deci $C = A + B$.",
            "steps": [rf"$x_C = {ax} + {bx} = {cx}$", rf"$y_C = {ay} + {by} = {cy}$"],
            "ok": True,
        }

    def _st_pythagoras(self):
        rng = self.rng
        ab, ac, bc = rng.choice(_PYTHAG)
        assert sp.simplify(sp.sqrt(ab ** 2 + ac ** 2) - bc) == 0
        ask = rng.choice(["bc", "perim", "area"])
        if ask == "bc":
            q = (rf"Se consideră triunghiul $ABC$, dreptunghic în $A$, cu $AB = {ab}$ și "
                 rf"$AC = {ac}$. Arătați că $BC = {bc}$.")
            ans, ans_l = sp.Integer(bc), rf"$BC = {bc}$"
            steps = [rf"$BC = \sqrt{{AB^2 + AC^2}} = \sqrt{{{ab**2}+{ac**2}}} = {bc}$"]
        elif ask == "perim":
            p = ab + ac + bc
            q = (rf"Se consideră triunghiul $ABC$, dreptunghic în $A$, cu $AB = {ab}$ și "
                 rf"$AC = {ac}$. Arătați că perimetrul triunghiului este egal cu ${p}$.")
            ans, ans_l = sp.Integer(p), rf"$P = {p}$"
            steps = [rf"$BC = \sqrt{{{ab**2}+{ac**2}}} = {bc}$",
                     rf"$P = {ab}+{ac}+{bc} = {p}$"]
        else:
            area = sp.Rational(ab * ac, 2)
            q = (rf"Se consideră triunghiul $ABC$, dreptunghic în $A$, cu $AB = {ab}$ și "
                 rf"$AC = {ac}$. Arătați că aria triunghiului este egală cu ${_l(area)}$.")
            ans, ans_l = area, rf"$\mathcal{{A}} = {_l(area)}$"
            steps = [rf"$\mathcal{{A}} = \frac{{AB \cdot AC}}{{2}} = \frac{{{ab}\cdot{ac}}}{{2}} = {_l(area)}$"]
        return {"question": q, "answer_latex": ans_l, "answer": ans,
                "hint": r"Folosiți teorema lui Pitagora: $BC^2 = AB^2 + AC^2$.",
                "steps": steps, "ok": True}

    def _st_collinear(self):
        rng = self.rng
        x1, y1 = rng.randint(-4, 4), rng.randint(-3, 3)
        m = rng.choice([-2, -1, 1, 2])
        n = y1 - m * x1                      # line through A with slope m
        x2 = x1 + rng.choice([2, 3, 4])
        y2 = m * x2 + n                      # B on the same line
        xc = x1 + rng.choice([5, 6, -5])     # C has known x, unknown y must lie on AB
        a = sp.Symbol("a")
        yc = sp.solve(sp.Eq((a - y1) * (x2 - x1), (y2 - y1) * (xc - x1)), a)[0]
        return {
            "question": rf"Se consideră punctele $A({x1}, {y1})$, $B({x2}, {y2})$ și "
                        rf"$C({xc}, a)$. Determinați numărul real $a$ pentru care punctele "
                        rf"$A$, $B$ și $C$ sunt coliniare.",
            "answer_latex": rf"$a = {_l(yc)}$",
            "answer": yc,
            "hint": r"Punctele sunt coliniare dacă $C$ aparține dreptei $AB$.",
            "steps": [rf"Dreapta $AB$: $y = {_l(m*X + n)}$", rf"$a = {_l(yc)}$"],
            "ok": True,
        }

    def _st_same_midpoint(self):
        rng = self.rng
        # ABCD parallelogram ⇔ AC and BD share a midpoint ⇔ D = A + C − B.
        ax, ay = rng.randint(-4, 4), rng.randint(-4, 4)
        bx, by = rng.randint(-4, 4), rng.randint(-4, 4)
        cx, cy = rng.randint(-4, 4), rng.randint(-4, 4)
        dx, dy = ax + cx - bx, ay + cy - by
        return {
            "question": rf"Se consideră punctele $A({ax}, {ay})$, $B({bx}, {by})$ și "
                        rf"$C({cx}, {cy})$. Determinați coordonatele punctului $D$ pentru care "
                        rf"segmentele $AC$ și $BD$ au același mijloc.",
            "answer_latex": rf"$D({dx}, {dy})$",
            "answer": (dx, dy),
            "hint": r"Mijloacele coincid $\Rightarrow A + C = B + D$, deci $D = A + C - B$.",
            "steps": [rf"$x_D = {ax} + {cx} - {bx} = {dx}$",
                      rf"$y_D = {ay} + {cy} - {by} = {dy}$"],
            "ok": True,
        }
