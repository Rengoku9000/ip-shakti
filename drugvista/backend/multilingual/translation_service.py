"""
Translation Service Abstraction for DrugVista / IP-SAKTI Sahayak
Provides deterministic local offline translation for English, Hindi, and Kannada,
preserving citation anchors, statutory provision labels, and epistemic uncertainty.
"""
import re
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from .language_policy import SupportedLanguage

logger = logging.getLogger(__name__)


class TranslationProvider(ABC):
    """Abstract interface for translation providers."""

    @abstractmethod
    def translate(self, text: str, source_language: str, target_language: str) -> str:
        """Translate given text from source language to target language."""
        pass


class DeterministicLocalTranslationProvider(TranslationProvider):
    """
    Offline deterministic translation provider using structured domain phrasebooks.
    Zero hallucination risk: protects citations and statutory identifiers verbatim.
    """

    # High-frequency legal & regulatory sentence templates
    HINDI_SENTENCE_MAP: Dict[str, str] = {
        "Evidence-supported analysis based on authoritative retrieved sources.":
            "प्रामाणिक पुनर्प्राप्त स्रोतों के आधार पर साक्ष्य-समर्थित विश्लेषण।",
        "Retrieved evidence provides partial support; key factual details require qualification.":
            "पुनर्प्राप्त साक्ष्य आंशिक समर्थन प्रदान करते हैं; मुख्य तथ्यों के लिए योग्यता की आवश्यकता है।",
        "Available authoritative evidence is insufficient to address this query.":
            "इस प्रश्न का समाधान करने के लिए उपलब्ध प्रामाणिक साक्ष्य अपर्याप्त हैं।",
        "Additional clarification regarding specific jurisdiction or formulation parameters is required.":
            "विशिष्ट क्षेत्राधिकार या फॉर्मूलेशन मापदंडों के संबंध में अतिरिक्त स्पष्टीकरण आवश्यक है।",
        "Human review by a qualified legal or regulatory professional is strongly recommended.":
            "एक योग्य कानूनी या नियामक विशेषज्ञ द्वारा मानवीय समीक्षा की दृढ़ता से अनुशंसा की जाती है।",
        "Request concerns confidential TKDL records which are not accessible in the public corpus.":
            "अनुरोध गोपनीय टीकेडीएल (TKDL) रिकॉर्ड से संबंधित है जो सार्वजनिक कॉर्पस में उपलब्ध नहीं हैं।",
        "No authoritative legal or regulatory evidence was retrieved.":
            "कोई प्रामाणिक कानूनी या नियामक साक्ष्य प्राप्त नहीं हुआ।",
        "Indian jurisdiction provisions applied exclusively.":
            "केवल भारतीय क्षेत्राधिकार के प्रावधान लागू किए गए।",
        "International treaty framework provisions applied exclusively.":
            "केवल अंतर्राष्ट्रीय संधि ढांचे के प्रावधान लागू किए गए।",
    }

    KANNADA_SENTENCE_MAP: Dict[str, str] = {
        "Evidence-supported analysis based on authoritative retrieved sources.":
            "ಅಧಿಕೃತ ಪಡೆದ ಮೂಲಗಳ ಆಧಾರದ ಮೇಲೆ ಸಾಕ್ಷ್ಯ-ಬೆಂಬಲಿತ ವಿಶ್ಲೇಷಣೆ.",
        "Retrieved evidence provides partial support; key factual details require qualification.":
            "ಪಡೆದ ಸಾಕ್ಷ್ಯವು ಭಾಗಶಃ ಬೆಂಬಲವನ್ನು ನೀಡುತ್ತದೆ; ಪ್ರಮುಖ ಸಂಗತಿಗಳಿಗೆ ಅರ್ಹತೆಯ ಅಗತ್ಯವಿದೆ.",
        "Available authoritative evidence is insufficient to address this query.":
            "ಈ ಪ್ರಶ್ನೆಗೆ ಉತ್ತರಿಸಲು ಲಭ್ಯವಿರುವ ಅಧಿಕೃತ ಸಾಕ್ಷ್ಯಗಳು ಸಾಕಷ್ಟಿಲ್ಲ.",
        "Additional clarification regarding specific jurisdiction or formulation parameters is required.":
            "ನಿರ್ದಿಷ್ಟ ವ್ಯಾಪ್ತಿ ಅಥವಾ ಸೂತ್ರೀಕರಣದ ನಿಯತಾಂಕಗಳ ಕುರಿತು ಹೆಚ್ಚಿನ ಸ್ಪಷ್ಟೀಕರಣದ ಅಗತ್ಯವಿದೆ.",
        "Human review by a qualified legal or regulatory professional is strongly recommended.":
            "ಅರ್ಹ ಕಾನೂನು ಅಥವಾ ನಿಯಂತ್ರಕ ತಜ್ಞರಿಂದ ಮಾನವ ಪರಿಶೀಲನೆಯನ್ನು ಬಲವಾಗಿ ಶಿಫಾರಸು ಮಾಡಲಾಗಿದೆ.",
        "Request concerns confidential TKDL records which are not accessible in the public corpus.":
            "ವಿನಂತಿಯು ಸಾರ್ವಜನಿಕ ಕಾರ್ಪಸ್‌ನಲ್ಲಿ ಪ್ರವೇಶಿಸಲಾಗದ ಗೌಪ್ಯ ಟಿಕೆಡಿಎಲ್ (TKDL) ದಾಖಲೆಗಳಿಗೆ ಸಂಬಂಧಿಸಿದೆ.",
        "No authoritative legal or regulatory evidence was retrieved.":
            "ಯಾವುದೇ ಅಧಿಕೃತ ಕಾನೂನು ಅಥವಾ ನಿಯಂತ್ರಕ ಸಾಕ್ಷ್ಯಗಳು ದೊರೆತಿಲ್ಲ.",
        "Indian jurisdiction provisions applied exclusively.":
            "ಭಾರತೀಯ ವ್ಯಾಪ್ತಿಯ ನಿಬಂಧನೆಗಳನ್ನು ಪ್ರತ್ಯೇಕವಾಗಿ ಅನ್ವಯಿಸಲಾಗಿದೆ.",
        "International treaty framework provisions applied exclusively.":
            "ಅಂತರರಾಷ್ಟ್ರೀಯ ಒಪ್ಪಂದದ ಚೌಕಟ್ಟಿನ ನಿಬಂಧನೆಗಳನ್ನು ಪ್ರತ್ಯೇಕವಾಗಿ ಅನ್ವಯಿಸಲಾಗಿದೆ.",
    }

    # Phrase-level substitution dictionaries
    HINDI_PHRASES: List[Tuple[str, str]] = [
        (r'\bPatents Act, 1970\b', 'पेटेंट अधिनियम, 1970'),
        (r'\bPatents Act\b', 'पेटेंट अधिनियम'),
        (r'\bBiological Diversity Act, 2002\b', 'जैविक विविधता अधिनियम, 2002'),
        (r'\bBiological Diversity Act\b', 'जैविक विविधता अधिनियम'),
        (r'\bDrugs & Cosmetics Act\b', 'औषधि और प्रसाधन सामग्री अधिनियम'),
        (r'\bNagoya Protocol\b', 'नागोया प्रोटोकॉल'),
        (r'\bWIPO GRATK Treaty\b', 'WIPO GRATK संधि'),
        (r'\bNational Biodiversity Authority\b', 'राष्ट्रीय जैव विविधता प्राधिकरण (NBA)'),
        (r'\btraditional knowledge\b', 'पारंपरिक ज्ञान'),
        (r'\bbiological resources?\b', 'जैविक संसाधन'),
        (r'\bcommercial utilization\b', 'व्यावसायिक उपयोग'),
        (r'\bfair and equitable benefit sharing\b', 'उचित और न्यायसंगत लाभ साझाकरण'),
        (r'\bprior approval\b', 'पूर्व अनुमोदन'),
        (r'\bclassical formulations?\b', 'शास्त्रीय फॉर्मूलेशन'),
        (r'\bpatent or proprietary medicines?\b', 'पेटेंट या स्वामित्व औषधि'),
        (r'\bpharmacopoeial standards?\b', 'भेषजसंहिता मानक'),
        (r'\bheavy metals?\b', 'भारी धातुएं'),
        (r'\bmicrobial contamination\b', 'सूक्ष्मजीवी संदूषण'),
        (r'\bmere admixture\b', 'मात्र मिश्रण'),
        (r'\bsynergistic effect\b', 'सहक्रियात्मक प्रभाव'),
        (r'\badopted but not in force\b', 'स्वीकृत लेकिन अभी लागू नहीं'),
        (r'\badopted not in force\b', 'स्वीकृत लेकिन अभी लागू नहीं'),
        (r'\bin force\b', 'लागू'),
        (r'\bmay be relevant\b', 'प्रासंगिक हो सकता है'),
        (r'\bappears to apply\b', 'लागू प्रतीत होता है'),
        (r'\bcannot determine\b', 'निर्धारित नहीं किया जा सकता'),
        (r'\binsufficient evidence\b', 'अपर्याप्त साक्ष्य'),
        (r'\brequires review\b', 'समीक्षा आवश्यक है'),
    ]

    KANNADA_PHRASES: List[Tuple[str, str]] = [
        (r'\bPatents Act, 1970\b', 'ಪೇಟೆಂಟ್ ಕಾಯ್ದೆ, 1970'),
        (r'\bPatents Act\b', 'ಪೇಟೆಂಟ್ ಕಾಯ್ದೆ'),
        (r'\bBiological Diversity Act, 2002\b', 'ಜೈವಿಕ ವೈವಿಧ್ಯತೆ ಕಾಯ್ದೆ, 2002'),
        (r'\bBiological Diversity Act\b', 'ಜೈವಿಕ ವೈವಿಧ್ಯತೆ ಕಾಯ್ದೆ'),
        (r'\bDrugs & Cosmetics Act\b', 'ಔಷಧಿಗಳು ಮತ್ತು ಸೌಂದರ್ಯವರ್ಧಕಗಳ ಕಾಯ್ದೆ'),
        (r'\bNagoya Protocol\b', 'ನಾಗೋಯಾ ಪ್ರೋಟೋಕಾಲ್'),
        (r'\bWIPO GRATK Treaty\b', 'WIPO GRATK ಒಪ್ಪಂದ'),
        (r'\bNational Biodiversity Authority\b', 'ರಾಷ್ಟ್ರೀಯ ಜೈವಿಕ ವೈವಿಧ್ಯ ಪ್ರಾಧಿಕಾರ (NBA)'),
        (r'\btraditional knowledge\b', 'ಸಾಂಪ್ರದಾಯಿಕ ಜ್ಞಾನ'),
        (r'\bbiological resources?\b', 'ಜೈವಿಕ ಸಂಪನ್ಮೂಲಗಳು'),
        (r'\bcommercial utilization\b', 'ವಾಣಿಜ್ಯ ಬಳಕೆ'),
        (r'\bfair and equitable benefit sharing\b', 'ನ್ಯಾಯಯುತ ಮತ್ತು ಸಮಾನ ಪ್ರಯೋಜನ ಹಂಚಿಕೆ'),
        (r'\bprior approval\b', 'ಪೂರ್ವ ಅನುಮೋದನೆ'),
        (r'\bclassical formulations?\b', 'ಶಾಸ್ತ್ರೀಯ ಸೂತ್ರೀಕರಣಗಳು'),
        (r'\bpatent or proprietary medicines?\b', 'ಸ್ವಾಮ್ಯದ ಔಷಧಗಳು'),
        (r'\bpharmacopoeial standards?\b', 'ಫಾರ್ಮಾಕೋಪಿಯಲ್ ಮಾನದಂಡಗಳು'),
        (r'\bheavy metals?\b', 'ಭಾರ ಲೋಹಗಳು'),
        (r'\bmicrobial contamination\b', 'ಸೂಕ್ಷ್ಮಜೀವಿಯ ಮಾಲಿನ್ಯ'),
        (r'\bmere admixture\b', 'ಕೇವಲ ಮಿಶ್ರಣ'),
        (r'\bsynergistic effect\b', 'ಸಿನರ್ಜಿಸ್ಟಿಕ್ ಪರಿಣಾಮ'),
        (r'\badopted but not in force\b', 'ಅಳವಡಿಸಿಕೊಳ್ಳಲಾಗಿದೆ ಆದರೆ ಇನ್ನೂ ಜಾರಿಯಲ್ಲಿಲ್ಲ'),
        (r'\badopted not in force\b', 'ಅಳವಡಿಸಿಕೊಳ್ಳಲಾಗಿದೆ ಆದರೆ ಇನ್ನೂ ಜಾರಿಯಲ್ಲಿಲ್ಲ'),
        (r'\bin force\b', 'ಜಾರಿಯಲ್ಲಿದೆ'),
        (r'\bmay be relevant\b', 'ಸಂಬಂಧಿತವಾಗಿರಬಹುದು'),
        (r'\bappears to apply\b', 'ಅನ್ವಯಿಸುವಂತೆ ತೋರುತ್ತದೆ'),
        (r'\bcannot determine\b', 'ನಿರ್ಧರಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ'),
        (r'\binsufficient evidence\b', 'ಸಾಕಷ್ಟು ಸಾಕ್ಷ್ಯಗಳಿಲ್ಲ'),
        (r'\brequires review\b', 'ಪರಿಶೀಲನೆ ಅಗತ್ಯವಿದೆ'),
    ]

    def translate(self, text: str, source_language: str, target_language: str) -> str:
        """
        Deterministic, local phrase-preserving translation.
        Protects citations and statutory section anchors verbatim.
        """
        src = (source_language or "ENGLISH").upper()
        tgt = (target_language or "ENGLISH").upper()

        if not text or src == tgt or tgt == SupportedLanguage.ENGLISH.value:
            return text

        # Step 1: Protect citations e.g. [1], [Patents Act 1970 — Section 3(p)]
        citation_placeholders: Dict[str, str] = {}

        def replace_citation(match):
            idx = len(citation_placeholders)
            placeholder = f"__CITATION_ANCHOR_{idx}__"
            citation_placeholders[placeholder] = match.group(0)
            return placeholder

        # Match square bracket citations and anchor references
        protected_text = re.sub(r'\[[0-9]+\]|\[[^\]]+—[^\]]+\]', replace_citation, text)

        # Step 2: Check for exact full-sentence template match
        stripped_txt = protected_text.strip()
        if tgt == SupportedLanguage.HINDI.value and stripped_txt in self.HINDI_SENTENCE_MAP:
            translated = self.HINDI_SENTENCE_MAP[stripped_txt]
        elif tgt == SupportedLanguage.KANNADA.value and stripped_txt in self.KANNADA_SENTENCE_MAP:
            translated = self.KANNADA_SENTENCE_MAP[stripped_txt]
        else:
            # Step 3: Apply phrase-level mapping
            translated = protected_text
            if tgt == SupportedLanguage.HINDI.value:
                for pat, rep in self.HINDI_PHRASES:
                    translated = re.sub(pat, rep, translated, flags=re.IGNORECASE)
            elif tgt == SupportedLanguage.KANNADA.value:
                for pat, rep in self.KANNADA_PHRASES:
                    translated = re.sub(pat, rep, translated, flags=re.IGNORECASE)

        # Step 4: Re-insert protected citations verbatim (IMMUTABILITY MANDATE)
        for placeholder, original_citation in citation_placeholders.items():
            translated = translated.replace(placeholder, original_citation)

        return translated


class TranslationService:
    """Translation manager with provider fallback and offline guarantee."""

    def __init__(self, primary_provider: Optional[TranslationProvider] = None):
        self.local_provider = DeterministicLocalTranslationProvider()
        self.primary_provider = primary_provider or self.local_provider

    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> str:
        """Execute translation through primary provider with deterministic local fallback."""
        if not text:
            return ""
        tgt = (target_language or "ENGLISH").upper()
        if tgt == SupportedLanguage.ENGLISH.value:
            return text

        try:
            return self.primary_provider.translate(text, source_language, target_language)
        except Exception as e:
            logger.warning(f"Primary translation failed: {e}. Falling back to deterministic local provider.")
            return self.local_provider.translate(text, source_language, target_language)


# Singleton translation service
translation_service = TranslationService()
