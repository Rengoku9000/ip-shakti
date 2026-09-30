"""
Controlled Terminology Dictionary for DrugVista / IP-SAKTI Sahayak
Provides multilingual mappings for legal/statutory terms, Ayurvedic formulations,
herbal ingredients, and deterministic provision preservation patterns.
"""
import re
from typing import Dict, List, Tuple, Optional


# ---------------------------------------------------------------------------
# 1. Statutory Provision Extractor & Preserver
# ---------------------------------------------------------------------------

STATUTORY_PATTERNS = [
    # Hindi/Kannada/English section pattern: धारा 3(p), कलम 3(d), ಪ್ರಕರಣ 3(e), Section 3(a), etc.
    r'(?:धारा|कलम|अनुभाग|प्रकरण|ಕಲಂ|ಪ್ರಕರಣ|ಸೆಕ್ಷನ್|section)\s*([0-9]+[a-zA-Z]*(?:\([a-zA-Z0-9]+\))*)',
    # Rule pattern: नियम 158-B, ನಿಯಮ 158-B, Rule 158-B, etc.
    r'(?:नियम|ನಿಯಮ|ರೂಲ್|rule)\s*([0-9]+(?:-[a-zA-Z0-9]+)?)',
    # Article pattern: अनुच्छेद 5, ವಿಧಿ 5, Article 5, etc.
    r'(?:अनुच्छेद|विधि|ಆರ್ಟಿಕಲ್|article)\s*([0-9]+(?:\([a-zA-Z0-9]+\))*)',
    # Schedule pattern: अनुसूची T, ಅನುಸೂಚಿ T, Schedule T, First Schedule, आदि
    r'(?:अनुसूची|ಅನುಸೂಚಿ|schedule)\s*([a-zA-Z0-9]+|first|second|प्रथम|द्वितीय|ಮೊದಲ|ಎರಡನೇ)',
]

STATUTORY_RE = re.compile("|".join(STATUTORY_PATTERNS), re.IGNORECASE)


def extract_statutory_identifiers(text: str) -> List[str]:
    """
    Extracts all statutory provision identifiers verbatim from text across all languages.
    Examples: 'Section 3(p)', 'Rule 158-B', 'Article 5', 'Schedule T'.
    """
    results = []
    # Search section
    for m in re.finditer(r'(?:धारा|कलम|अनुभाग|प्रकरण|ಕಲಂ|ಸೆಕ್ಷನ್|section)\s*([0-9]+[a-zA-Z]*(?:\([a-zA-Z0-9]+\))*)', text, re.I):
        sec_num = m.group(1).strip()
        results.append(f"Section {sec_num}")
    # Search rule
    for m in re.finditer(r'(?:नियम|ನಿಯಮ|ರೂಲ್|rule)\s*([0-9]+(?:-[a-zA-Z0-9]+)?)', text, re.I):
        rule_num = m.group(1).strip()
        results.append(f"Rule {rule_num}")
    # Search article
    for m in re.finditer(r'(?:अनुच्छेद|विधि|ಆರ್ಟಿಕಲ್|article)\s*([0-9]+(?:\([a-zA-Z0-9]+\))*)', text, re.I):
        art_num = m.group(1).strip()
        results.append(f"Article {art_num}")
    # Search schedule
    for m in re.finditer(r'(?:अनुसूची|ಅನುಸೂಚಿ|schedule)\s*([a-zA-Z0-9]+|first|second|प्रथम|द्वितीय|ಮೊದಲ|ಎರಡನೇ)', text, re.I):
        sched = m.group(1).strip()
        if sched.lower() in {"first", "प्रथम", "ಮೊದಲ"}:
            results.append("First Schedule")
        elif sched.lower() in {"second", "द्वितीय", "ಎರಡನೇ"}:
            results.append("Second Schedule")
        else:
            results.append(f"Schedule {sched.upper()}")
    return list(dict.fromkeys(results))


# ---------------------------------------------------------------------------
# 2. Herbal & Botanical Canonical Normalization
# ---------------------------------------------------------------------------

