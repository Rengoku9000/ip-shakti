"""
Entity and Formulation Signal Extractor for IP-SAKTI Sahayak
Phase 2B.1 — Formulation & Query Classification + Jurisdiction Routing.

Extracts candidate botanical ingredients, formulation dosage forms/signals,
regulatory bodies, statutes, and treaties from normalized user queries.
Follows zero-hallucination normalization strictly based on authoritative pharmacopoeial reference.
"""
import re
import unicodedata
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict

from .vocabularies import EntityType


@dataclass
class Entity:
    """Structured representation of an extracted entity or ingredient."""
    name: str
    normalized_name: Optional[str] = None
    entity_type: str = EntityType.GENERAL.value
    confidence: float = 1.0
    source: str = "USER_QUERY"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Authoritative botanical mapping (common/Ayurvedic names to accepted botanical binomials)
# Based on the Ayurvedic Pharmacopoeia of India (API) Part I & ASU standards.
# Unmapped ingredients will retain normalized_name=None to prevent hallucination.
BOTANICAL_KNOWLEDGE_BASE: Dict[str, str] = {
    # Common / Sanskrit / Hindi names -> Accepted botanical scientific name
    "ashwagandha": "Withania somnifera",
    "asgandh": "Withania somnifera",
    "withania somnifera": "Withania somnifera",
    "turmeric": "Curcuma longa",
    "haldi": "Curcuma longa",
    "haridra": "Curcuma longa",
    "curcuma longa": "Curcuma longa",
    "neem": "Azadirachta indica",
    "nimba": "Azadirachta indica",
    "azadirachta indica": "Azadirachta indica",
    "tulsi": "Ocimum sanctum",
    "holy basil": "Ocimum sanctum",
    "ocimum sanctum": "Ocimum sanctum",
    "ocimum tenuiflorum": "Ocimum sanctum",
    "amla": "Phyllanthus emblica",
    "amalaki": "Phyllanthus emblica",
    "indian gooseberry": "Phyllanthus emblica",
    "phyllanthus emblica": "Phyllanthus emblica",
    "emblica officinalis": "Phyllanthus emblica",
    "brahmi": "Bacopa monnieri",
    "bacopa monnieri": "Bacopa monnieri",
    "guggulu": "Commiphora wightii",
    "guggul": "Commiphora wightii",
    "commiphora wightii": "Commiphora wightii",
    "commiphora mukul": "Commiphora wightii",
    "shatavari": "Asparagus racemosus",
    "asparagus racemosus": "Asparagus racemosus",
    "ginger": "Zingiber officinale",
    "shunthi": "Zingiber officinale",
    "adrak": "Zingiber officinale",
    "zingiber officinale": "Zingiber officinale",
    "pippali": "Piper longum",
    "long pepper": "Piper longum",
    "piper longum": "Piper longum",
    "maricha": "Piper nigrum",
    "black pepper": "Piper nigrum",
    "piper nigrum": "Piper nigrum",
    "haritaki": "Terminalia chebula",
    "terminalia chebula": "Terminalia chebula",
    "bibhitaki": "Terminalia bellirica",
    "baheda": "Terminalia bellirica",
    "terminalia bellirica": "Terminalia bellirica",
    "giloy": "Tinospora cordifolia",
    "guduchi": "Tinospora cordifolia",
    "tinospora cordifolia": "Tinospora cordifolia",
    "sarpagandha": "Rauvolfia serpentina",
    "rauvolfia serpentina": "Rauvolfia serpentina",
    "arjuna": "Terminalia arjuna",
    "terminalia arjuna": "Terminalia arjuna",
    "vasa": "Justicia adhatoda",
    "vasaka": "Justicia adhatoda",
    "adhatoda vasica": "Justicia adhatoda",
    "licorice": "Glycyrrhiza glabra",
    "liquorice": "Glycyrrhiza glabra",
    "mulethi": "Glycyrrhiza glabra",
    "yashtimadhu": "Glycyrrhiza glabra",
    "glycyrrhiza glabra": "Glycyrrhiza glabra",
    "kumari": "Aloe barbadensis",
    "aloe vera": "Aloe barbadensis",
    "aloe barbadensis": "Aloe barbadensis",
    "kalmegh": "Andrographis paniculata",
    "andrographis paniculata": "Andrographis paniculata",
    "manjistha": "Rubia cordifolia",
    "rubia cordifolia": "Rubia cordifolia",
    "kutki": "Picrorhiza kurroa",
    "picrorhiza kurroa": "Picrorhiza kurroa",
    "punarnava": "Boerhavia diffusa",
    "boerhavia diffusa": "Boerhavia diffusa",
    "shankhpushpi": "Convolvulus pluricaulis",
    "convolvulus pluricaulis": "Convolvulus pluricaulis",
    "jatamansi": "Nardostachys jatamansi",
    "nardostachys jatamansi": "Nardostachys jatamansi",
    "vacha": "Acorus calamus",
    "acorus calamus": "Acorus calamus",
    "triphala": "Triphala formulation",
    "trikatu": "Trikatu formulation",
    "chyawanprash": "Chyawanprash formulation",
}

