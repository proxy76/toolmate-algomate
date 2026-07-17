"""Extract individual BAC problems from the per-position collage PDFs into SVGs.

The source PDFs are collages: each problem is a region of an original BAC paper
placed on the page as a form XObject. A form's /BBox clips its content, which is
why every crop carries slivers of its neighbours — the sliced `SUBIECTUL I` header
above and the first line of the next problem below. Those must not reach the site.

Finding the real problem inside a crop means splitting it into bands of ink
separated by whitespace, then deciding which bands are the problem. Two rejected
approaches, recorded so nobody re-derives them:

* Font boxes lie. A stretched glyph like the parentheses in `(√3-1)²` has a box far
  taller than its ink, so it escapes the BBox while rendering perfectly. Trimming to
  font boxes decapitates real equations.
* Distance doesn't separate. Measured over the corpus, gaps *inside* one problem run
  up to ~13pt (the spacing between sub-points a/b/c) while gaps to a neighbour's
  fragment start at 0.25pt. The distributions overlap almost completely.

What holds is the definition of a sliver: it is content that *continues past the
crop*, so the BBox cuts it and its ink runs flush to the boundary. A problem the
crop contains in full always has daylight around it. So a band flush to an edge is a
neighbour; it fences off that end of the crop, and everything inside the fence is
the problem.

(Also tried and rejected: reading a band as junk when no text line's centre lands in
it. A tall fraction breaks into slim bands — the numerator's overhang wins no centre
of its own — and the rule then fences away half the equation.)

Two passes, because one threshold can't do both jobs. A coarse pass places the
fences: it must not let the 0.5pt cell rules, which run a crop's full height, bridge
every band into one. A fine pass then measures the ink inside those fences, reading
faint marks the coarse pass misses, like a lone superscript.

Output format is a real trade, measured over the whole corpus rather than assumed:

    SVG   121 MB on disk,  9.9 KB per problem gzipped, crisp at any zoom
    PNG    32 MB on disk, 13.9 KB per problem,         crisp to ~3.5 px/pt

PNG is already compressed, so its disk size *is* its wire size, while SVG's 121 MB
gzips down to 23 MB in flight. PNG therefore wins the repo by ~4x and loses the wire
by ~40%. Pass `--format` to pick.

Run from the repo root:
    python scripts/extract_arhiva.py --format png
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import fitz
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "separate-problems-mate-info-and-tehnologic"
OUT_DIR = ROOT / "frontend" / "public" / "arhiva"

# The math ink the rest of the site sets equations in (tailwind `mathink`).
# Sources draw pure black; recolouring keeps the archive from looking pasted in.
MATH_INK = "#261f1b"
MATH_INK_RGB = (0x26, 0x1F, 0x1B)

# Raster scale, in image px per point of artwork — what a retina screen asks for.
# A card is ~880 CSS px wide for a ~500pt problem (1.76 px/pt) and doubles on a 2x
# display; a phone holds 1.15 px/pt (see MIN_LEGIBLE_PX_PER_PT) and triples on a 3x
# one. Both land at ~3.5. At 2.0 the maths is visibly soft.
RASTER_SCALE = 3.5

# Ink shades kept when quantising. The ramp from paper to ink is one hue, so this is
# far more than banding needs, and indexed colour costs a byte a pixel like grey does
# while compressing better.
RASTER_COLORS = 64

# Breathing room around the tightened crop, in points.
PAD_X = 6.0
PAD_Y = 4.0

# Space between the pieces of a problem the original paper broke over a page.
PART_GAP = 7.0

# Slack around the frame when culling offscreen SVG content, in points. The SVG
# already clips to the frame, so this only has to cover error in the box estimates
# below — set it wide and a 16pt-tall problem keeps three lines of invisible
# neighbours on either side.
MARGIN = 2.0

# A glyph outline's extent in em units. Real ink stays well inside this.
EM_LO, EM_HI = -0.4, 1.2

# Decimal places kept in path and matrix numbers. Glyph outlines are in em units, so
# this is ~0.0015px at display size — well under a rendered pixel at any zoom.
COORD_PLACES = 4

# Ink profiling. 4 samples/pt resolves the ~1pt gutter between a sliced header and
# the rule below it, which is the tightest gap we have to cut in.
ZOOM = 4
INK_LEVEL = 200  # 8-bit grey at or below this is a mark

# Segmentation threshold: a row needs this many dark pixels to open a band. The
# 0.5pt cell rules run the full height of a crop and would otherwise bridge every
# band into one; at this resolution they contribute ~4px, so a rules-only row reads
# as the gap it is. Too coarse to measure with — a lone superscript falls under it.
MIN_INK_PX = 14

# Extent threshold, applied only once the cuts are fixed and the cell rules are
# masked out. Low enough to hold a superscript's thinnest row, high enough to
# ignore antialiasing haze. Measuring with MIN_INK_PX instead decapitates exponents.
EXTENT_INK_PX = 2

# A column inked over this share of the crop's height is a cell rule, not content.
RULE_COVERAGE = 0.7
RULE_BLEED = 2  # px of antialiasing to strip either side of one

# A band no taller than this that runs across this share of the problem's width is a
# table border. Fraction bars are the same weight but nothing like as wide.
RULE_MAX_PT = 1.5
RULE_SPAN = 0.55

# How near an edge a band must come to count as flush with it. A sliver can stop a
# pixel short — the BBox may happen to cut between two glyph bottoms — and an exact
# test then reads it as free-standing content and lets it through.
TOUCH_TOL = 2

# `q /fitzca… gs … BT/helv 44 Tf … (algomate.ro) Tj ET Q` — the watermark the
# collage tool stamps across the middle of every page. It overlaps real crops.
WATERMARK_RE = re.compile(rb"q\s*/fitzca\w+\s+gs.*?algomate\.ro.*?ET\s*Q", re.S)

FILENAME_RE = re.compile(
    r"^(?P<spec>Mate-Info|Tehnologic)"
    r" - Subiectul (?P<subject>I{1,3})"
    r" - Exercitiul (?P<exercise>\d+)$"
)

# Labels the collage draws above each crop: `2013 · Varianta 2`, `2016 · Simulare`,
# `2014 · Model`, or a bare `2014`.
LABEL_RE = re.compile(r"^(?P<year>20\d\d)(?:\s*·\s*(?P<session>.+))?$")

# The paper's own furniture, never part of a problem. The last problem of a section
# is cropped with the *next* section's heading sitting under it, fully rendered — no
# ink rule can catch that, because nothing about it is cut. It has to be read.
FURNITURE_RE = re.compile(
    r"SUBIECTUL|de\s*puncte|Toate\s+subiectele|Timp\s+de\s+lucru|Ministerul"
    r"|Examenul\s+de|Prob[aă]\s+(scris|E)|Filiera|Bacalaureat",
    re.I,
)

SPEC_SLUG = {"Mate-Info": "mate-info", "Tehnologic": "tehnologic"}
SUBJECT_NUM = {"I": 1, "II": 2, "III": 3}


@dataclass
class Problem:
    year: int
    session: str
    index: int
    # (page, form name, box) per crop. More than one when the original paper broke the
    # problem over a page and the collage cropped each piece separately.
    parts: list[tuple[int, str, fitz.Rect]]


def strip_watermark(doc: fitz.Document) -> None:
    """Drop the watermark from every page's content stream, in memory."""
    for page in doc:
        for xref in page.get_contents():
            data = doc.xref_stream(xref)
            cleaned = WATERMARK_RE.sub(b"", data)
            if cleaned != data:
                doc.update_stream(xref, cleaned)


