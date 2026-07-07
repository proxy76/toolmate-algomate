"""PDF export tests — the renderer produces a valid PDF for every profile."""
from django.test import SimpleTestCase

from apps.exercises.generators import engine
from apps.exercises.pdf_renderer import render_exam_pdf


class ExportPDFTests(SimpleTestCase):
    def test_renders_valid_pdf_per_profile(self):
        for profile in ("M1", "M2", "M3"):
            data = dict(engine.generate_full_simulation(profile=profile, seed="pdftest"))
            data["session"] = "Simulare"
            pdf = render_exam_pdf(data)
            self.assertTrue(pdf.startswith(b"%PDF"), f"{profile}: not a PDF")
            self.assertGreater(len(pdf), 5000, f"{profile}: PDF suspiciously small")

    def test_m3_variant_selects_label(self):
        data = dict(engine.generate_full_simulation(profile="M3", seed="v"))
        data["m3_variant"] = "pedagogic"
        self.assertTrue(render_exam_pdf(data).startswith(b"%PDF"))