# Formulation signals: Classical forms and modern delivery forms
FORMULATION_SIGNALS: Dict[str, Dict[str, str]] = {
    # Classical ASU dosage forms
    "churna": {"type": "POWDER", "tradition": "CLASSICAL"},
    "churnas": {"type": "POWDER", "tradition": "CLASSICAL"},
    "choorna": {"type": "POWDER", "tradition": "CLASSICAL"},
    "choornas": {"type": "POWDER", "tradition": "CLASSICAL"},
    "kwatha": {"type": "DECOCTION", "tradition": "CLASSICAL"},
    "kwathas": {"type": "DECOCTION", "tradition": "CLASSICAL"},
    "kashaya": {"type": "DECOCTION", "tradition": "CLASSICAL"},
    "kashayas": {"type": "DECOCTION", "tradition": "CLASSICAL"},
    "arishta": {"type": "FERMENTED", "tradition": "CLASSICAL"},
    "arishtas": {"type": "FERMENTED", "tradition": "CLASSICAL"},
    "asava": {"type": "FERMENTED", "tradition": "CLASSICAL"},
    "asavas": {"type": "FERMENTED", "tradition": "CLASSICAL"},
    "vati": {"type": "TABLET_PILL", "tradition": "CLASSICAL"},
    "vatis": {"type": "TABLET_PILL", "tradition": "CLASSICAL"},
    "gutika": {"type": "TABLET_PILL", "tradition": "CLASSICAL"},
    "gutikas": {"type": "TABLET_PILL", "tradition": "CLASSICAL"},
    "taila": {"type": "MEDICATED_OIL", "tradition": "CLASSICAL"},
    "tailas": {"type": "MEDICATED_OIL", "tradition": "CLASSICAL"},
    "thailam": {"type": "MEDICATED_OIL", "tradition": "CLASSICAL"},
    "ghrita": {"type": "MEDICATED_GHEE", "tradition": "CLASSICAL"},
    "ghritas": {"type": "MEDICATED_GHEE", "tradition": "CLASSICAL"},
    "ghritam": {"type": "MEDICATED_GHEE", "tradition": "CLASSICAL"},
    "avaleha": {"type": "CONFECTION", "tradition": "CLASSICAL"},
    "avalehas": {"type": "CONFECTION", "tradition": "CLASSICAL"},
    "rasayana": {"type": "REJUVENATOR", "tradition": "CLASSICAL"},
    "rasayanas": {"type": "REJUVENATOR", "tradition": "CLASSICAL"},
    "bhasma": {"type": "CALCINED_ASH", "tradition": "CLASSICAL"},
    "bhasmas": {"type": "CALCINED_ASH", "tradition": "CLASSICAL"},
    "lepa": {"type": "PASTE", "tradition": "CLASSICAL"},
    "lepas": {"type": "PASTE", "tradition": "CLASSICAL"},
    "sattva": {"type": "EXTRACT_SEDIMENT", "tradition": "CLASSICAL"},
    "sattvam": {"type": "EXTRACT_SEDIMENT", "tradition": "CLASSICAL"},
    # Modern / conventional dosage forms
    "tablet": {"type": "TABLET", "tradition": "MODERN"},
    "tablets": {"type": "TABLET", "tradition": "MODERN"},
    "capsule": {"type": "CAPSULE", "tradition": "MODERN"},
    "capsules": {"type": "CAPSULE", "tradition": "MODERN"},
    "extract": {"type": "EXTRACT", "tradition": "MODERN"},
    "extracts": {"type": "EXTRACT", "tradition": "MODERN"},
    "decoction": {"type": "DECOCTION", "tradition": "GENERAL"},
    "decoctions": {"type": "DECOCTION", "tradition": "GENERAL"},
    "powder": {"type": "POWDER", "tradition": "GENERAL"},
    "powders": {"type": "POWDER", "tradition": "GENERAL"},
    "oil": {"type": "OIL", "tradition": "GENERAL"},
    "oils": {"type": "OIL", "tradition": "GENERAL"},
    "syrup": {"type": "SYRUP", "tradition": "MODERN"},
    "granules": {"type": "GRANULES", "tradition": "MODERN"},
    "ointment": {"type": "OINTMENT", "tradition": "MODERN"},
}