HERBAL_TERMS_MAP: Dict[str, Tuple[str, str]] = {
    # Hindi
    "अश्वगंधा": ("Ashwagandha", "Withania somnifera"),
    "हल्दी": ("Turmeric", "Curcuma longa"),
    "नीम": ("Neem", "Azadirachta indica"),
    "तुलसी": ("Tulsi", "Ocimum sanctum"),
    "गिलोय": ("Guduchi", "Tinospora cordifolia"),
    "गुडूची": ("Guduchi", "Tinospora cordifolia"),
    "गुग्गुलु": ("Guggulu", "Commiphora mukul"),
    "आंवला": ("Amla", "Phyllanthus emblica"),
    "हरीतकी": ("Haritaki", "Terminalia chebula"),
    "हरड़": ("Haritaki", "Terminalia chebula"),
    "बिभीतक": ("Bibhitaki", "Terminalia bellirica"),
    "बहेड़ा": ("Bibhitaki", "Terminalia bellirica"),
    "पिप्पली": ("Pippali", "Piper longum"),
    "काली मिर्च": ("Maricha", "Piper nigrum"),
    "मरिच": ("Maricha", "Piper nigrum"),
    "सोंठ": ("Shunthi", "Zingiber officinale"),
    "शुंठी": ("Shunthi", "Zingiber officinale"),

    # Kannada
    "ಅಶ್ವಗಂಧ": ("Ashwagandha", "Withania somnifera"),
    "ಅರಿಶಿನ": ("Turmeric", "Curcuma longa"),
    "ಬೇವು": ("Neem", "Azadirachta indica"),
    "ತುಳಸಿ": ("Tulsi", "Ocimum sanctum"),
    "ಗುಡುಚಿ": ("Guduchi", "Tinospora cordifolia"),
    "ಅಮೃತಬಳ್ಳಿ": ("Guduchi", "Tinospora cordifolia"),
    "ಗುಗ್ಗುಳು": ("Guggulu", "Commiphora mukul"),
    "ನೆಲ್ಲಿಕಾಯಿ": ("Amla", "Phyllanthus emblica"),
    "ಹರಿತಕಿ": ("Haritaki", "Terminalia chebula"),
    "ಅಳಲೆಕಾಯಿ": ("Haritaki", "Terminalia chebula"),
    "ಬಿಭೀತಕಿ": ("Bibhitaki", "Terminalia bellirica"),
    "ತಾರೇಕಾಯಿ": ("Bibhitaki", "Terminalia bellirica"),
    "ಹಿಪ್ಪಲಿ": ("Pippali", "Piper longum"),
    "ಕಾಳುಮೆಣಸು": ("Maricha", "Piper nigrum"),
    "ಒಣಶುಂಠಿ": ("Shunthi", "Zingiber officinale"),
    "ಶುಂಠಿ": ("Shunthi", "Zingiber officinale"),

    # English / Latin synonyms
    "ashwagandha": ("Ashwagandha", "Withania somnifera"),
    "turmeric": ("Turmeric", "Curcuma longa"),
    "curcuma longa": ("Turmeric", "Curcuma longa"),
    "withania somnifera": ("Ashwagandha", "Withania somnifera"),
    "guduchi": ("Guduchi", "Tinospora cordifolia"),
    "tinospora cordifolia": ("Guduchi", "Tinospora cordifolia"),
    "neem": ("Neem", "Azadirachta indica"),
    "tulsi": ("Tulsi", "Ocimum sanctum"),
    "guggulu": ("Guggulu", "Commiphora mukul"),
    "amla": ("Amla", "Phyllanthus emblica"),
}


# ---------------------------------------------------------------------------
# 3. Ayurvedic Formulation Types
# ---------------------------------------------------------------------------

FORMULATION_TYPES_MAP: Dict[str, str] = {
    # Hindi
    "चूर्ण": "Churna",
    "क्वाथ": "Kwatha",
    "कषाय": "Kashaya",
    "अरिष्ट": "Arishta",
    "आसव": "Asava",
    "वटी": "Vati",
    "तैल": "Taila",
    "घृत": "Ghrita",
    "अवलेह": "Avaleha",
    "भस्म": "Bhasma",
    "रसायन": "Rasayana",
    "लेप": "Lepa",

    # Kannada
    "ಚೂರ್ಣ": "Churna",
    "ಕ್ವಾಥ": "Kwatha",
    "ಕಷಾಯ": "Kashaya",
    "ಅರಿಷ್ಟ": "Arishta",
    "ಆಸವ": "Asava",
    "ವಟಿ": "Vati",
    "ತೈಲ": "Taila",
    "ಘೃತ": "Ghrita",
    "ಅವಲೇಹ": "Avaleha",
    "ಭಸ್ಮ": "Bhasma",
    "ರಸಾಯನ": "Rasayana",
    "ಲೇಪ": "Lepa",

    # English
    "churna": "Churna",
    "kwatha": "Kwatha",
    "kashaya": "Kashaya",
    "arishta": "Arishta",
    "asava": "Asava",
    "vati": "Vati",
    "taila": "Taila",
    "thailam": "Taila",
    "ghrita": "Ghrita",
    "avaleha": "Avaleha",
    "bhasma": "Bhasma",
    "rasayana": "Rasayana",
    "lepa": "Lepa",
}


# ---------------------------------------------------------------------------
# 4. Legal & Regulatory Concept Normalization
# ---------------------------------------------------------------------------

