"""BAC-faithful PDF builder (spec §1, §4–§11).

Assembles the official exam layout: per-page header/footer with rules and
"Pagina X din Y", centered title block, bullet rules, three sections, and the
point/label/text column structure. Math is embedded as inline images
(see :mod:`mathimg`).
"""
from __future__ import annotations

import os
import re
import tempfile
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from .fonts import FAMILY, register_fonts
from .mathimg import fragment_render

SERIF, BOLD, ITALIC = FAMILY, f"{FAMILY}-Bold", f"{FAMILY}-Italic"

PAGE_W, PAGE_H = A4
ML = MR = 20 * mm
MT = 22 * mm
MB = 18 * mm
HEADER_H = 30
FOOTER_H = 26
USABLE_W = PAGE_W - ML - MR
FRAME_TOP = PAGE_H - MT - HEADER_H
FRAME_Y1 = MB + FOOTER_H

COL_POINTS = 24
COL_LABEL = 22
COL_TEXT = USABLE_W - COL_POINTS - COL_LABEL
BODY_FS = 9.5
MATH_FS = 10.5

INSTITUTION = ["Ministerul Educației și Cercetării",
               "Centrul Național de Politici și Evaluare în Educație"]

PROFILE_LABELS = {
    "M1": ("Matematică M_mate-info", "Probă scrisă la matematică M_mate-info",
           "Filiera teoretică, profilul real, specializarea matematică-informatică; "
           "Filiera vocațională, profilul militar, specializarea matematică-informatică"),
    "M2": ("Matematică M_șt-nat", "Probă scrisă la matematică M_șt-nat",
           "Filiera teoretică, profilul real, specializarea științe ale naturii"),
    "M3_pedagogic": ("Matematică M_pedagogic", "Probă scrisă la matematică M_pedagogic",
                     "Filiera vocațională, profilul pedagogic, specializarea învățător-educatoare"),
    "M3_tehnologic": ("Matematică M_tehnologic", "Probă scrisă la matematică M_tehnologic",
                      "Filiera tehnologică: profilul servicii, toate calificările profesionale; "
                      "profilul resurse, toate calificările profesionale; profilul tehnic, "
                      "toate calificările profesionale"),
}


def _profile_key(data: dict) -> str:
    # Product mapping of the three app profiles to official exam variants:
    # M1 → mate-info, M2 → tehnologic, M3 → pedagogic (M3 sub-variant overridable).
    p = data.get("profile", "M1")
    if p == "M1":
        return "M1"
    if p == "M2":
        return "M3_tehnologic"
    return "M3_" + data.get("m3_variant", "pedagogic")


def _truncate(text: str, n: int) -> str:
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


# --- styles ------------------------------------------------------------------
def _styles():
    return {
        "title": ParagraphStyle("t", fontName=BOLD, fontSize=10, leading=14, alignment=TA_CENTER),
        "proba": ParagraphStyle("p", fontName=SERIF, fontSize=10, leading=14, alignment=TA_CENTER),
        "math_label": ParagraphStyle("m", fontName=BOLD, fontSize=12, leading=16, alignment=TA_CENTER),
        "session": ParagraphStyle("s", fontName=BOLD, fontSize=12, leading=16, alignment=TA_CENTER),
        "filiera": ParagraphStyle("f", fontName=ITALIC, fontSize=9, leading=12, alignment=TA_CENTER),
        "bullet": ParagraphStyle("b", fontName=SERIF, fontSize=9.5, leading=13, leftIndent=12),
        "section": ParagraphStyle("h", fontName=BOLD, fontSize=10.5, leading=14),
        "body": ParagraphStyle("body", fontName=SERIF, fontSize=BODY_FS, leading=13.3,
                               alignment=TA_JUSTIFY),
        "points": ParagraphStyle("pts", fontName=BOLD, fontSize=9.5, leading=13.3),
        "label": ParagraphStyle("lbl", fontName=SERIF, fontSize=9.5, leading=13.3),
        "pnum": ParagraphStyle("pn", fontName=BOLD, fontSize=10, leading=13.3),
    }


# --- mixed text + inline math ------------------------------------------------
_SEG = re.compile(r"(\$.+?\$)", re.DOTALL)


def _mixed_markup(text: str, imgdir: str, cache: dict) -> str:
    out = []
    for seg in _SEG.split(text or ""):
        if len(seg) >= 2 and seg.startswith("$") and seg.endswith("$"):
            latex = seg[1:-1]
            key = (latex, MATH_FS)
            if key not in cache:
                png, w, h, depth, is_env = fragment_render(latex, MATH_FS)
                path = os.path.join(imgdir, f"m{len(cache)}.png")
                with open(path, "wb") as fh:
                    fh.write(png)
                # baseline-align normal math (image bottom sits `depth` below the
                # text baseline); center composed matrix/cases blocks on the line.
                valign = "middle" if is_env else f"{-depth:.2f}"
                cache[key] = (path.replace("\\", "/"), w, h, valign)
            path, w, h, valign = cache[key]
            if w > COL_TEXT:
                h = h * COL_TEXT / w
                w = COL_TEXT
            out.append(
                f'<img src="{path}" width="{w:.2f}" height="{h:.2f}" valign="{valign}"/>'
            )
        elif seg:
            out.append(escape(seg))
    return "".join(out)


def _body_para(text, styles, imgdir, cache):
    return Paragraph(_mixed_markup(text, imgdir, cache), styles["body"])


_NOPAD = TableStyle([
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ("TOPPADDING", (0, 0), (-1, -1), 0),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
])


