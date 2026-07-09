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
    SUPPORTED_PROFILES = ["mate-info", "tehnologic", "stiintele-naturii", "pedagogic"]

    def _generate_params(self) -> dict:
        rng = self.rng
        d1 = [self._st_point_on_line, self._st_midpoint, self._st_distance,
              self._st_vector_point, self._st_pythagoras, self._st_symmetric_point,
              self._st_show_right, self._st_show_isosceles]
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

    def _st_symmetric_point(self):
        rng = self.rng
        # M is the midpoint of AB; given A and M, find B = 2M − A. (Corpus pos-5.)
        ax, ay = rng.randint(-5, 5), rng.randint(-5, 5)
        mx, my = ax + rng.choice([-4, -3, -2, 2, 3, 4]), ay + rng.choice([-4, -3, -2, 2, 3, 4])
        bx, by = 2 * mx - ax, 2 * my - ay
        return {
            "question": rf"Se consideră punctele $A({ax}, {ay})$ și $M({mx}, {my})$. "
                        rf"Determinați coordonatele punctului $B$, știind că $M$ este "
                        rf"mijlocul segmentului $AB$.",
            "answer_latex": rf"$B({bx}, {by})$",
            "answer": (bx, by),
            "hint": r"$M$ mijloc $\Rightarrow M = \frac{A+B}{2}$, deci $B = 2M - A$.",
            "steps": [rf"$x_B = 2\cdot{mx} - ({ax}) = {bx}$",
                      rf"$y_B = 2\cdot{my} - ({ay}) = {by}$"],
            "ok": True,
        }

    def _st_show_right(self):
        rng = self.rng
        # Right angle at A: AB ⟂ AC via perpendicular integer vectors u, (−u_y, u_x).
        ax, ay = rng.randint(-4, 4), rng.randint(-4, 4)
        p, q = rng.choice([1, 2, 3]), rng.choice([1, 2, 3, 4])
        s1, s2, k = rng.choice([1, -1]), rng.choice([1, -1]), rng.choice([1, 2])
        bx, by = ax + s1 * p, ay + s1 * q
        cx, cy = ax + s2 * (-q) * k, ay + s2 * p * k
        if (bx, by) == (cx, cy):
            raise ValueError("degenerate")
        assert (bx - ax) * (cx - ax) + (by - ay) * (cy - ay) == 0
        return {
            "question": rf"În reperul cartezian $xOy$ se consideră punctele $A({ax}, {ay})$, "
                        rf"$B({bx}, {by})$ și $C({cx}, {cy})$. Arătați că triunghiul $ABC$ "
                        rf"este dreptunghic în $A$.",
            "answer_latex": r"$\vec{AB} \cdot \vec{AC} = 0$",
            "answer": sp.Integer(0),
            "hint": r"Unghiul din $A$ este drept dacă $\vec{AB} \cdot \vec{AC} = 0$.",
            "steps": [rf"$\vec{{AB}}=({bx - ax}, {by - ay})$, $\vec{{AC}}=({cx - ax}, {cy - ay})$",
                      rf"$\vec{{AB}}\cdot\vec{{AC}} = {(bx-ax)*(cx-ax)} + {(by-ay)*(cy-ay)} = 0$"],
            "ok": True,
        }

    def _st_show_isosceles(self):
        rng = self.rng
        # Apex A equidistant from B and C: two distinct, non-opposite length-5 vectors.
        vecs = [(0, 5), (3, 4), (4, 3), (5, 0), (0, -5), (3, -4), (-3, 4), (-4, 3), (-5, 0)]
        ax, ay = rng.randint(-3, 3), rng.randint(-3, 3)
        for _ in range(30):
            u, v = rng.sample(vecs, 2)
            if u[0] * v[1] - u[1] * v[0] != 0:        # non-collinear ⇒ real triangle
                break
        else:
            raise ValueError("degenerate")
        bx, by = ax + u[0], ay + u[1]
        cx, cy = ax + v[0], ay + v[1]
        return {
            "question": rf"În reperul cartezian $xOy$ se consideră punctele $A({ax}, {ay})$, "
                        rf"$B({bx}, {by})$ și $C({cx}, {cy})$. Arătați că triunghiul $ABC$ "
                        rf"este isoscel.",
            "answer_latex": r"$AB = AC = 5$",
            "answer": sp.Integer(5),
            "hint": r"Calculați lungimile $AB$ și $AC$; triunghiul e isoscel dacă $AB = AC$.",
            "steps": [rf"$AB = \sqrt{{{u[0]**2}+{u[1]**2}}} = 5$",
                      rf"$AC = \sqrt{{{v[0]**2}+{v[1]**2}}} = 5$"],
            "ok": True,
        }

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
