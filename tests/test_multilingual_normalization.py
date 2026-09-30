"""
Unit Tests for Multilingual Query Normalization (Phase 2C - Section 25)
Verifies:
- Original query preserved
- Normalized query generated
- Legal identifiers preserved verbatim
- Ingredient entities preserved
- Formulation entities preserved
- Jurisdiction signals preserved
"""
import unittest
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "drugvista" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from multilingual.query_normalizer import query_normalizer
from multilingual.language_policy import SupportedLanguage


class TestMultilingualNormalization(unittest.TestCase):
    """Test suite for query normalization across languages."""

    def test_hindi_query_normalization(self):
        """Hindi query should preserve original, extract terms, and normalize statutory provisions."""
        q = "क्या भारत में अश्वगंधा और हल्दी से बने आयुर्वेदिक फॉर्मूलेशन को पेटेंट अधिनियम की धारा 3(p) के तहत पेटेंट कराया जा सकता है?"
        ml = query_normalizer.normalize(q)

        # 1. Original text preserved exactly
        self.assertEqual(ml.original_text, q)

        # 2. Detected language
        self.assertEqual(ml.detected_language, SupportedLanguage.HINDI.value)

        # 3. Legal statutory provision preserved verbatim
        self.assertIn("Section 3(p)", ml.normalized_text)
        self.assertIn("Section 3(p)", ml.retrieval_text)

        # 4. Ingredients extracted and present
        term_canonicals = [t["canonical"] for t in ml.terminology_matches]
        self.assertIn("Ashwagandha", term_canonicals)
        self.assertIn("Turmeric", term_canonicals)
        self.assertTrue("ashwagandha" in ml.normalized_text.lower() or "withania" in ml.normalized_text.lower())

        # 5. Jurisdiction signal preserved
        self.assertIn("india", ml.normalized_text.lower())

        # 6. Translation flag set
        self.assertTrue(ml.translation_used)

    def test_kannada_query_normalization(self):
        """Kannada query should preserve original and normalize statutory provisions and entities."""
        q = "ಭಾರತದಲ್ಲಿ ಪೇಟೆಂಟ್ ಕಾಯ್ದೆಯ ಕಲಂ 3(p) ಅಡಿಯಲ್ಲಿ ಸಾಂಪ್ರದಾಯಿಕ ಜ್ಞಾನ ಆಧಾರಿತ ಅಶ್ವಗಂಧ ಚೂರ್ಣಕ್ಕೆ ಪೇಟೆಂಟ್ ಪಡೆಯಬಹುದೇ?"
        ml = query_normalizer.normalize(q)

        # 1. Original text preserved exactly
        self.assertEqual(ml.original_text, q)

        # 2. Detected language
        self.assertEqual(ml.detected_language, SupportedLanguage.KANNADA.value)

        # 3. Statutory provision preserved verbatim
        self.assertIn("Section 3(p)", ml.normalized_text)

        # 4. Formulation extracted
        form_matches = [t["canonical"] for t in ml.terminology_matches if t["category"] == "FORMULATION_TYPE"]
        self.assertIn("Churna", form_matches)

        # 5. Jurisdiction signal preserved
        self.assertIn("india", ml.normalized_text.lower())

    def test_english_query_unaltered(self):
        """English queries should pass through without modification except whitespace normalization."""
        q = "Can an Ayurvedic polyherbal formulation be patented under Section 3(p) of the Patents Act, 1970 in India?"
        ml = query_normalizer.normalize(q)
        self.assertEqual(ml.original_text, q)
        self.assertEqual(ml.detected_language, SupportedLanguage.ENGLISH.value)
        self.assertFalse(ml.translation_used)
        self.assertEqual(ml.normalized_text, q)

    def test_abs_section_6_normalization(self):
        """Hindi ABS query should preserve Section 6 and Biological Diversity Act references."""
        q = "भारत में जैविक संसाधन पर आधारित पेटेंट आवेदन हेतु जैविक विविधता अधिनियम की धारा 6 के तहत पूर्व अनुमोदन आवश्यक है?"
        ml = query_normalizer.normalize(q)
        self.assertIn("Section 6", ml.normalized_text)
        self.assertIn("biological diversity act", ml.normalized_text.lower())
        self.assertIn("india", ml.normalized_text.lower())

    def test_rule_158_b_normalization(self):
        """Kannada regulatory query should preserve Rule 158-B."""
        q = "ಭಾರತದಲ್ಲಿ ಸ್ವಾಮ್ಯದ ಆಯುರ್ವೇದ ಔಷಧಿಗಳಿಗೆ ನಿಯಮ 158-B ಅಡಿಯಲ್ಲಿ ಯಾವ ಪರವಾನಗಿ ಅವಶ್ಯಕತೆಗಳು ಅನ್ವಯಿಸುತ್ತವೆ?"
        ml = query_normalizer.normalize(q)
        self.assertIn("Rule 158-B", ml.normalized_text)
        self.assertIn("india", ml.normalized_text.lower())


if __name__ == "__main__":
    unittest.main()
