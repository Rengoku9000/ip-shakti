"""
Multilingual Text Intelligence Package for DrugVista / IP-SAKTI Sahayak
Supports English, Hindi, and Kannada queries and responses over authoritative
legal and regulatory evidence with immutable citation provenance.
"""
from .language_policy import (
    SupportedLanguage,
    ScriptType,
    LanguageErrorState,
    LanguageDetectionResult,
    MultilingualQuery
)
from .language_detector import language_detector, LanguageDetector
from .query_normalizer import query_normalizer, QueryNormalizer
from .translation_service import (
    translation_service,
    TranslationService,
    TranslationProvider,
    DeterministicLocalTranslationProvider
)
from .answer_localizer import answer_localizer, AnswerLocalizer
from .terminology import (
    extract_statutory_identifiers,
    HERBAL_TERMS_MAP,
    FORMULATION_TYPES_MAP,
    LEGAL_CONCEPTS_MAP
)

__all__ = [
    "SupportedLanguage",
    "ScriptType",
    "LanguageErrorState",
    "LanguageDetectionResult",
    "MultilingualQuery",
    "language_detector",
    "LanguageDetector",
    "query_normalizer",
    "QueryNormalizer",
    "translation_service",
    "TranslationService",
    "TranslationProvider",
    "DeterministicLocalTranslationProvider",
    "answer_localizer",
    "AnswerLocalizer",
    "extract_statutory_identifiers",
    "HERBAL_TERMS_MAP",
    "FORMULATION_TYPES_MAP",
    "LEGAL_CONCEPTS_MAP",
]
