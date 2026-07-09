"""Canonical registry data — profiles, topic restrictions, labels, exam rules.

Single source of truth derived from ``generator.md`` §3–5, §8.2, §10.2. The
``CLASS_REGISTRY`` fills up as topics are ported to classes (see
GENERATOR_REWORK.md §7). Until a topic is ported, the legacy function registry in
``generators/__init__.py`` still serves it.
"""
from __future__ import annotations

# topic_code -> human label (Romanian). Spec §12 terminology.
TOPIC_LABELS: dict[str, str] = {
    "arithmetic": "Calcul numeric",
    "powers": "Puteri și radicali",
    "logarithms": "Logaritmi",
    "functions": "Funcții",
    "equations": "Ecuații în ℝ",
    "complex": "Numere complexe",
    "polynomials": "Polinoame",
    "matrices": "Matrice și determinanți",
    "systems": "Sisteme de ecuații liniare",
    "algebraic_structures": "Structuri algebrice",
    "sequences": "Șiruri",
    "limits": "Limite de funcții",
    "derivatives": "Derivate",
    "integrals": "Primitive și integrale",
    "geometry": "Geometrie plană și analitică",
    "trigonometry": "Trigonometrie",
    "combinatorics": "Combinatorică și probabilități",
    "progressions": "Progresii",
    "statistics": "Statistică",
}

# Allowed topics per profile (spec §8.2 PROFILE_TOPICS, verbatim).
PROFILE_TOPICS: dict[str, list[str]] = {
    "mate-info": [
        "powers", "logarithms", "functions", "equations", "complex", "polynomials",
        "matrices", "systems", "algebraic_structures",
        "sequences", "limits", "derivatives", "integrals",
        "geometry", "trigonometry", "combinatorics", "progressions",
    ],
    "stiintele-naturii": [
        "arithmetic", "powers", "logarithms", "functions", "equations", "complex",  # complex: algebraic only
        "polynomials", "matrices", "systems", "algebraic_structures",
        "sequences", "limits", "derivatives", "integrals",
        "geometry", "trigonometry", "combinatorics", "progressions",
    ],
    "tehnologic": [
        "arithmetic", "powers", "logarithms", "functions", "equations", "complex",  # complex: algebraic only
        "polynomials", "matrices", "systems", "algebraic_structures",
        "sequences", "limits", "derivatives", "integrals",
        "geometry", "trigonometry", "combinatorics", "progressions",
    ],
    "pedagogic": [
        "arithmetic", "powers", "logarithms", "functions", "equations",
        "matrices",                 # 2×2 only
        "algebraic_structures",     # basic
        "geometry", "trigonometry", "combinatorics",
        "progressions", "statistics",
        "derivatives",              # polynomials only
    ],
}

# Canonical ordered list of profile slugs (hardest → easiest). Single source of
# truth — serializers, views, and the frontend derive their choices from this, so
# adding a level (e.g. ``stiintele-naturii``) means editing only the data above.
PROFILES: tuple[str, ...] = tuple(PROFILE_TOPICS)

# Human display names (Romanian) for each profile slug.
PROFILE_DISPLAY: dict[str, str] = {
    "mate-info": "Matematică–Informatică",
    "stiintele-naturii": "Științele Naturii",
    "tehnologic": "Tehnologic",
    "pedagogic": "Pedagogic",
}

# Per-profile capability flags the generators must honor (spec §3–5, §13.1).
PROFILE_CAPS: dict[str, dict] = {
    "mate-info": {"matrix_size": (2, 3), "complex": "full", "derivatives": "full"},
    "stiintele-naturii": {"matrix_size": (2,), "complex": "algebraic_only", "derivatives": "full"},
    "tehnologic": {"matrix_size": (2, 3), "complex": "algebraic_only", "derivatives": "full"},
    "pedagogic": {"matrix_size": (2,), "complex": None, "derivatives": "poly_only"},
}

