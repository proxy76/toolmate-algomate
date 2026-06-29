"""Linear systems — single-item class (spec §3.2, §4.3). M1/M2.

  d1: a 2×2 system with a unique integer solution.
  d2: a 3×3 system (M1) with a unique integer solution, or a parametric 2×2
      system — find the parameter for which it has a unique solution (det ≠ 0).
  d3: parametric system (det as a polynomial in the parameter).
Solutions are built from a chosen integer solution and verified with sympy
(``linsolve`` / ``det``) so they are always consistent (§11.4).
"""
from __future__ import annotations

import sympy as sp

from ..base import ExerciseGenerator

x, y, z, m = sp.symbols("x y z m", real=True)


def _l(expr) -> str:
    return sp.latex(expr)


def _nz(rng, lo=-4, hi=4):
    v = rng.randint(lo, hi)
    return v if v != 0 else 1


class SystemsGenerator(ExerciseGenerator):
    TOPIC_CODE = "systems"
    SUPPORTED_PROFILES = ["M1", "M2"]

    def _generate_params(self) -> dict:
        rng = self.rng
        d = self.difficulty
        if d == 1:
            pool = [self._st_2x2]
        elif d == 2:
            pool = [self._st_3x3, self._st_parametric] if self.profile == "M1" \
                else [self._st_parametric, self._st_2x2]
        else:
            pool = [self._st_parametric]
        return rng.choice(pool)()

    def _compute_answer(self, params):
        return params.get("answer")

    def _validate(self, params, answer) -> bool:
        return params.get("ok", True) and len(params["answer_latex"]) < 240

    def _build_question(self, params):
        return params["question"]

    def _build_answer_latex(self, params, answer):
        return params["answer_latex"]

    def _build_hint(self, params):
        return params.get("hint", "")

    def _build_steps(self, params):
        return params.get("steps", [])

    # --- subtypes ------------------------------------------------------------
    def _st_2x2(self):
        rng = self.rng
        A = sp.Matrix([[_nz(rng), _nz(rng)], [_nz(rng), _nz(rng)]])
        while A.det() == 0:
            A = sp.Matrix([[_nz(rng), _nz(rng)], [_nz(rng), _nz(rng)]])
        x0, y0 = rng.randint(-3, 3), rng.randint(-3, 3)
        b = A * sp.Matrix([x0, y0])
        sol = sp.linsolve((A, b), (x, y))
        assert sol == sp.FiniteSet((x0, y0))
        e1 = sp.Eq(A[0, 0] * x + A[0, 1] * y, b[0])
        e2 = sp.Eq(A[1, 0] * x + A[1, 1] * y, b[1])
        return {
            "question": rf"Rezolvați în $\mathbb{{R}} \times \mathbb{{R}}$ sistemul de ecuații: "
                        rf"$\begin{{cases}} {_l(e1.lhs)} = {_l(e1.rhs)} \\ "
                        rf"{_l(e2.lhs)} = {_l(e2.rhs)} \end{{cases}}$",
            "answer_latex": rf"$(x, y) = ({x0}, {y0})$",
            "answer": (x0, y0),
            "hint": r"Metoda reducerii sau a substituției (sau regula lui Cramer).",
            "steps": [rf"$(x, y) = ({x0}, {y0})$"],
            "ok": True,
        }

    def _st_3x3(self):
        rng = self.rng

        def rand_row():
            return [_nz(rng, -3, 3) for _ in range(3)]

        A = sp.Matrix([rand_row(), rand_row(), rand_row()])
        tries = 0
        while A.det() == 0 and tries < 20:
            A = sp.Matrix([rand_row(), rand_row(), rand_row()])
            tries += 1
        assert A.det() != 0
        sol_vec = [rng.randint(-2, 2) for _ in range(3)]
        b = A * sp.Matrix(sol_vec)
        sol = sp.linsolve((A, b), (x, y, z))
        assert sol == sp.FiniteSet(tuple(sol_vec))
        rows = []
        for i, var_lhs in enumerate(
            [A[i, 0] * x + A[i, 1] * y + A[i, 2] * z for i in range(3)]
        ):
            rows.append(rf"{_l(var_lhs)} = {_l(b[i])}")
        sys_l = r" \\ ".join(rows)
        return {
            "question": rf"Rezolvați sistemul de ecuații liniare: "
                        rf"$\begin{{cases}} {sys_l} \end{{cases}}$",
            "answer_latex": rf"$(x, y, z) = ({sol_vec[0]}, {sol_vec[1]}, {sol_vec[2]})$",
            "answer": tuple(sol_vec),
            "hint": r"Folosiți regula lui Cramer sau eliminarea Gauss.",
            "steps": [rf"$(x, y, z) = ({sol_vec[0]}, {sol_vec[1]}, {sol_vec[2]})$"],
            "ok": True,
        }

    def _st_parametric(self):
        rng = self.rng
        # System with matrix A(m) = [[1, m], [m, 4]] → det = 4 − m²; unique ⇔ m ∉ {−2, 2}.
        p = rng.choice([4, 9, 1])
        A = sp.Matrix([[1, m], [m, p]])
        det = sp.expand(A.det())             # p − m²
        bad = sorted(sp.solve(sp.Eq(det, 0), m), key=lambda s: float(s))
        bad_l = ",\\ ".join(_l(s) for s in bad)
        return {
            "question": rf"Se consideră sistemul $\begin{{cases}} x + m y = 1 \\ "
                        rf"m x + {p} y = 2 \end{{cases}}$, unde $m$ este parametru real. "
                        rf"Determinați valorile lui $m$ pentru care sistemul are soluție unică.",
            "answer_latex": rf"$m \in \mathbb{{R}} \setminus \{{{bad_l}\}}$",
            "answer": tuple(bad),
            "hint": r"Sistemul are soluție unică dacă determinantul matricei este nenul.",
            "steps": [rf"$\det = {_l(det)}$",
                      rf"$\det \neq 0 \iff m \notin \{{{bad_l}\}}$"],
            "ok": True,
        }