def parse_labels(page: fitz.Page) -> list[tuple[str, float]]:
    """Return the collage's `(label, y_top)` captions, top-down, in reading order."""
    out = []
    for blk in page.get_text("dict")["blocks"]:
        if blk["type"] != 0:
            continue
        for ln in blk["lines"]:
            text = "".join(s["text"] for s in ln["spans"]).strip()
            # Captions are the only 8pt helv text on the page.
            if ln["spans"][0]["size"] > 9:
                continue
            first = text.split("\n")[0].strip()
            if LABEL_RE.match(first):
                out.append((first, ln["bbox"][1]))
    out.sort(key=lambda t: t[1])
    return out


def crops(page: fitz.Page) -> list[tuple[str, fitz.Rect]]:
    """Top-level form placements = the problem crops, `(name, rect)`, top-down."""
    H = page.rect.height
    out = []
    for xref, name, invoker, bbox in page.get_xobjects():
        if invoker != 0:
            continue  # nested inside another form, not a crop
        # get_xobjects reports the form BBox in PDF (y-up) space.
        out.append((name, fitz.Rect(bbox[0], H - bbox[3], bbox[2], H - bbox[1])))
    out.sort(key=lambda t: t[1].y0)
    return out


def isolate(doc: fitz.Document, pno: int, name: str) -> fitz.Document:
    """A one-page copy of `pno` drawing only the form `name`.

    Every crop on a collage page is a form holding an entire exam page, positioned so
    its own problem lands in the right place. They overlap heavily and only the forms'
    BBox clips keep each from covering the others. Rendering the page as-is therefore
    carries ~12 exam pages of ink, all landing on top of the one problem we want, and
    correctness rides entirely on clip paths surviving. Isolating the form drops the
    other pages at the source, which is both smaller and no longer clip-dependent.
    """
    tmp = fitz.open()
    tmp.insert_pdf(doc, from_page=pno, to_page=pno)
    page = tmp[0]
    xrefs = page.get_contents()
    tmp.update_stream(xrefs[0], f"/{name} Do".encode())
    for extra in xrefs[1:]:
        tmp.update_stream(extra, b"")
    return tmp