# Exam composition per profile (spec §10.2). Slot topics that offer a choice are
# given as tuples; the engine picks one per-seed. M3's II/III are single-topic
# 6-item formats (spec §5.4).
SIMULATION_RULES: dict[str, dict] = {
    # Subiectul I slots follow the fixed position→topic roles of the real papers
    # (info-on-sub1.md §0/§10): 1 algebra-on-numbers · 2 functions · 3 equation in ℝ
    # · 4 probability/percentage · 5 analytic geometry · 6 trigonometry/triangle.
    "mate-info": {
        "subiect_I": [
            # 1: the real M1 papers open with complex numbers or a progression
            # term-finding item about equally often, with radicals (powers) and
            # base-10 logarithm identities as the secondary flavours. Repetition
            # weights the uniform picker toward that observed distribution.
            ("complex", "complex", "progressions", "progressions", "powers", "logarithms"),
            ("functions",),                          # 2: functions (quadratic-dominated)
            ("equations",),                          # 3: equation in ℝ
            ("combinatorics",),                      # 4: probability / subsets
            ("geometry",),                           # 5: analytic geometry
            ("trigonometry",),                       # 6: trig / triangle
        ],
        "subiect_II": {"format": "two_problems",
                       "problems": [("matrices", "matrices_system"),
                                    ("polynomials", "algebraic_structures")]},
        "subiect_III": {"format": "two_problems",
                        "problems": [("derivatives",), ("integrals",)]},
    },
    "stiintele-naturii": {
        # M_șt-nat (files/exam_corpus/stiintele-naturii/ANALYSIS/): Subiectul I & II
        # play like tehnologic (easy; 2×2 matrices), but Subiectul III is real
        # analysis — a rational/ln derivative study + genuine definite integrals
        # (the derivatives/integrals generators branch on the profile for this).
        "subiect_I": [
            ("progressions", "progressions", "arithmetic"),  # 1: progression term (+ occasional numeric)
            ("functions",),                          # 2: linear/affine function
            ("equations",),                          # 3: equation in ℝ (log/exp)
            ("combinatorics",),                      # 4: probability / counting
            ("geometry",),                           # 5: analytic geometry
            ("trigonometry",),                       # 6: trig / triangle
        ],
        # Subiectul II: 2×2 matrices (affine param / solve-X) + law / polynomials.
        "subiect_II": {"format": "two_problems",
                       "problems": [("matrices_2x2",),
                                    ("algebraic_structures", "polynomials")]},
        # Subiectul III: rational/ln derivative study + genuine definite integrals.
        "subiect_III": {"format": "two_problems",
                        "problems": [("derivatives",), ("integrals",)]},
    },
    "tehnologic": {
        # M_tehnologic Subiectul I (info from files/exam_corpus/M2/ANALYSIS_M2.md):
        # 1 numeric computation (fractions/radicals) · 2 linear function · 3 equation
        # · 4 probability over a small explicit set / percentage · 5 geometry · 6 trig.
        "subiect_I": [
            ("arithmetic", "arithmetic", "progressions"),  # 1: numeric calc (+ occasional progression)
            ("functions",),                          # 2: linear function
            ("equations",),                          # 3: equation in ℝ
            ("combinatorics",),                      # 4: probability over explicit set / %
            ("geometry",),                           # 5: analytic geometry
            ("trigonometry",),                       # 6: trig / triangle
        ],
        # Subiectul II: 2×2 matrices (concrete / affine param) + law / polynomials.
        "subiect_II": {"format": "two_problems",
                       "problems": [("matrices_2x2",),
                                    ("algebraic_structures", "polynomials")]},
        "subiect_III": {"format": "two_problems",
                        "problems": [("derivatives",), ("integrals",)]},
    },
    "pedagogic": {
        "subiect_I": [
            ("progressions", "powers"),              # 1: progressions / powers
            ("functions",),                          # 2: functions (linear only)
            ("equations",),                          # 3: equation (simple)
            ("combinatorics", "statistics"),         # 4: probability / percentage
            ("geometry",),                           # 5: geometry (simple)
            ("trigonometry", "geometry"),            # 6: triangle / Pythagoras
        ],
        "subiect_II": {"format": "single_topic_6_items", "topic": "algebraic_structures"},
        "subiect_III": {"format": "single_topic_6_items", "topic": "matrices"},
    },
}


# topic_code -> ExerciseGenerator subclass (single-item). Filled during porting.
CLASS_REGISTRY: dict[str, type] = {}

# topic_code -> ProblemGenerator subclass (multi sub-item). Filled during porting.
PROBLEM_REGISTRY: dict[str, type] = {}


def _register():
    """Import ported topic classes and populate the registries.

    Wrapped in try/except per topic so a not-yet-ported topic never breaks import
    (the legacy function registry covers it meanwhile).
    """
    from importlib import import_module

    single = {
        "arithmetic": ("topics.arithmetic", "ArithmeticGenerator"),
        "derivatives": ("topics.derivatives", "DerivativesGenerator"),
        "functions": ("topics.functions", "FunctionsGenerator"),
        "equations": ("topics.equations", "EquationsGenerator"),
        "geometry": ("topics.geometry", "GeometryGenerator"),
        "logarithms": ("topics.logarithms", "LogarithmsGenerator"),
        "sequences": ("topics.sequences", "SequencesGenerator"),
        "statistics": ("topics.statistics", "StatisticsGenerator"),
        "systems": ("topics.systems", "SystemsGenerator"),
        "powers": ("topics.powers", "PowersGenerator"),
        "complex": ("topics.complex", "ComplexNumbersGenerator"),
        "trigonometry": ("topics.trigonometry", "TrigonometryGenerator"),
        "combinatorics": ("topics.combinatorics", "CombinatoricsGenerator"),
        "progressions": ("topics.progressions", "ProgressionsGenerator"),
        "limits": ("topics.limits", "LimitsGenerator"),
        # Single-item facades over the problem-only topics (antrenament practice
        # of one cerință at a time; the problem forms stay in PROBLEM_REGISTRY).
        "matrices": ("topics.facades", "MatricesFacade"),
        "polynomials": ("topics.facades", "PolynomialsFacade"),
        "integrals": ("topics.facades", "IntegralsFacade"),
        "algebraic_structures": ("topics.facades", "AlgebraicStructuresFacade"),
    }
    problem = {
        "matrices": ("topics.matrices", "MatricesProblem"),
        "matrices_system": ("topics.matrices", "MatrixSystemProblem"),
        "matrices_2x2": ("topics.matrices", "Matrix2x2Problem"),
        "algebraic_structures": ("topics.algebraic_structures", "AlgebraicStructuresProblem"),
        "derivatives": ("topics.derivatives", "DerivativesStudyProblem"),
        "integrals": ("topics.integrals", "IntegralsProblem"),
        "polynomials": ("topics.polynomials", "PolynomialsProblem"),
    }
    for code, (mod, cls) in single.items():
        try:
            m = import_module(f"{__package__}.{mod}")
            CLASS_REGISTRY[code] = getattr(m, cls)
        except Exception:
            pass
    for code, (mod, cls) in problem.items():
        try:
            m = import_module(f"{__package__}.{mod}")
            PROBLEM_REGISTRY[code] = getattr(m, cls)
        except Exception:
            pass


_register()
