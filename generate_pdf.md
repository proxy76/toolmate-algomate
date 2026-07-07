# PDF Export — Implementation Specification
## Feature: Generate BAC-Faithful PDF from Algomate Exercise Sets

> **Goal**: A new endpoint `POST /api/v1/exercises/export-pdf/` receives a generated exercise set (or simulation) and returns a binary PDF that is visually **1:1 with the official MEN BAC exam documents**. All layout, typography, spacing, borders, header/footer, section structure, and math rendering must match the reference documents precisely.

---

## 1. Reference Document Analysis

The following measurements and rules are derived from direct inspection of official MEN BAC PDF documents (e.g. `2025_E_c_Matematica_SM_M_tehnologic_Simulare_XII_Subiect_LRO.pdf`).

### 1.1 Page Setup

| Property | Value |
|---|---|
| Page size | A4 — 210 × 297 mm (595.28 × 841.89 pt in ReportLab) |
| Top margin | 22 mm (62.4 pt) |
| Bottom margin | 18 mm (51.0 pt) |
| Left margin | 20 mm (56.7 pt) |
| Right margin | 20 mm (56.7 pt) |
| Usable width | 170 mm (481.9 pt) |
| Page count | 1 page for M3; 2 pages for M1/M2 (Subiectul III spills to page 2) |

### 1.2 Fonts

The official document uses **Times New Roman** throughout. ReportLab ships with no TTF fonts; use the `reportlab` `TTFont` registration mechanism with system Times New Roman, or bundle the font files.

| Role | Family | Style | Size |
|---|---|---|---|
| Header institution line | Times New Roman | Regular | 9 pt |
| Header exam title line | Times New Roman | Bold | 9 pt |
| Header profile/filiera line | Times New Roman | Italic | 8.5 pt |
| "Pagina X din Y" footer | Times New Roman | Regular | 8.5 pt |
| Exam title block ("Examenul național…") | Times New Roman | Bold | 10 pt |
| "Proba E. c)" sub-label | Times New Roman | Regular | 10 pt |
| Profile name ("Matematică M_tehnologic") | Times New Roman | Bold | 12 pt |
| Session label ("Simulare") | Times New Roman | Bold | 12 pt |
| Filiera description under title | Times New Roman | Italic | 9 pt |
| Bullet rule lines ("Toate subiectele…") | Times New Roman | Regular | 9.5 pt |
| Section header ("SUBIECTUL I (30 de puncte)") | Times New Roman | Bold | 10.5 pt |
| Sub-problem header ("1.", "2.") | Times New Roman | Bold | 10 pt |
| Point label ("5p") | Times New Roman | Bold | 9.5 pt |
| Item number ("1.", "2." inside subiect I) | Times New Roman | Regular | 9.5 pt |
| Exercise body text | Times New Roman | Regular | 9.5 pt |
| Sub-item label ("a)", "b)", "c)") | Times New Roman | Regular | 9.5 pt |
| Math inline | Times New Roman | Italic | 9.5 pt (see §3) |

**Font fallback strategy**: If Times New Roman TTF is not available on the server, use `Liberation Serif` (metrically identical, freely distributable). Register both faces (regular, bold, italic, bold-italic) with ReportLab's `pdfmetrics.registerFont`.

### 1.3 Header Block (repeated on every page)

The header occupies the top of every page, separated from the body by a **single horizontal rule** (0.5 pt, full usable width).

```
┌──────────────────────────────────────────────────────────┐
│  Ministerul Educației și Cercetării          [right-align]│
│  Centrul Național de Politici și Evaluare în Educație    │
│                                                           │
│  Probă scrisă la matematică M_tehnologic Simulare [right]│
│  Filiera tehnologică: profilul servicii, ... [right]     │
│                                              Pagina 1 din 1│
├──────────────────────────────────────────────────────────┤
```

Layout rules:
- Left column (institution): left-aligned, stacked two lines, 9 pt regular.
- Right column (exam metadata): right-aligned, stacked — first line is exam label (bold 9 pt), second line is profile/filiera (italic 8.5 pt), third line "Pagina X din Y" (regular 8.5 pt).
- Both columns sit in a **two-column table** spanning full usable width.
- The horizontal rule is drawn immediately **below** this two-column block, before any body content.
- Header table total height: approximately 24 pt.

### 1.4 Title Block (first page only, below the header rule)

