"""Generator + engine test suite (spec §14.4, §14.2–14.3).

Pure-logic tests (no DB) over the generation engine: reproducibility, variety,
exam structure & points, profile restrictions, per-generator robustness, and
sympy correctness of the headline computations. Run with:

    python manage.py test apps.exercises
"""
import random

import sympy as sp
from django.test import SimpleTestCase

from apps.exercises.generators import engine
from apps.exercises.generators.registry import (
    CLASS_REGISTRY,
    PROBLEM_REGISTRY,
    PROFILE_TOPICS,
    PROFILES,
)


class ReproducibilityTests(SimpleTestCase):
    def test_generate_same_seed_same_set(self):
        a = engine.generate_exercises(profile="mate-info", topics=["derivatives"],
                                      difficulty=2, count=10, seed="test123")
        b = engine.generate_exercises(profile="mate-info", topics=["derivatives"],
                                      difficulty=2, count=10, seed="test123")
        self.assertEqual(a, b)

    def test_simulate_same_seed_same_paper(self):
        for profile in PROFILES:
            s1 = engine.generate_full_simulation(profile=profile, seed="repro")
            s2 = engine.generate_full_simulation(profile=profile, seed="repro")
            self.assertEqual(s1, s2)


class VarietyTests(SimpleTestCase):
    def test_variety_above_threshold(self):
        # spec §14.4: > 50 distinct questions over 20 seeds × 5 items
        questions = []
        for i in range(20):
            res = engine.generate_exercises(profile="mate-info", topics=["derivatives"],
                                            difficulty=2, count=5, seed=str(i))
            questions += [it["question_latex"] for it in res["items"]]
        self.assertGreater(len(set(questions)), 50)


class SimulationStructureTests(SimpleTestCase):
    def test_structure_and_points(self):
        for profile in PROFILES:
            sim = engine.generate_full_simulation(profile=profile, seed="struct")
            self.assertEqual(sim["subiect_I"]["points"], 30)
            self.assertEqual(len(sim["subiect_I"]["items"]), 6)
            self.assertTrue(all(it["points"] == 5 for it in sim["subiect_I"]["items"]))
            for key in ("subiect_II", "subiect_III"):
                sub = sim[key]
                self.assertEqual(sub["points"], 30)
                subs = sum(len(p["sub_items"]) for p in sub["problems"])
                self.assertEqual(subs * 5, 30)
                for p in sub["problems"]:
                    self.assertTrue(p["statement_latex"].strip())
                    for si in p["sub_items"]:
                        self.assertTrue(si["question_latex"].strip())
                        self.assertTrue(si["answer_latex"].strip())
            grand = sum(sim[k]["points"] for k in ("subiect_I", "subiect_II", "subiect_III"))
            self.assertEqual(grand, 90)
            self.assertEqual(grand + sim["officiu_points"], 100)

    def test_m3_special_casing(self):
        m3 = engine.generate_full_simulation(profile="pedagogic", seed="m3")
        ii, iii = m3["subiect_II"]["problems"], m3["subiect_III"]["problems"]
        self.assertEqual(len(ii), 1)
        self.assertEqual(len(ii[0]["sub_items"]), 6)
        self.assertEqual(ii[0]["topic_primary"], "algebraic_structures")
        self.assertEqual(len(iii), 1)
        self.assertEqual(len(iii[0]["sub_items"]), 6)
        self.assertEqual(iii[0]["topic_primary"], "matrices")
        si_topics = [it["topic"] for it in m3["subiect_I"]["items"]]
        self.assertNotIn("complex", si_topics)
        self.assertNotIn("integrals", si_topics)

    def test_progressive_difficulty_in_problems(self):
        # spec §10.3: sub-items escalate (a ≤ b ≤ c …)
        sim = engine.generate_full_simulation(profile="mate-info", seed="prog")
        for key in ("subiect_II", "subiect_III"):
            for p in sim[key]["problems"]:
                diffs = [s["difficulty"] for s in p["sub_items"]]
                self.assertEqual(diffs, sorted(diffs))