def ink_map(page: fitz.Page, crop: fitz.Rect) -> np.ndarray:
    """Boolean mark/no-mark raster of the crop as it actually renders."""
    pm = page.get_pixmap(
        matrix=fitz.Matrix(ZOOM, ZOOM), clip=crop, colorspace=fitz.csGRAY
    )
    arr = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.stride)
    return arr[:, : pm.width] <= INK_LEVEL


def bands(rows: np.ndarray) -> list[tuple[int, int]]:
    """Runs of True in a 1-D mask, as [start, end) index pairs."""
    edges = np.diff(np.concatenate(([0], rows.view(np.int8), [0])))
    return list(zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)))


def rule_columns(ink: np.ndarray) -> np.ndarray:
    """Columns belonging to a cell rule rather than to content.

    Widened by RULE_BLEED: a rule's antialiased flanks fall under the coverage
    test on their own, and the few grey pixels they leave on every row are enough
    to read a blank strip as inked, stretching a box to the fence.
    """
    mask = ink.mean(axis=0) > RULE_COVERAGE
    wide = mask.copy()
    for shift in range(1, RULE_BLEED + 1):
        wide[shift:] |= mask[:-shift]
        wide[:-shift] |= mask[shift:]
    return wide


def furniture_rows(page: fitz.Page, crop: fitz.Rect) -> list[tuple[float, float]]:
    """Row spans of the paper's headings within `crop`, in crop-local pixels."""
    out = []
    for blk in page.get_text("dict")["blocks"]:
        if blk["type"] != 0:
            continue
        for ln in blk["lines"]:
            text = "".join(s["text"] for s in ln["spans"])
            if not FURNITURE_RE.search(text):
                continue
            y0, y1 = ln["bbox"][1], ln["bbox"][3]
            if y1 <= crop.y0 or y0 >= crop.y1:
                continue
            out.append(((y0 - crop.y0) * ZOOM, (y1 - crop.y0) * ZOOM))
    return out