```
Examenul național de bacalaureat [YEAR]        ← bold 10pt, centered
Proba E. c)                                    ← regular 10pt, centered
Matematică M_tehnologic                        ← bold 12pt, centered
[Session — "Varianta N" or "Simulare"]         ← bold 12pt, centered
Filiera tehnologică: [full filiera text]        ← italic 9pt, centered, multi-line
```

Spacing:
- 8 pt gap between header rule and title block start.
- 2 pt between each line within the title block.
- After the last filiera line: a **bullet rule block** (see §1.5) follows with 8 pt gap.

### 1.5 Bullet Rule Block (first page only)

Two lines with bullet (•) prefix, 9.5 pt regular, indented 12 pt from left margin:

```
• Toate subiectele sunt obligatorii. Se acordă zece puncte din oficiu.
• Timpul de lucru efectiv este de trei ore.
```

After this block: 10 pt gap, then the first section header.

### 1.6 Section Headers

Each of the three subjects begins with a bold uppercase header:

```
SUBIECTUL I (30 de puncte)
SUBIECTUL al II-lea (30 de puncte)
SUBIECTUL al III-lea (30 de puncte)
```

Rules:
- Font: Times New Roman Bold, 10.5 pt.
- No border or background — plain text only.
- 10 pt space **above** section header (except the very first one which follows the bullet block).
- 6 pt space **below** section header before the first item.

### 1.7 Item Layout — Subiectul I

Each item is a single-row layout:

```
5p  1. [exercise text ...]
```

Exact column layout using a **3-column table**:

| Column | Width | Content | Alignment |
|---|---|---|---|
| Points | 22 pt | `5p` | Right |
| Number | 18 pt | `1.` | Left |
| Text | remaining (≈ 441 pt) | Exercise body | Left, justified |

Rules:
- Row padding: 0 pt top/bottom between rows; 3 pt space between items (achieved with spacer row or `spaceBefore=3`).
- The points column ("5p") is **bold**.
- The item number ("1.") is regular weight.
- No bullet, no indentation beyond the table column structure.

### 1.8 Item Layout — Subiectul II and III (Problems with sub-items)

Each problem has two levels:

**Level 1 — Problem header** (e.g. "1. Se consideră matricea A(x) = ..."):

```
  1. [problem statement text...]
```

- No points prefix on the problem header line itself.
- Indent: 18 pt from left margin (aligns with item number column).
- Font: Regular 9.5 pt.

**Level 2 — Sub-items a), b), c)**:

```
5p  a) [sub-item text...]
5p  b) [sub-item text...]
5p  c) [sub-item text...]
```

- Same 3-column table as Subiectul I (22 pt points | 22 pt label | remaining text).
- Sub-item label is `a)`, `b)`, `c)` — regular weight.
- 3 pt vertical space between sub-items.
- 6 pt vertical space between the end of problem 1's sub-items and the start of problem 2's header.

### 1.9 Footer Block (repeated on every page)

The footer sits at the bottom of every page, separated from the body by a **single horizontal rule** (0.5 pt, full usable width).

```
─────────────────────────────────────────────────────────
Ministerul Educației și Cercetării          Probă scrisă la matematică M_[profile] [session]
Centrul Național de Politici și Evaluare    Filiera ...: profilul ..., ...
în Educație                                                    Pagina 1 din 1
```

Footer layout rules:
- Identical two-column structure to the header.
- Left: institution name (two lines, 8.5 pt regular).
- Right: exam label (bold 8.5 pt), filiera (italic 8 pt), "Pagina X din Y" (regular 8 pt).
- Footer table sits within the bottom margin area — it does not consume body space.
- The footer rule is drawn **above** the footer table, not below.

---

## 2. Backend Implementation

### 2.1 New Endpoint

```
POST /api/v1/exercises/export-pdf/
Content-Type: application/json

{
  "profile":   "M1" | "M2" | "M3",
  "session":   "Simulare" | "Varianta 1" | "Sesiunea I 2025" | ...,
  "year":      2025,
  "filiera":   "Filiera tehnologică: profilul servicii, ...",
  "subiect_I":   { ... },   // same structure as /simulate/ response
  "subiect_II":  { ... },
  "subiect_III": { ... }
}

Response:
  Content-Type: application/pdf
  Content-Disposition: attachment; filename="algomate_[profile]_[session].pdf"
  [binary PDF body]
```

For the `/simulate/` endpoint, add an optional `?format=pdf` query parameter that returns the PDF directly instead of JSON, passing through the same generation pipeline.

### 2.2 Django View

