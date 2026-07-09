# Engine 2 — Four-Level Rework (Implementation Log & Continuity Doc)

> **Read this first, every session, alongside [`GENERATOR_REWORK.md`](GENERATOR_REWORK.md).**
> This file is the persistent brain for the *second* rework of the Algomate
> generator: expanding from **3 internal profiles (M1/M2/M3)** to the **4 real BAC
> specializations**, renaming codes to explicit slugs, building the brand-new
> **științele-naturii** level, and widening value / formulation / problem-type
> **diversity** across all four — additively, without losing existing problems.
>
> Relationship to the older doc: `GENERATOR_REWORK.md` recorded Sessions 1–8 (the
> class-architecture rework + M1/M2 corpus faithfulness). It stays authoritative
> for *how the engine is built* (base classes, `ProblemGenerator`, simulate shape,
> difficulty spread, validation gardens). **This doc governs the 4-level work on
> top of it.** When they disagree about profile identity, **this doc wins**.

---

## 0. Branch & app-green protocol

- Branch: `feature/engine2`.
- Every session must end **green**: `python manage.py check`, `python manage.py
  test apps.exercises`, and frontend `tsc -b` + `vite build` all pass. Never leave
  imports broken. Commit only when the user asks.

---

## 1. The four levels (user-confirmed 2026-07-09)

The real Romanian BAC has **four** math specializations. We now model all four as
first-class profiles, keyed by **explicit slug** (decision D-A below).

| Slug | Romanian name | Old code | Difficulty | Status |
|------|---------------|----------|-----------|--------|
| `mate-info` | Matematică–Informatică | **M1** | hardest | exists (keep behaviour) |
| `stiintele-naturii` | Științele Naturii | *(none)* | ↓ between mate-info & tehnologic | **NEW — build** |
| `tehnologic` | Tehnologic | **M2** | ↓ | exists (keep behaviour) |
| `pedagogic` | Pedagogic | **M3** | easiest | exists (keep behaviour) |

**Mapping is exact:** old `M1`→`mate-info`, `M2`→`tehnologic`, `M3`→`pedagogic`
(behaviour preserved), and `stiintele-naturii` is a genuinely new 4th profile
derived from its own corpus. (This corrects earlier UI mislabels noted in
`GENERATOR_REWORK.md` — Științele Naturii had been dropped entirely; it is now a
real level, not a relabel of tehnologic.)

### 1.1 Științele-naturii profile (from corpus, initial read)
St-nat is a **hybrid**, structurally like mate-info but easier, and *not* a clone
of any existing level:
- **Subiectul I** (6×5p): 1 progression term · 2 linear/affine function · 3 equation
  in ℝ (log/exp/irrational) · 4 probability over a small explicit set · 5 analytic
  geometry (right-triangle proof) · 6 trigonometric identity/value.
- **Subiectul II**: prob-1 = **2×2 matrices** (affine `B(a)=aM+N`, det, identity,
  non-invertibility) — like tehnologic, **not** mate-info's 3×3; prob-2 = **law of
  composition** (`x∘y=xy+…`) with comm/neutral/solve cerinte.
- **Subiectul III**: prob-1 = **derivatives**, rational-function study (f′, horizontal
  asymptote, inequality); prob-2 = **integrals** (definite ∫, genuine — unlike the
  lighter tehnologic mix).
- Keeps **complex (algebraic)** and **integrals**, which distinguishes it from the
  reduced tehnologic profile. Full per-position/per-problem analysis → task #5.

---

## 2. Key decisions

- **D-A — Explicit slug codes.** Canonical profile identifiers become
  `mate-info` / `stiintele-naturii` / `tehnologic` / `pedagogic` **everywhere**:
  registry, engine, serializers (`PROFILE_CHOICES`), views (`TopicsView` tuple),
  DB (`ExerciseSession.profile`, widen `max_length`), PDF filenames, frontend
  `Profile` type + all pages. A **data migration** maps existing saved sessions
  `M1→mate-info`, `M2→tehnologic`, `M3→pedagogic`. Rationale: the M1/M2/M3 codes
  were already a documented source of confusion; slugs are self-describing and the
  4th level has no natural number.
- **D-B — Preserve, then extend.** The existing mate-info/tehnologic/pedagogic
  behaviour is kept intact through the rename (pure identifier swap, no logic
  change). Diversity work is **strictly additive**: widen picked values, add
  authentic task formulations, add problem subtypes. **Never delete an existing
  problem**; rewrite one *only* when the corpus shows it doesn't correspond.
