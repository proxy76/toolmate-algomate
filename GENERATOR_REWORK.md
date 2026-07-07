# Generator Rework — Implementation Log & Continuity Doc

> **Read this first, every session.** This is the persistent brain for the
> multi-session rework of the Algomate BAC exercise/exam generator. The
> canonical spec is [`generator.md`](generator.md) (1867 lines) — this file is
> the *condensed plan + gap analysis + step tracker + session log* so a new
> session can resume without re-reading everything. When `generator.md` and this
> file disagree, **`generator.md` wins** — fix this file.

> **STATUS: feature-complete vs `generator.md`.** All topics are class-based; the
> legacy function modules are removed (P4.5). Problem-only topics now also have
> single-item facades for antrenament (S5 cont.). Remaining work is optional polish
> (more subtype variety, more tests).
>
> **M1 faithfulness pass vs the `files/` 24-paper corpus (Session 7, 2026-07-07).**
> Audited every M1 topic against `files/exam_corpus/` and closed the biggest "tells":
> pos-2 now quadratic-dominated; pos-4 dropped urns for the real digit-condition
> family; pos-1 rotates complex/progressions/powers/logarithms with authentic "Arătați
> că" phrasings (M1 progressions enabled, OQ1 reversed); Subiect II prob-1 now rotates
> the homomorphism family with a new **matrix A(a)+system** family; M1 integrals no
> longer always the sequence mode. All sympy-verified; 18/18 tests green.
>
> **Subiectul I aligned to `info-on-sub1.md` (Session 4, 2026-06-30).** Subiectul I
> now follows the fixed position→topic roles of the real papers (1 algebra-on-numbers
> · 2 **functions** · 3 **equation in ℝ** · 4 probability/percentage · 5 analytic
> geometry · 6 trig/triangle). Two new single-item topics — `functions` and
> `equations` — were added for positions 2 & 3 (previously `derivatives` /
> `logarithms` stood in). Position 4 (`combinatorics`) gained the authentic
> two-digit-probability / subsets / percentage phrasings.

**Continuity protocol per session**
1. Read this file top-to-bottom (esp. *Step Plan* and *Session Log*).
2. Pick the next unchecked step. Re-open the relevant `generator.md` section.
3. Implement. Keep the app **green** at the end of every session (imports OK,
   `python manage.py check` passes, frontend `tsc -b` + `vite build` pass).