```python
# apps/exercises/views.py

from django.http import HttpResponse
from .pdf_renderer import render_exam_pdf

class ExportPDFView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serializer = ExamPDFSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        pdf_bytes = render_exam_pdf(data)

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        profile = data["profile"]
        session = data.get("session", "subiect").replace(" ", "_")
        response["Content-Disposition"] = (
            f'attachment; filename="algomate_{profile}_{session}.pdf"'
        )
        return response
```

### 2.3 Module Layout

```
apps/exercises/
  pdf_renderer/
    __init__.py          # exports render_exam_pdf()
    builder.py           # main orchestrator
    layout.py            # page constants, margin definitions
    fonts.py             # font registration
    header_footer.py     # header/footer canvas drawing
    math_renderer.py     # LaTeX → PNG via matplotlib
    components.py        # reusable Flowable subclasses
```

### 2.4 Dependencies

Add to `requirements.txt`:

```
reportlab>=4.2.0
matplotlib>=3.9.0
Pillow>=10.0.0
```

`matplotlib` is used **only** for LaTeX → raster image conversion (see §3). It ships with a bundled TeX rendering pipeline (`mathtext`) that handles the subset of LaTeX used in BAC exercises without requiring a full TeX installation.

---

## 3. Math Rendering Strategy

### 3.1 The Problem

ReportLab cannot natively render LaTeX math. The official documents use Times New Roman with proper mathematical symbols. The closest faithful reproduction strategy is:

**Convert each LaTeX math fragment to a PNG image via `matplotlib.mathtext`**, then embed the PNG inline in the ReportLab Paragraph/Flowable at the correct baseline.

### 3.2 Implementation

```python
# apps/exercises/pdf_renderer/math_renderer.py

import io
import hashlib
from functools import lru_cache

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.mathtext as mathtext
from PIL import Image

# Target resolution: 150 DPI gives crisp output at 9.5pt body size
MATH_DPI = 150
# Font size matching the body text (9.5pt → approximate mathtext size)
MATH_FONTSIZE = 10.5

@lru_cache(maxsize=1024)
def latex_to_png_bytes(latex_expr: str, fontsize: float = MATH_FONTSIZE) -> bytes:
    """
    Converts a LaTeX math string (without $ delimiters) to PNG bytes.
    Result is cached by expression string.
    """
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.patch.set_alpha(0)

    renderer = mathtext.MathTextParser("bitmap")
    # Wrap in $ if not already wrapped
    expr = latex_expr.strip()
    if not expr.startswith("$"):
        expr = f"${expr}$"

    try:
        text = fig.text(0, 0, expr, fontsize=fontsize,
                        color="black", va="baseline", ha="left",
                        usetex=False)
        # Use stix font for best BAC-like appearance
        plt.rcParams.update({
            "mathtext.fontset": "stix",
            "font.family": "STIXGeneral",
        })

        # Measure bounding box and resize figure
        fig.canvas.draw()
        bbox = text.get_window_extent()
        width_in  = (bbox.width  + 4) / MATH_DPI
        height_in = (bbox.height + 4) / MATH_DPI
        fig.set_size_inches(width_in, height_in)
        text.set_position((2 / (bbox.width + 4), 2 / (bbox.height + 4)))

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=MATH_DPI,
                    bbox_inches="tight", pad_inches=0,
                    transparent=True)
        buf.seek(0)
        return buf.read()
    finally:
        plt.close(fig)
```

### 3.3 Text + Math Mixing Strategy

BAC exercise text mixes Romanian prose and inline math. The pattern is:

```
"Se consideră funcția $f : \\mathbb{R} \\to \\mathbb{R}$, $f(x) = x^2 - 2\\ln x$."
```

Parse each exercise string by splitting on `$...$` delimiters. For each segment:
- **Plain text**: render as ReportLab `Paragraph` fragment (Times New Roman 9.5 pt).
- **Math segment**: call `latex_to_png_bytes()`, embed as `Image` flowable, scale height to match text baseline.

```python
# components.py

import re
from reportlab.platypus import Paragraph, Image as RLImage, Flowable
from reportlab.lib.styles import ParagraphStyle
from io import BytesIO

MATH_PATTERN = re.compile(r'\$(.*?)\$', re.DOTALL)

def build_mixed_paragraph(text: str, style: ParagraphStyle) -> list:
    """
    Splits a BAC exercise string into a list of Flowables:
    alternating Paragraphs (plain text) and inline math Images.
    Returns a list suitable for appending to a ReportLab story.
    """
    parts = MATH_PATTERN.split(text)
    # parts alternates: [plain, math, plain, math, ...]
    flowables = []
    inline_fragments = []  # collect for a single HRFlowable line

    for i, part in enumerate(parts):
        if i % 2 == 0:
            # Plain text segment
            if part.strip():
                inline_fragments.append(('text', part))
        else:
            # Math segment
            png_bytes = latex_to_png_bytes(part)
            inline_fragments.append(('math', png_bytes))

    # Build as a single InlineMathParagraph (custom Flowable below)
    flowables.append(InlineMathParagraph(inline_fragments, style))
    return flowables
```

