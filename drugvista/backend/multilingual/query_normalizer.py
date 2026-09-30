"""
Multilingual Query Normalizer for DrugVista / IP-SAKTI Sahayak
Converts input text across Hindi, Kannada, Mixed, and English into a canonical
English representation suitable for Phase 2B.1 classification and semantic retrieval.
Strictly preserves original query, statutory anchors, and botanical entities.
"""
import re
import logging
from typing import Optional, List, Dict, Any
from .language_policy import (
    SupportedLanguage,
    ScriptType,
    MultilingualQuery,
    LanguageDetectionResult
)
from .language_detector import language_detector
from .terminology import (
    extract_statutory_identifiers,
    HERBAL_TERMS_MAP,
    FORMULATION_TYPES_MAP,
    LEGAL_CONCEPTS_MAP
)

logger = logging.getLogger(__name__)


class QueryNormalizer:
    """
    Normalizes queries across Indian languages into canonical semantic English
    while preserving exact statutory numbers, entities, and jurisdiction signals.
    """

    # Common grammatical and question patterns
    HINDI_PATTERNS = [
        (r'क्या\s+(.+?)\s+(?:को\s+)?पेटेंट कराया जा सकता है(?:\?)?', r'Can \1 be patented?'),
        (r'क्या\s+(.+?)\s+के लिए पेटेंट मिल सकता है(?:\?)?', r'Can \1 obtain a patent?'),
        (r'क्या\s+(.+?)\s+हेतु पूर्व अनुमोदन आवश्यक है(?:\?)?', r'Is prior approval required for \1?'),
        (r'लाइसेंसिंग आवश्यकताएं क्या हैं(?:\?)?', r'What licensing requirements apply?'),
        (r'क्या आवश्यकताएं हैं(?:\?)?', r'What are the requirements?'),
        (r'गुणवत्ता मानक क्या हैं(?:\?)?', r'What are the quality standards?'),
        (r'कैसे लागू होती है(?:\?)?', r'how does it apply?'),
        (r'कैसे लागू होता है(?:\?)?', r'how does it apply?'),
        (r'के तहत', r'under'),
        (r'के अनुसार', r'according to'),
        (r'में भारत', r'in India'),
        (r'भारत में', r'in India'),
        (r'भारतीय कानून', r'Indian law'),
        (r'भारतीय', r'Indian'),
        (r'अंतर्राष्ट्रीय', r'international'),
        (r'प्रावधान', r'provision'),
    ]

    KANNADA_PATTERNS = [
        (r'(.+?)\s+ಪೇಟೆಂಟ್ ಪಡೆಯಬಹುದೇ(?:\?)?', r'Can \1 be patented?'),
        (r'(.+?)\s+ಪೂರ್ವ ಅನುಮೋದನೆ ಅಗತ್ಯವಿದೆಯೇ(?:\?)?', r'Is prior approval required for \1?'),
        (r'ಪರವಾನಗಿ ಅವಶ್ಯಕತೆಗಳು ಯಾವುವು(?:\?)?', r'What licensing requirements apply?'),
        (r'ಗುಣಮಟ್ಟದ ಮಾನದಂಡಗಳು ಯಾವುವು(?:\?)?', r'What are the quality standards?'),
        (r'ಹೇಗೆ ಅನ್ವಯಿಸುತ್ತದೆ(?:\?)?', r'how does it apply?'),
        (r'ಅಡಿಯಲ್ಲಿ', r'under'),
        (r'ಪ್ರಕಾರ', r'according to'),
        (r'ಭಾರತದಲ್ಲಿ', r'in India'),
        (r'ಭಾರತೀಯ ಕಾಯ್ದೆ', r'Indian law'),
        (r'ಭಾರತೀಯ', r'Indian'),
        (r'ಅಂತರರಾಷ್ಟ್ರೀಯ', r'international'),
        (r'ನಿಬಂಧನೆಗಳು', r'provisions'),
    ]

    def normalize(
        self,
        query: str,
        explicit_language: Optional[str] = None
    ) -> MultilingualQuery:
        """
        Normalize query into canonical English for classification & retrieval.
        Preserves original query completely.
        """
        stripped_query = (query or "").strip()
        if not stripped_query:
            return MultilingualQuery(
                original_text="",
                detected_language=SupportedLanguage.UNKNOWN.value,
                normalized_text="",
                retrieval_text="",
                translation_used=False,
                terminology_matches=[]
            )

        # 1. Detect language
        detection = language_detector.detect(stripped_query)
        detected_lang = detection.language

        # If explicit language passed by user, respect it unless completely invalid
        effective_lang = detected_lang
        if explicit_language:
            exp_clean = explicit_language.strip().upper()
            if exp_clean in {l.value for l in SupportedLanguage}:
                effective_lang = exp_clean

        # 2. Extract statutory anchors verbatim (IMMUTABLE across all languages)
        statutory_ids = extract_statutory_identifiers(stripped_query)

        # 3. Extract terminology matches (herbs, formulations, legal terms)
        term_matches: List[Dict[str, str]] = []

        # Check herbs
        for k_term, (common_name, botanical) in HERBAL_TERMS_MAP.items():
            if k_term.lower() in stripped_query.lower():
                term_matches.append({
                    "term": k_term,
                    "category": "HERBAL_INGREDIENT",
                    "canonical": common_name,
                    "botanical": botanical
                })

        # Check formulations
        for f_term, canonical_form in FORMULATION_TYPES_MAP.items():
            if f_term.lower() in stripped_query.lower():
                term_matches.append({
                    "term": f_term,
                    "category": "FORMULATION_TYPE",
                    "canonical": canonical_form
                })

        # 4. Canonical normalization
        normalized = stripped_query
        translation_used = False

        if effective_lang == SupportedLanguage.ENGLISH.value and not detection.is_mixed:
            # English query: canonicalize whitespace
            normalized = re.sub(r'\s+', ' ', stripped_query)
            translation_used = False
        else:
            # Non-English or Mixed: Apply systematic terminology and phrase substitution
            translation_used = True

            # Step A: Apply phrase patterns
            if effective_lang == SupportedLanguage.HINDI.value or detection.script == ScriptType.DEVANAGARI.value:
                for pat, rep in self.HINDI_PATTERNS:
                    normalized = re.sub(pat, rep, normalized, flags=re.IGNORECASE)
            elif effective_lang == SupportedLanguage.KANNADA.value or detection.script == ScriptType.KANNADA.value:
                for pat, rep in self.KANNADA_PATTERNS:
                    normalized = re.sub(pat, rep, normalized, flags=re.IGNORECASE)

            # Step B: Replace legal concepts (longest matches first)
            for k_concept, eng_concept in sorted(LEGAL_CONCEPTS_MAP.items(), key=lambda x: len(x[0]), reverse=True):
                if k_concept in normalized:
                    normalized = normalized.replace(k_concept, eng_concept)

            # Step C: Replace herbal terms with English equivalents (longest matches first)
            for k_herb, (eng_herb, _) in sorted(HERBAL_TERMS_MAP.items(), key=lambda x: len(x[0]), reverse=True):
                if k_herb in normalized:
                    normalized = normalized.replace(k_herb, eng_herb)

            # Step D: Replace formulation terms (longest matches first)
            for k_form, eng_form in sorted(FORMULATION_TYPES_MAP.items(), key=lambda x: len(x[0]), reverse=True):
                if k_form in normalized:
                    normalized = normalized.replace(k_form, eng_form)

            # Step E: Ensure statutory provision identifiers remain intact
            for stat_id in statutory_ids:
                if stat_id.lower() not in normalized.lower():
                    normalized += f" under {stat_id}"

            # Step F: Normalize leftover particles / interrogatives
            # Hindi leftover words
            normalized = re.sub(r'\b(?:के|की|का|को|से|में|पर|और|या|लिए|किए|होता|होती|हैं|है)\b', ' ', normalized)
            # Kannada leftover words
            normalized = re.sub(r'\b(?:ಮತ್ತು|ಅಥವಾ|ಬಗ್ಗೆ|ನಲ್ಲಿ|ಗಾಗಿ|ಆಗಿದೆ|ಇದೆ|ಯಾವ|ಯಾವಾಗ|ಹಾಗೂ)\b', ' ', normalized)

            normalized = re.sub(r'\s+', ' ', normalized).strip()

        # Build retrieval text enriched with exact statutory anchors and jurisdiction
        retrieval_text = normalized
        if statutory_ids:
            for stat_id in statutory_ids:
                if stat_id.lower() not in retrieval_text.lower():
                    retrieval_text = f"{stat_id} {retrieval_text}"

        logger.info(
            f"Normalized query: lang={effective_lang} (det={detected_lang}), "
            f"orig='{stripped_query[:40]}...' -> norm='{normalized[:50]}...'"
        )

        return MultilingualQuery(
            original_text=stripped_query,
            detected_language=detected_lang,
            normalized_text=normalized,
            retrieval_text=retrieval_text,
            translation_used=translation_used,
            terminology_matches=term_matches,
            confidence=detection.confidence,
            script=detection.script,
            is_mixed=detection.is_mixed,
            requested_language=explicit_language
        )


# Singleton normalizer
query_normalizer = QueryNormalizer()
