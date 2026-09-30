"""
Language Detector for DrugVista / IP-SAKTI Sahayak
Implements deterministic Unicode script analysis and vocabulary inspection
for English, Hindi (Devanagari), Kannada, Mixed, and Unknown languages.
"""
import re
import unicodedata
from typing import List, Tuple
from .language_policy import (
    SupportedLanguage,
    ScriptType,
    LanguageDetectionResult
)


class LanguageDetector:
    """
    Deterministic language detector based on Unicode block distribution
    and domain vocabulary signals.
    """

    # Transliterated Hindi markers (in Latin script)
    HINDI_ROMAN_MARKERS = {
        "kya", "hai", "mein", "aur", "kaise", "hota", "hoti", "hote",
        "nahi", "nahin", "ke", "ki", "ko", "se", "par", "bhi", "is", "iska",
        "iski", "iske", "lagu", "dhaara", "dhara", "kanoon"
    }

    # Transliterated Kannada markers (in Latin script)
    KANNADA_ROMAN_MARKERS = {
        "yenu", "hege", "alli", "agide", "bagge", "matthu", "yava",
        "kooda", "ittu", "beku", "gala", "inda", "annu", "ge", "reethi"
    }

    def detect(self, text: str) -> LanguageDetectionResult:
        """
        Analyze input text and return deterministic language and script classifications.
        """
        if not text or not text.strip():
            return LanguageDetectionResult(
                language=SupportedLanguage.UNKNOWN.value,
                confidence=0.0,
                script=ScriptType.UNKNOWN.value,
                signals=["empty_input"]
            )

        stripped = text.strip()
        # Strip numbers and punctuation to count alphabetic script characters
        clean_text = re.sub(r'[\d\s\W_]+', '', stripped)
        if not clean_text:
            return LanguageDetectionResult(
                language=SupportedLanguage.UNKNOWN.value,
                confidence=0.0,
                script=ScriptType.UNKNOWN.value,
                signals=["punctuation_or_digits_only"]
            )

        devanagari_count = 0
        kannada_count = 0
        latin_count = 0
        other_count = 0

        for ch in clean_text:
            cp = ord(ch)
            if 0x0900 <= cp <= 0x097F:
                devanagari_count += 1
            elif 0x0C80 <= cp <= 0x0CFF:
                kannada_count += 1
            elif ('a' <= ch <= 'z') or ('A' <= ch <= 'Z'):
                latin_count += 1
            else:
                other_count += 1

        total = len(clean_text)
        dev_ratio = devanagari_count / total
        kan_ratio = kannada_count / total
        lat_ratio = latin_count / total
        oth_ratio = other_count / total

        signals = [
            f"devanagari_ratio={dev_ratio:.2f}",
            f"kannada_ratio={kan_ratio:.2f}",
            f"latin_ratio={lat_ratio:.2f}"
        ]

        # 1. Check for completely unsupported script (e.g., Cyrillic, Arabic, CJK)
        if oth_ratio > 0.40:
            signals.append("unsupported_script")
            return LanguageDetectionResult(
                language=SupportedLanguage.UNKNOWN.value,
                confidence=round(oth_ratio, 2),
                script=ScriptType.UNKNOWN.value,
                signals=signals
            )

        # 2. Strong dominance check (protects statutory letters like 158-B or 33EEB from falsely triggering MIXED)
        if dev_ratio >= 0.65 and dev_ratio > (lat_ratio * 2.0):
            conf = min(1.0, 0.75 + (dev_ratio * 0.25))
            return LanguageDetectionResult(
                language=SupportedLanguage.HINDI.value,
                confidence=round(conf, 2),
                script=ScriptType.DEVANAGARI.value,
                signals=signals
            )

        if kan_ratio >= 0.65 and kan_ratio > (lat_ratio * 2.0):
            conf = min(1.0, 0.75 + (kan_ratio * 0.25))
            return LanguageDetectionResult(
                language=SupportedLanguage.KANNADA.value,
                confidence=round(conf, 2),
                script=ScriptType.KANNADA.value,
                signals=signals
            )

        # 3. Mixed Script Handling (e.g. English + Hindi or English + Kannada)
        if (dev_ratio >= 0.18 or kan_ratio >= 0.18) and lat_ratio >= 0.20:
            signals.append("mixed_script_detected")
            if dev_ratio >= kan_ratio:
                return LanguageDetectionResult(
                    language=SupportedLanguage.MIXED.value,
                    confidence=0.95,
                    script=ScriptType.MIXED.value,
                    is_mixed=True,
                    secondary_language=SupportedLanguage.HINDI.value,
                    signals=signals
                )
            else:
                return LanguageDetectionResult(
                    language=SupportedLanguage.MIXED.value,
                    confidence=0.95,
                    script=ScriptType.MIXED.value,
                    is_mixed=True,
                    secondary_language=SupportedLanguage.KANNADA.value,
                    signals=signals
                )

        # 3. Pure / Dominant Devanagari (Hindi)
        if dev_ratio >= 0.30 and dev_ratio > kan_ratio:
            conf = min(1.0, 0.75 + (dev_ratio * 0.25))
            return LanguageDetectionResult(
                language=SupportedLanguage.HINDI.value,
                confidence=round(conf, 2),
                script=ScriptType.DEVANAGARI.value,
                signals=signals
            )

        # 4. Pure / Dominant Kannada
        if kan_ratio >= 0.30 and kan_ratio > dev_ratio:
            conf = min(1.0, 0.75 + (kan_ratio * 0.25))
            return LanguageDetectionResult(
                language=SupportedLanguage.KANNADA.value,
                confidence=round(conf, 2),
                script=ScriptType.KANNADA.value,
                signals=signals
            )

        # 5. Latin Script: Check for English vs Transliterated Hindi / Kannada
        if lat_ratio >= 0.60:
            words = set(re.findall(r'[a-zA-Z]+', stripped.lower()))
            hindi_hits = words.intersection(self.HINDI_ROMAN_MARKERS)
            kannada_hits = words.intersection(self.KANNADA_ROMAN_MARKERS)

            if len(hindi_hits) >= 2:
                signals.append(f"transliterated_hindi_markers={list(hindi_hits)}")
                return LanguageDetectionResult(
                    language=SupportedLanguage.HINDI.value,
                    confidence=0.88,
                    script=ScriptType.LATIN.value,
                    signals=signals
                )
            elif len(kannada_hits) >= 2:
                signals.append(f"transliterated_kannada_markers={list(kannada_hits)}")
                return LanguageDetectionResult(
                    language=SupportedLanguage.KANNADA.value,
                    confidence=0.88,
                    script=ScriptType.LATIN.value,
                    signals=signals
                )

            # Default pure English
            return LanguageDetectionResult(
                language=SupportedLanguage.ENGLISH.value,
                confidence=1.0,
                script=ScriptType.LATIN.value,
                signals=signals
            )

        # 6. Fallback Unknown
        return LanguageDetectionResult(
            language=SupportedLanguage.UNKNOWN.value,
            confidence=0.50,
            script=ScriptType.UNKNOWN.value,
            signals=signals + ["low_confidence_script"]
        )


# Singleton instance
language_detector = LanguageDetector()