### 3.4 InlineMathParagraph Custom Flowable

Because ReportLab's `Paragraph` cannot natively mix text and images on the same baseline, implement a custom `Flowable`:

```python
class InlineMathParagraph(Flowable):
    """
    Renders a line (or wrapped multi-line) of mixed text and inline
    math images, correctly baseline-aligned.
    """
    LINE_HEIGHT_MULTIPLIER = 1.4   # leading = font_size * 1.4

    def __init__(self, fragments: list, style: ParagraphStyle):
        super().__init__()
        self.fragments = fragments
        self.style = style
        self._layout = None

    def wrap(self, available_width, available_height):
        self._compute_layout(available_width)
        return (available_width, self._total_height)

    def draw(self):
        # Draw each fragment at its computed (x, y) position
        canvas = self.canv
        for frag in self._layout:
            if frag["type"] == "text":
                canvas.setFont(frag["font"], frag["size"])
                canvas.drawString(frag["x"], frag["y"], frag["content"])
            elif frag["type"] == "math":
                img = frag["image"]
                canvas.drawInlineImage(img, frag["x"], frag["y"],
                                       width=frag["w"], height=frag["h"])

    def _compute_layout(self, available_width):
        # Word-wrap aware layout: place fragments left-to-right,
        # wrapping when x + fragment_width > available_width.
        # Math images scale to font cap-height.
        ...
```

> **Implementation note for the agent**: The `_compute_layout` method must iterate fragments, measure each (text via `canvas.stringWidth`, images via PIL image size scaled to cap height), wrap lines, and record absolute `(x, y)` positions. This is the most complex part of the renderer — allocate time accordingly. A working but slightly imperfect line-wrap is acceptable for v1; perfect wrapping can be a follow-up.

---

## 4. Page Template and Frame Definition

Use ReportLab's `BaseDocTemplate` + `PageTemplate` + `Frame` system for automatic page breaks and header/footer repetition.

```python
# builder.py

from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame
from reportlab.lib.units import mm

PAGE_W, PAGE_H = 210 * mm, 297 * mm
MARGIN_L = 20 * mm
MARGIN_R = 20 * mm
MARGIN_T = 22 * mm
MARGIN_B = 18 * mm
HEADER_H = 26    # pt — space reserved at top for header block
FOOTER_H = 22    # pt — space reserved at bottom for footer block

# The content Frame sits between header and footer
content_frame = Frame(
    x1=MARGIN_L,
    y1=MARGIN_B + FOOTER_H,
    width=PAGE_W - MARGIN_L - MARGIN_R,
    height=PAGE_H - MARGIN_T - MARGIN_B - HEADER_H - FOOTER_H,
    leftPadding=0, rightPadding=0,
    topPadding=0,  bottomPadding=0,
    id="content",
)

def on_page(canvas, doc):
    """Called by ReportLab before each page is drawn."""
    draw_header(canvas, doc)
    draw_footer(canvas, doc)

page_template = PageTemplate(
    id="bac",
    frames=[content_frame],
    onPage=on_page,
)

doc = BaseDocTemplate(
    output_path,
    pagesize=(PAGE_W, PAGE_H),
    leftMargin=MARGIN_L, rightMargin=MARGIN_R,
    topMargin=MARGIN_T,  bottomMargin=MARGIN_B,
)
doc.addPageTemplates([page_template])
```

---

## 5. Header and Footer Drawing Functions