def has_text(page: fitz.Page, box: fitz.Rect) -> bool:
    """Does `box` hold any of the problem's own words?

    A page break can leave a crop holding nothing but the rule that closed the table.
    It is a part of the problem only if it says something.
    """
    for blk in page.get_text("dict")["blocks"]:
        if blk["type"] != 0:
            continue
        for ln in blk["lines"]:
            text = "".join(s["text"] for s in ln["spans"]).strip()
            if not text or FURNITURE_RE.search(text):
                continue
            mid = (ln["bbox"][1] + ln["bbox"][3]) / 2
            if box.y0 <= mid <= box.y1:
                return True
    return False


def marker_row(page: fitz.Page, crop: fitz.Rect, exercise: int) -> float | None:
    """Where the `N.` that opens this exercise sits, in crop-local pixels.

    Scrambled as the maths is, the numbering extracts cleanly, and it is the one
    mark that says "the problem starts here" rather than merely "ink is here".
    """
    pattern = re.compile(rf"^\s*(?:5p\s*)?{exercise}\.\s*\S")
    for blk in page.get_text("dict")["blocks"]:
        if blk["type"] != 0:
            continue
        for ln in blk["lines"]:
            text = "".join(s["text"] for s in ln["spans"])
            if not pattern.match(text):
                continue
            mid = (ln["bbox"][1] + ln["bbox"][3]) / 2
            if crop.y0 <= mid <= crop.y1:
                return (mid - crop.y0) * ZOOM
    return None


def tight_box(
    page: fitz.Page, crop: fitz.Rect, exercise: int
) -> tuple[fitz.Rect, bool] | None:
    """Shrink `crop` to just the problem, dropping the neighbours' slivers.

    See the module docstring. Returns the box and whether it needed no trimming,
    which the caller reports on — a crop we never cut is one to eyeball.
    """
    ink = ink_map(page, crop)
    height = ink.shape[0]
    coarse = bands(ink.sum(axis=1) >= MIN_INK_PX)
    if not coarse:
        return None

    furniture = furniture_rows(page, crop)

    def is_furniture(a: int, b: int) -> bool:
        return any(fa < b and fb > a for fa, fb in furniture)

    # Pass 1 — fence off everything that isn't the problem. `core` is the ground the
    # fences may never take: anchor it on the band holding the exercise's own `N.`.
    # Density is the fallback but gets this wrong exactly where it costs most — a
    # statement carrying a matrix breaks into thin per-row bands, so the heaviest
    # band lands on some sub-point, and the fence then eats the statement above it.
    plain = [ab for ab in coarse if not is_furniture(*ab)]
    if not plain:
        return None
    mark = marker_row(page, crop, exercise)
    if mark is None:
        core = max(plain, key=lambda ab: ink[ab[0] : ab[1]].sum())
    else:
        core = min(plain, key=lambda ab: max(ab[0] - mark, 0, mark - ab[1]))

    body = ink.copy()
    body[:, rule_columns(ink)] = False
    fine = bands(body.sum(axis=1) >= EXTENT_INK_PX)

    # Fence on the fine bands, not the coarse ones: a sliver can be faint enough that
    # the coarse pass barely sees it, and an unfenced sliver lands on the site. A fine
    # band that runs into the statement is skipped rather than fenced against — better
    # to leave a sliver than to cut the problem — which is what `core` guards.
    lo, hi = 0, height
    for a, b in fine:
        junk = a <= TOUCH_TOL or is_furniture(a, b)  # flush to top, or a heading
        if junk and b <= core[0]:
            lo = max(lo, b)
        junk = b >= height - TOUCH_TOL or is_furniture(a, b)  # flush to bottom, ditto
        if junk and a >= core[1]:
            hi = min(hi, a)

    # Pass 2 — measure. Inside the fence there is only this problem, so take all of
    # its ink, down to the faintest row the coarse pass read straight past.
    rows = np.flatnonzero(body[lo:hi].sum(axis=1) >= EXTENT_INK_PX)
    if not len(rows):
        return None
    top, bot = lo + rows[0], lo + rows[-1] + 1

    # Cutting the heading above a problem can orphan the rule that underlined it,
    # leaving a stray line across the top of the card. Whether one survives depends on
    # where the crop happened to fall, so cards would disagree with each other.
    span = np.flatnonzero(body[top:bot].any(axis=0))
    if len(span):
        wide = RULE_SPAN * (span[-1] - span[0])
        edges = bands(body[lo:hi].sum(axis=1) >= EXTENT_INK_PX)
        for a, b in edges:  # leading
            a, b = lo + a, lo + b
            if a != top or b - a > RULE_MAX_PT * ZOOM:
                break
            cols = np.flatnonzero(body[a:b].any(axis=0))
            if not len(cols) or cols[-1] - cols[0] < wide:
                break
            nxt = [x for x, _ in edges if lo + x > b]
            if not nxt:
                break
            top = lo + nxt[0]
        for a, b in reversed(edges):  # trailing
            a, b = lo + a, lo + b
            if b != bot or b - a > RULE_MAX_PT * ZOOM:
                break
            cols = np.flatnonzero(body[a:b].any(axis=0))
            if not len(cols) or cols[-1] - cols[0] < wide:
                break
            prev = [y for _, y in edges if lo + y < a]
            if not prev:
                break
            bot = lo + prev[-1]

    # Horizontal extent comes from the ink itself, so the frame can't clip a glyph.
    cols = np.flatnonzero(ink[top:bot].any(axis=0))
    box = fitz.Rect(
        crop.x0 + cols[0] / ZOOM,
        crop.y0 + top / ZOOM,
        crop.x0 + (cols[-1] + 1) / ZOOM,
        crop.y0 + bot / ZOOM,
    )
    return box, (lo, hi) == (0, height)


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in value if not unicodedata.combining(c))
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value or "x"


