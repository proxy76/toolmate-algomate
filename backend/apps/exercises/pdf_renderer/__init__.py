"""BAC-faithful PDF export. Public entry point: :func:`render_exam_pdf`."""
from __future__ import annotations

import io
import shutil
import tempfile

from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate

from . import builder as B
from .fonts import register_fonts


def render_exam_pdf(data: dict) -> bytes:
    """Render an exam set (the /simulate response shape, plus optional
    session/year/filiera/m3_variant) into a BAC-faithful PDF; return bytes."""
    register_fonts()
    key = B._profile_key(data)
    _, exam_label, default_filiera = B.PROFILE_LABELS[key]
    session = data.get("session", "Simulare")
    meta = {
        "exam_label": f"{exam_label} {session}".strip(),
        "filiera": data.get("filiera", default_filiera),
    }

    imgdir = tempfile.mkdtemp(prefix="bacpdf_")
    try:
        styles = B._styles()
        cache: dict = {}
        story = B._build_story(data, styles, imgdir, cache)

        buf = io.BytesIO()
        doc = BaseDocTemplate(
            buf, pagesize=(B.PAGE_W, B.PAGE_H),
            leftMargin=B.ML, rightMargin=B.MR, topMargin=B.MT, bottomMargin=B.MB,
            title=f"Algomate — {meta['exam_label']}",
        )
        frame = Frame(B.ML, B.FRAME_Y1, B.USABLE_W, B.FRAME_TOP - B.FRAME_Y1,
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="content")
        doc.addPageTemplates([PageTemplate(id="bac", frames=[frame])])
        doc.build(story, canvasmaker=B.make_canvas(meta))
        return buf.getvalue()
    finally:
        shutil.rmtree(imgdir, ignore_errors=True)