```python
# header_footer.py

from reportlab.lib.units import mm, pt
from reportlab.lib import colors

RULE_THICKNESS = 0.5   # pt

def draw_header(canvas, doc):
    """Draws the two-column header and its bottom rule on the current page."""
    canvas.saveState()

    page_w = doc.pagesize[0]
    page_h = doc.pagesize[1]
    top_y  = page_h - doc.topMargin + 4   # start just inside top margin

    col_left_w  = (page_w - doc.leftMargin - doc.rightMargin) * 0.52
    col_right_w = (page_w - doc.leftMargin - doc.rightMargin) * 0.48

    # Left column: institution
    canvas.setFont("TimesNewRoman", 9)
    canvas.drawString(doc.leftMargin, top_y - 10, "Ministerul Educației și Cercetării")
    canvas.drawString(doc.leftMargin, top_y - 20,
                      "Centrul Național de Politici și Evaluare în Educație")

    # Right column: exam label (bold), filiera (italic), page number (regular)
    right_x = page_w - doc.rightMargin
    profile_label = _get_profile_label(doc.exam_data)

    canvas.setFont("TimesNewRoman-Bold", 9)
    canvas.drawRightString(right_x, top_y - 10, profile_label)

    canvas.setFont("TimesNewRoman-Italic", 8.5)
    filiera_short = _truncate_filiera(doc.exam_data["filiera"], 72)
    canvas.drawRightString(right_x, top_y - 20, filiera_short)

    canvas.setFont("TimesNewRoman", 8.5)
    page_str = f"Pagina {canvas.getPageNumber()} din {doc.exam_data['total_pages']}"
    canvas.drawRightString(right_x, top_y - 30, page_str)

    # Horizontal rule
    rule_y = page_h - doc.topMargin
    canvas.setLineWidth(RULE_THICKNESS)
    canvas.setStrokeColor(colors.black)
    canvas.line(doc.leftMargin, rule_y, page_w - doc.rightMargin, rule_y)

    canvas.restoreState()


def draw_footer(canvas, doc):
    """Draws the horizontal rule and two-column footer at the bottom."""
    canvas.saveState()

    page_w = doc.pagesize[0]
    bot_y  = doc.bottomMargin   # footer sits just above bottom margin

    # Rule above footer
    canvas.setLineWidth(RULE_THICKNESS)
    canvas.line(doc.leftMargin, bot_y + 22, page_w - doc.rightMargin, bot_y + 22)

    # Left: institution (2 lines)
    canvas.setFont("TimesNewRoman", 8.5)
    canvas.drawString(doc.leftMargin, bot_y + 14, "Ministerul Educației și Cercetării")
    canvas.drawString(doc.leftMargin, bot_y + 5,
                      "Centrul Național de Politici și Evaluare în Educație")

    # Right: exam label, filiera, page
    right_x = page_w - doc.rightMargin
    canvas.setFont("TimesNewRoman-Bold", 8.5)
    canvas.drawRightString(right_x, bot_y + 14, _get_profile_label(doc.exam_data))

    canvas.setFont("TimesNewRoman-Italic", 8)
    canvas.drawRightString(right_x, bot_y + 6,
                           _truncate_filiera(doc.exam_data["filiera"], 72))

    canvas.setFont("TimesNewRoman", 8)
    page_str = f"Pagina {canvas.getPageNumber()} din {doc.exam_data['total_pages']}"
    canvas.drawRightString(right_x, bot_y - 2, page_str)

    canvas.restoreState()
```

---

## 6. Content Story Assembly

```python
# builder.py (continued)

from reportlab.platypus import Spacer, HRFlowable, Paragraph, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from .components import build_mixed_paragraph, PointsItemRow

def build_story(exam_data: dict) -> list:
    story = []

    # ── Title block (first page only) ──────────────────────────────────────
    story += _build_title_block(exam_data)
    story.append(Spacer(1, 8))
    story += _build_bullet_rules()
    story.append(Spacer(1, 10))

    # ── SUBIECTUL I ────────────────────────────────────────────────────────
    story.append(_section_header("SUBIECTUL I (30 de puncte)"))
    story.append(Spacer(1, 6))
    for item in exam_data["subiect_I"]["items"]:
        story += _build_subiect_I_item(item)
        story.append(Spacer(1, 3))

    # ── SUBIECTUL II ───────────────────────────────────────────────────────
    story.append(Spacer(1, 10))
    story.append(_section_header("SUBIECTUL al II-lea (30 de puncte)"))
    story.append(Spacer(1, 6))
    for prob in exam_data["subiect_II"]["problems"]:
        story += _build_problem(prob)
        story.append(Spacer(1, 6))

    # ── SUBIECTUL III ──────────────────────────────────────────────────────
    story.append(Spacer(1, 10))
    story.append(_section_header("SUBIECTUL al III-lea (30 de puncte)"))
    story.append(Spacer(1, 6))
    for prob in exam_data["subiect_III"]["problems"]:
        story += _build_problem(prob)
        story.append(Spacer(1, 6))

    return story


def _build_subiect_I_item(item: dict) -> list:
    """Builds the 5p + number + text row for a Subiectul I item."""
    return [PointsItemRow(
        points="5p",
        label=f"{item['number']}.",
        content_latex=item["question_latex"],
    )]


def _build_problem(prob: dict) -> list:
    """Builds a full problem block: statement + sub-items a/b/c."""
    rows = []
    # Problem statement (no points prefix)
    rows += [ProblemStatement(
        number=f"{prob['number']}.",
        content_latex=prob.get("statement_latex", ""),
    )]
    rows.append(Spacer(1, 2))
    # Sub-items
    for sub in prob["sub_items"]:
        rows.append(PointsItemRow(
            points="5p",
            label=f"{sub['label']})",
            content_latex=sub["question_latex"],
        ))
        rows.append(Spacer(1, 3))
    return rows
```