LEGAL_CONCEPTS_MAP: Dict[str, str] = {
    # Hindi
    "पेटेंट": "patent",
    "पेटेंट अधिनियम": "Patents Act",
    "भारतीय पेटेंट अधिनियम": "Indian Patents Act",
    "पारंपरिक ज्ञान": "traditional knowledge",
    "जैविक संसाधन": "biological resource",
    "जैव विविधता अधिनियम": "Biological Diversity Act",
    "जैविक विविधता अधिनियम": "Biological Diversity Act",
    "जैव विविधता": "biological diversity",
    "जैविक विविधता": "biological diversity",
    "लाभ साझाकरण": "benefit sharing",
    "पहुंच और लाभ साझाकरण": "access and benefit sharing",
    "राष्ट्रीय जैव विविधता प्राधिकरण": "National Biodiversity Authority",
    "पूर्व कला": "prior art",
    "शास्त्रीय फॉर्मूलेशन": "classical formulation",
    "शास्त्रोक्त औषधि": "classical ASU drug",
    "स्वामित्व औषधि": "patent or proprietary medicine",
    "औषधि अधिनियम": "Drugs and Cosmetics Act",
    "पेटेंट या प्रोप्राइटरी": "patent or proprietary",
    "भेषजसंहिता": "pharmacopoeia",
    "भारतीय आयुर्वेदिक भेषजसंहिता": "Ayurvedic Pharmacopoeia of India",
    "गुणवत्ता मानक": "quality standards",
    "भारी धातुएं": "heavy metals",
    "सूक्ष्मजीवी संदूषण": "microbial contamination",
    "लाइसेंसिंग": "licensing",
    "लाइसेंस": "license",
    "नागोया प्रोटोकॉल": "Nagoya Protocol",
    "ट्रीटी": "treaty",
    "संधि": "treaty",
    "अनुमोदन": "prior approval",
    "पूर्व अनुमोदन": "prior approval",
    "सहमति": "prior approval",
    "उल्लंघन": "infringement",
    "सहक्रियात्मक": "synergistic",
    "मिश्रण": "admixture",
    "मात्र मिश्रण": "mere admixture",
    "टीकेडीएल डेटाबेस खोजें": "search TKDL database in India",
    "टीकेडीएल": "TKDL India",
    "गोपनीय": "confidential",
    "खोजें": "search",

    # Kannada
    "ಪೇಟೆಂಟ್": "patent",
    "ಪೇಟೆಂಟ್ ಕಾಯ್ದೆ": "Patents Act",
    "ಭಾರತೀಯ ಪೇಟೆಂಟ್ ಕಾಯ್ದೆ": "Indian Patents Act",
    "ಸಾಂಪ್ರದಾಯಿಕ ಜ್ಞಾನ": "traditional knowledge",
    "ಜೈವಿಕ ಸಂಪನ್ಮೂಲ": "biological resource",
    "ಜೈವಿಕ ವೈವಿಧ್ಯತೆ": "biological diversity",
    "ಜೈವಿಕ ವೈವಿಧ್ಯತೆ ಕಾಯ್ದೆ": "Biological Diversity Act",
    "ಪ್ರಯೋಜನ ಹಂಚಿಕೆ": "benefit sharing",
    "ಪೂರ್ವ ಕಲೆ": "prior art",
    "ಶಾಸ್ತ್ರೀಯ ಸೂತ್ರೀಕರಣ": "classical formulation",
    "ಸ್ವಾಮ್ಯದ ಔಷಧಿ": "patent or proprietary medicine",
    "ಔಷಧ ಕಾಯ್ದೆ": "Drugs and Cosmetics Act",
    "ಔಷಧಿ ಕಾಯ್ದೆ": "Drugs and Cosmetics Act",
    "ಫಾರ್ಮಾಕೋಪಿಯಾ": "pharmacopoeia",
    "ಗುಣಮಟ್ಟದ ಮಾನದಂಡಗಳು": "quality standards",
    "ಭಾರ ಲೋಹಗಳು": "heavy metals",
    "ಪರವಾನಗಿ": "license",
    "ಪೂರ್ವ ಅನುಮೋದನೆ": "prior approval",
    "ಅನುಮೋದನೆ": "prior approval",
    "ನಾಗೋಯಾ ಪ್ರೋಟೋಕಾಲ್": "Nagoya Protocol",
    "ಒಪ್ಪಂದ": "treaty",
    "ರಾಷ್ಟ್ರೀಯ ಜೈವಿಕ ವೈವಿಧ್ಯ ಪ್ರಾಧಿಕಾರ": "National Biodiversity Authority",
    "ಮಿಶ್ರಣ": "admixture",
    "ಕೇವಲ ಮಿಶ್ರಣ": "mere admixture",
    "ಸಿನರ್ಜಿ": "synergy",
    "ಟಿಕೆಡಿಎಲ್ ಡೇಟಾಬೇಸ್ ಹುಡುಕಿ": "search TKDL database in India",
    "ಟಿಕೆಡಿಎಲ್": "TKDL India",
    "ಗೌಪ್ಯ": "confidential",
    "ಹುಡುಕಿ": "search",
}