MATRIX_RE = re.compile(r'transform="matrix\(([-\d.eE,\s]+)\)"')
HREF_RE = re.compile(r'xlink:href="#([^"]+)"')
CLIP_USE_RE = re.compile(r'clip-path="url\(#([^)]+)\)"')
DEFS_ID_RE = re.compile(r'<(?:path|clipPath)\s+id="([^"]+)"')
NUM_RE = re.compile(r"-?\d*\.?\d+(?:[eE][-+]?\d+)?")
CMD_RE = re.compile(r"([MmLlHhVvCcSsQqTtAaZz])([^MmLlHhVvCcSsQqTtAaZz]*)")


def _apply(mat: list[float], x: float, y: float) -> tuple[float, float]:
    a, b, c, d, e, f = mat
    return a * x + c * y + e, b * x + d * y + f


def _mat_bbox(mat, x0, y0, x1, y1):
    pts = [_apply(mat, x, y) for x, y in ((x0, y0), (x1, y0), (x0, y1), (x1, y1))]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def _path_bbox(d: str):
    """Bounding box of an SVG path, or None if it uses anything unexpected."""
    x = y = 0.0
    xs, ys = [], []
    for cmd, args in CMD_RE.findall(d):
        nums = [float(n) for n in NUM_RE.findall(args)]
        up = cmd.upper()
        rel = cmd.islower()
        if up == "Z":
            continue
        if up in "MLT":
            step = 2
        elif up in "HV":
            step = 1
        elif up in "SQ":
            step = 4
        elif up == "C":
            step = 6
        else:
            return None  # arcs: rare here, and not worth approximating wrongly
        if not nums or len(nums) % step:
            return None
        for i in range(0, len(nums), step):
            chunk = nums[i : i + step]
            if up == "H":
                x = x + chunk[0] if rel else chunk[0]
            elif up == "V":
                y = y + chunk[0] if rel else chunk[0]
            else:
                for j in range(0, step, 2):
                    px = x + chunk[j] if rel else chunk[j]
                    py = y + chunk[j + 1] if rel else chunk[j + 1]
                    xs.append(px)
                    ys.append(py)
                x, y = px, py
            xs.append(x)
            ys.append(y)
    if not xs:
        return None
    return min(xs), min(ys), max(xs), max(ys)