---

## 7. PointsItemRow Custom Flowable

This is the core layout primitive. It must render exactly as in the reference document.

```python
# components.py

class PointsItemRow(Flowable):
    """
    Renders one exercise item as:
        [5p]  [N.]  [text with inline math...]
    with exact column widths matching the official document.
    """
    COL_POINTS_W = 22   # pt
    COL_LABEL_W  = 18   # pt
    FONT_SIZE    = 9.5
    LEADING      = 13.3  # 9.5 * 1.4

    def __init__(self, points: str, label: str, content_latex: str):
        super().__init__()
        self.points = points          # e.g. "5p"
        self.label  = label           # e.g. "1." or "a)"
        self.content_latex = content_latex

    def wrap(self, available_width, available_height):
        text_width = available_width - self.COL_POINTS_W - self.COL_LABEL_W
        self._text_width = text_width
        self._lines = self._layout_content(text_width)
        self._height = len(self._lines) * self.LEADING + 2
        return (available_width, self._height)

    def draw(self):
        c = self.canv
        y = self._height - self.LEADING  # start from top

        # Points column (bold)
        c.setFont("TimesNewRoman-Bold", self.FONT_SIZE)
        c.drawRightString(self.COL_POINTS_W - 2, y, self.points)

        # Label column (regular)
        c.setFont("TimesNewRoman", self.FONT_SIZE)
        c.drawString(self.COL_POINTS_W + 2, y, self.label)

        # Content lines (text + math images interleaved)
        x_content = self.COL_POINTS_W + self.COL_LABEL_W
        for line in self._lines:
            x = x_content
            for frag in line:
                if frag["type"] == "text":
                    c.setFont("TimesNewRoman", self.FONT_SIZE)
                    c.drawString(x, y, frag["content"])
                    x += frag["width"]
                elif frag["type"] == "math":
                    c.drawInlineImage(
                        frag["image_buf"],
                        x, y - frag["descend"],
                        width=frag["width"], height=frag["height"]
                    )
                    x += frag["width"]
            y -= self.LEADING

    def _layout_content(self, text_width: float) -> list:
        """
        Parses content_latex, splits on $...$, measures widths,
        and wraps into lines that fit within text_width.
        """
        # Parse mixed segments
        segments = _parse_latex_segments(self.content_latex)
        lines  = []
        current_line = []
        current_x = 0

        for seg in segments:
            if seg["type"] == "text":
                # Split into words, measure each
                words = seg["content"].split()
                for w in words:
                    w_with_space = w + " "
                    w_width = _measure_text(w_with_space, "TimesNewRoman", self.FONT_SIZE)
                    if current_x + w_width > text_width and current_line:
                        lines.append(current_line)
                        current_line = []
                        current_x = 0
                    current_line.append({
                        "type": "text", "content": w_with_space, "width": w_width
                    })
                    current_x += w_width

            elif seg["type"] == "math":
                png = latex_to_png_bytes(seg["content"])
                w, h, descend = _scale_math_image(png, self.FONT_SIZE)
                if current_x + w > text_width and current_line:
                    lines.append(current_line)
                    current_line = []
                    current_x = 0
                current_line.append({
                    "type": "math",
                    "image_buf": BytesIO(png),
                    "width": w, "height": h, "descend": descend,
                })
                current_x += w

        if current_line:
            lines.append(current_line)

        return lines
```

---

## 8. M3 Special Case — Single-Topic Sub-problems

For M3, Subiectul II and Subiectul III each consist of **6 sub-items on the same topic** rather than 2 problems × 3 sub-items. The statement of the topic is introduced once, then all 6 items follow in sequence.