- **D-C — Exam-first priority.** For every level, get the **simulare (full exam)**
  faithful first (tasks #5, #7), then enrich the **single-problem** `/generate`
  generators (task #6).
- **D-D — Corpus is the authority.** `files/exam_corpus/<slug>/` (below) is ground
  truth. Read the extracted `.txt` (cheap) before touching a generator; open the
  source `.pdf` only when the extraction is ambiguous (math superscripts/mangled
  diacritics). Generated output for a level must fall *inside* that level's real
  distribution.

---

## 3. Corpus map — `files/exam_corpus/`

Reorganized 2026-07-09 from the raw download (`download_bac_mate.sh`, which pulls
subiecte+bareme 2013→present from pro-matematica.ro into the git-ignored
`bac-matematica/`). **889 official papers**, one folder per level, per year, each
`.pdf` paired with a layout-preserving `.txt` extraction (poppler `pdftotext
-layout`).

```
files/exam_corpus/
  README.md                         # corpus guide + filename decoding
  mate-info/          2013..2026/   # 232 papers (.pdf + .txt)
    ANALYSIS/                       # migrated M1 analysis (subiect_I_by_position,
                                    #   subiect_II_problems, subiect_III_problems,
                                    #   GENERATION_GUIDE.md, README_orig.md)
    _legacy/M1/                     # old 24-paper curated corpus (raw_pdf+extracted),
                                    #   incl. 2021 pandemic test-variants — kept intact
  stiintele-naturii/  2013..2026/   # 226 papers   [ANALYSIS to be written — task #5]
  tehnologic/         2013..2026/   # 237 papers
    ANALYSIS/ANALYSIS_tehnologic.md # migrated ANALYSIS_M2.md
    _legacy/                        # old 135-paper session-organized M2 corpus, intact
  pedagogic/          2013..2026/   # 194 papers   [ANALYSIS to be written]
```

**Filename grammar:** `YYYY_E_c_Matematica_<SESS>_M_<level>_<Subiect|Barem>_<NN>_LRO.pdf`
- `SESS`: `S1`=Sesiunea I (iunie/iulie) · `S2`=Sesiunea II (august) · `S1R`/`S2R`=rezervă
  · `SS`=Sesiunea Specială · `SM`=Simulare/Model. (2020/21 also have lowercase
  `..._M_<level>_Test_NN` pandemic training variants.)
- Always read the **Barem** next to a Subiect — it gives the exact accepted answers
  used to sympy-verify generated equivalents.

**Coverage:** every (level × year 2013–2026) has 3–8 subiecte. Git note: the
`.txt` + `ANALYSIS` are lightweight and should be tracked; the ~146 MB of raw PDFs
are reproducible via the committed download script — **raw-PDF tracking to be
decided with the user at commit time** (leaning: gitignore new raw PDFs, keep the
already-tracked `_legacy` ones).

---

## 4. Step plan (master TODO — mirrors the task list)

### Phase A — Corpus foundation
- [x] A1 Fix `download_bac_mate.sh` (matched only absolute URLs; site uses relative
      hrefs → downloaded nothing) + add curl retry/timeout hardening.
- [x] A2 Download full corpus 2013–2026, all 4 levels (889 papers).
- [x] A3 Organize into `files/exam_corpus/<slug>/<year>/` + `pdftotext` extraction;
      preserve legacy M1/M2 corpora + analysis; drop root dup `.md`.
- [x] A4 Write this doc.
- [x] A5 Write `files/exam_corpus/README.md` (corpus guide). Per-new-level ANALYSIS
      (`stiintele-naturii`, `pedagogic`) is written during their exam tasks (#5/#7).

### Phase B — Slug rename (foundation for all engine work; keep app green) — DONE
> Kept to the **3 existing** profiles (renamed only). `stiintele-naturii` joins the
> data + choice-lists in Phase C1 where its engine rules are actually built, so
> "selectable profile" always equals "working profile".
- [x] B1 Backend data: `registry.py` `PROFILE_TOPICS`/`PROFILE_CAPS`/`SIMULATION_RULES`
      keys → slugs. Added `PROFILES = tuple(PROFILE_TOPICS)` + `PROFILE_DISPLAY` as the
      single source of truth.
- [x] B2 Engine + topic modules: every quoted `"M1"|"M2"|"M3"` (SUPPORTED_PROFILES,
      `profile ==` branches, `_MODES` keys) → slug (bulk sed; all verified as genuine
      profile literals first). engine.py invalid-profile message now lists `PROFILE_TOPICS`.
- [x] B3 API: `serializers.PROFILE_CHOICES = PROFILES`; `TopicsView` iterates
      `PROFILES`; **removed obsolete `m3_variant`**; PDF `PROFILE_LABELS` rekeyed to
      slugs (`_profile_key` returns the slug directly).
- [x] B4 DB: `ExerciseSession.profile` + `User.profile` widened to `max_length=32`;
      `User` choices → slug labels, default `mate-info`. Data migrations (both apps)
      remap M1→mate-info / M2→tehnologic / M3→pedagogic (reversible). Historical
      `accounts/0002` left as-is (converted forward by the new migration).
- [x] B5 Frontend: `Profile` type → slugs; new shared `PROFILES` const in `types.ts`
      (Home/Practice/Simulate/Register import it; local dup lists removed); Register
      options + Home copy fixed (stale mislabels gone).
- [x] B6 Tests: profile literals updated; `test_m3_variant` → `test_profile_label_mapping`.
      Green: `check`, 19/19 tests, `makemigrations --check` clean, `tsc`+`vite build`,
      live smoke (I/II/III counts correct, M3 special-cased, old codes rejected).

### Phase C — EXAM (simulare) generators  *(priority tier 1)*
- [x] C1 **Built `stiintele-naturii`** exam (task #5). Corpus analysis →
      `stiintele-naturii/ANALYSIS/`. Wired into registry (PROFILE_TOPICS between
      mate-info & tehnologic; CAPS `matrix_size=(2,), complex=algebraic_only`;
      SIMULATION_RULES: I progression-opener/function/log-eq/prob/geo/trig · II
      `matrices_2x2` + law↔polynomials · III **real analysis**), `User` choices,
      frontend `PROFILES`. Reuses tehnologic paths for I/II (added st-nat to
      `SUPPORTED_PROFILES` wherever tehnologic was, + routed complex→algebraic,
      combinatorics→blend, matrices→2×2); **new st-nat branch** in
      `DerivativesStudyProblem` (rational/ln study) — integrals already give genuine
      direct-∫ for non-mate-info. Faithful: 2×2 matrices, rational/ln Subiect III,
      genuine ∫. **Also fixed pre-existing latent PDF bugs** (mathtext: `\ge`/`\le`,
      unbraced `\sqrt2`) via a normalization in `mathimg._preprocess` → 80/80 PDFs
      across 4 profiles × 20 seeds render. Tests: PROFILES-parametrized + 2 st-nat +
      hardened PDF (4×3 seeds) = **21 green**.
- [~] C2 **Rework existing** exams (task #7): additive diversity from the fuller
      corpus. **Done so far:** measured per-position form/value diversity over 120
      sims/level → targeted the thinnest spots. Integrals Subiect III p2 (all levels)
      5→18 families (form ~10→28); mate-info trig pos-6 d2 made the full authentic
      pool (26/11→85/47); pedagogic pos-1 → arithmetic-dominant numeric identity per
      corpus (8→20 form). **Remaining thin spots** (for next pass): enrich the
      `arithmetic` generator (log-identity/conjugate/decimal forms → lifts tehnologic
      & st-nat pos-1 too), mate-info pos-3 equations (12 form), pos-5 geometry (14),
      matrices problem cerință variety (~10 form).

### Phase D — SINGLE-PROBLEM generators  *(priority tier 2)*
- [ ] D1 Diversify `/generate` single-item + facade generators for all 4 levels
      (task #6).

---

## 5. Per-level status

Legend: ✅ faithful+diverse · 🟡 works, needs diversity · 🔲 exists pre-rename · ❌ absent

| Level | Rename | Exam (simulare) | Single-problem | Corpus analysis |
|-------|--------|-----------------|----------------|-----------------|
| mate-info | ✅ | 🟡 (S7 faithful; diversify) | 🟡 | ✅ (M1 ANALYSIS) |
| stiintele-naturii | ✅ | ✅ (built, faithful) | 🟡 (via shared paths) | ✅ (ANALYSIS written) |
| tehnologic | ✅ | 🟡 (S8 faithful; diversify) | 🟡 | ✅ (M2 ANALYSIS) |
| pedagogic | ✅ | 🟡 (special-cased; diversify) | 🟡 | ⬜ to write |

---

## 6. Open questions / risks
- **OQ-A** Raw-PDF git tracking (146 MB) — decide with user at first commit.
- **OQ-B** `stiintele-naturii` matrix size: corpus shows **2×2** in Subiect II — do
  not inherit mate-info's 3×3. Confirm across more papers in task #5.
- **R-A** The rename touches ~30 files + a DB migration; do it as one atomic,
  test-covered session so the app never half-renames.
- **R-B** Diversity must stay *inside* each level's distribution — always sympy-verify
  new subtypes and keep answers clean (int / simple fraction / √2,√3,√5).

## 7. Session log

### Session A — 2026-07-09 — Corpus foundation + plan
- Read `GENERATOR_REWORK.md` + current engine (registry/engine/views/serializers/
  models/frontend). Confirmed with user: **explicit slug codes**, exact old→new
  mapping, `stiintele-naturii` = new 4th level.
- Fixed two real bugs in `download_bac_mate.sh` (relative-href extraction; retry
  hardening). Downloaded **889 papers** (2013–2026, 4 levels), full coverage.
- Reorganized into `files/exam_corpus/<slug>/<year>/` with `.txt` extractions;
  preserved legacy M1/M2 corpora + all ANALYSIS docs; removed root dup `.md`.
- Initial corpus reads confirm the st-nat hybrid profile (§1.1) and that the
  pedagogic special-casing (Subiect II law×6, Subiect III matrix2×2×6) is faithful.
- Wrote this doc. **Next:** A5 (corpus README), then Phase B (slug rename, atomic).

### Session B — 2026-07-09 — Phase B slug rename (atomic, green)
- Renamed the 3 existing profiles `M1/M2/M3` → `mate-info/tehnologic/pedagogic`
  across the whole stack; **no behaviour change** (pure identifier swap). Discovered
  and fixed the stale mislabels the memory warned about (accounts `User.profile`
  choices + `Register.tsx` had M2="Științele Naturii", M3="Pedagogic/Tehnologic";
  the engine always meant M2=tehnologic, M3=pedagogic — migrated by that authority).
- Added `registry.PROFILES` + `PROFILE_DISPLAY` and a shared frontend `PROFILES`
  const so the profile list has one source of truth (adding st-nat later = edit the
  registry data + `User` choices only). Removed obsolete `m3_variant`; rekeyed PDF
  `PROFILE_LABELS` to slugs (the șt-nat label block already existed — reused for C1).
- Two reversible data migrations (accounts + exercises) remap existing rows.
- **Green:** `manage.py check`, 19/19 tests, `makemigrations --check` clean,
  `tsc -b`+`vite build`, live smoke (mate-info/tehnologic I=6/II=2/III=2; pedagogic
  I=6/II=1/III=1; old `M1` rejected). Nothing committed.
- **Next:** Phase C1 — build `stiintele-naturii` (add it to registry data + `User`
  choices + frontend `PROFILES`, derive its rules from `files/exam_corpus/
  stiintele-naturii/`, write its ANALYSIS).

### Session C — 2026-07-09 — Built the științele-naturii level (Phase C1)
- Analyzed the șt-nat corpus (2019–2026 papers) → `stiintele-naturii/ANALYSIS/`.
  Identity: Subiect I & II like tehnologic (easy; **2×2** matrices; law↔polynomials),
  but **Subiect III is real analysis** (rational/ln derivative study + genuine ∫).
  User confirmed "build as specified".
- Wiring: registry (PROFILE_TOPICS ordered mate-info→**șt-nat**→tehnologic→pedagogic;
  CAPS 2×2 + complex algebraic-only; SIMULATION_RULES with progression opener &
  real-analysis III), `User.profile` choices (+migration 0004), frontend `PROFILES`.
  Added șt-nat to `SUPPORTED_PROFILES` wherever tehnologic appeared (one guarded sed);
  routed complex→algebraic-only, combinatorics→digit+explicit-set blend, matrices→2×2,
  derivatives StudyProblem→rational/ln mode. Single-item derivatives share mate-info
  templates; integrals already emit genuine direct-∫ for non-mate-info.
- **Latent PDF bug fixes (all profiles):** matplotlib mathtext choked on `\ge`/`\le`
  and unbraced `\sqrt2`. Fixed the `\ge` at source (progressions/equations) and added
  a mathtext-compat normalization to `mathimg._preprocess` (`\sqrt<c>`→`\sqrt{<c>}`,
  `\ge`→`\geq`, `\le`→`\leq`) — PDF-only, frontend KaTeX untouched.
- **Green:** 21 tests (PROFILES-parametrized incl. șt-nat + 2 dedicated + hardened
  4×3-seed PDF), `check`, `makemigrations --check` clean, `tsc`+`vite build`,
  **80/80 PDFs** (4 profiles × 20 seeds). Nothing committed.
- **Next:** Phase C2 (task #7) — diversify the *existing* exams (mate-info/tehnologic/
  pedagogic), corpus-driven & additive; then D1 (task #6) single-problem diversity.