def cull_svg(svg: str, width: float, height: float) -> str:
    """Drop everything that falls outside the frame.

    MuPDF clips the page but does not cull it: the crop is a form XObject holding a
    whole exam page, so a 16pt-tall problem ships with ~30k glyphs of neighbouring
    text behind a clip path — megabytes to render one line. Nothing here changes what
    is drawn inside the frame; it only discards what could never be seen.
    """
    lines = svg.split("\n")
    try:
        ds, de = lines.index("<defs>"), lines.index("</defs>")
    except ValueError:
        return svg

    def visible(bbox) -> bool:
        if bbox is None:
            return True  # unparsed: keep, a stray glyph beats a missing one
        x0, y0, x1, y1 = bbox
        return x1 >= -MARGIN and y1 >= -MARGIN and x0 <= width + MARGIN and y0 <= height + MARGIN

    kept = []
    for line in lines[de + 1 :]:
        s = line.strip()
        if s.startswith("<use") or (s.startswith("<path") and "id=" not in s):
            m = MATRIX_RE.search(s)
            mat = [float(v) for v in m.group(1).replace(",", " ").split()] if m else None
            if s.startswith("<use"):
                # A glyph outline lives in its em box; the matrix places and scales it.
                box = _mat_bbox(mat, EM_LO, EM_LO, EM_HI, EM_HI) if mat else None
            else:
                dm = re.search(r'\sd="([^"]*)"', s)
                box = _path_bbox(dm.group(1)) if dm else None
                if box and mat:
                    box = _mat_bbox(mat, *box)
            if not visible(box):
                continue
        kept.append(line)

    # Groups whose contents all went are just noise now.
    changed = True
    while changed:
        changed = False
        out = []
        for line in kept:
            if out and out[-1].strip().startswith("<g") and line.strip() == "</g>":
                out.pop()
                changed = True
                continue
            out.append(line)
        kept = out

    used = set()
    for line in kept:
        used.update(HREF_RE.findall(line))
        used.update(CLIP_USE_RE.findall(line))

    defs, keep_block, depth = [], True, 0
    for line in lines[ds + 1 : de]:
        s = line.strip()
        if s.startswith("<clipPath"):
            keep_block = (DEFS_ID_RE.search(s).group(1) in used) if DEFS_ID_RE.search(s) else True
            depth = 1
        elif s.startswith("<path") and depth == 0:
            m = DEFS_ID_RE.search(s)
            if m and m.group(1) not in used:
                continue
        if keep_block:
            defs.append(line)
        if s.startswith("</clipPath>"):
            keep_block, depth = True, 0

    return "\n".join(lines[: ds + 1] + defs + lines[de:de + 1] + kept)


D_ATTR_RE = re.compile(r'\sd="([^"]*)"')
MATRIX_ANY_RE = re.compile(r"matrix\(([^)]*)\)")
DATA_TEXT_RE = re.compile(r'\sdata-text="[^"]*"')


def _round(text: str, places: int) -> str:
    def one(m):
        v = round(float(m.group(0)), places)
        s = f"{v:.{places}f}".rstrip("0").rstrip(".")
        if s in ("", "-", "-0"):
            return "0"
        if s.startswith("0."):
            return s[1:]
        if s.startswith("-0."):
            return "-" + s[2:]
        return s

    return NUM_RE.sub(one, text)


def shrink_svg(svg: str) -> str:
    """Trim the fat MuPDF leaves behind, without touching what renders.

    Glyph outlines are two thirds of a file's bytes, written in em units at nine
    decimal places — a resolution of 0.0015px at display size. Four is past the point
    any renderer can tell the difference, and roughly halves the corpus.
    """
    svg = DATA_TEXT_RE.sub("", svg)  # a debugging aid, not a rendering instruction
    svg = svg.replace(' xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"', "")
    svg = D_ATTR_RE.sub(lambda m: ' d="%s"' % _round(m.group(1), COORD_PLACES), svg)
    svg = MATRIX_ANY_RE.sub(lambda m: "matrix(%s)" % _round(m.group(1), COORD_PLACES), svg)
    return svg