```python
def _build_m3_single_topic_subject(subject_data: dict) -> list:
    """
    M3-specific layout:
      [Topic statement paragraph]
      5p  1. [item]
      5p  2. [item]
      ...
      5p  6. [item]
    """
    rows = []
    # Introductory statement (if present)
    if subject_data.get("statement_latex"):
        rows += build_mixed_paragraph(subject_data["statement_latex"], BODY_STYLE)
        rows.append(Spacer(1, 4))
    # All 6 items with numeric labels (not a/b/c)
    for item in subject_data["items"]:
        rows.append(PointsItemRow(
            points="5p",
            label=f"{item['number']}.",
            content_latex=item["question_latex"],
        ))
        rows.append(Spacer(1, 3))
    return rows
```

---

## 9. Profile Name Mapping

The profile label in the header/footer must exactly match the official document wording:

```python
PROFILE_LABELS = {
    "M1": {
        "math_label":  "Matematică M_mate-info",
        "exam_label":  "Probă scrisă la matematică M_mate-info",
        "filiera_default": (
            "Filiera teoretică, profilul real, specializarea matematică-informatică;\n"
            "Filiera vocațională, profilul militar, specializarea matematică-informatică"
        ),
    },
    "M2": {
        "math_label":  "Matematică M_şt-nat",
        "exam_label":  "Probă scrisă la matematică M_şt-nat",
        "filiera_default": (
            "Filiera teoretică, profilul real, specializarea științe ale naturii"
        ),
    },
    "M3_pedagogic": {
        "math_label":  "Matematică M_pedagogic",
        "exam_label":  "Probă scrisă la matematică M_pedagogic",
        "filiera_default": (
            "Filiera vocațională, profilul pedagogic, specializarea învățător-educatoare"
        ),
    },
    "M3_tehnologic": {
        "math_label":  "Matematică M_tehnologic",
        "exam_label":  "Probă scrisă la matematică M_tehnologic",
        "filiera_default": (
            "Filiera tehnologică: profilul servicii, toate calificările profesionale; "
            "profilul resurse, toate calificările profesionale; "
            "profilul tehnic, toate calificările profesionale"
        ),
    },
}
```

---

## 10. Page Count Logic

```python
def compute_total_pages(exam_data: dict) -> int:
    """
    M3: always 1 page (all 3 subjects fit on A4).
    M2: always 1 page (confirmed across all 2015-2025 variants).
    M1: always 2 pages (Subiectul III always spills to page 2).
    
    This matches the official document pattern observed in all reference PDFs.
    """
    if exam_data["profile"] == "M1":
        return 2
    return 1
```

---

## 11. Title Block Assembly

```python
def _build_title_block(exam_data: dict) -> list:
    profile_info = PROFILE_LABELS[exam_data["profile"]]
    year = exam_data.get("year", 2025)
    session = exam_data.get("session", "Simulare")

    styles = []

    # "Examenul național de bacalaureat YEAR"
    styles.append(Paragraph(
        f"Examenul național de bacalaureat {year}",
        ParagraphStyle("ExamTitle", fontName="TimesNewRoman-Bold",
                       fontSize=10, leading=14, alignment=TA_CENTER)
    ))
    # "Proba E. c)"
    styles.append(Paragraph(
        "Proba E. c)",
        ParagraphStyle("ProbaLabel", fontName="TimesNewRoman",
                       fontSize=10, leading=14, alignment=TA_CENTER)
    ))
    # "Matematică M_tehnologic"
    styles.append(Paragraph(
        profile_info["math_label"],
        ParagraphStyle("MathLabel", fontName="TimesNewRoman-Bold",
                       fontSize=12, leading=16, alignment=TA_CENTER)
    ))
    # "Simulare" or "Varianta N"
    styles.append(Paragraph(
        session,
        ParagraphStyle("Session", fontName="TimesNewRoman-Bold",
                       fontSize=12, leading=16, alignment=TA_CENTER)
    ))
    # Filiera (italic, may be multi-line)
    filiera = exam_data.get("filiera", profile_info["filiera_default"])
    styles.append(Paragraph(
        filiera,
        ParagraphStyle("Filiera", fontName="TimesNewRoman-Italic",
                       fontSize=9, leading=12, alignment=TA_CENTER)
    ))

    return styles
```

---

## 12. Frontend Integration

### 12.1 Download Button