class ProfileRestrictionTests(SimpleTestCase):
    def test_m3_menu_excludes_advanced_topics(self):
        m3 = {t["code"] for t in engine.supported_topics("pedagogic")}
        for forbidden in ("complex", "integrals", "limits", "sequences", "systems"):
            self.assertNotIn(forbidden, m3)

    def test_m3_matrices_problem_is_2x2(self):
        from apps.exercises.generators.topics.matrices import MatricesProblem
        ctx = MatricesProblem("pedagogic", random.Random("x"), six_items=True)._generate_context()
        self.assertEqual(ctx["size"], 2)


class StiinteleNaturiiTests(SimpleTestCase):
    """M_șt-nat faithfulness: tehnologic-like I/II (2×2 matrices) but a real-analysis
    Subiectul III (rational/ln derivative study + genuine integrals)."""

    def test_subiect_iii_derivative_is_real_analysis(self):
        # Never the tehnologic poly-dominant study nor mate-info bijectivity —
        # a rational/ln function study (rational | ln_extrem | cubic).
        from apps.exercises.generators.topics.derivatives import DerivativesStudyProblem
        modes = set()
        for s in range(40):
            ctx = DerivativesStudyProblem(
                "stiintele-naturii", random.Random(f"sn{s}")
            )._generate_context()
            modes.add(ctx["mode"])
        self.assertTrue(modes <= {"rational", "ln_extrem", "cubic"}, modes)
        self.assertNotIn("poly", modes)
        self.assertNotIn("exp_bijective", modes)

    def test_matrices_are_2x2_and_integrals_are_direct(self):
        import re
        from apps.exercises.generators.topics.matrices import Matrix2x2Problem
        self.assertIn("stiintele-naturii", Matrix2x2Problem.SUPPORTED_PROFILES)
        for seed in ("sn", "sn2", "sn3"):
            sim = engine.generate_full_simulation(profile="stiintele-naturii", seed=seed)
            ii = sim["subiect_II"]["problems"]
            iii = sim["subiect_III"]["problems"]
            self.assertEqual(ii[0]["topic_primary"], "matrices")
            self.assertIn(ii[1]["topic_primary"], ("algebraic_structures", "polynomials"))
            self.assertEqual([p["topic_primary"] for p in iii], ["derivatives", "integrals"])
            # Every matrix in the statement must be 2×2: each \begin{matrix} block
            # has exactly one row separator (\\) ⇒ two rows. (A 3×3 would have two.)
            blocks = re.findall(r"\\begin\{matrix\}(.*?)\\end\{matrix\}",
                                ii[0]["statement_latex"], re.S)
            self.assertTrue(blocks)
            for b in blocks:
                self.assertEqual(b.count(r"\\"), 1, ii[0]["statement_latex"])


class GeneratorRobustnessTests(SimpleTestCase):
    def test_every_available_topic_generates(self):
        # spec §14.2: generate() should not raise. Exercise the whole pipeline
        # (class + legacy) for every available topic, profile and difficulty.
        for profile in PROFILES:
            for t in [x["code"] for x in engine.supported_topics(profile)]:
                for d in (1, 2, 3):
                    res = engine.generate_exercises(profile=profile, topics=[t],
                                                    difficulty=d, count=4, seed=f"{t}{d}")
                    self.assertEqual(len(res["items"]), 4)
                    for it in res["items"]:
                        self.assertTrue(it["question_latex"].strip())
                        self.assertTrue(it["answer_latex"].strip())

    def test_problem_generators_emit_full_problems(self):
        for topic, cls in PROBLEM_REGISTRY.items():
            for profile in cls.SUPPORTED_PROFILES:
                six = topic in ("matrices", "algebraic_structures") and profile == "pedagogic"
                kwargs = {"six_items": True} if six else {}
                prob = cls(profile, random.Random(f"{topic}{profile}"), **kwargs).generate(1)
                self.assertEqual(len(prob["sub_items"]), 6 if six else 3)
                # topic_primary is the human topic (``cls.TOPIC_CODE``); some
                # registry keys are variants of a topic (e.g. matrices_system).
                self.assertEqual(prob["topic_primary"], cls.TOPIC_CODE)


