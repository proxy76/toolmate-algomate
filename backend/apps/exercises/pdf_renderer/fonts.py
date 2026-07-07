"""Serif font registration for the BAC PDF (spec §1.2).

Prefers Times New Roman, then Liberation Serif (metrically identical), then
matplotlib's bundled DejaVu Serif as a guaranteed fallback — all carry the
Romanian diacritics (ș, ț, ă, â, î). Registered under the family ``BACSerif``.
"""
from __future__ import annotations

import os

import matplotlib
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FAMILY = "BACSerif"
_BOLD = f"{FAMILY}-Bold"
_ITALIC = f"{FAMILY}-Italic"
_BOLDITALIC = f"{FAMILY}-BoldItalic"

_CANDIDATES = {
    FAMILY: ["times.ttf", "Times New Roman.ttf", "LiberationSerif-Regular.ttf", "DejaVuSerif.ttf"],
    _BOLD: ["timesbd.ttf", "Times New Roman Bold.ttf", "LiberationSerif-Bold.ttf", "DejaVuSerif-Bold.ttf"],
    _ITALIC: ["timesi.ttf", "Times New Roman Italic.ttf", "LiberationSerif-Italic.ttf", "DejaVuSerif-Italic.ttf"],
    _BOLDITALIC: ["timesbi.ttf", "LiberationSerif-BoldItalic.ttf", "DejaVuSerif-BoldItalic.ttf"],
}

_SEARCH_DIRS = [
    r"C:\Windows\Fonts",
    "/usr/share/fonts",
    "/usr/share/fonts/truetype/liberation",
    "/usr/share/fonts/truetype/dejavu",
    os.path.join(matplotlib.get_data_path(), "fonts", "ttf"),
]

_registered = False


def _find(filename: str) -> str | None:
    for d in _SEARCH_DIRS:
        if not os.path.isdir(d):
            continue
        direct = os.path.join(d, filename)
        if os.path.isfile(direct):
            return direct
        for root, _dirs, files in os.walk(d):
            if filename in files:
                return os.path.join(root, filename)
    return None


def register_fonts() -> None:
    global _registered
    if _registered:
        return
    for font_name, candidates in _CANDIDATES.items():
        path = next((p for c in candidates if (p := _find(c))), None)
        if path is None:
            raise RuntimeError(f"Niciun fișier de font găsit pentru {font_name} ({candidates}).")
        pdfmetrics.registerFont(TTFont(font_name, path))
    pdfmetrics.registerFontFamily(
        FAMILY, normal=FAMILY, bold=_BOLD, italic=_ITALIC, boldItalic=_BOLDITALIC
    )
    _registered = True
