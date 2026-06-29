"""Matrices — multi-part problem generator (spec §9.2, §10.4, §5.4).

The canonical BAC matrix problem fixes a parametrized family ``A(x)`` and poses
linked cerinte about it. We use a verified *homomorphism family* — a matrix with
``det(A(x)) = 1`` and ``A(x)·A(y) = A(x+y)`` (i.e. ``A(x) = I + xN + …`` with ``N``
nilpotent) — which is exactly the family that appears most often in the exam
(references note #2). Every property is checked with sympy before use.

Profiles (spec §3–5, §13.1):
- M1: 3×3, sub-items a/b/c.
- M2: 2×2 or 3×3, sub-items a/b/c.
- M3: 2×2 only, the single-topic **6 sub-items** format (Subiectul III).
"""
from __future__ import annotations

import sympy as sp

from ..base import ProblemGenerator

x, y = sp.symbols("x y", real=True)


def _ml(M) -> str:
    return sp.latex(M, mat_delim="(")


class MatricesProblem(ProblemGenerator):
    TOPIC_CODE = "matrices"
    SUPPORTED_PROFILES = ["M1", "M2", "M3"]

    def __init__(self, profile, rng, *, six_items: bool = False, size: int | None = None):
        super().__init__(profile, rng)
        self.six = six_items
        if six_items:
            self.SUB_LABELS = ("a", "b", "c", "d", "e", "f")
            self.SUB_DIFFICULTIES = (1, 1, 2, 2, 3, 3)
        if size is not None:
            self.size = size
        elif profile == "M3":
            self.size = 2
        elif profile == "M1":
            self.size = 3
        else:
            self.size = rng.choice([2, 3])

    # --- family construction (verified) --------------------------------------
    def _candidate_families(self, size):
        if size == 2:
            nilpotents = [
                sp.Matrix([[0, 1], [0, 0]]),
                sp.Matrix([[0, 0], [1, 0]]),
                sp.Matrix([[1, 1], [-1, -1]]),
                sp.Matrix([[1, -1], [1, -1]]),
                sp.Matrix([[0, 2], [0, 0]]),
                sp.Matrix([[2, 2], [-2, -2]]),
            ]
            return [(lambda t, N=N: sp.eye(2) + t * N) for N in nilpotents]
        return [
            lambda t: sp.Matrix([[1, t, t ** 2], [0, 1, 2 * t], [0, 0, 1]]),
            lambda t: sp.eye(3) + t * sp.Matrix([[0, 1, 0], [0, 0, 0], [0, 0, 0]]),
            lambda t: sp.eye(3) + t * sp.Matrix([[0, 1, 1], [0, 0, 0], [0, 0, 0]]),
            lambda t: sp.eye(3) + t * sp.Matrix([[0, 2, 0], [0, 0, 0], [0, 0, 0]]),
        ]

    def _pick_family(self, size):
        fams = self._candidate_families(size)
        self.rng.shuffle(fams)
        zero = sp.zeros(size)
        for A in fams:
            det_const = sp.simplify(sp.det(A(x)) - 1) == 0
            homo = sp.simplify(A(x) * A(y) - A(x + y)) == zero
            ident = sp.simplify(A(0) - sp.eye(size)) == zero
            if det_const and homo and ident:
                return A
        raise ValueError("no valid homomorphism family")

    def _generate_context(self) -> dict:
        rng = self.rng
        A = self._pick_family(self.size)
        return {
            "A": A,
            "size": self.size,
            "x0": rng.choice([1, 2, 3]),
            "y0": rng.choice([1, 2, 3]),
            "a": rng.choice([2, 3, 4]),
        }

    def _validate_context(self, ctx) -> bool:
        A, size = ctx["A"], ctx["size"]
        zero = sp.zeros(size)
        return (
            sp.simplify(sp.det(A(x)) - 1) == 0
            and sp.simplify(A(x) * A(y) - A(x + y)) == zero
        )

    def _build_statement(self, ctx) -> str:
        A, size = ctx["A"], ctx["size"]
        return (
            rf"Se consideră matricea $A(x) = {_ml(A(x))}$, unde $x$ este număr real, "
            rf"și $I_{{{size}}}$ matricea unitate de ordin ${size}$."
        )

    # --- cerinte (each sympy-verified) ---------------------------------------
    def _c_det_value(self, ctx, label, tier):
        A, x0 = ctx["A"], ctx["x0"]
        d = sp.det(A(x0))
        assert sp.simplify(d - 1) == 0
        return {
            "question_latex": rf"Arătați că $\det\big(A({x0})\big) = {sp.latex(d)}$.",
            "answer_latex": rf"$\det\big(A({x0})\big) = {sp.latex(d)}$",
            "hint_latex": r"Înlocuiți $x$ cu valoarea dată și calculați determinantul.",
            "steps_latex": [rf"$A({x0}) = {_ml(A(x0))}$",
                            rf"$\det\big(A({x0})\big) = {sp.latex(d)}$"],
        }

    def _c_product_concrete(self, ctx, label, tier):
        A, x0, y0 = ctx["A"], ctx["x0"], ctx["y0"]
        lhs = sp.simplify(A(x0) * A(y0))
        assert sp.simplify(lhs - A(x0 + y0)) == sp.zeros(ctx["size"])
        return {
            "question_latex": rf"Arătați că $A({x0})\cdot A({y0}) = A({x0 + y0})$.",
            "answer_latex": rf"$A({x0})\cdot A({y0}) = {_ml(lhs)} = A({x0 + y0})$",
            "hint_latex": r"Efectuați produsul matriceal și comparați cu $A(x_0+y_0)$.",
            "steps_latex": [rf"$A({x0})\cdot A({y0}) = {_ml(lhs)}$",
                            rf"$A({x0 + y0}) = {_ml(A(x0 + y0))}$"],
        }

    def _c_product_general(self, ctx, label, tier):
        A = ctx["A"]
        prod = sp.simplify(A(x) * A(y))
        assert sp.simplify(prod - A(x + y)) == sp.zeros(ctx["size"])
        return {
            "question_latex": r"Arătați că $A(x)\cdot A(y) = A(x+y)$, pentru orice "
                              r"$x, y \in \mathbb{R}$.",
            "answer_latex": rf"$A(x)\cdot A(y) = {_ml(prod)} = A(x+y)$",
            "hint_latex": r"Efectuați produsul în general și grupați termenii după $x+y$.",
            "steps_latex": [rf"$A(x)\cdot A(y) = {_ml(prod)}$",
                            rf"$A(x+y) = {_ml(A(x + y))}$"],
        }

    def _c_inverse(self, ctx, label, tier):
        A, a, size = ctx["A"], ctx["a"], ctx["size"]
        prod = sp.simplify(A(a) * A(-a))
        assert sp.simplify(prod - sp.eye(size)) == sp.zeros(size)
        return {
            "question_latex": rf"Arătați că $A({a})\cdot A({-a}) = I_{{{size}}}$ "
                              rf"și deduceți inversa matricei $A({a})$.",
            "answer_latex": rf"$A({a})\cdot A({-a}) = I_{{{size}}}$, deci "
                            rf"$A({a})^{{-1}} = A({-a})$",
            "hint_latex": r"Folosiți $A(x)\cdot A(y) = A(x+y)$ cu $y = -x$.",
            "steps_latex": [rf"$A({a})\cdot A({-a}) = A(0) = I_{{{size}}}$"],
        }

    def _c_power(self, ctx, label, tier):
        A, a = ctx["A"], ctx["a"]
        # spot-check the closed form on small n with sympy
        for k in (2, 3, 4):
            assert sp.simplify(A(a) ** k - A(a * k)) == sp.zeros(ctx["size"])
        return {
            "question_latex": rf"Demonstrați că $A({a})^{{n}} = A({a}n)$, pentru orice "
                              r"$n \in \mathbb{N}^*$.",
            "answer_latex": rf"$A({a})^{{n}} = A({a}n)$",
            "hint_latex": r"Inducție după $n$, folosind $A(x)\cdot A(y) = A(x+y)$.",
            "steps_latex": [
                rf"$A({a})^{{1}} = A({a})$",
                rf"$A({a})^{{k+1}} = A({a})^{{k}}\cdot A({a}) = A({a}k)\cdot A({a}) "
                rf"= A({a}k + {a}) = A({a}(k+1))$",
            ],
        }

    def _c_system(self, ctx, label, tier):
        A, a = ctx["A"], ctx["a"]
        x1, y1 = self.rng.choice([1, 2, 3]), self.rng.choice([-2, -1, 1, 2])
        rhs = sp.simplify(A(a) * sp.Matrix([x1, y1]))
        u, v = sp.symbols("u v", real=True)
        sol = sp.linsolve((A(a), rhs), (u, v))
        assert sol == sp.FiniteSet((x1, y1))
        rhs_l = _ml(rhs)
        return {
            "question_latex": rf"Determinați numerele reale $x$ și $y$ pentru care "
                              rf"$A({a})\cdot \begin{{pmatrix}} x \\ y \end{{pmatrix}} = {rhs_l}$.",
            "answer_latex": rf"$x = {x1},\ y = {y1}$",
            "hint_latex": r"Scrieți sistemul liniar și rezolvați-l.",
            "steps_latex": [rf"$A({a})\cdot \begin{{pmatrix}} x \\ y \end{{pmatrix}} = {rhs_l}$",
                            rf"$\Rightarrow x = {x1},\ y = {y1}$"],
        }

    def _plan(self):
        if self.six:  # M3, 2×2, six items
            return [self._c_det_value, self._c_product_concrete, self._c_product_general,
                    self._c_inverse, self._c_power, self._c_system]
        last = self._c_system if self.size == 2 else self._c_power
        return [self._c_det_value, self._c_product_general, last]

    def _build_sub_item(self, ctx, label, difficulty) -> dict:
        idx = self.SUB_LABELS.index(label)
        return self._plan()[idx](ctx, label, difficulty)