# Regulatory bodies and statutes
KNOWN_STATUTES = {
    "patents act": "Patents Act, 1970",
    "indian patent act": "Patents Act, 1970",
    "drugs and cosmetics act": "Drugs and Cosmetics Act, 1940",
    "drugs & cosmetics act": "Drugs and Cosmetics Act, 1940",
    "biological diversity act": "Biological Diversity Act, 2002",
    "bda 2002": "Biological Diversity Act, 2002",
    "biodiversity act": "Biological Diversity Act, 2002",
    "nagoya protocol": "Nagoya Protocol on Access and Benefit Sharing",
    "wipo gratk treaty": "WIPO GRATK Treaty, 2024",
    "gratk treaty": "WIPO GRATK Treaty, 2024",
    "treaty on intellectual property, genetic resources and associated traditional knowledge": "WIPO GRATK Treaty, 2024",
    "patent cooperation treaty": "Patent Cooperation Treaty (PCT)",
    "pct": "Patent Cooperation Treaty (PCT)",
    "convention on biological diversity": "Convention on Biological Diversity (CBD)",
    "cbd": "Convention on Biological Diversity (CBD)",
}

KNOWN_BODIES = {
    "national biodiversity authority": "National Biodiversity Authority (NBA)",
    "nba": "National Biodiversity Authority (NBA)",
    "state biodiversity board": "State Biodiversity Board (SBB)",
    "sbb": "State Biodiversity Board (SBB)",
    "ministry of ayush": "Ministry of Ayush",
    "ayush ministry": "Ministry of Ayush",
    "ayush": "Ministry of Ayush",
    "ip india": "Office of the Controller General of Patents, Designs and Trade Marks (IP India)",
    "patent office": "Indian Patent Office",
    "tkdl": "Traditional Knowledge Digital Library (TKDL)",
    "pcimh": "Pharmacopoeia Commission for Indian Medicine and Homoeopathy (PCIM&H)",
    "wipo": "World Intellectual Property Organization (WIPO)",
    "cdsco": "Central Drugs Standard Control Organisation (CDSCO)",
}


def normalize_query(query: str) -> str:
    """
    Standardize text: Unicode NFKC normalization, lowercase, punctuation spacing,
    and single whitespace collapse. Preserves original query unmodified separately.
    """
    if not query:
        return ""
    # Unicode normalize
    text = unicodedata.normalize("NFKC", query)
    # Lowercase
    text = text.lower()
    # Normalize punctuation and hyphens
    text = re.sub(r"[\u2010\u2011\u2012\u2013\u2014\u2015\-]", " ", text)
    # Remove special punctuation but keep basic alphanumeric and whitespace
    text = re.sub(r"[^\w\s\.\,\/]", " ", text)
    # Collapse multiple whitespaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