def _points_row(points, label, text, styles, imgdir, cache):
    t = Table([[Paragraph(points, styles["points"]),
                Paragraph(label, styles["label"]),
                _body_para(text, styles, imgdir, cache)]],
              colWidths=[COL_POINTS, COL_LABEL, COL_TEXT])
    t.setStyle(_NOPAD)
    return t


def _statement_row(number, text, styles, imgdir, cache):
    t = Table([["", Paragraph(number, styles["pnum"]),
                _body_para(text, styles, imgdir, cache)]],
              colWidths=[COL_POINTS, COL_LABEL, COL_TEXT])
    t.setStyle(_NOPAD)
    return t


# --- header / footer via a deferred-numbering canvas -------------------------
def make_canvas(meta: dict):
    label = meta["exam_label"]
    filiera = _truncate(meta["filiera"], 86)

    class NumberedCanvas(canvas.Canvas):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self._saved = []

        def showPage(self):
            self._saved.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total = len(self._saved)
            for state in self._saved:
                self.__dict__.update(state)
                self._chrome(total)
                super().showPage()
            super().save()

        def _chrome(self, total):
            self.saveState()
            self.setStrokeColor(colors.black)
            self.setFillColor(colors.black)
            right = PAGE_W - MR
            page_str = f"Pagina {self._pageNumber} din {total}"
            # header
            self.setFont(SERIF, 9)
            self.drawString(ML, FRAME_TOP + 30, INSTITUTION[0])
            self.drawString(ML, FRAME_TOP + 20, INSTITUTION[1])
            self.setFont(BOLD, 9)
            self.drawRightString(right, FRAME_TOP + 30, label)
            self.setFont(ITALIC, 8.5)
            self.drawRightString(right, FRAME_TOP + 20, filiera)
            self.setFont(SERIF, 8.5)
            self.drawRightString(right, FRAME_TOP + 10, page_str)
            self.setLineWidth(0.5)
            self.line(ML, FRAME_TOP + 5, right, FRAME_TOP + 5)
            # footer
            self.line(ML, FRAME_Y1 - 5, right, FRAME_Y1 - 5)
            self.setFont(SERIF, 8.5)
            self.drawString(ML, FRAME_Y1 - 14, INSTITUTION[0])
            self.drawString(ML, FRAME_Y1 - 23, INSTITUTION[1])
            self.setFont(BOLD, 8.5)
            self.drawRightString(right, FRAME_Y1 - 14, label)
            self.setFont(SERIF, 8)
            self.drawRightString(right, FRAME_Y1 - 23, page_str)
            self.restoreState()

    return NumberedCanvas


# --- story assembly ----------------------------------------------------------
def _is_m3_single(subiect: dict) -> bool:
    probs = subiect.get("problems", [])
    return len(probs) == 1 and len(probs[0].get("sub_items", [])) > 3


def _build_story(data, styles, imgdir, cache):
    key = _profile_key(data)
    math_label, _exam_label, default_filiera = PROFILE_LABELS[key]
    year = data.get("year", 2025)
    session = data.get("session", "Simulare")
    filiera = data.get("filiera", default_filiera)

    story = [
        Paragraph(f"Examenul național de bacalaureat {year}", styles["title"]),
        Paragraph("Proba E. c)", styles["proba"]),
        Paragraph(math_label, styles["math_label"]),
        Paragraph(session, styles["session"]),
        Paragraph(filiera, styles["filiera"]),
        Spacer(1, 8),
        Paragraph("•&nbsp;Toate subiectele sunt obligatorii. Se acordă zece puncte din oficiu.",
                  styles["bullet"]),
        Paragraph("•&nbsp;Timpul de lucru efectiv este de trei ore.", styles["bullet"]),
        Spacer(1, 10),
    ]

    def section(title):
        story.append(Paragraph(title, styles["section"]))
        story.append(Spacer(1, 6))

    # SUBIECTUL I
    section("SUBIECTUL I (30 de puncte)")
    for item in data["subiect_I"]["items"]:
        story.append(_points_row("5p", f"{item['number']}.", item["question_latex"],
                                  styles, imgdir, cache))
        story.append(Spacer(1, 3))

    # SUBIECTUL II / III
    for num, title in ((2, "SUBIECTUL al II-lea (30 de puncte)"),
                       (3, "SUBIECTUL al III-lea (30 de puncte)")):
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black,
                                spaceBefore=0, spaceAfter=8))
        section(title)
        subiect = data[f"subiect_{'II' if num == 2 else 'III'}"]
        if _is_m3_single(subiect):
            prob = subiect["problems"][0]
            if prob.get("statement_latex"):
                story.append(_statement_row("", prob["statement_latex"], styles, imgdir, cache))
                story.append(Spacer(1, 4))
            for i, sub in enumerate(prob["sub_items"], start=1):
                story.append(_points_row("5p", f"{i}.", sub["question_latex"],
                                         styles, imgdir, cache))
                story.append(Spacer(1, 3))
        else:
            for prob in subiect["problems"]:
                if prob.get("statement_latex"):
                    story.append(_statement_row(f"{prob['number']}.", prob["statement_latex"],
                                                styles, imgdir, cache))
                    story.append(Spacer(1, 2))
                for sub in prob["sub_items"]:
                    story.append(_points_row("5p", f"{sub['label']})", sub["question_latex"],
                                             styles, imgdir, cache))
                    story.append(Spacer(1, 3))
                story.append(Spacer(1, 6))
    return story
