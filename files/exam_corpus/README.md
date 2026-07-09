# BAC Mathematics Exam Corpus

Official Romanian Baccalaureate mathematics papers (subiecte + bareme), 2013–2026,
for all four specializations. This is the **ground-truth authority** for the
generator: any generated exam/problem for a level must fall inside that level's
real distribution here. See [`../../ENGINE2_REWORK.md`](../../ENGINE2_REWORK.md)
for how this corpus drives the engine rework, and each level's `ANALYSIS/` for the
distilled position→topic→phrasing findings.

## Layout

```
<level>/<year>/<paper>.pdf   + <paper>.txt   # one folder per level per year
<level>/ANALYSIS/                            # distilled findings (read these first)
<level>/_legacy/                             # older curated corpora, kept intact
```

Levels (hardest → easiest): `mate-info` · `stiintele-naturii` · `tehnologic` ·
`pedagogic`.

| Level | Papers | ANALYSIS |
|-------|-------:|----------|
| mate-info | 232 | ✅ `subiect_I_by_position.md`, `subiect_II_problems.md`, `subiect_III_problems.md`, `GENERATION_GUIDE.md` |
| stiintele-naturii | 226 | ⬜ to write |
| tehnologic | 237 | ✅ `ANALYSIS_tehnologic.md` |
| pedagogic | 194 | ⬜ to write |

## How to use it

1. Read the `.txt` first — it's a `pdftotext -layout` extraction, cheap to grep and
   read. Structure (SUBIECTUL I/II/III, item numbers, a/b/c) is preserved.
2. Romanian diacritics are dropped and some math superscripts flatten (old PDF font
   encoding). When an item is ambiguous, open the paired `.pdf`.
3. Always pair a **Subiect** with its **Barem** (same session/variant): the barem
   lists the accepted answers you use to sympy-verify generated equivalents.

## Filename grammar

`YYYY_E_c_Matematica_<SESS>_M_<level>_<Subiect|Barem>_<NN>_LRO.pdf`

- `SESS`: `S1` Sesiunea I (iunie/iulie) · `S2` Sesiunea II (august) · `S1R`/`S2R`
  rezervă · `SS` Sesiunea Specială · `SM` Simulare / Model.
- 2020–2021 also include lowercase `..._M_<level>_Test_NN.pdf` — extra training
  variants issued during the pandemic reorganization.
- `NN` is the variant number; `LRO` = limba română.

## Provenance / regenerating

Sourced from pro-matematica.ro via [`../../download_bac_mate.sh`](../../download_bac_mate.sh)
(idempotent; 2013→present, all four specializations). The raw download lands in the
git-ignored `bac-matematica/`; this curated tree is produced by organizing that into
`<level>/<year>/` and extracting text. The 391 "failures" the script reports are the
site's own dead links (404s), not missing content.
