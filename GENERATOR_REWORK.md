# Generator Rework — Implementation Log & Continuity Doc

> **Read this first, every session.** This is the persistent brain for the
> multi-session rework of the Algomate BAC exercise/exam generator. The
> canonical spec is [`generator.md`](generator.md) (1867 lines) — this file is
> the *condensed plan + gap analysis + step tracker + session log* so a new
> session can resume without re-reading everything. When `generator.md` and this
> file disagree, **`generator.md` wins** — fix this file.

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
- [ ] P2.1 logarithms (incl. M3)  · [ ] P2.2 complex (M1 full / M2 algebraic)
- [ ] P2.3 polynomials  · [ ] P2.4 geometry (NEW)  · [ ] P2.5 trigonometry
- [ ] P2.6 combinatorics  · [ ] P2.7 integrals (problem-capable)

### Phase 3 — Complete M2/M3 + extras (spec §14.1 Faza 3)
- [ ] P3.1 progressions  · [ ] P3.2 sequences (NEW)  · [ ] P3.3 limits
- [ ] P3.4 powers  · [ ] P3.5 statistics (NEW)  · [ ] P3.6 systems (NEW)

### Phase 4 — Hardening & conventions
- [ ] P4.1 `latexconv.py` + apply §12 grammar/sets everywhere.
- [ ] P4.2 Central validation gardens (§11.3–11.4).
- [ ] P4.3 Test suite: reproducibility, variety (>50/100), points, profile-restriction (§14.4).
- [ ] P4.4 Final checklist pass (§14.2–14.3) per generator + SimulateView.
- [ ] P4.5 Remove legacy function modules once all topics ported.

## 7. Generator status

Legend: ✅ class+problem done · 🟡 class single-item · ⬜ legacy func only · ❌ missing

| Topic | M1 | M2 | M3 | Notes |
|-------|----|----|----|-------|
| derivatives | 🟡 | 🟡 | 🟡 | single-item class done; Subiect-III problem-form still adapter (Phase 2) |
| matrices | ✅ | ✅ | ✅ | `MatricesProblem` (a/b/c + M3 6-item), homomorphism family, sympy-verified |
| algebraic_structures | ✅ | ✅ | ✅ | `AlgebraicStructuresProblem` (a/b/c + M3 6-item), comm/assoc/neutral verified |
| integrals | ⬜ | ⬜ | — | M3 excluded |
| logarithms | ⬜ | ⬜ | ❌ | add M3 |
| complex | ⬜ | ⬜(alg) | — | M3 excluded |
| polynomials | ⬜ | ⬜ | — | |
| geometry | ❌ | ❌ | ❌ | NEW, all profiles |
| trigonometry | ⬜ | ⬜ | ⬜ | |
| combinatorics | ⬜ | ⬜ | ⬜ | |
| progressions | — | ⬜ | ⬜ | M1 excluded per spec §8.2 |
| sequences | ❌ | ❌ | — | NEW M1/M2 |
| limits | ⬜ | ⬜ | — | |
| powers | ⬜ | ⬜ | ⬜ | |
| statistics | — | — | ❌ | NEW M3 |
| systems | ❌ | ❌ | — | NEW M1/M2 |

## 8. Open questions / risks

- **OQ1** M1 `progressions`: spec §8.2 PROFILE_TOPICS omits it for M1, but §2.2 table
  lists progresii at M1 slot 1. Decision: follow PROFILE_TOPICS (no M1 progressions);
  M1 slot 1 uses logarithms/complex. Revisit if exam evidence says otherwise.
- **OQ2** `compute_item_difficulty` vs user-requested single difficulty for `/generate`:
  apply the spread so a set has natural variation; the item's stamped `difficulty`
  reflects the tier that produced it (never lies). Confirm UI shows per-item tier.
- **OQ3** Legacy `simulate` keys are `subiectul_I/II/III`; spec uses `subiect_I/II/III`.
  Switching renames the API field → frontend must change in the same session (P1.5/6).
- **R1** Big surface; keep each session shippable. Never leave imports broken.
- **R2** Some §9.2 matrix homomorphism families need sympy verification of
  `A(x)·A(y)=A(x+y)` symbolically — validate, don't assume.

## 9. Session Log

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