Add a **"Descarcă PDF"** (Download PDF) button to both the `/practice` and `/simulate` pages. This button:
1. Calls `POST /api/v1/exercises/export-pdf/` with the current exercise set JSON.
2. Receives the binary PDF response.
3. Triggers a browser download via `URL.createObjectURL(blob)`.

```typescript
// frontend/src/api/exercises.ts

export async function exportPDF(examData: ExamData): Promise<void> {
  const response = await apiClient.post("/exercises/export-pdf/", examData, {
    responseType: "blob",
  });

  const blob = new Blob([response.data], { type: "application/pdf" });
  const url  = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `algomate_${examData.profile}_${examData.session ?? "subiect"}.pdf`;
  link.click();
  URL.revokeObjectURL(url);
}
```

### 12.2 Loading State

The PDF generation is CPU-bound (matplotlib rendering). Typical latency is 2–5 seconds for a full simulation. The button must show a loading spinner during generation.

---

## 13. Caching

Math images are expensive. Cache `latex_to_png_bytes` results in memory (already handled by `@lru_cache`). For production, persist to Redis using the LaTeX string as the key:

```python
import hashlib, redis

_redis = redis.Redis.from_url(settings.REDIS_URL)

def latex_to_png_bytes_cached(latex_expr: str, fontsize: float = MATH_FONTSIZE) -> bytes:
    key = "math:" + hashlib.md5(f"{latex_expr}:{fontsize}".encode()).hexdigest()
    cached = _redis.get(key)
    if cached:
        return cached
    result = latex_to_png_bytes(latex_expr, fontsize)
    _redis.setex(key, 3600 * 24, result)   # 24h TTL
    return result
```

---

## 14. Implementation Checklist

### Phase 1 — Core renderer
- [ ] Register Times New Roman (regular, bold, italic, bold-italic) with `pdfmetrics`
- [ ] Implement `latex_to_png_bytes()` with STIX font, correct DPI, transparent background
- [ ] Implement `PointsItemRow` Flowable with correct column widths (22 pt / 18 pt / remaining)
- [ ] Implement `InlineMathParagraph` / `_layout_content` with line-wrapping
- [ ] Implement `draw_header()` and `draw_footer()` with correct two-column layout and rule

### Phase 2 — Story assembly
- [ ] Implement `_build_title_block()` with all 5 lines and correct styles
- [ ] Implement `_build_bullet_rules()` (two bullet lines)
- [ ] Implement `_section_header()` (bold, 10.5 pt)
- [ ] Implement `_build_subiect_I_item()` (6 items)
- [ ] Implement `_build_problem()` (statement + a/b/c sub-items)
- [ ] Implement `_build_m3_single_topic_subject()` (6 numbered items)
- [ ] Wire `compute_total_pages()` and pass to `on_page` callback

### Phase 3 — API + frontend
- [ ] `ExportPDFView` returning `application/pdf` response
- [ ] URL route: `path("exercises/export-pdf/", ExportPDFView.as_view())`
- [ ] `ExamPDFSerializer` validating the input structure
- [ ] Frontend `exportPDF()` function
- [ ] "Descarcă PDF" button with loading state on `/simulate` and `/practice`

### Phase 4 — QA
- [ ] Generate one PDF per profile (M1, M2, M3_pedagogic, M3_tehnologic)
- [ ] Visually compare header/footer position against reference PDF
- [ ] Verify math images are baseline-aligned with surrounding text
- [ ] Verify "Pagina 1 din 2" appears correctly on M1 two-page output
- [ ] Stress test: 50 concurrent requests — no process hang from matplotlib

---

## 15. Known Edge Cases

| Case | Handling |
|---|---|
| Very long LaTeX expression in a single `$...$` block | Scale math image down or allow it to overflow onto a new line as a standalone block |
| Problem statement LaTeX that itself contains multi-line math (e.g. matrix display) | Render as display-mode math image, full-width, centered, with 4 pt vertical padding |
| Romanian diacritics in plain text (ș, ț, ă, â, î) | Ensure TTF font file contains these glyphs; test explicitly |
| `\mathbb{R}`, `\to`, `\infty`, `\geq`, `\leq` | All supported by matplotlib STIX mathtext — no custom handling needed |
| `\begin{pmatrix}...\end{pmatrix}` (matrix in LaTeX) | Supported by matplotlib mathtext in display mode; render as full-width centered image |
| `\log_{2}`, `\ln`, `\lim_{x \to 0}` | Supported natively by matplotlib mathtext |
| Exam with 0 items in a subject (degenerate case) | Render section header with a placeholder "—" row; do not crash |