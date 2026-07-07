"""Single-item facades over the problem-only topics (training / antrenament).

``matrices``, ``polynomials``, ``integrals`` and ``algebraic_structures`` are
``ProblemGenerator``s (linked a/b/c) used in the Simulare (Subiectele II/III). To
let users practice *one cerință at a time* in ``/generate``, each facade generates
a full problem and surfaces a single sub-item — matched to the requested
difficulty — as a standalone exercise, prefixing the shared statement.

This deliberately reuses each problem's own randomized cerință pool + sympy
verification, so no mathematics is duplicated: the variety a user sees in
antrenament is exactly the variety the Simulare produces, one cerință at a time.
"""
from __future__ import annotations

import random

from ..base import ExerciseGenerator
from ..validation import item_is_clean
from .algebraic_structures import AlgebraicStructuresProblem
from .integrals import IntegralsProblem
from .matrices import MatricesProblem
from .polynomials import PolynomialsProblem


class _ProblemFacade(ExerciseGenerator):
    """Surface one sub-item of a ProblemGenerator as a standalone exercise."""

    PROBLEM_CLS: type | None = None

    # ABC hooks are unused — ``generate`` is overridden — but must exist.
    def _generate_params(self) -> dict:
        return {}

    def _compute_answer(self, params):
        return None

    def _validate(self, params, answer) -> bool:
        return True

    def _build_question(self, params) -> str:
        return ""

    def generate(self) -> dict:
        for _ in range(self.MAX_RETRIES):
            try:
                # Fresh derived rng per attempt: keeps reproducibility (seeded from
                # self.rng) while letting an over-long roll be retried away.
                r = random.Random(self.rng.random())
                prob = self.PROBLEM_CLS(self.profile, r).generate(1)
                cands = [s for s in prob["sub_items"] if s["difficulty"] == self.difficulty]
                sub = (cands or prob["sub_items"])[0]
                statement = prob["statement_latex"].strip()
                question = f"{statement} {sub['question_latex'].strip()}".strip()
                item = {
                    "topic": self.TOPIC_CODE,
                    "difficulty": self.difficulty,
                    "question_latex": question,
                    "answer_latex": sub["answer_latex"],
                }
                if sub.get("hint_latex"):
                    item["hint_latex"] = sub["hint_latex"]
                if sub.get("steps_latex"):
                    item["steps_latex"] = sub["steps_latex"]
                if item_is_clean(item):
                    return item
            except Exception:
                continue
        raise RuntimeError(
            f"Facada {self.TOPIC_CODE} nu a putut produce un exercițiu valid "
            f"(profile={self.profile}, difficulty={self.difficulty})"
        )


class MatricesFacade(_ProblemFacade):
    TOPIC_CODE = "matrices"
    SUPPORTED_PROFILES = MatricesProblem.SUPPORTED_PROFILES
    PROBLEM_CLS = MatricesProblem


class PolynomialsFacade(_ProblemFacade):
    TOPIC_CODE = "polynomials"
    SUPPORTED_PROFILES = PolynomialsProblem.SUPPORTED_PROFILES
    PROBLEM_CLS = PolynomialsProblem


class IntegralsFacade(_ProblemFacade):
    TOPIC_CODE = "integrals"
    SUPPORTED_PROFILES = IntegralsProblem.SUPPORTED_PROFILES
    PROBLEM_CLS = IntegralsProblem


class AlgebraicStructuresFacade(_ProblemFacade):
    TOPIC_CODE = "algebraic_structures"
    SUPPORTED_PROFILES = AlgebraicStructuresProblem.SUPPORTED_PROFILES
    PROBLEM_CLS = AlgebraicStructuresProblem