4. Update the *Step Plan* checkboxes, the *Generator Status* table, and append a
   *Session Log* entry (date, what changed, what's next, any decisions).

---

## 1. Goal

Rework the exercise + exam generator so it **fully** implements `generator.md`:
authentic BAC formulations (RO), three profiles (M1/M2/M3) with their exact
topic restrictions, structural difficulty, sympy-verified correctness, seedable
reproducibility, and a Simulare that reproduces the official paper structure
(Subiectul I = 6×5p items; II & III = 2 problems × a/b/c × 5p; M3 special-cased).

## 2. Current state (baseline before rework)

Function-based engine, working and deployed. Key files:
- `backend/apps/exercises/engine.py` — `generate_set()`, `simulate_bac()`.
- `backend/apps/exercises/generators/__init__.py` — `REGISTRY: (topic,profile)->callable`, `SUPPORTED_TOPICS_PER_PROFILE`, `TOPIC_LABELS`.
- `backend/apps/exercises/generators/_utils.py` — `make()`, `choose_subtype()`, tiers, `latex()`, coef helpers. **Difficulty is structural** (coefficients stay small at all levels).
- `backend/apps/exercises/generators/<topic>.py` — 11 function modules:
  powers, logarithms, complex_numbers, polynomials, matrices, limits,
  derivatives, integrals, trigonometry, combinatorics, progressions.
- API: `views.py` (TopicsView, GenerateView, SimulateView, SessionListCreateView),
  `serializers.py`, `models.py` (`ExerciseSession` snapshot).
- Frontend consumes: `/generate` -> `{seed, items:[Exercise]}`;
  `/simulate` -> `{seed, subiectul_I[], subiectul_II[], subiectul_III[]}` (FLAT).
  Types in `frontend/src/types.ts`; rendered by `Practice.tsx` / `Simulate.tsx`.

## 3. Gap analysis (current → target per `generator.md`)

| # | Area | Current | Target (spec §) | Action |
|---|------|---------|-----------------|--------|
| G1 | Architecture | function generators | class `ExerciseGenerator` ABC + `topics/` + `registry.py` + `difficulty.py` + `engine.py` (§8.1–8.3) | Migrate to classes |
| G2 | **Multi-part problems** | single items only | Subiect II/III = problems w/ linked a/b/c sub-items (§2.3–2.4, §10) | New `ProblemGenerator` ABC |
| G3 | Simulate shape | flat `subiectul_*` lists, II/III only 2 items | nested `subiect_I.items[6]`, `subiect_II/III.problems[2].sub_items[a,b,c]`, points, 90+10 (§10.1) | Rework engine + **frontend** |
| G4 | M3 special exam | not handled | II = 1 law-of-composition w/ 6 sub-items; III = 1 matrix-2×2 w/ 6 sub-items (§5.4, §10.2) | `single_topic_6_items` format |
| G5 | Missing generators | — | `geometry`, `algebraic_structures`, `systems`, `sequences`, `statistics` absent; `logarithms`/M3 absent (§8.2 PROFILE_TOPICS) | Build them |
| G6 | Per-item seeds | one shared rng, sequential draws | derived `random.Random(f"{seed}_{i}_{topic}")` (§8.3, §13.2) | Adopt |
| G7 | Difficulty spread | one tier for whole set | `compute_item_difficulty` 80/20, 20/60/20, 10/90 (§8.4) | Adopt |
| G8 | Variety guard | shuffle only | no repeated subtype back-to-back; test wants >50 distinct/100 (§13.2, §14.4) | Add rotation + test |
| G9 | Validation gardens | ad-hoc per gen | central NaN/zoo, latex<300, coef≤1000, domain non-empty, log/sqrt/det/continuity (§11.3–11.4) | Central `_validate` + helpers |
| G10 | LaTeX/grammar | `latex(mul_symbol=dot)` | sets map, RO article agreement, `sympy_to_bac_latex` (§12) | Conventions module |
| G11 | Profile caps | partial | M3 matrices 2×2 only; M2 complex algebraic-only; M3 derivatives poly-only (§3–5, §13.1) | Encode in registry/caps |
| G12 | Difficulty numbers | strictly structural | spec allows modest coef growth + more params at d2/d3 while keeping results clean (§7.2) | Blend: technique-first, mild coef growth, clean answers |

## 4. Key decisions

- **D1 — Adopt the spec's class architecture** as canonical. Port each topic to a
  class in `generators/topics/`. Keep legacy function modules working until each
  topic is ported (parity-then-switch), so the app never breaks mid-migration.
- **D2 — Two base classes.** `ExerciseGenerator` (single item, spec §8.1) and a new
  `ProblemGenerator` (shared context + a/b/c sub-items) — the spec's §10 demands
  linked sub-items, which the single-item ABC cannot express. A `ProblemGenerator`
  emits `{number, topic_primary, statement_latex, sub_items:[{label,points,difficulty,question_latex,hint_latex,answer_latex,steps_latex}]}`.
- **D3 — Simulate naming follows the spec:** `subiect_I/II/III` with nested
  `items`/`problems`. The frontend will be migrated to the new shape (G3). Until
  then, the legacy `simulate_bac` stays so the live app keeps working; switch
  `SimulateView` only when the new path + frontend are ready (one session, atomic).
- **D4 — Difficulty (G12):** technique-first per `_utils.py` philosophy, but honor
  §7.2 by allowing *mild* coefficient/parameter growth at d2/d3. **Answers must
  stay clean** (int / simple fraction / √2,√3,√5) per §13.2. Never escalate by
  arithmetic mess alone.
- **D5 — Reproducibility (G6):** per-item derived seeds. `generate_exercises` and
  `generate_full_simulation` both derive a child `random.Random` per item/sub-item
  from the master seed so the same seed reproduces the same paper exactly (§14.4).
- **D6 — Continuity doc location:** this file at repo root; a project memory points
  to it. Do not duplicate spec content — link to `generator.md` sections.

## 5. Target architecture (spec §8, adapted)

```
apps/exercises/
  generators/
    __init__.py            # (legacy registry — shrinks as topics are ported)
    base.py                # ExerciseGenerator (ABC) + ProblemGenerator (ABC)   [NEW]
    difficulty.py          # DIFFICULTY params + compute_item_difficulty        [NEW]
    latexconv.py           # sets map, RO grammar, sympy_to_bac_latex (§12)      [planned]
    registry.py            # CLASS_REGISTRY, PROFILE_TOPICS, PROFILE_CAPS, LABELS [NEW, canonical data]
    topics/
      __init__.py
      derivatives.py       # class DerivativesGenerator  (reference, §9.1)
      ... (one class per topic; problem-capable topics also export a ProblemGenerator)
    engine.py              # generate_exercises() + generate_full_simulation()   [planned: replaces app-level engine.py]
```

Canonical data (from spec §8.2, §10.2, §3–5):

**PROFILE_TOPICS**
- M1: powers, logarithms, complex, polynomials, matrices, systems, algebraic_structures, sequences, limits, derivatives, integrals, geometry, trigonometry, combinatorics
- M2: + progressions; complex = **algebraic only**
- M3: powers, logarithms, matrices(**2×2**), algebraic_structures(basic), geometry, trigonometry, combinatorics, progressions, statistics, derivatives(**poly only**)

**PROFILE_CAPS**
- M3: `matrix_size=2`, `derivatives=poly_only`, no {complex, integrals, limits, sequences, systems, polynomials-Horner, abstract structures}
- M2: `complex=algebraic_only`; matrices 2×2 & 3×3; structures reduced
- M1: full

**SIMULATION_RULES** (slot topics per profile — spec §10.2): see `generator.md` §10.2 verbatim. Summary:
- M1 I: [log|complex], derivatives(simple), [log|powers|complex], combinatorics, geometry, trigonometry · II: matrices, [polynomials|algebraic_structures] · III: derivatives, integrals
- M2 I: [progressions|log], derivatives, [log|powers], combinatorics, geometry, trigonometry · II: matrices, algebraic_structures · III: derivatives, integrals
- M3 I: progressions, derivatives, logarithms, [combinatorics|statistics], geometry, geometry · II: **algebraic_structures ×6** · III: **matrices(2×2) ×6**

**Difficulty distribution** (§8.4): d1→[1,1,1,1,2], d2→[1,2,2,2,3], d3→[2,3,3,3,3], indexed by `position % 5`.

**Progressive a/b/c** (§10.3): a→d1/2, b→d2, c→d3; later sub-items may reuse earlier results.

## 6. Step Plan (master TODO)

### Phase 0 — Foundation (non-breaking; additive modules)
- [x] P0.1 Read `generator.md` fully + survey current code.
- [x] P0.2 Write this continuity doc.
- [x] P0.3 `generators/base.py`: `ExerciseGenerator` + `ProblemGenerator` ABCs.
- [x] P0.4 `generators/difficulty.py`: `DIFFICULTY` params + `compute_item_difficulty`.
- [x] P0.5 `generators/registry.py`: `PROFILE_TOPICS`, `PROFILE_CAPS`, `TOPIC_LABELS`, empty `CLASS_REGISTRY`, `SIMULATION_RULES`.
- [x] P0.6 `generators/topics/` package + port **derivatives** to a class (reference, §9.1) as proof of the foundation.
- [x] P0.7 Smoke test: reproducibility + sympy correctness for the ported class. (Keep legacy live; do not wire yet.)

### Phase 1 — Engine + problem model
- [x] P1.1 `ProblemGenerator` slice: `matrices` problem (a/b/c + M3 6-item) — verified homomorphism family (det=1, A(x)A(y)=A(x+y)), product/inverse/power/system cerinte. `topics/matrices.py`.
- [x] P1.2 `algebraic_structures` problem (§9.3, §5.4) incl. M3 6-item. Correct neutral elements (spec's §9.3 "e=1" label is wrong — verified with sympy). `topics/algebraic_structures.py`.
- [x] P1.3 New `engine.generate_exercises` (per-item seeds G6, difficulty spread G7, variety guard G8). `generators/engine.py`.
- [x] P1.4 New `engine.generate_full_simulation` (nested shape G3/G4, points 90+10, M3 special-cased G4). `generators/engine.py`.
- [x] P1.5 Frontend: new `SimulateResponse`/`SimItem`/`SimProblem`/`SimSubItem` types + `Simulate.tsx` rewritten to render Subiectul I items and II/III problems with a/b/c sub-items + inline hint/answer/steps reveals.
- [x] P1.6 Switched `GenerateView`→`generate_exercises`, `SimulateView`→`generate_full_simulation`, `TopicsView`→new catalogue; **deleted legacy app-level `engine.py`**. New engine is **LIVE**.

> **State after session 2: the new engine is LIVE.** Views use
> `generators/engine.py`; legacy app-level `engine.py` deleted. `/simulate`
> returns the nested `subiect_I/II/III` shape and the frontend renders it.
> Legacy *function* generators remain as fallbacks inside the new engine.
>
> **Note — problem-only topics:** `matrices` & `algebraic_structures` are now
> `ProblemGenerator`s, so they are **not** offered in the `/generate` single-item
> menu (only the function/class single-item generators are). If single-item
> practice of these is wanted, add a single-item facade later (not spec-required).
>
> **Transitional bridges in the new engine (remove as topics are ported):**
> - Subiect II/III problems use real `ProblemGenerator`s for `matrices` &
>   `algebraic_structures` (so **M3 II/III are fully linked 6-item problems**);
>   other problem slots (derivatives/integrals/polynomials) use
>   `_adapter_problem` (a/b/c from single-item gens, empty `statement_latex`).
> - Subiect I slots whose topic has no generator yet (`geometry`, `statistics`)
>   fall back to an available profile topic via `_pick_topic`. Build those in
>   Phase 2/3 to honor §10.2 exactly.

### Phase 2 — Port Subiectul-I + M1 topics (spec §14.1 Faza 2)
- [x] P2.1 logarithms (incl. **M3**) — `topics/logarithms.py` class (identity / simple eq / linear eq / inequality; M3 restricted to simple). Removes the M3 Subiectul I logarithms fallback.
- [x] P2.2 complex (M1 full / M2 algebraic) — `topics/complex.py` class
- [x] P2.3 polynomials — `PolynomialsProblem` (M1/M2 Subiectul II prob 2: f(1) fixed / division / Viète). **Retires the polynomials adapter.**
- [x] P2.4 geometry (NEW, all profiles) — `topics/geometry.py`, removes Subiectul I fallback
- [x] P2.5 trigonometry — `topics/trigonometry.py` class  · [x] P2.6 combinatorics — `topics/combinatorics.py` class
- [x] P2.7 integrals (problem-capable) — `IntegralsProblem` (primitive / ∫ / area, all sympy-verified)
- [x] P2.8 derivatives Subiectul-III problem-form — `DerivativesStudyProblem` (cubic: f'/monotonie/1-root; rational: f'/oblique/vertical asymptote). **Retires the `_adapter_problem` for M1/M2 Subiectul III.**

### Phase 3 — Complete M2/M3 + extras (spec §14.1 Faza 3)
- [x] P3.1 progressions — `topics/progressions.py` class  · [x] P3.2 sequences (NEW) — `topics/sequences.py` (limits/series/recurrence/Cesàro)
- [x] P3.3 limits — `topics/limits.py` class  · [x] P3.4 powers — `topics/powers.py` class
- [x] P3.5 statistics (NEW) — `topics/statistics.py` (mean/median/find-value, M3)
- [x] P3.6 systems (NEW) — `topics/systems.py` (2×2 / 3×3 / parametric, M1/M2)
- [x] P3.7 engine fix — `_pick_problem_topic` prefers problem-capable topics for
  Subiect II/III, so the `_adapter_problem` is no longer reached in normal
  simulate (every II/III problem is a real linked `ProblemGenerator`).

### Phase 4 — Hardening & conventions
- [x] P4.1 `latexconv.py` — `LATEX_SETS`, `RO_TERMS`, `sympy_to_bac_latex` (used by base default). Note: deliberately does **not** apply the spec's buggy `\log→\ln` replacement. Generators already follow §12 grammar/sets in their strings.
- [x] P4.2 Central validation gardens — `validation.py` (`is_sane_value`, `is_clean_latex`, `item_is_clean`); wired as a final gate in `ExerciseGenerator.generate` and `ProblemGenerator.generate` (§11.3–11.4).
- [x] P4.3 Test suite — `apps/exercises/tests/test_generators.py` (15 tests, `python manage.py test apps.exercises`): reproducibility, variety >50/100, structure+points, M3 special-casing, progressive difficulty, profile restriction, per-generator robustness, sympy correctness, validation.
- [x] P4.4 Checklist-as-tests — §14.2–14.3 items covered by the suite (robustness, structure, points, restrictions, correctness).
- [x] P4.5 **Remove legacy function modules** — DONE. Ported the 6 remaining
  single-item topics to classes via a new `TieredExerciseGenerator` base, then
  deleted all 11 legacy `generators/*.py` topic modules and the legacy
  `__init__.py` `REGISTRY`; `engine.py` no longer has a legacy fallback. The
  codebase is now **fully class-based** (12 single-item in `CLASS_REGISTRY`, 5
  problems in `PROBLEM_REGISTRY`; only `_utils.py` helpers remain).
  **Architecture rule established:** multi-part topics (`matrices`, `polynomials`,
  `integrals`, `algebraic_structures`) are **problem-only** (simulate Subiect
  II/III); atomic topics are single-item (`/generate`). So those four are no
  longer in the `/generate` menu — add single-item facades later only if
  individual practice of them is wanted.

## 7. Generator status

Legend: ✅ class+problem done · 🟡 class single-item · ⬜ legacy func only · ❌ missing

| Topic | M1 | M2 | M3 | Notes |
|-------|----|----|----|-------|
| functions | 🟡 | 🟡 | 🟡 | `FunctionsGenerator` (Subiectul I pos 2). **S7: authentic quadratic/parabola family** (vertex ordinate sign / on-Ox / tangent / f>0 ∀x / two roots / ∩ line / point-on-parabola) at tier 2/3 → M1 pos-2 quadratic-dominated; M3 linear-only — `info-on-sub1.md` §2 |
| equations | 🟡 | 🟡 | 🟡 | `EquationsGenerator` (Subiectul I pos 3; exp/log/irr/abs under the invariant wrapper; M3 single-step base∈{2,3,10}) — `info-on-sub1.md` §3 |
| derivatives | ✅ | ✅ | 🟡 | single-item class (all) + `DerivativesStudyProblem` (M1/M2 Subiect III); M2 cubic/rational, **M1 adds exp-bijectivity + ln-extremum** (S6) |
| matrices | ✅ | ✅ | ✅ | `MatricesProblem` (a/b/c + M3 6-item), homomorphism family, sympy-verified; **randomized cerinte** (det/trace/sum/product/commut./inverse/find-x/solve-X/power/system, distinct-theme guard) + 10×2 & 6×3 families (S5). **S7: `MatrixSystemProblem`** — the "matrice A(a)+sistem" family (det value / unique-solution / solve-with-property), M1/M2 prob-1 rotates homomorphism↔system ~50/50 |
| algebraic_structures | ✅ | ✅ | ✅ | `AlgebraicStructuresProblem` (a/b/c + M3 6-item), comm/assoc/neutral verified; **M1 adds associativity + morphism cerinte** (S6) |
| integrals | ✅ | ✅ | — | `IntegralsProblem`; M2 primitive/∫/area; M1 sequence Iₙ + recurrence + limit (S6) — **S7: now ~30% sequence / ~70% direct-∫/area** (was 100% sequence) to match corpus frequency; M3 excluded |
| logarithms | ✅ | ✅ | ✅ | `LogarithmsGenerator` class. **S7: now the numeric-identity/inequality flavour** (base-10 `lg` multi-term + subtraction identities) — log *equations* belong to the `equations` topic, so the pos-1 exam slot is a genuine identity |
| complex | ✅ | ✅(alg) | — | `ComplexNumbersGenerator` class; M2 algebraic-only; M3 excluded. **S7: authentic pos-1 "Arătați că <expr>=<val>" / modulus-of-expression / find-(a,b)** items (weighted ×2 at M1 pos-1 tier), replacing the "Calculează" tells |
| polynomials | ✅ | ✅ | — | `PolynomialsProblem` (Subiect II prob 2: eval/division/Viète), sympy-verified |
| geometry | ✅ | ✅ | ✅ | `GeometryGenerator` single-item (point/midpoint/distance/vector/Pitagora), all sympy-verified |
| trigonometry | ✅ | ✅ | ✅ | `TrigonometryGenerator` class; **rich pos-6 tier-1 pool** (values/expr, right-triangle ratio/perimeter/side/two-angle, area+parametrized identity, Pyth. ratio) + **enriched d2/d3** (tg-from-ratio, parametrized double-angle, quadratic-in-sin/cos, provable identities) (S5); M3 = remarkable values only |
| combinatorics | ✅ | ✅ | ✅ | `CombinatoricsGenerator` class; M3 = direct counting. **S7: dropped urns** (not in corpus); added the real pos-4 digit-condition family (2-/3-digit divisibility/parity/prime/product-of-digits/distinct/bounds + subsets + counts) |
| progressions | ✅ | ✅ | ✅ | `ProgressionsGenerator` class. **S7: enabled for M1** (OQ1 reversed) + corpus phrasings (term-from-two-terms, consecutive-terms proof); serves M1/M2/M3 Subiectul I pos-1 |
| sequences | ✅ | ✅ | — | `SequencesGenerator` (limits/series/recurrence/Cesàro), sympy-verified |
| limits | ✅ | ✅ | — | `LimitsGenerator` class |
| powers | ✅ | ✅ | ✅ | `PowersGenerator` class; M3 = D1 laws only |
| statistics | — | — | ✅ | `StatisticsGenerator` (mean/median/find-value), exact rationals |
| systems | ✅ | ✅ | — | `SystemsGenerator` (2×2 / 3×3 / parametric), `linsolve`/`det` verified |

## 8. Open questions / risks

- **OQ1** M1 `progressions`: **RESOLVED (Session 7, 2026-07-07)** — the `files/`
  corpus shows arithmetic/geometric term-finding is ~40% of real M1 pos-1 items, so
  progressions is now **enabled for M1** (PROFILE_TOPICS + pos-1 rotation). The earlier
  "follow PROFILE_TOPICS (no M1 progressions)" decision is reversed by exam evidence.
- **OQ2** `compute_item_difficulty` vs user-requested single difficulty for `/generate`:
  apply the spread so a set has natural variation; the item's stamped `difficulty`
  reflects the tier that produced it (never lies). Confirm UI shows per-item tier.
- **OQ3** Legacy `simulate` keys are `subiectul_I/II/III`; spec uses `subiect_I/II/III`.
  Switching renames the API field → frontend must change in the same session (P1.5/6).
- **R1** Big surface; keep each session shippable. Never leave imports broken.
- **R2** Some §9.2 matrix homomorphism families need sympy verification of
  `A(x)·A(y)=A(x+y)` symbolically — validate, don't assume.

## 9. Session Log

### Session 7 — 2026-07-07 — M1 faithfulness pass against the `files/` exam corpus
- **Context:** a new 24-paper M1 corpus was added under `files/exam_corpus/`
  (raw PDFs + extractions + per-position/­per-problem ANALYSIS + a generation guide).
  Mandate: make generated M1 output fall *inside* the real distribution. Audited every
  M1 topic against the corpus and fixed the biggest "tells". **App green: 18/18 tests,
  `manage.py check` clean.** Corpus is M1-only — M2/M3 largely untouched (they inherit
  the richer pools harmlessly; behaviour targeted at M1's tiers/slots).
- **Subiectul I:**
  - **Pos 2 (`functions.py`):** added the authentic quadratic/parabola family
    (`_p_vertex_ordinate_pos`, `_p_vertex_on_ox`, `_p_positive_all`, `_p_two_roots`,
    `_p_tangent_linear`, `_p_intersect_line`, `_p_point_on_parabola`) at tier 2/3 so
    M1 pos-2 is **quadratic-dominated** as in the real papers (was affine-dominated;
    the lone parabola subtype sat at d3, rarely drawn). 34 distinct forms, all
    sympy-verified, clean integer/interval/±integer answers.
  - **Pos 4 (`combinatorics.py`):** **removed urn/ball probability** from the M1 draw
    (not in the corpus — a clear machine tell). Added the real digit-condition family
    (`_p4_3digit_not_mult`, `_p4_3digit_prime_digits`, `_p4_3digit_prod_digits`,
    `_p4_2digit_sum_div3`, `_p4_2digit_div9`, `_p4_2digit_digits_bound`,
    `_p4_2digit_distinct_odd`, `_p4_count_from_set`, `_p4_subsets_at_most`) filling
    tiers 1–3; combinatorial equations (Aₙ²/Cₙ²/Cₙ³) kept only as a light d2 presence.
    0 urns / 45 distinct forms at M1 d2; exact reduced fractions (prime-distinct → 2/75).
  - **Pos 1 (`progressions.py`, `complex.py`, `powers.py`, `logarithms.py`,
    `registry.py`):** rebalanced from complex-dominated `("complex"×3,"powers","log")`
    to `("complex"×2,"progressions"×2,"powers","logarithms")` — matching the corpus
    (complex + progressions dominate; radicals/lg secondary). Enabled **M1 progressions**
    (OQ1 reversed) and added the corpus phrasings (term-from-two-terms,
    consecutive-terms proof). Added authentic complex "Arătați că <expr>=<val>",
    modulus-of-expression (Pythagorean → integer), and find-(a,b) items (weighted ×2 at
    the tier M1 pos-1 uses) replacing the "Calculează"/"Adu la forma algebrică" tells.
    Added radical-simplification items to powers (`√A−√B=k√m`, conjugate product).
    Made `logarithms` the **numeric-identity/inequality** flavour at all tiers
    (base-10 `lg` multi-term identities + subtraction) — log *equations* stay the
    `equations` topic, so the pos-1 exam slot is a genuine identity (was leaking
    equations at d2). Distribution over 300 sims: complex 104 / progressions 96 /
    powers 56 / logarithms 44.
- **Subiectul II — `MatrixSystemProblem` (`matrices.py`, NEW):** the "3×3 matrix A(a)
  + linear system" family — the *other* dominant real prob-1 form (~10/24 papers),
  previously entirely missing. (a) det(A(a0))=int, (b) values of a for a unique
  solution (A(a) invertible), (c) solve at a fixed a with a property (integer triple,
  sometimes consecutive AP terms). Templates are filtered so det(A(a)) has clean
  integer roots; det/roots/linsolve all sympy-verified. Registered as
  `matrices_system` (TOPIC_CODE stays `matrices`); M1/M2 Subiect II prob-1 now
  **rotates** homomorphism ↔ system (~50/50). New correctness test
  `test_matrix_system_is_consistent`.
- **Subiectul III — `integrals.py`:** M1 no longer *always* the sequence-Iₙ mode
  (it was 100%, but only ~1/4 of real M1 integral problems are sequences) — now ~30%
  sequence / ~70% direct-integral/area, matching the corpus.
- **Files touched:** `topics/{functions,combinatorics,progressions,complex,powers,
  logarithms,matrices,integrals}.py`, `registry.py`, `tests/test_generators.py`.
- **Next (optional, corpus-driven):** enrich `algebraic_structures` law variety
  (corpus has many more law shapes than the 2 families); vary the polynomials cubic
  family (corpus has degree-4 + several degree-3); richer `DerivativesStudyProblem`
  functions (products poly×eˣ) to lift toward the corpus ceiling; consider matching the
  BAC `mul_symbol` convention (drop `\cdot` for `xy`/`2e^{2x}`) — app-wide, defer.

### Session 6 (cont.) — 2026-07-04 — M1 Subiectul I made harder (all 6 positions)
- **Problem reported (M1):** Subiectul I too easy — pos1 only trivial complex
  arithmetic, pos3 single-step equations, pos4 only `A_n^k`/`C_n^k` evaluation.
- **Root cause:** `generate_full_simulation` built Subiectul I at **difficulty 1 for
  every profile**, so M1 got the trivial d1 subtypes.
- **Fix (M1 only):** `engine.py` now generates M1 Subiectul I at **difficulty 2**
  (`si_diff = 2 if profile=="M1" else 1`); M2/M3 unchanged. Then enriched the thin
  d2 pools of the flagged topics:
  - `complex.py`: `_d2_show_natural` ((a−bi)(a+bi)∈ℕ) + `_d2_show_real`
    (mate-info style `m(a+bi)+i(c+di)∈ℝ`), sympy-verified.
  - `combinatorics.py`: `_d2_arrangement_eq` (`A_n^2=val`), `_d2_comb_eq3`
    (`C_n^3=val`), and moved the combinations-probability into d2 (no more bare
    evaluations at pos4). Fixed `\ge`→`\geq` for mathtext/PDF.
  - `equations.py`: `_log_sum` (`log_b(x+p)+log_b(x+q)=log_b C`, distinct args,
    domain-checked).
  - `trigonometry.py`: `_t_sin_double` (sin 2x from a given ratio) + `_t_trig_quadratic`
    into d2.
- **Verified:** 17/17 green (incl. PDF); M1 Subiectul I all d2; per-position full-question
  variety over 200 sims — pos1 162, pos2 183, pos3 130, pos4 61, pos5 179, pos6 27;
  M2 Subiectul I unchanged (d1). Note: Subiectul I is otherwise a shared common-core
  section — M1 differs from M2 by *tier* (d2 vs d1) and by pos-1 topic (complex).

### Session 6 — 2026-07-04 — M1 (mate-info) made distinctly harder than M2
- **Problem reported:** in `/simulate`, M1 problems looked ~identical to M2 and
  weren't harder. Root cause: M1 and M2 shared the *same* `DerivativesStudyProblem`,
  `IntegralsProblem`, `AlgebraicStructuresProblem` code paths.
- **Researched the official 2024 models** (edupedu CDN): `M_mate-info` vs `M_st-nat`
  barems. Key M1 signatures — Subiect III: **bijectivity** proof (inj.+surj.) and a
  **sequence of integrals** with a proven **recurrence** + limit; Subiect II:
  **morphism/associativity** on the law of composition; Subiect I: **complex
  numbers** at position 1.
- **Implemented (M1-only branches; every M2 path left byte-identical):**
  - `topics/derivatives.py` `DerivativesStudyProblem`: M1 adds `exp_bijective`
    (f=x+e^{kx}: f'/monotonie/**bijectivă**) and `ln_extrem` (f=x−a·ln x:
    f'/monotonie/**minim**) modes; M2 stays cubic/rational.
  - `topics/integrals.py` `IntegralsProblem`: M1 uses a **sequence** mode
    (`I_n=∫₀¹ xⁿ/(x+1)` or `/(x²+1)`): compute `I_1`, prove `I_n+I_{n-1}=1/n` (resp.
    `I_n+I_{n-2}=1/(n-1)`, verified for concrete n), `lim I_n=0`; M2 stays
    primitive/∫/area. Added `_lln` (ln display).
  - `topics/algebraic_structures.py`: M1 plan adds `_c_associativity` and
    `_c_morphism` (`g(x)=x−c` morphism onto (ℝ*,·)/(ℝ,+), sympy-verified);
    `_law_family` now also returns `(c, kind)`. M2 plan unchanged.
  - `registry.py` `SIMULATION_RULES["M1"]["subiect_I"]` pos-1 weighted toward
    **complex** (~0.6) via repetition, so M1 papers lead with complex numbers while
    M2 never does. (Subiectul I is otherwise a shared common-core section — only
    pos-1 differs between profiles in the real papers.)
  - Fixed matplotlib-mathtext PDF rendering: use `\geq`/`\leq` (not `\ge`/`\le`).
- **Verified:** 17/17 tests green (incl. PDF); M1 deriv c) ∈ {bijectivă, minim, 1
  root, asymptotă}, M1 integrals all sequences (recurrence sympy-verified), M1
  structures surface morphism/assoc; M2 deriv/integrals variants unchanged; M1 pos-1
  ≈62% complex vs M2 0%.

### Session 5 (cont.) — 2026-07-04 — antrenament parity (trig d2/d3 + problem facades)
- **Question raised:** do the Session-5 randomizations reach *antrenament* (`/generate`)?
  Findings — trig richness lived only in tier 1, so training was rich at d1
  (129/240) but thin at d2 (55) and **d3 = 1 static** item; and matrices/other
  problem-only topics weren't in the `/generate` menu at all.
- **Trig d2/d3 enriched** (`topics/trigonometry.py`): parametrized the double-angle
  equation (4 factorable variants, every root sympy-checked), added
  `_t_trig_from_ratio` (d2), `_t_trig_quadratic` (quadratic in sin/cos, 4 variants),
  `_t_prove_identity` (4 provable identities, symbolic check). → d2 71/240, d3 30/240.
- **Single-item facades** (`topics/facades.py`): `_ProblemFacade(ExerciseGenerator)`
  generates a full problem and surfaces one sub-item (matched to the requested
  difficulty), prefixing the shared statement — reusing each problem's randomized
  cerință pool + sympy verification. Concrete facades for `matrices`,
  `polynomials`, `integrals`, `algebraic_structures`, registered in
  `CLASS_REGISTRY` (problem forms stay in `PROBLEM_REGISTRY`). They now appear in
  `/generate` (M1/M2 all four; M3 matrices + algebraic_structures). Verified
  self-contained (no "punctul a)" cross-refs) and varied (matrices 116,
  algebraic_structures 67 distinct/135).
- **Also randomized `algebraic_structures` 3-item plan** (like matrices in S5):
  tiered cerințe with a distinct-theme guard, plan chosen once in
  `_generate_context` — benefits both its Simulare problem and its facade.
- **Architecture change:** the P4.5 rule "problem-only topics are dropped from
  `/generate`" is now **relaxed** — those four are practiceable as single items via
  facades, while still driving Subiectele II/III as linked problems.
- **Verified:** 17/17 tests green, `manage.py check` clean.

### Session 5 — 2026-07-04 — M2 variety: Subiectul I pos 6 (trig) + Subiectul II (matrices)
- **Problem reported (M2):** Simulare pos-6 was near-identical every time (only
  `sin/cos` of a remarkable angle), and the Subiectul II matrix problem felt like
  "~3 kinds" (cerinte were fixed by position: a=det, b=product-general,
  c=system/power).
- **Root causes:** Simulare Subiectul I always calls generators at **difficulty 1**,
  and trig's tier-1 pool was a single subtype; the matrix `_plan()` was a fixed
  position→cerinta list, so only the family + numbers varied.
- **`topics/trigonometry.py` — rich tier-1 pool** (info-on-sub1 §6, all four content
  families the user chose): remarkable values (+tg) & value expressions & `E(π/k)`;
  right-triangle ratio / perimeter / side-from-`tg B` / 30-60 two-angle; area with
  radical answers + `tg B = 1/tg C` identity; Pythagorean ratio; simple equation on
  `[0,2π)`. All sympy-verified, radicals kept short. **M3 unchanged in spirit**
  (remarkable values only, §5.2, now 2 subtypes). Result: pos-6 ≈ 10/12 distinct
  across seeds, 105 distinct forms / 200 rolls.
- **`topics/matrices.py` — randomized cerinte + new types.** Added `_c_trace`,
  `_c_sum`, `_c_commutative`, `_c_find_x` (find x from `A(x)=M`), `_c_solve_matrix`
  (`A(x0)·X=A(y0)`), `_c_inverse_explicit` (all sympy-verified). New `_pick_plan`
  draws a/b/c from difficulty tiers with a **distinct-theme guard** (no two of
  det/trace/sum/product/inverse/solve/power repeat); the plan is computed **once**
  in `_generate_context` and stored on `ctx` (label consistency + reproducibility).
  Added 4 more 2×2 and 2 more 3×3 homomorphism families. M3 six-item format kept as
  the fixed comprehensive tour. Result: 189 distinct cerinta-triples / 300 rolls
  (was ~fixed).
- **Verified:** 17/17 tests green, `manage.py check` clean; rendered M2 matrix
  problems correct (inverse `A(a)⁻¹=A(-a)`, trace=n, product expansion); trig items
  clean. Only M2 targeted per request; M1 inherits the same richer pools (harmless),
  M3 unchanged.
- **Follow-up done (same session):** the complementary-angle identity is now
  parametrized — random right-angle vertex × acute-pair order × identity form
  (`tg u = 1/tg v`, `tg u·tg v = 1`, `sin u = cos v`, `cos u = sin v`,
  `sin²u + sin²v = 1`), each numerically sympy-checked → 30 distinct variants.
- **Next (optional):** apply the same cerinta-randomization idea to
  `algebraic_structures`; consider pos-1 M1 complex "show that" phrasings (§1).

### Session 4 — 2026-06-30 — Subiectul I aligned to `info-on-sub1.md`
- **Goal:** make Subiectul I (training *and* mock exams) reproduce the real-paper
  *position→topic* structure + authentic phrasings from `info-on-sub1.md`.
- **New `topics/functions.py` `FunctionsGenerator`** (M1/M2/M3) — Subiectul I
  position 2 (§2): `f(x0)=val`, point-on-graph (find b), `(f∘g)(x0)`, `f(x0)=g(x0)`,
  `(f∘f)(x0)=val`, linearity identity `f(kx)-k·f(x)`, and parabola-vertex-on-Ox
  (M1/M2 only). M3 = linear/affine subtypes only. All answers integer, built by
  design and re-verified with sympy.
- **New `topics/equations.py` `EquationsGenerator`** (M1/M2/M3) — Subiectul I
  position 3 (§3): invariant wrapper "Rezolvați în mulțimea numerelor reale
  ecuația $…$" over exponential / logarithmic / irrational / modulus bodies. Roots
  constructed clean, domain enforced, extraneous discarded, sympy-verified. M3 =
  single-step only, base ∈ {2,3,10}.
- **`topics/combinatorics.py`** — added the position-4 (§4) authentic items:
  two-digit-number probability (divisibility / units parity / divisor), `k`-subset
  counting, and practical percentage (scumpire/ieftinire). Placed at tier 1 so the
  Subiectul I slot (and M3) draws them.
- **`registry.py`** — registered both classes; added `functions`/`equations` to
  `TOPIC_LABELS` and `PROFILE_TOPICS` (all profiles); **rewrote `SIMULATION_RULES`
  `subiect_I`** for M1/M2/M3 to the fixed roles (pos2=functions, pos3=equations,
  pos1=complex/powers/log resp. progressions/powers, pos6=trig/triangle).
- **Verified:** `python manage.py test apps.exercises` → 17/17 green;
  smoke run — functions/equations generate over all profiles×difficulties without
  raising; simulated Subiectul I shows the exact position→topic map for M1/M2/M3;
  `/generate` menus expose the two new topics for training.
- **Next (optional):** weight pos-1 toward `complex` for M1 (§7 note ~0.7); enrich
  pos-1 "show that" complex phrasings (§1 T1.M1.a–f); consider a dedicated
  parabola/quadratic-function subtype set.

### Session 1 — 2026-06-28
- Read `generator.md` in full (1867 lines) + surveyed current `exercises` app.
- Wrote this continuity doc (gap analysis, decisions, phased plan, status table).
- Implemented Phase 0 foundation (additive, non-breaking): `base.py`
  (`ExerciseGenerator` + `ProblemGenerator`), `difficulty.py`, `registry.py`,
  `topics/` package, `topics/derivatives.py` (reference class), + smoke test.
- Legacy engine/generators untouched and still live — app remains green.
- **Next:** P1.1 (matrices ProblemGenerator) then P1.3/P1.4 (new engine + simulate).

### Session 2 — 2026-06-28
- Built the **multi-part problem model** end to end (the core of the rework):
  - `topics/matrices.py` — `MatricesProblem`: verified homomorphism family
    (`det(A(x))=1`, `A(x)·A(y)=A(x+y)`), cerinte = det / product / inverse /
    power / 2×2 system. M1=3×3, M2=2or3, M3=2×2 six-item. Registered in
    `PROBLEM_REGISTRY`.
  - `topics/algebraic_structures.py` — `AlgebraicStructuresProblem`: laws
    `(x−c)(y−c)+c` (neutral c+1) & `x+y−c` (neutral c); comm/assoc/neutral all
    sympy-verified. M1/M2 a/b/c; M3 six-item. (Fixed: spec §9.3's "e=1" label is
    mathematically wrong — true neutral computed/verified.)
  - `generators/engine.py` — new `generate_exercises` (per-item seeds, §8.4
    difficulty spread, variety guard) + `generate_full_simulation` (nested
    `subiect_I/II/III`, points 90+10, M3 special-cased). Bridges class/legacy
    generators; adapter + slot fallback for unported topics.
- Smoke test `smoke_p1.py`: matrices/laws verified over 180 problems, simulate
  structure+points+reproducibility for all profiles, variety 95/100,
  M3 II=lege×6 / III=matrice2×2×6, no complex/integrals in M3. `manage.py check` clean.
- **P1.5 + P1.6 done — new engine is LIVE.** Switched all three views to the new
  engine, deleted legacy app-level `engine.py`, rewrote `types.ts` + `Simulate.tsx`
  to render the nested paper (Subiectul I items; II/III problems with a/b/c sub-items
  + inline hint/answer/steps). Verified end-to-end via DRF test client (200s,
  correct shapes, M3 special-casing, difficulty spread). Frontend `tsc -b` + `vite
  build` pass; `manage.py check` clean.
- **Phase 1 COMPLETE.** App green and live on the new architecture.
- **Next (Phase 2):** port Subiectul-I + M1 topics to classes and add the missing
  generators — start P2.4 `geometry` (NEW, all profiles; removes a simulate
  fallback) and P2.1 `logarithms` incl. M3; then problem-forms for
  `derivatives`/`integrals` (Subiectul III) to replace the `_adapter_problem`
  bridge with truly linked sub-items.

### Session 3 — 2026-06-29  (branch `feature/phase2`, off `feature/phase1`)
- **P2.4 `geometry`** (NEW, single-item, all profiles) — `topics/geometry.py`:
  point-on-line, midpoint, distance (Pythagorean triples → integer), vector
  equality, right-triangle/Pitagora (BC/perimeter/area), + d2 collinearity &
  parallelogram. All values sympy-computed. Now in `CLASS_REGISTRY` → appears in
  the `/generate` menu and **removes the Subiectul I geometry fallback**.
- **P2.8 `DerivativesStudyProblem`** (M1/M2 Subiect III) — added to
  `topics/derivatives.py`: cubic mode (f' / strict monotonie / exactly one real
  root, guaranteed by a>0) and rational mode (f' / oblique + vertical asymptote),
  all sympy-verified. In `PROBLEM_REGISTRY`.
- **P2.7 `IntegralsProblem`** (M1/M2 Subiect III) — `topics/integrals.py`:
  primitive check (F'=f), definite integral (Leibniz–Newton), area (exact, split
  at sign changes). In `PROBLEM_REGISTRY`.
- **Effect:** M1/M2 **Subiectul III is now real linked problems** (derivatives +
  integrals), not the adapter; geometry is live in Subiectul I. No frontend change
  needed (statements now populate where the adapter left them blank).
- Verified `smoke_p2.py`: 360 geometry items; 60 derivatives + 60 integrals
  problems sympy-verified; simulate M1/M2 III statements present & topics correct;
  geometry present in Subiectul I. P1 regression + `manage.py check` clean.
- **Next:** P2.1 logarithms (incl. M3 — removes another Subiectul I fallback),
  P2.3 polynomials problem-form (M1/M2 Subiect II prob 2), P2.2 complex, then
  Phase 3 (`progressions`/`sequences`/`statistics`/`systems`).

### Session 3 (cont.) — 2026-06-29  (branch `feature/phase2`)
- **P2.1 `logarithms`** ported to a class `topics/logarithms.py` (M1/M2/M3):
  identity (∑log = int), simple eq `log_b(x²+px)=log_b(C)`, linear eq
  `log_b x − log_b(x−a)=1`, inequality `log_b(x²+1) ≤ log_b(C)`. M3 restricted to
  the simple eq/identity (base 2,3,10, §5.2). Now in `CLASS_REGISTRY` →
  supersedes the legacy logarithms function and **removes the M3 Subiectul I
  logarithms fallback**.
- **P2.3 `PolynomialsProblem`** (`topics/polynomials.py`, M1/M2 Subiect II prob 2):
  shared cubic `X³+aX²−aX+c₀`; (a) `f(1)` fixed ∀a, (b) quotient/remainder ÷(X+1),
  (c) determine `a` from `∑xᵢ² = K` via Viète. All sympy-verified. **Retires the
  polynomials adapter** — M1/M2 Subiectul II is now real linked problems.
- Verified `smoke_p2b.py`: 360 log items (incl. M3-simple), 60 polynomial
  problems; simulate M1/M2 II statements present; M3 Subiectul I now has
  logarithms. P1+P2 regression + `manage.py check` clean.
- **Next:** P2.2 complex (M1 full / M2 algebraic), P2.5 trigonometry, P2.6
  combinatorics (port to classes); then Phase 3 + Phase 4 hardening.

### Session 3 (cont. 4) — Port remaining 6 + unblock P4.5 — 2026-06-29  (branch `feature/phase2`)
- Added `TieredExerciseGenerator` base (reuses `_utils.choose_subtype` + subtype
  functions, applies the validation gate).
- Ported the 6 remaining legacy single-item topics to classes in `topics/`:
  `powers`, `complex` (M2 algebraic-only), `trigonometry`, `combinatorics`,
  `progressions`, `limits` — subtype logic copied verbatim from the legacy
  modules (already production-correct), registered in `CLASS_REGISTRY`.
- **Deleted all 11 legacy `generators/*.py` topic modules** + emptied the legacy
  `__init__.py` `REGISTRY`; removed the legacy fallback from `engine.py`. Codebase
  is **fully class-based** now (`_utils.py` kept as shared helpers).
- **Decision:** multi-part topics (`matrices`, `polynomials`, `integrals`,
  `algebraic_structures`) are problem-only → dropped from the `/generate` menu
  (M1 10 / M2 11 / M3 8 single-item topics); every `PROFILE_TOPICS` entry is still
  covered (single-item *or* problem). Optional follow-up: single-item facades.
- Verified: 15-test suite green, `manage.py check`, live generate/simulate for all
  profiles (II/III all real problems), full topic coverage with no "uncovered".
- **Rework is feature-complete vs `generator.md`.**

### Session 3 (cont. 3) — Phase 4 hardening — 2026-06-29  (branch `feature/phase2`)
- `generators/latexconv.py` (P4.1): `LATEX_SETS`, `RO_TERMS`, `sympy_to_bac_latex`
  (base default answer formatter). Skips the spec's incorrect `\log→\ln`.
- `generators/validation.py` (P4.2): `is_sane_value` / `is_clean_latex` /
  `item_is_clean`; wired as a final gate in both base `generate()` methods so
  undefined/oversized/empty payloads are rejected uniformly (retry) on top of
  each topic's `_validate`.
- `apps/exercises/tests/test_generators.py` (P4.3/P4.4): **15 tests**, all green
  via `python manage.py test apps.exercises` — reproducibility, variety >50/100,
  structure+points 90+10, M3 special-casing, progressive a≤b≤c difficulty,
  profile restrictions, every-available-topic robustness, sympy correctness
  (derivative/matrix-homomorphism/integral-primitive/law-neutral), validation.
- P4.5 (remove legacy) is BLOCKED until the remaining 6 legacy topics are ported.
- **Next:** port `complex` (M2 algebraic-only), `trigonometry`, `combinatorics`,
  `progressions`, `limits`, `powers` to classes → then P4.5 deletes the legacy
  modules and the rework is feature-complete vs `generator.md`.

### Session 3 (cont. 2) — 2026-06-29  (branch `feature/phase2`)
- **NEW generators** (filled the last `PROFILE_TOPICS` gaps):
  - `topics/sequences.py` `SequencesGenerator` (M1/M2): rational limit, recurrence
    term, infinite geometric series, Cesàro–Stolz (M1). sympy `limit`/`summation`.
  - `topics/statistics.py` `StatisticsGenerator` (M3): mean, median, find-value
    for a target mean. Exact `Rational`s (no floats).
  - `topics/systems.py` `SystemsGenerator` (M1/M2): 2×2, 3×3 (M1), parametric
    (det ≠ 0). Built from a chosen integer solution, verified with `linsolve`.
  - All three registered in `CLASS_REGISTRY` → now in the `/generate` menus.
- **Engine fix (P3.7):** `_pick_problem_topic` prefers a real `ProblemGenerator`
  for Subiect II/III; `algebraic_structures` (problem-only) was previously
  discarded by the single-item availability check and fell through to the
  adapter. Now **every II/III problem across M1/M2/M3 × seeds is a real linked
  problem** — the adapter is a dead safety net.
- Verified `smoke_p3.py` (600 items) + P1/P2/P2b regression + "no empty
  statements across M1/M2/M3 × 5 seeds" + `manage.py check` + live menus/generate.
- Coverage: M1 13/14, M2 14/15, M3 8/10 (the absent ones are `algebraic_structures`
  / M3 `matrices`, intentionally problem-only).
- **Next:** port `complex` (M2 algebraic restriction), `trigonometry`,
  `combinatorics`, `progressions`, `limits`, `powers` to classes (cleanup; they
  work as legacy now), then Phase 4 hardening (`latexconv.py`, central validation,
  committed test suite, remove legacy modules).
