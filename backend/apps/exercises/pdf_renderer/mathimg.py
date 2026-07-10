r"""LaTeX math → transparent PNG, for inline embedding in the BAC PDF.

matplotlib ``mathtext`` renders most BAC math, but it does **not** support the
``matrix`` / ``pmatrix`` / ``cases`` environments our generators emit, nor
``\displaystyle`` / ``\big``. So we:

- render ordinary math with ``mathtext`` (after stripping the unsupported tokens),
- compose ``matrix`` / ``pmatrix`` / ``cases`` ourselves from per-cell mathtext
  images, drawing the delimiters with PIL.

Backgrounds are made fully transparent via a luminance→alpha conversion (black
glyphs, transparent paper) so cells never paint white boxes. ``fragment_render``
also returns the baseline depth so the caller can align inline images correctly.
"""
from __future__ import annotations

import io
import re
from functools import lru_cache

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.font_manager import FontProperties  # noqa: E402
from matplotlib.mathtext import math_to_image  # noqa: E402
from PIL import Image, ImageDraw, ImageOps  # noqa: E402

plt.rcParams.update({"mathtext.fontset": "stix"})

DPI = 200
PX_PER_PT = DPI / 72.0

_ENV = re.compile(
    r"\\left\(\\begin\{matrix\}(?P<m>.*?)\\end\{matrix\}\\right\)"
    r"|\\begin\{pmatrix\}(?P<p>.*?)\\end\{pmatrix\}"
    r"|\\begin\{cases\}(?P<c>.*?)\\end\{cases\}",
    re.DOTALL,
)
# mathtext lacks manual delimiter sizing (\big, \Big, …) and \displaystyle.
_BIG = re.compile(r"\\(?:bigg|Bigg|big|Big)[lrm]?\b\s*")
# matplotlib mathtext is stricter than KaTeX (the frontend): it needs braced
# roots (``\sqrt{2}`` not ``\sqrt2``) and the full ``\geq``/``\leq`` spellings.
# Normalise these here so any generator's KaTeX-valid LaTeX also renders in PDF.
_SQRT = re.compile(r"\\sqrt([\dA-Za-z])")
_TFRAC = re.compile(r"\\tfrac\b")   # mathtext has \frac/\dfrac but not \tfrac
_GE = re.compile(r"\\ge(?![A-Za-z])")
_LE = re.compile(r"\\le(?![A-Za-z])")


def _preprocess(latex: str) -> str:
    s = _BIG.sub("", latex.replace(r"\displaystyle", ""))
    s = _SQRT.sub(r"\\sqrt{\1}", s)
    s = _TFRAC.sub(r"\\frac", s)
    s = _LE.sub(r"\\leq", _GE.sub(r"\\geq", s))
    return s.strip()


@lru_cache(maxsize=4096)
def _raw(expr: str, fontsize: float) -> tuple[bytes, float]:
    buf = io.BytesIO()
    # matplotlib mathtext sizes the canvas to the *advance* width, which clips the
    # right overhang of a trailing italic glyph (a bare ``$f$`` loses most of the
    # letter). A trailing thin space ``\,`` keeps the last glyph off the edge so
    # its ink is fully rendered.
    depth = math_to_image(f"${expr}\\,$", buf, prop=FontProperties(size=fontsize),
                          dpi=DPI, format="png", color="black")
    return buf.getvalue(), float(depth)


def _img(expr: str, fontsize: float) -> Image.Image:
    """Transparent RGBA image (black glyphs) for a plain mathtext expression."""
    expr = expr.strip()
    if not expr:
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    raw, _ = _raw(expr, fontsize)
    gray = Image.open(io.BytesIO(raw)).convert("L")   # white bg, black glyphs
    out = Image.new("RGBA", gray.size, (0, 0, 0, 0))
    out.putalpha(ImageOps.invert(gray))               # white→0, black→255 alpha
    return out


def _parse_rows(body: str) -> list[list[str]]:
    rows = [r for r in re.split(r"\\\\", body) if r.strip() != ""]
    return [[c.strip() for c in r.split("&")] for r in rows]


