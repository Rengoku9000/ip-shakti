"""
Language Policy & Taxonomy for DrugVista / IP-SAKTI Sahayak
Defines supported language enums, scripts, detection results,
error states, and the core MultilingualQuery representation.
"""
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any, Optional


class SupportedLanguage(str, Enum):
    ENGLISH = "ENGLISH"
    HINDI = "HINDI"
    KANNADA = "KANNADA"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


class ScriptType(str, Enum):
    LATIN = "LATIN"
    DEVANAGARI = "DEVANAGARI"
    KANNADA = "KANNADA"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


class LanguageErrorState(str, Enum):
    LANGUAGE_NOT_SUPPORTED = "LANGUAGE_NOT_SUPPORTED"
    LANGUAGE_DETECTION_UNCERTAIN = "LANGUAGE_DETECTION_UNCERTAIN"
    TRANSLATION_UNAVAILABLE = "TRANSLATION_UNAVAILABLE"
    MIXED_LANGUAGE = "MIXED_LANGUAGE"


@dataclass
class LanguageDetectionResult:
    """Outcome of deterministic script and vocabulary inspection."""
    language: str
    confidence: float
    script: str
    is_mixed: bool = False
    secondary_language: Optional[str] = None
    signals: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MultilingualQuery:
    """
    Intermediate representation of user query across languages.
    Preserves original text while generating a canonical normalized
    representation for classification and semantic retrieval.
    """
    original_text: str
    detected_language: str
    normalized_text: str
    retrieval_text: str
    translation_used: bool
    terminology_matches: List[Dict[str, str]] = field(default_factory=list)
    confidence: float = 1.0
    script: str = ScriptType.LATIN.value
    is_mixed: bool = False
    requested_language: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
