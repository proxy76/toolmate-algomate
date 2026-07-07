# M1 Exam Corpus — READ THIS BEFORE GENERATING ANYTHING

This folder contains **24 official Romanian Bacalaureat M1 (mate-info) papers** from 2021–2025 —
exam variants, simulations, models, and official test sets — plus grouped analyses.

**This corpus exists for one reason: your generated exercises were not faithful to the real exam
distribution.** The fix is to make your output fall *inside* the distribution these 24 papers define.
Rules described in prose are not enough; you must observe the real examples directly.

---

## Scope: M1 ONLY

Every file here is M1 / mate-info. Do **not** use this corpus to generate M2, M3-tehnologic, or
M3-pedagogic — their structure, topics, and difficulty differ. If asked to generate a non-M1 profile,
stop and say the corpus does not cover it.

---

## Folder layout

```
exam_corpus/
  README.md                          ← this file
  M1/
    raw_pdf/        24 original PDFs (ground truth for exact math notation)
    extracted/      24 plain-text extractions (one .txt per paper)
  ANALYSIS/
    subiect_I_by_position.md         every Subiectul I item, grouped by position 1–6
    subiect_II_problems.md           every Subiectul II problem block (matrices, structures)
    subiect_III_problems.md          every Subiectul III problem block (derivatives, integrals)
  GENERATION_GUIDE_M1.md             how to turn observations into a correct generator
```

---

## MANDATORY procedure before writing or modifying any M1 generator

Do these steps **in order**, every time, for the specific subiect/position you are working on:

1. **Read the relevant ANALYSIS file end to end.**
   - Generating a Subiectul I item at position `k`? Read the POSITION `k` section of
     `ANALYSIS/subiect_I_by_position.md` — all 24 samples, not the first few.
   - Working on Subiectul II or III? Read the whole corresponding ANALYSIS file.

2. **Read at least 8 full papers** in `M1/extracted/` spanning different years (e.g. one 2021 test,
   2022 var, 2023 var, 2024 var, 2025 simulare, plus models). See a full paper as a whole, not just
   isolated items — the balance across the six positions matters.

3. **Write down what you observe** for the position/problem you will generate:
   - the **topic** (fixed per position — see the guide),
   - the **3–6 recurring phrasing patterns** actually used (quote them),
   - the **coefficient / number ranges** that actually appear (smallest and largest),
   - the **difficulty ceiling**: what is the single HARDEST real example, and why is it the hardest?

4. **Only now write the generator.** Its output must satisfy:
   > **Distribution rule — non-negotiable.** If a generated item is more complex, uses larger numbers,
   > combines more concepts, or uses a phrasing that appears in *none* of the 24 real papers, it is
   > **wrong**. Regenerate. Your job is to stay inside the observed distribution, not to invent
   > harder or "more interesting" problems.

5. **Self-check against ground truth (closes the loop):**
   After generating N items for a position, place them side by side with 5 real items from the corpus
   for the same position. Ask: *could a student or examiner tell which are machine-generated?*
   List every "tell":
   - phrasing that never appears in the real papers,
   - numbers larger or uglier than anything real,
   - wrong difficulty (too hard OR too trivial),
   - missing the standard wrapper sentence,
   - an answer that isn't clean (not an integer / simple fraction / short radical / short ln).
   Fix each tell, regenerate, and repeat until no tells remain.

---

## About the extracted text quality

PDF extraction of mathematics is lossy. In the `.txt` files you will see artifacts:
`(cid:2)` = ∘ (function composition), `‡` or stray subscripts = index notation,
`ℝℝ` or `ℝfi ℝ` = ℝ→ℝ, `i2 =- 1` = i² = −1, matrices flattened onto one line, fractions inlined.

**Read the extractions for phrasing, structure, topic, difficulty, and number ranges** — they are
fully reliable for that. For **exact mathematical notation**, open the corresponding file in
`M1/raw_pdf/`, which is the ground truth. Never reproduce the `(cid:...)` artifacts in generated output.

---

## What the corpus proves about M1 structure (verified across all 24 papers)

- **Subiectul I**: 6 independent items, 5p each. Positions map to fixed topics (see the guide).
- **Subiectul II**: 2 problems × (a, b, c). Problem 1 ≈ matrices/systems; Problem 2 ≈ algebraic
  structures (law of composition) or polynomials. Difficulty rises a → b → c.
- **Subiectul III**: 2 problems × (a, b, c). Problem 1 = function study (derivatives, monotonicity,
  asymptotes, inequalities). Problem 2 = integrals (definite integral, area, integral inequalities).
  Difficulty rises a → b → c, and (b)/(c) frequently depend on (a).
- Every paper is 2 pages. 10 points from oficiu. 3 hours, no calculator — so **every answer must be
  hand-computable**.
