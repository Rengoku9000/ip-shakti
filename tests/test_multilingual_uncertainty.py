"""
Unit Tests for Uncertainty, Abstention & Negative Corruption (Phase 2C - Sections 28 & 33)
Verifies:
- Machine-readable status preservation (HUMAN_REVIEW_RECOMMENDED, INSUFFICIENT_EVIDENCE, CLARIFICATION_REQUIRED)
- Epistemic uncertainty preservation across English, Hindi, and Kannada
- Negation preservation
- Treaty status preservation
- Jurisdiction preservation
"""
import unittest
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "drugvista" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from reasoning.evidence_model import (
    StructuredReasoningResult,
    Claim
)
from multilingual.answer_localizer import answer_localizer
from multilingual.translation_service import translation_service


class TestMultilingualUncertainty(unittest.TestCase):
    """Test suite ensuring epistemic modesty, abstention, and negation preservation."""

    def test_human_review_status_preservation(self):
        """HUMAN_REVIEW_RECOMMENDED state must remain identical across all languages."""
        canonical = StructuredReasoningResult(
            status="HUMAN_REVIEW_RECOMMENDED",
            sufficiency="NONE",
            summary="Human review by a qualified legal professional is strongly recommended.",
            human_review=True,
            human_review_reasons=["Confidential TKDL search requested"]
        )

        for lang in ["HINDI", "KANNADA"]:
            loc_res, _ = answer_localizer.localize(canonical, target_language=lang)
            # Machine-readable status and flag must not change
            self.assertEqual(loc_res.status, "HUMAN_REVIEW_RECOMMENDED")
            self.assertTrue(loc_res.human_review)

    def test_insufficient_evidence_preservation(self):
        """INSUFFICIENT_EVIDENCE state must remain identical across all languages."""
        canonical = StructuredReasoningResult(
            status="INSUFFICIENT_EVIDENCE",
            sufficiency="INSUFFICIENT",
            summary="Available authoritative evidence is insufficient to address this query.",
            human_review=False
        )

        for lang in ["HINDI", "KANNADA"]:
            loc_res, _ = answer_localizer.localize(canonical, target_language=lang)
            self.assertEqual(loc_res.status, "INSUFFICIENT_EVIDENCE")
            self.assertFalse(loc_res.human_review)

    def test_clarification_required_preservation(self):
        """CLARIFICATION_REQUIRED state must remain identical across all languages."""
        canonical = StructuredReasoningResult(
            status="CLARIFICATION_REQUIRED",
            sufficiency="NONE",
            summary="Additional clarification regarding specific jurisdiction is required.",
            clarification_needed=["Jurisdiction was not specified in the query."]
        )

        for lang in ["HINDI", "KANNADA"]:
            loc_res, _ = answer_localizer.localize(canonical, target_language=lang)
            self.assertEqual(loc_res.status, "CLARIFICATION_REQUIRED")

    def test_negative_corruption_uncertainty(self):
        """Translation of 'may be relevant' must not become definitive 'is applicable'."""
        text = "This provision may be relevant to the formulation."
        hi = translation_service.translate(text, "ENGLISH", "HINDI")
        kan = translation_service.translate(text, "ENGLISH", "KANNADA")

        # Must retain probabilistic modality
        self.assertIn("प्रासंगिक हो सकता है", hi)
        self.assertIn("ಸಂಬಂಧಿತವಾಗಿರಬಹುದು", kan)

    def test_negative_corruption_treaty_status(self):
        """'adopted but not in force' must not become 'currently binding'."""
        text = "The treaty is adopted but not in force."
        hi = translation_service.translate(text, "ENGLISH", "HINDI")
        kan = translation_service.translate(text, "ENGLISH", "KANNADA")

        self.assertIn("स्वीकृत लेकिन अभी लागू नहीं", hi)
        self.assertIn("ಅಳವಡಿಸಿಕೊಳ್ಳಲಾಗಿದೆ ಆದರೆ ಇನ್ನೂ ಜಾರಿಯಲ್ಲಿಲ್ಲ", kan)


if __name__ == "__main__":
    unittest.main()