class EntityExtractor:
    """
    Deterministic rule-based extractor for botanicals, formulation signals,
    statutes, and regulatory bodies.
    """

    def __init__(self):
        # Precompile regex matchers sorted by length descending to catch multi-word phrases first
        self._botanical_patterns = [
            (name, re.compile(rf"\b{re.escape(name)}\b", re.IGNORECASE))
            for name in sorted(BOTANICAL_KNOWLEDGE_BASE.keys(), key=len, reverse=True)
        ]
        self._signal_patterns = [
            (name, re.compile(rf"\b{re.escape(name)}\b", re.IGNORECASE))
            for name in sorted(FORMULATION_SIGNALS.keys(), key=len, reverse=True)
        ]
        self._statute_patterns = [
            (name, re.compile(rf"\b{re.escape(name)}\b", re.IGNORECASE))
            for name in sorted(KNOWN_STATUTES.keys(), key=len, reverse=True)
        ]
        self._body_patterns = [
            (name, re.compile(rf"\b{re.escape(name)}\b", re.IGNORECASE))
            for name in sorted(KNOWN_BODIES.keys(), key=len, reverse=True)
        ]

    def extract_entities(self, query: str) -> Tuple[List[Entity], List[str]]:
        """
        Extract all recognized entities and signals from a query.
        Returns a tuple of (entities, explanations).
        """
        norm_query = normalize_query(query)
        entities: List[Entity] = []
        explanations: List[str] = []
        seen_keys = set()

        # 1. Extract botanicals
        for name, pattern in self._botanical_patterns:
            if pattern.search(norm_query):
                canonical = BOTANICAL_KNOWLEDGE_BASE[name]
                # Avoid duplicates if both common and latin name matched
                key = f"BOTANICAL_{canonical}"
                if key not in seen_keys:
                    seen_keys.add(key)
                    # Capitalize display name
                    disp_name = name.title() if len(name) > 3 else name.upper()
                    entities.append(
                        Entity(
                            name=disp_name,
                            normalized_name=canonical,
                            entity_type=EntityType.BOTANICAL.value,
                            confidence=0.95,
                            source="USER_QUERY"
                        )
                    )
                    explanations.append(f"Detected botanical ingredient '{disp_name}' (normalized: {canonical})")

        # 2. Extract formulation dosage form signals
        for sig, pattern in self._signal_patterns:
            if pattern.search(norm_query):
                key = f"SIGNAL_{sig}"
                if key not in seen_keys:
                    seen_keys.add(key)
                    meta = FORMULATION_SIGNALS[sig]
                    entities.append(
                        Entity(
                            name=sig.lower(),
                            normalized_name=meta["type"],
                            entity_type=EntityType.FORMULATION_FORM.value,
                            confidence=0.90,
                            source="USER_QUERY"
                        )
                    )
                    explanations.append(f"Detected formulation signal '{sig}' ({meta['tradition']} {meta['type']})")

        # 3. Extract statutes
        for stat, pattern in self._statute_patterns:
            if pattern.search(norm_query):
                official = KNOWN_STATUTES[stat]
                key = f"STATUTE_{official}"
                if key not in seen_keys:
                    seen_keys.add(key)
                    entities.append(
                        Entity(
                            name=stat.title(),
                            normalized_name=official,
                            entity_type=EntityType.STATUTE.value,
                            confidence=0.98,
                            source="USER_QUERY"
                        )
                    )
                    explanations.append(f"Detected statute/treaty reference '{official}'")

        # 4. Extract regulatory bodies
        for body, pattern in self._body_patterns:
            if pattern.search(norm_query):
                official_body = KNOWN_BODIES[body]
                key = f"BODY_{official_body}"
                if key not in seen_keys:
                    seen_keys.add(key)
                    entities.append(
                        Entity(
                            name=body.upper() if len(body) <= 5 else body.title(),
                            normalized_name=official_body,
                            entity_type=EntityType.REGULATORY_BODY.value,
                            confidence=0.95,
                            source="USER_QUERY"
                        )
                    )
                    explanations.append(f"Detected authority/body '{official_body}'")

        return entities, explanations


# Singleton extractor
entity_extractor = EntityExtractor()