def to_png(
    doc: fitz.Document, parts: list[tuple[int, str, fitz.Rect]], frame: fitz.Rect
) -> Image.Image:
    """Render one problem to a raster, framed to a shared left margin.

    No `isolate` here, unlike the SVG path: rasterising honours the forms' clips, so
    the neighbouring exam pages stacked behind this crop simply don't get drawn.
    """
    K = RASTER_SCALE
    tiles, width = [], round(frame.width * K)
    for pno, _, clip in parts:
        b = fitz.Rect(frame.x0, clip.y0, frame.x1, clip.y1)
        pm = doc[pno].get_pixmap(matrix=fitz.Matrix(K, K), clip=b, colorspace=fitz.csGRAY)
        a = np.frombuffer(pm.samples, np.uint8).reshape(pm.height, pm.stride)
        tiles.append(a[:, : pm.width])

    gap = round(PART_GAP * K)
    height = sum(t.shape[0] for t in tiles) + gap * (len(tiles) - 1)
    canvas = np.full((height, width), 255, np.uint8)
    y = 0
    for t in tiles:
        canvas[y : y + t.shape[0], : t.shape[1]] = t[:, :width]
        y += t.shape[0] + gap

    # Paper-to-ink ramp, so the raster carries the same colour as the vector path.
    t = canvas.astype(np.float32) / 255.0
    rgb = np.stack([MATH_INK_RGB[i] + (255 - MATH_INK_RGB[i]) * t for i in range(3)], -1)
    img = Image.fromarray(rgb.astype(np.uint8), "RGB")
    return img.convert("P", palette=Image.ADAPTIVE, colors=RASTER_COLORS)