def _hconcat(images, gap=2):
    images = [im for im in images if im.width and im.height]
    if not images:
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    h = max(im.height for im in images)
    w = sum(im.width for im in images) + gap * (len(images) - 1)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    x = 0
    for im in images:
        out.alpha_composite(im, (x, (h - im.height) // 2))
        x += im.width + gap
    return out


def _vconcat(images, align="left", gap=4):
    images = [im for im in images if im.width and im.height]
    if not images:
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    w = max(im.width for im in images)
    g = int(gap * PX_PER_PT / 2)
    h = sum(im.height for im in images) + g * (len(images) - 1)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    y = 0
    for im in images:
        x = 0 if align == "left" else (w - im.width) // 2
        out.alpha_composite(im, (x, y))
        y += im.height + g
    return out


def _grid_image(rows: list[list[str]], fontsize: float) -> Image.Image:
    cells = [[_img(c, fontsize) for c in row] for row in rows]
    ncol = max((len(r) for r in cells), default=0)
    pad = max(int(5 * PX_PER_PT / 2), 4)
    col_w = [0] * ncol
    row_h = [max((c.height for c in r), default=0) for r in cells]
    for r in cells:
        for j, c in enumerate(r):
            col_w[j] = max(col_w[j], c.width)
    out = Image.new("RGBA",
                    (sum(col_w) + pad * (ncol + 1), sum(row_h) + pad * (len(cells) + 1)),
                    (0, 0, 0, 0))
    y = pad
    for i, r in enumerate(cells):
        x = pad
        for j in range(ncol):
            if j < len(r):
                c = r[j]
                out.alpha_composite(c, (x + (col_w[j] - c.width) // 2,
                                        y + (row_h[i] - c.height) // 2))
            x += col_w[j] + pad
        y += row_h[i] + pad
    return out


def _with_parens(grid: Image.Image) -> Image.Image:
    h = grid.height
    pw = max(int(h * 0.16), 4)
    thick = max(int(1.3 * PX_PER_PT), 2)
    out = Image.new("RGBA", (grid.width + 2 * pw + 2 * thick, h), (0, 0, 0, 0))
    out.alpha_composite(grid, (pw + thick, 0))
    d = ImageDraw.Draw(out)
    bulge = pw * 2
    d.arc([thick, 1, thick + bulge, h - 2], 105, 255, fill=(0, 0, 0, 255), width=thick)
    rx = out.width - 1 - thick
    d.arc([rx - bulge, 1, rx, h - 2], -75, 75, fill=(0, 0, 0, 255), width=thick)
    return out


def _with_brace(stack: Image.Image) -> Image.Image:
    h = stack.height
    bw = max(int(h * 0.12), 5)
    t = max(int(1.3 * PX_PER_PT), 2)
    out = Image.new("RGBA", (stack.width + bw + 2 * t, h), (0, 0, 0, 0))
    out.alpha_composite(stack, (bw + 2 * t, 0))
    d = ImageDraw.Draw(out)
    mid = bw + t
    pts = [(mid, 0), (t, h // 4), (t, h // 2 - t), (1, h // 2), (t, h // 2 + t),
           (t, 3 * h // 4), (mid, h)]
    d.line(pts, fill=(0, 0, 0, 255), width=t, joint="curve")
    return out


def _env_image(match: re.Match, fontsize: float) -> Image.Image:
    if match.group("c") is not None:
        rows = [r.strip() for r in re.split(r"\\\\", match.group("c")) if r.strip()]
        return _with_brace(_vconcat([_img(r, fontsize) for r in rows], align="left"))
    body = match.group("m") if match.group("m") is not None else match.group("p")
    return _with_parens(_grid_image(_parse_rows(body), fontsize))


@lru_cache(maxsize=4096)
def fragment_render(latex: str, fontsize: float):
    """Render one ``$...$`` fragment.

    Returns ``(png_bytes, width_pt, height_pt, depth_pt, is_env)``. ``depth_pt`` is
    how far the content sits below the text baseline (for inline ``valign``);
    ``is_env`` marks composed matrix/cases fragments (center them on the line).
    """
    s = _preprocess(latex)
    if not _ENV.search(s):
        img = _img(s, fontsize)
        # math_to_image parses at 72 dpi, so its returned depth is already in
        # points (the descent below the baseline). Using it directly aligns the
        # math baseline with the text baseline; the earlier `* 72/DPI` shrank it
        # ~2.8×, so expressions floated above the line.
        _raw_bytes, depth_pt = _raw(s, fontsize) if s else (b"", 0.0)
        is_env = False
    else:
        pieces = []
        last = 0
        for m in _ENV.finditer(s):
            if m.start() > last:
                pieces.append(_img(s[last:m.start()], fontsize))
            pieces.append(_env_image(m, fontsize))
            last = m.end()
        if last < len(s):
            pieces.append(_img(s[last:], fontsize))
        img = _hconcat(pieces)
        depth_pt = 0.0
        is_env = True
    buf = io.BytesIO()
    img.save(buf, format="png")
    return (buf.getvalue(), img.width / PX_PER_PT, img.height / PX_PER_PT, depth_pt, is_env)
