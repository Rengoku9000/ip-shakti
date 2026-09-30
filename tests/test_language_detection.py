"""
Unit Tests for Language Detection (Phase 2C - Section 24)
Tests English, Hindi, Kannada, mixed language, empty, punctuation,
statutory identifiers, and transliterated queries.
"""
import unittest
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "drugvista" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from multilingual.language_detector import language_detector
from multilingual.language_policy import SupportedLanguage, ScriptType


class TestLanguageDetection(unittest.TestCase):
    """Test suite for deterministic language and script detection."""

    def test_english_query(self):
        """Pure English text should detect ENGLISH with LATIN script and 1.0 confidence."""
        res = language_detector.detect("Can Section 3(p) of the Patents Act exclude my Ayurvedic formulation?")
        self.assertEqual(res.language, SupportedLanguage.ENGLISH.value)
        self.assertEqual(res.script, ScriptType.LATIN.value)
        self.assertEqual(res.confidence, 1.0)
        self.assertFalse(res.is_mixed)

    def test_hindi_query(self):
        """Devanagari text should detect HINDI with DEVANAGARI script."""
        res = language_detector.detect("क्या धारा 3(p) के तहत आयुर्वेदिक फॉर्मूलेशन को पेटेंट कराया जा सकता है?")
        self.assertEqual(res.language, SupportedLanguage.HINDI.value)
        self.assertEqual(res.script, ScriptType.DEVANAGARI.value)
        self.assertGreaterEqual(res.confidence, 0.85)
        self.assertFalse(res.is_mixed)

    def test_kannada_query(self):
        """Kannada text should detect KANNADA with KANNADA script."""
        res = language_detector.detect("ಭಾರತದಲ್ಲಿ ಪೇಟೆಂಟ್ ಕಾಯ್ದೆಯ ಕಲಂ 3(p) ಅಡಿಯಲ್ಲಿ ಪೇಟೆಂಟ್ ಪಡೆಯಬಹುದೇ?")
        self.assertEqual(res.language, SupportedLanguage.KANNADA.value)
        self.assertEqual(res.script, ScriptType.KANNADA.value)
        self.assertGreaterEqual(res.confidence, 0.85)
        self.assertFalse(res.is_mixed)

    def test_mixed_english_hindi(self):
        """Mixed English and Hindi text should detect MIXED script safely."""
        res = language_detector.detect("What is Section 3(p) and इसका Ayurveda से क्या संबंध है?")
        self.assertEqual(res.language, SupportedLanguage.MIXED.value)
        self.assertEqual(res.script, ScriptType.MIXED.value)
        self.assertTrue(res.is_mixed)
        self.assertEqual(res.secondary_language, SupportedLanguage.HINDI.value)

    def test_mixed_english_kannada(self):
        """Mixed English and Kannada text should detect MIXED script safely."""
        res = language_detector.detect("Can you explain Section 6 and ಜೈವಿಕ ಸಂಪನ್ಮೂಲಗಳ ಪೇಟೆಂಟ್ ಅರ್ಜಿ?")
        self.assertEqual(res.language, SupportedLanguage.MIXED.value)
        self.assertEqual(res.script, ScriptType.MIXED.value)
        self.assertTrue(res.is_mixed)
        self.assertEqual(res.secondary_language, SupportedLanguage.KANNADA.value)

    def test_empty_input(self):
        """Empty or whitespace-only query should return UNKNOWN with zero confidence."""
        res = language_detector.detect("   ")
        self.assertEqual(res.language, SupportedLanguage.UNKNOWN.value)
        self.assertEqual(res.confidence, 0.0)

    def test_punctuation_only_input(self):
        """Punctuation and digit only query should return UNKNOWN."""
        res = language_detector.detect("??? !!! 12345 --")
        self.assertEqual(res.language, SupportedLanguage.UNKNOWN.value)
        self.assertEqual(res.confidence, 0.0)

    def test_statutory_identifiers_in_indian_scripts(self):
        """Presence of alphanumeric statutory sections inside Indian scripts should still detect native language."""
        res = language_detector.detect("नियम 158-B और धारा 33EEB के तहत लाइसेंस की शर्तें क्या हैं?")
        self.assertEqual(res.language, SupportedLanguage.HINDI.value)
        self.assertEqual(res.script, ScriptType.DEVANAGARI.value)

    def test_transliterated_hindi(self):
        """Transliterated Hindi words written in Latin script should detect HINDI with LATIN script."""
        res = language_detector.detect("kya yeh formulation patent ho sakta hai aur iska kanoon kya hai?")
        self.assertEqual(res.language, SupportedLanguage.HINDI.value)
        self.assertEqual(res.script, ScriptType.LATIN.value)

    def test_unsupported_language_script(self):
        """Text in Cyrillic, Chinese, or Arabic should return UNKNOWN."""
        res = language_detector.detect("Можно ли запатентовать аюрведический состав?")
        self.assertEqual(res.language, SupportedLanguage.UNKNOWN.value)


if __name__ == "__main__":
    unittest.main()