class CorrectnessTests(SimpleTestCase):
    """Headline computations are sympy-correct (spec §11)."""

    def test_derivative_is_correct(self):
        from apps.exercises.generators.topics.derivatives import DerivativesGenerator, x
        for s in range(30):
            g = DerivativesGenerator("mate-info", 2, random.Random(f"d{s}"))
            params = g._generate_params()
            ans = g._compute_answer(params)
            self.assertEqual(sp.simplify(ans["f_prime"] - sp.diff(g._expr(params), x)), 0)

    def test_matrix_family_is_homomorphism(self):
        from apps.exercises.generators.topics.matrices import MatricesProblem, x, y
        for s in range(20):
            ctx = MatricesProblem("mate-info", random.Random(f"m{s}"))._generate_context()
            A, size = ctx["A"], ctx["size"]
            self.assertEqual(sp.simplify(sp.det(A(x)) - 1), 0)
            self.assertEqual(sp.simplify(A(x) * A(y) - A(x + y)), sp.zeros(size))

    def test_matrix_system_is_consistent(self):
        from apps.exercises.generators.topics.matrices import (
            MatrixSystemProblem, _a, _xs, _ys, _zs,
        )
        for s in range(20):
            ctx = MatrixSystemProblem("mate-info", random.Random(f"ms{s}"))._generate_context()
            A, a0, det0 = ctx["A"], ctx["a0"], ctx["det0"]
            # (a) determinant value; (b) roots make A singular; (c) solution at a1.
            self.assertEqual(int(A.subs(_a, a0).det()), det0)
            for r in ctx["roots"]:
                self.assertEqual(sp.simplify(A.subs(_a, r).det()), 0)
            A1 = A.subs(_a, ctx["a1"])
            self.assertNotEqual(A1.det(), 0)
            sol = sp.linsolve((A1, ctx["b"]), (_xs, _ys, _zs))
            self.assertEqual(sol, sp.FiniteSet(tuple(ctx["s"])))

    def test_matrix_2x2_is_consistent(self):
        from apps.exercises.generators.topics.matrices import Matrix2x2Problem, _px
        for s in range(30):
            ctx = Matrix2x2Problem("tehnologic", random.Random(f"m2x2_{s}"))._generate_context()
            if ctx["mode"] == "concrete":
                A, B, C = ctx["A"], ctx["B"], ctx["C"]
                self.assertEqual(sp.simplify(ctx["cA"] * A + ctx["cB"] * B - ctx["cC"] * C),
                                 sp.zeros(2, 2))
                self.assertEqual(sp.simplify(ctx["X"] * A - ctx["R"]), sp.zeros(2, 2))
                self.assertTrue(all(v.is_integer for v in ctx["X"]))
            else:
                A = ctx["A"]
                self.assertEqual(int(A.subs(_px, ctx["x0"]).det()), ctx["dval"])
                self.assertEqual(sp.simplify(A.subs(_px, ctx["p"]) + A.subs(_px, ctx["q"])
                                             - 2 * A.subs(_px, ctx["m"])), sp.zeros(2, 2))
                self.assertEqual(int(A.subs(_px, ctx["x1"]).det()), ctx["k"])

    def test_integral_primitive_correct(self):
        from apps.exercises.generators.topics.integrals import IntegralsProblem, x
        for s in range(20):
            ctx = IntegralsProblem("tehnologic", random.Random(f"i{s}"))._generate_context()
            self.assertEqual(sp.simplify(sp.diff(ctx["F"], x) - ctx["f"]), 0)
            self.assertEqual(
                sp.simplify(sp.integrate(ctx["f"], (x, ctx["lo"], ctx["hi"])) - ctx["value"]), 0)

    def test_law_neutral_correct(self):
        from apps.exercises.generators.topics.algebraic_structures import (
            AlgebraicStructuresProblem,
        )
        xx, yy = sp.symbols("x y", real=True)
        for s in range(20):
            ctx = AlgebraicStructuresProblem("mate-info", random.Random(f"a{s}"))._generate_context()
            f, e = ctx["f"], ctx["e"]
            self.assertEqual(sp.simplify(f(xx, e) - xx), 0)
            self.assertEqual(sp.simplify(f(xx, yy) - f(yy, xx)), 0)


class ValidationTests(SimpleTestCase):
    def test_validation_helpers(self):
        from apps.exercises.generators.validation import is_clean_latex, is_sane_value
        self.assertTrue(is_clean_latex("$x = 3$"))
        self.assertFalse(is_clean_latex(""))
        self.assertFalse(is_clean_latex("$\\text{nan}$"))
        self.assertTrue(is_sane_value(sp.Integer(5)))
        self.assertFalse(is_sane_value(sp.nan))
        self.assertTrue(is_sane_value(None))  # custom-string answers allowed
