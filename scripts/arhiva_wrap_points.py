"""Find where each problem's artwork can be broken, so a phone can wrap it.

A picture doesn't reflow. On a narrow screen a ~500pt problem either shrinks below
reading size or scrolls sideways — and switching PNG to SVG changes nothing, since a
vector image bakes in its layout just as hard. The way out is to cut the artwork and
stack the pieces, which needs two things measured off the image itself:

* the rows — each printed line of the problem, so pieces stack in reading order
  (left half of every line followed by the right halves would be nonsense);
* the columns where a cut lands in whitespace rather than through a glyph.

Both come straight from the ink, so the numbers describe exactly what ships. The
page then slices the one PNG with CSS — no second asset, no repo cost.

Writes `x0` and `lines` into each set manifest, reading the PNGs rather than the
source PDFs — so it measures exactly what ships, and re-runs in a couple of minutes.

Run from the repo root, *after* `extract_arhiva.py` (which rewrites the manifests
and would drop these fields):
    python scripts/extract_arhiva.py
    python scripts/arhiva_wrap_points.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ARH = ROOT / "frontend" / "public" / "arhiva"

INK_LEVEL = 200  # 8-bit grey at or below this is a mark

# A row needs this many dark px to be part of a line. The cell rules are masked out
# first, so this only has to clear antialiasing haze.
MIN_ROW_INK = 2

# A column inked over this share of the artwork's height is a cell rule, not content.
# Rules run the full height and would otherwise weld every line into one band.
RULE_COVERAGE = 0.7
RULE_BLEED = 2

# A run of blank columns at least this wide (in points) is a real gap between terms —
# somewhere a break reads as a line wrap rather than a severed expression. Below this
# it's just inter-letter spacing.
MIN_GAP_PT = 2.2

# Lines closer than this (in points) are one visual line: a fraction's numerator sits
# in its own band of ink but must never be split away from its denominator.
LINE_MERGE_PT = 1.6

# Ink taller than this (in points) is a built-up structure — a fraction, a matrix, a
# braced system — not a row of prose. Body text is ~11pt and reaches ~13pt with
# subscripts; a fraction clears 18pt.
TALL_PT = 15.0

# How far either side of a gap to look for such a structure, in points. A gap flanked
# by one is refused: the aligned rows of a system leave blank columns running straight
# through the brace, and a cut there would strand every equation from its `= 0`.
GUARD_PT = 7.0


def rule_columns(ink: np.ndarray) -> np.ndarray:
    mask = ink.mean(axis=0) > RULE_COVERAGE
    wide = mask.copy()
    for shift in range(1, RULE_BLEED + 1):
        wide[shift:] |= mask[:-shift]
        wide[:-shift] |= mask[shift:]
    return wide


def bands(flags: np.ndarray) -> list[tuple[int, int]]:
    edges = np.diff(np.concatenate(([0], flags.view(np.int8), [0])))
    return list(zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)))


def analyse(path: Path, width_pt: float) -> tuple[float, list]:
    """`(x0, [[[x0, x1, top, height], …], …])` in points — lines of segments.

    A segment is one chunk of a line between two safe cuts, carrying its own tight
    box. Boxes are per segment rather than per line so a wrapped row is only as tall
    as what it actually holds: a line containing a fraction is tall, and a carried-over
    `∈ ℝ.` inheriting that height would float in a band of white.

    `x0` is shared by the whole problem so every line still starts on the same
    column — per-line lefts would flatten the indent that separates the `5p` gutter
    from the statement.
    """
    img = Image.open(path).convert("L")
    ink = np.array(img) <= INK_LEVEL
    if not ink.any():
        return 0.0, []
    px_per_pt = img.width / width_pt

    body = ink.copy()
    body[:, rule_columns(ink)] = False  # rules would weld the lines together
    rows = bands(body.sum(axis=1) >= MIN_ROW_INK)
    if not rows:
        return 0.0, []

    # Fold together bands that are really one line (a fraction's numerator, bar and
    # denominator each read as their own band of ink).
    merge = LINE_MERGE_PT * px_per_pt
    merged = [list(rows[0])]
    for a, b in rows[1:]:
        if a - merged[-1][1] <= merge:
            merged[-1][1] = b
        else:
            merged.append([a, b])

    out = []
    for top, bot in merged:
        # Gaps come from the *unmasked* ink: the cell rule is real furniture, and a
        # cut through it would look like a mistake.
        strip = ink[top:bot]
        cols = strip.any(axis=0)
        if not cols.any():
            continue
        first, last = np.flatnonzero(cols)[[0, -1]]

        # How tall the ink stands in each column — the tell for a built-up structure.
        rows_idx = np.arange(strip.shape[0])[:, None]
        hi = np.where(strip, rows_idx, -1).max(axis=0)
        lo = np.where(strip, rows_idx, strip.shape[0]).min(axis=0)
        extent = np.where(cols, hi - lo + 1, 0)
        guard = max(1, round(GUARD_PT * px_per_pt))
        tall = TALL_PT * px_per_pt

        cuts = []
        for a, b in bands(~cols):
            if a <= first or b >= last:
                continue  # leading/trailing margin, not a gap between terms
            if (b - a) < MIN_GAP_PT * px_per_pt:
                continue
            near = extent[max(0, a - guard) : min(len(extent), b + guard)]
            if near.size and near.max() > tall:
                continue  # a fraction/matrix/system straddles this gap
            cuts.append((a + b) // 2)

        # Cut the line into segments and give each its own tight box. Unsafe gaps
        # were skipped above, so a fraction or matrix stays whole inside one segment.
        #
        # Heights come from the rule-masked ink: the `5p` cell rule runs the full
        # height of the problem, and letting it set a row's height would strand one
        # line of text in a band of white three times too tall. The rule still draws —
        # a row's window spans it — it just gets cropped to the row it sits in.
        strip_body = body[top:bot]
        segs = []
        for a, b in zip([first, *cuts], [*cuts, last + 1]):
            sub = strip_body[:, a:b]
            if not sub.any():
                continue  # nothing but furniture in this chunk
            rr = np.flatnonzero(sub.any(axis=1))
            cc = np.flatnonzero(strip[:, a:b].any(axis=0)) + a
            # Whole points, rounded outward. A tenth of a point is below anything a
            # screen can show, and integers cost ~40% fewer bytes in a manifest a
            # phone has to fetch before it can draw anything; rounding out rather
            # than to-nearest guarantees a box never crops the ink it describes.
            x_0, x_1 = np.floor(cc[0] / px_per_pt), np.ceil((cc[-1] + 1) / px_per_pt)
            y_0 = np.floor((top + rr[0]) / px_per_pt)
            y_1 = np.ceil((top + rr[-1] + 1) / px_per_pt)
            segs.append([int(x_0), int(x_1), int(y_0), int(y_1 - y_0)])
        if segs:
            out.append(segs)

    x0 = np.flatnonzero(ink.any(axis=0))[0] / px_per_pt
    return int(np.floor(x0)), out


def main() -> None:
    total_lines = total_cuts = 0
    for f in sorted(ARH.glob("*.json")):
        if f.name == "index.json":
            continue
        man = json.loads(f.read_text(encoding="utf-8"))
        for p in man["problems"]:
            x0, lines = analyse(ARH / p["src"].replace("/arhiva/", ""), man["width"])
            p["x0"] = x0
            p["lines"] = lines
            total_lines += len(lines)
            total_cuts += sum(max(len(segs) - 1, 0) for segs in lines)
        f.write_text(json.dumps(man, ensure_ascii=False), encoding="utf-8")
        print(f"  {f.stem:22s} {man['count']:4d} problems  {f.stat().st_size/1024:6.1f} KB")
    print(f"\n  {total_lines} lines, {total_cuts} break points")


if __name__ == "__main__":
    main()
