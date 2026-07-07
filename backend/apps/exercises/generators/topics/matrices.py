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
                sp.Matrix([[0, 3], [0, 0]]),
                sp.Matrix([[2, 4], [-1, -2]]),
                sp.Matrix([[3, 3], [-3, -3]]),
                sp.Matrix([[0, 0], [2, 0]]),
            ]
            return [(lambda t, N=N: sp.eye(2) + t * N) for N in nilpotents]
        return [
            lambda t: sp.Matrix([[1, t, t ** 2], [0, 1, 2 * t], [0, 0, 1]]),
            lambda t: sp.eye(3) + t * sp.Matrix([[0, 1, 0], [0, 0, 0], [0, 0, 0]]),
            lambda t: sp.eye(3) + t * sp.Matrix([[0, 1, 1], [0, 0, 0], [0, 0, 0]]),
            lambda t: sp.eye(3) + t * sp.Matrix([[0, 2, 0], [0, 0, 0], [0, 0, 0]]),
            lambda t: sp.eye(3) + t * sp.Matrix([[0, 1, 0], [0, 0, 1], [0, 0, 0]]),
            lambda t: sp.eye(3) + t * sp.Matrix([[0, 0, 2], [0, 0, 0], [0, 0, 0]]),
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
        ctx = {
            "A": A,
            "size": self.size,
            "x0": rng.choice([1, 2, 3]),
            "y0": rng.choice([1, 2, 3]),
            "a": rng.choice([2, 3, 4]),
            "x1": rng.choice([1, 2, 3, 4]),   # for "find x from A(x)=M"
        }
        # Decide which cerinte fill a/b/c ONCE (so the 3 labels stay consistent).
        ctx["plan"] = self._pick_plan()
        return ctx

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

    def _c_trace(self, ctx, label, tier):
        A, x0, size = ctx["A"], ctx["x0"], ctx["size"]
        tr = sp.trace(A(x0))
        assert sp.simplify(tr - size) == 0
        return {
            "question_latex": rf"Arătați că urma matricei $A({x0})$ este egală cu ${size}$.",
            "answer_latex": rf"$\operatorname{{Tr}}\big(A({x0})\big) = {size}$",
            "hint_latex": r"Urma este suma elementelor de pe diagonala principală.",
            "steps_latex": [rf"$A({x0}) = {_ml(A(x0))}$",
                            rf"$\operatorname{{Tr}}\big(A({x0})\big) = {size}$"],
        }

    def _c_sum(self, ctx, label, tier):
        A, x0, y0 = ctx["A"], ctx["x0"], ctx["y0"]
        S = sp.simplify(A(x0) + A(y0))
        return {
            "question_latex": rf"Calculați suma $A({x0}) + A({y0})$.",
            "answer_latex": rf"$A({x0}) + A({y0}) = {_ml(S)}$",
            "hint_latex": r"Adunați matricele element cu element.",
            "steps_latex": [rf"$A({x0}) = {_ml(A(x0))},\quad A({y0}) = {_ml(A(y0))}$",
                            rf"$A({x0}) + A({y0}) = {_ml(S)}$"],
        }

    def _c_commutative(self, ctx, label, tier):
        A, size = ctx["A"], ctx["size"]
        lhs, rhs = sp.simplify(A(x) * A(y)), sp.simplify(A(y) * A(x))
        assert sp.simplify(lhs - rhs) == sp.zeros(size)
        return {
            "question_latex": r"Arătați că $A(x)\cdot A(y) = A(y)\cdot A(x)$, pentru orice "
                              r"$x, y \in \mathbb{R}$.",
            "answer_latex": r"$A(x)\cdot A(y) = A(y)\cdot A(x) = A(x+y)$",
            "hint_latex": r"Ambele produse sunt egale cu $A(x+y)$.",
            "steps_latex": [rf"$A(x)\cdot A(y) = {_ml(lhs)}$",
                            rf"$A(y)\cdot A(x) = {_ml(rhs)}$"],
        }

    def _c_find_x(self, ctx, label, tier):
        A, x1 = ctx["A"], ctx["x1"]
        M = sp.simplify(A(x1))
        return {
            "question_latex": rf"Determinați numărul real $x$ pentru care $A(x) = {_ml(M)}$.",
            "answer_latex": rf"$x = {x1}$",
            "hint_latex": r"Identificați un element care depinde de $x$ și rezolvați ecuația.",
            "steps_latex": [rf"Din egalitatea matricelor rezultă $x = {x1}$."],
        }

    def _c_solve_matrix(self, ctx, label, tier):
        A, x0, size = ctx["A"], ctx["x0"], ctx["size"]
        y1 = x0 + self.rng.choice([1, 2, 3])
        X = sp.simplify(A(y1 - x0))
        assert sp.simplify(A(x0) * X - A(y1)) == sp.zeros(size)
        return {
            "question_latex": rf"Determinați matricea $X$ pentru care "
                              rf"$A({x0})\cdot X = A({y1})$.",
            "answer_latex": rf"$X = A({y1 - x0}) = {_ml(X)}$",
            "hint_latex": rf"Înmulțiți la stânga cu $A(-{x0})$: $X = A({y1} - {x0})$.",
            "steps_latex": [rf"$X = A(-{x0})\cdot A({y1}) = A({y1 - x0}) = {_ml(X)}$"],
        }

    def _c_inverse_explicit(self, ctx, label, tier):
        A, a, size = ctx["A"], ctx["a"], ctx["size"]
        inv = sp.simplify(A(a).inv())
        assert sp.simplify(inv - A(-a)) == sp.zeros(size)
        return {
            "question_latex": rf"Arătați că matricea $A({a})$ este inversabilă și "
                              rf"calculați $A({a})^{{-1}}$.",
            "answer_latex": rf"$A({a})^{{-1}} = {_ml(inv)}$",
            "hint_latex": rf"$\det\big(A({a})\big) = 1 \neq 0$; folosiți "
                          rf"$A({a})^{{-1}} = A({-a})$.",
            "steps_latex": [rf"$\det\big(A({a})\big) = 1 \Rightarrow A({a})$ este inversabilă",
                            rf"$A({a})^{{-1}} = A({-a}) = {_ml(inv)}$"],
        }

    # --- cerinta planning -----------------------------------------------------
    def _pick_plan(self):
        """Choose a/b/c cerinte at random from difficulty tiers, keeping the three
        themes distinct so a paper never repeats a theme (e.g. two "product" items).
        Called once per context (stored on ``ctx``) for label consistency."""
        if self.six:  # M3, 2×2, six items — a fixed comprehensive tour of the family.
            return [self._c_det_value, self._c_product_concrete, self._c_product_general,
                    self._c_inverse, self._c_power, self._c_system]
        rng, size = self.rng, self.size
        # (method, theme) grouped by escalating difficulty.
        t1 = [(self._c_det_value, "det"), (self._c_trace, "trace"),
              (self._c_product_concrete, "product"), (self._c_sum, "sum")]
        t2 = [(self._c_product_general, "product"), (self._c_commutative, "product"),
              (self._c_inverse, "inverse"), (self._c_find_x, "solve")]
        t3 = [(self._c_power, "power"), (self._c_solve_matrix, "solve"),
              (self._c_inverse_explicit, "inverse")]
        if size == 2:
            t3 = t3 + [(self._c_system, "solve")]
        for _ in range(40):
            a, b, c = rng.choice(t1), rng.choice(t2), rng.choice(t3)
            if len({a[1], b[1], c[1]}) == 3:      # distinct themes
                return [a[0], b[0], c[0]]
        # Deterministic fallback (always valid, distinct themes).
        return [self._c_det_value, self._c_product_general,
                self._c_system if size == 2 else self._c_power]

    def _build_sub_item(self, ctx, label, difficulty) -> dict:
        idx = self.SUB_LABELS.index(label)
        return ctx["plan"][idx](ctx, label, difficulty)


# =============================================================================
# Matrix A(a) + linear system — the *other* dominant Subiectul II problem-1 form
# (~10 of the 24 real M1 papers). A 3×3 matrix A(a) whose determinant is a
# polynomial in ``a`` with clean integer roots, together with a linear system:
#   (a) det(A(a0)) = <integer>
#   (b) values of a for which the system has a unique solution (A(a) invertible)
#   (c) for a fixed a, solve the system, with a property on the solution
#       (integer triple, sometimes consecutive terms of a progression).
# Everything is verified with sympy (det, roots, linsolve).
# =============================================================================
_a = sp.Symbol("a", real=True)
_xs, _ys, _zs = sp.symbols("x y z", real=True)


def _row_latex(coeffs, rhs) -> str:
    """Render one linear equation ``c_x·x + c_y·y + c_z·z = rhs`` in BAC style,
    parenthesizing coefficients that depend on the parameter ``a``."""
    parts = []
    for c, v in zip(coeffs, ("x", "y", "z")):
        if c == 0:
            continue
        if c == 1:
            term, sign = v, "+"
        elif c == -1:
            term, sign = v, "-"
        elif getattr(c, "is_number", False):
            n = abs(c)
            term = (v if n == 1 else rf"{sp.latex(n)}{v}")
            sign = "+" if c > 0 else "-"
        else:                                  # a-dependent → parenthesize
            term, sign = rf"({sp.latex(c)}){v}", "+"
        parts.append((sign, term))
    if not parts:
        return rf"0 = {sp.latex(rhs)}"
    s0, t0 = parts[0]
    out = (f"-{t0}" if s0 == "-" else t0)
    for sign, term in parts[1:]:
        out += f" {sign} {term}"
    return rf"{out} = {sp.latex(rhs)}"


class MatrixSystemProblem(ProblemGenerator):
    TOPIC_CODE = "matrices"                     # same label/topic as MatricesProblem
    SUPPORTED_PROFILES = ["M1", "M2"]

    def _random_template(self):
        """A 3×3 matrix with ``a`` on a few (mostly diagonal) positions and small
        integer entries elsewhere."""
        rng = self.rng
        a_pos = {(i, i) for i in range(3) if rng.random() < 0.7}
        while len(a_pos) < 2:
            a_pos.add((rng.randrange(3), rng.randrange(3)))
        if rng.random() < 0.3:
            a_pos.add((rng.randrange(3), rng.randrange(3)))
        fill = lambda: rng.choice([-1, 0, 1, 1, 2])
        return sp.Matrix(3, 3,
                         lambda i, j: (_a if (i, j) in a_pos else 0) + fill())

    def _generate_context(self) -> dict:
        rng = self.rng
        for _ in range(400):
            A = self._random_template()
            detp = sp.Poly(sp.expand(A.det()), _a)
            if not (1 <= detp.degree() <= 3):
                continue
            if any(not c.is_integer for c in detp.all_coeffs()):
                continue
            rts = sp.roots(detp)
            if sum(rts.values()) != detp.degree() or not all(r.is_rational for r in rts):
                continue
            roots = sorted(set(rts), key=lambda r: float(r))
            if not (1 <= len(roots) <= 2):
                continue
            a1 = next((v for v in rng.sample([-2, -1, 1, 2, 3], 5) if v not in roots), None)
            if a1 is None or A.subs(_a, a1).det() == 0:
                continue
            is_ap = rng.random() < 0.5
            if is_ap:
                t, d = rng.randint(-2, 3), rng.choice([-2, -1, 1, 2])
                s = sp.Matrix([t, t + d, t + 2 * d])
            else:
                s = sp.Matrix([rng.randint(-3, 3) for _ in range(3)])
            b = A.subs(_a, a1) * s
            a0 = rng.choice([-2, -1, 0, 1, 2, 3])
            det0 = int(A.subs(_a, a0).det())
            if abs(det0) > 60:
                continue
            return {"A": A, "roots": roots, "a1": a1, "s": s, "b": b,
                    "a0": a0, "det0": det0, "is_ap": is_ap}
        raise ValueError("no valid matrix-system template")

    def _validate_context(self, ctx) -> bool:
        A, a1, s, b = ctx["A"], ctx["a1"], ctx["s"], ctx["b"]
        A1 = A.subs(_a, a1)
        if A1.det() == 0:
            return False
        sol = sp.linsolve((A1, b), (_xs, _ys, _zs))
        return sol == sp.FiniteSet(tuple(s))

    def _build_statement(self, ctx) -> str:
        A, b = ctx["A"], ctx["b"]
        rows = [_row_latex(list(A.row(i)), b[i]) for i in range(3)]
        sys = r" \\ ".join(rows)
        return (rf"Se consideră matricea $A(a) = {_ml(A)}$ și sistemul de ecuații "
                rf"$\begin{{cases}} {sys} \end{{cases}}$, unde $a$ este număr real.")

    def _sub_tiers(self):
        return (1, 2, 3)

    def _build_sub_item(self, ctx, label, difficulty) -> dict:
        return {"a": self._sys_det, "b": self._sys_unique, "c": self._sys_solve}[label](ctx)

    def _sys_det(self, ctx):
        A, a0, det0 = ctx["A"], ctx["a0"], ctx["det0"]
        assert int(A.subs(_a, a0).det()) == det0
        return {
            "question_latex": rf"Arătați că $\det\big(A({a0})\big) = {det0}$.",
            "answer_latex": rf"$\det\big(A({a0})\big) = {det0}$",
            "hint_latex": r"Înlocuiți $a$ cu valoarea dată și calculați determinantul.",
            "steps_latex": [rf"$A({a0}) = {_ml(A.subs(_a, a0))}$",
                            rf"$\det\big(A({a0})\big) = {det0}$"],
        }

    def _sys_unique(self, ctx):
        roots = ctx["roots"]
        excl = ",\\ ".join(sp.latex(r) for r in roots)
        return {
            "question_latex": r"Determinați valorile reale ale lui $a$ pentru care sistemul "
                              r"de ecuații are soluție unică.",
            "answer_latex": rf"$a \in \mathbb{{R}} \setminus \{{{excl}\}}$",
            "hint_latex": r"Sistemul are soluție unică $\iff \det\big(A(a)\big) \neq 0$.",
            "steps_latex": [rf"$\det\big(A(a)\big) = 0 \Rightarrow a \in \{{{excl}\}}$",
                            rf"soluție unică pentru $a \in \mathbb{{R}} \setminus \{{{excl}\}}$"],
        }

    def _sys_solve(self, ctx):
        a1, s, is_ap = ctx["a1"], ctx["s"], ctx["is_ap"]
        x0, y0, z0 = (int(v) for v in s)
        extra = ""
        if is_ap:
            assert 2 * y0 == x0 + z0
            extra = (r" Arătați că numerele $x_0$, $y_0$ și $z_0$ sunt termeni consecutivi "
                     r"ai unei progresii aritmetice.")
        return {
            "question_latex": rf"Pentru $a = {a1}$, determinați soluția "
                              rf"$(x_0, y_0, z_0)$ a sistemului de ecuații.{extra}",
            "answer_latex": rf"$(x_0, y_0, z_0) = ({x0}, {y0}, {z0})$"
                            + (rf",\quad 2y_0 = x_0 + z_0" if is_ap else ""),
            "hint_latex": rf"Pentru $a = {a1}$ sistemul este compatibil determinat; "
                          rf"rezolvați-l (Cramer sau reducere).",
            "steps_latex": [rf"$(x_0, y_0, z_0) = ({x0}, {y0}, {z0})$"],
        }