def to_svg(
    doc: fitz.Document, parts: list[tuple[int, str, fitz.Rect]], frame: fitz.Rect
) -> str:
    """Render one problem to a standalone SVG, framed to a shared left margin.

    A problem broken over a page break in the original paper arrives as several
    crops; stack them so it reads as the single problem it is.
    """
    boxes = [fitz.Rect(frame.x0, c.y0, frame.x1, c.y1) for _, _, c in parts]
    height = sum(b.height for b in boxes) + PART_GAP * (len(boxes) - 1)

    out = fitz.open()
    page = out.new_page(width=frame.width, height=height)
    y = 0.0
    for (pno, name, _), box in zip(parts, boxes):
        src = isolate(doc, pno, name)
        page.show_pdf_page(
            fitz.Rect(0, y, frame.width, y + box.height), src, 0, clip=box
        )
        src.close()
        y += box.height + PART_GAP
    svg = page.get_svg_image(text_as_path=True)
    out.close()

    svg = shrink_svg(cull_svg(svg, frame.width, height))

    # MuPDF writes glyph outlines as pure black; retint to the site's math ink.
    svg = svg.replace('fill="#000000"', f'fill="{MATH_INK}"')
    svg = svg.replace('stroke="#000000"', f'stroke="{MATH_INK}"')
    # A fixed width would fight the responsive column; let CSS size it.
    svg = re.sub(r'(<svg[^>]*?)\swidth="[^"]*"\sheight="[^"]*"', r"\1", svg, count=1)
    return svg


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--format",
        choices=("png", "svg"),
        default="png",
        help="png: ~4x smaller repo. svg: ~40%% less over the wire, crisp at any zoom.",
    )
    fmt = ap.parse_args().format
    print(f"  format: {fmt}")

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)

    manifest: dict[str, dict] = {}
    total = 0
    uncut: list[str] = []

    for path in sorted(SRC_DIR.glob("*.pdf")):
        m = FILENAME_RE.match(path.stem)
        if not m:
            print(f"  ?? skipping unrecognised file: {path.name}")
            continue

        spec = SPEC_SLUG[m["spec"]]
        subject = SUBJECT_NUM[m["subject"]]
        exercise = int(m["exercise"])
        key = f"{spec}-{subject}-{exercise}"

        doc = fitz.open(path)
        strip_watermark(doc)

        # Pass 1: hand each crop to the caption above it, and learn the file's shared
        # left/right margin so every problem renders on one grid. Captions and crops
        # are not 1:1 — a problem split over a page break in the original paper is
        # cropped in parts, all belonging to the caption that opened it.
        found: list[Problem] = []
        frame = fitz.Rect()
        current: Problem | None = None
        for pno, page in enumerate(doc):
            labels = parse_labels(page)
            li = 0
            for name, rect in crops(page):
                owner = None
                while li < len(labels) and labels[li][1] <= rect.y0:
                    owner = labels[li][0]
                    li += 1

                res = tight_box(page, rect, exercise)
                if res is None:
                    print(f"  !! {path.stem} p{pno}: empty crop at y={rect.y0:.0f}")
                    continue
                box, untrimmed = res
                if untrimmed:
                    # Nothing was cut, so no sliver was detected on either side.
                    # Legitimate for a tightly-cropped problem, but worth a look.
                    uncut.append(f"{path.stem} p{pno} y={rect.y0:.0f} {owner}")
                frame |= fitz.Rect(box.x0, 0, box.x1, 1)

                if owner is not None:
                    lm = LABEL_RE.match(owner)
                    current = Problem(
                        year=int(lm["year"]),
                        session=(lm["session"] or "Sesiunea principală").strip(),
                        index=len(found),
                        parts=[],
                    )
                    found.append(current)
                if current is None:
                    print(f"  !! {path.stem} p{pno}: crop before any caption")
                    continue
                # The caption still opens the problem, but a wordless crop is just
                # the rule left behind by a page break — not a piece of it.
                if has_text(page, box):
                    current.parts.append((pno, name, box))

        frame = fitz.Rect(frame.x0 - PAD_X, 0, frame.x1 + PAD_X, 1)

        # Pass 2: cut the SVGs against that shared frame.
        entries = []
        (OUT_DIR / key).mkdir(exist_ok=True)
        for p in found:
            if not p.parts:
                continue
            slug = f"{p.year}-{slugify(p.session)}-{p.index:03d}"
            out = OUT_DIR / key / f"{slug}.{fmt}"
            if fmt == "svg":
                out.write_text(to_svg(doc, p.parts, frame), encoding="utf-8")
            else:
                to_png(doc, p.parts, frame).save(out, "PNG", optimize=True)
            height = sum(b.height for _, _, b in p.parts) + PART_GAP * (len(p.parts) - 1)
            entries.append(
                {
                    "id": f"{key}/{slug}",
                    "year": p.year,
                    "session": p.session,
                    "src": f"/arhiva/{key}/{slug}.{fmt}",
                    # Lets the list reserve exact space before the artwork loads.
                    "ratio": round(frame.width / height, 3),
                }
            )
        doc.close()

        entries.sort(key=lambda e: (-e["year"], e["session"]))
        manifest[key] = {
            "specialization": spec,
            "subject": subject,
            "exercise": exercise,
            "count": len(entries),
            # Every problem in a set is cut to this one frame, so they all render at
            # the same scale. It is also the width below which the maths stops being
            # legible, which is what the list uses to decide when to let a card scroll.
            "width": round(frame.width, 2),
            "problems": entries,
        }
        total += len(entries)
        print(f"  {path.stem:44s} {len(entries):4d} problems")
        (OUT_DIR / f"{key}.json").write_text(
            json.dumps(manifest[key], ensure_ascii=False), encoding="utf-8"
        )

    index = {
        "total": total,
        "sets": {
            k: {
                "specialization": v["specialization"],
                "subject": v["subject"],
                "exercise": v["exercise"],
                "count": v["count"],
                "years": sorted({p["year"] for p in v["problems"]}, reverse=True),
            }
            for k, v in manifest.items()
        },
    }
    (OUT_DIR / "index.json").write_text(
        json.dumps(index, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\n  {total} problems -> {OUT_DIR}")
    if uncut:
        print(f"  {len(uncut)} crops trimmed on neither side — spot-check these:")
        for line in uncut[:15]:
            print(f"    {line}")


if __name__ == "__main__":
    main()
