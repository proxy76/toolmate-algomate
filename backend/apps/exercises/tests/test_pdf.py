"""PDF export tests — the renderer produces a valid PDF for every profile."""
from django.test import SimpleTestCase

from apps.exercises.generators import engine
from apps.exercises.generators.registry import PROFILES
from apps.exercises.pdf_renderer import render_exam_pdf


class ExportPDFTests(SimpleTestCase):
    def test_renders_valid_pdf_per_profile(self):
        # Several seeds per profile so subtype-specific LaTeX (e.g. progressions'
        # index notation) is actually exercised through matplotlib mathtext.
        for profile in PROFILES:
            for seed in ("pdftest", "prog", "k2"):
                data = dict(engine.generate_full_simulation(profile=profile, seed=seed))
                data["session"] = "Simulare"
                pdf = render_exam_pdf(data)
                self.assertTrue(pdf.startswith(b"%PDF"), f"{profile}/{seed}: not a PDF")
                self.assertGreater(len(pdf), 5000, f"{profile}/{seed}: PDF too small")

    def test_profile_label_mapping(self):
        # Each profile slug maps to its own official exam-variant label block.
        from apps.exercises.pdf_renderer.builder import PROFILE_LABELS, _profile_key

        for profile in PROFILES:
            self.assertEqual(_profile_key({"profile": profile}), profile)
            self.assertIn(profile, PROFILE_LABELS)
