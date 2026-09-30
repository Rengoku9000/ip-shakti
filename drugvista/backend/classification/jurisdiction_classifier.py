"""
Jurisdiction Classifier for IP-SAKTI Sahayak
Phase 2B.1 — Formulation & Query Classification + Jurisdiction Routing.

Strictly identifies applicable legal jurisdictions: INDIA vs INTERNATIONAL vs UNSPECIFIED.
Explicitly detects mixed-jurisdiction queries (e.g., comparative analyses) to enable
dual-track evidence routing while ensuring 0% cross-jurisdiction leakage.
Never defaults unspecified queries to Indian law.
"""
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict

import config
from .vocabularies import JurisdictionChoice
from .entity_extractor import normalize_query


@dataclass
class JurisdictionClassification:
    """Structured representation of detected legal jurisdiction(s)."""
    primary: str = JurisdictionChoice.UNSPECIFIED.value
    secondary: Optional[str] = None
    mixed: bool = False
    confidence: float = 0.0
    signals: List[str] = field(default_factory=list)
    explanation: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class JurisdictionClassifier:
    """
    Deterministic rule-based jurisdiction classifier.
    Matches authoritative domestic signals against multilateral/international signals.
    """

    def __init__(self, confidence_threshold: Optional[float] = None):
        self.threshold = confidence_threshold or config.JURISDICTION_CONFIDENCE_THRESHOLD

        # India-specific signals (statutes, bodies, provisions, terms)
        self.india_patterns = [
            ("india", re.compile(r"\b(india|indian|in\s+india|under\s+indian\s+law)\b", re.IGNORECASE)),
            ("indian_statutes", re.compile(
                r"\b(patents\s+act|drugs\s+and\s+cosmetics(\s+(act|rules))?|drugs\s+&\s+cosmetics(\s+(act|rules))?|biological\s+diversity\s+act|bda\s+2002|bda\b|patent\s+rules|schedule\s+t|schedule\s+i\b|rule\s+158\s*[\-\w]*|rule\s+161)\b",
                re.IGNORECASE
            )),
            ("indian_authorities", re.compile(
                r"\b(ministry\s+of\s+ayush|ayush|ip\s+india|patent\s+office|controller\s+general|nba|national\s+biodiversity\s+authority|sbb|state\s+biodiversity\s+board|pcim&h|pcimh|cdsco|tkdl)\b",
                re.IGNORECASE
            )),
            ("indian_legal_sections", re.compile(
                r"\b(section\s+3\s*\(p\)|section\s+3\s*\(d\)|section\s+3\s*\(e\)|section\s+6\b|rule\s+161|form\s+1|form\s+i|form\s+3)\b",
                re.IGNORECASE
            )),
            ("indian_pharmacopoeia", re.compile(
                r"\b(ayurvedic\s+pharmacopoeia\s+of\s+india|api\s+part|ayurvedic\s+formulary\s+of\s+india|afi)\b",
                re.IGNORECASE
            )),
        ]

        # International-specific signals (treaties, conventions, global bodies, foreign contexts)
        self.international_patterns = [
            ("international_general", re.compile(
                r"\b(international|globally|foreign|cross\s+border|worldwide|overseas|foreign\s+patent)\b",
                re.IGNORECASE
            )),
            ("treaties", re.compile(
                r"\b(nagoya\s+protocol|wipo\s+gratk\s+treaty|gratk\s+treaty|convention\s+on\s+biological\s+diversity|cbd|patent\s+cooperation\s+treaty|pct|trips\s+agreement|trips|wto)\b",
                re.IGNORECASE
            )),
            ("international_bodies", re.compile(
                r"\b(wipo|world\s+intellectual\s+property\s+organization|cop\s+mop|unep|who|uspto|epo)\b",
                re.IGNORECASE
            )),
            ("treaty_articles", re.compile(
                r"\b(article\s+5\b|article\s+6\b|article\s+15\b|article\s+16\b|article\s+17\b|mandatory\s+disclosure\s+requirement)\b",
                re.IGNORECASE
            )),
        ]

        # Explicit comparison signals
        self.comparison_patterns = re.compile(
            r"\b(compare|comparison|versus|vs\.?|difference\s+between|how\s+does.+differ\s+from|aligned\s+with|compliant\s+with\s+both)\b",
            re.IGNORECASE
        )

    def classify(self, query: str) -> JurisdictionClassification:
        """
        Classifies the jurisdiction of the query into INDIA, INTERNATIONAL,
        a MIXED dual-track, or UNSPECIFIED.
        """
        norm_query = normalize_query(query)
        india_signals: List[str] = []
        intl_signals: List[str] = []

        # 1. Detect India signals
        for label, pat in self.india_patterns:
            matches = pat.findall(norm_query)
            if matches:
                # Store matched terms
                match_strs = [m if isinstance(m, str) else m[0] for m in matches]
                india_signals.extend(match_strs)

        # 2. Detect International signals
        for label, pat in self.international_patterns:
            matches = pat.findall(norm_query)
            if matches:
                match_strs = [m if isinstance(m, str) else m[0] for m in matches]
                intl_signals.extend(match_strs)

        # De-duplicate signals
        india_signals = sorted(list(set(s.strip() for s in india_signals if s.strip())))
        intl_signals = sorted(list(set(s.strip() for s in intl_signals if s.strip())))

        has_india = len(india_signals) > 0
        has_intl = len(intl_signals) > 0
        is_comparative = bool(self.comparison_patterns.search(norm_query))

        # Case 1: Mixed Jurisdiction (Both Indian and International signals detected)
        if has_india and has_intl:
            explanations = [
                f"Detected Indian jurisdiction signals: {', '.join(india_signals)}.",
                f"Detected International jurisdiction signals: {', '.join(intl_signals)}.",
                "Query involves both domestic Indian law and international regimes; requires dual evidence tracks."
            ]
            return JurisdictionClassification(
                primary=JurisdictionChoice.INDIA.value,
                secondary=JurisdictionChoice.INTERNATIONAL.value,
                mixed=True,
                confidence=0.94,
                signals=india_signals + intl_signals,
                explanation=explanations
            )

        # Case 2: India-exclusive
        if has_india and not has_intl:
            explanations = [
                f"Detected Indian jurisdiction signals: {', '.join(india_signals)}.",
                "Retaining strict India-only legal scope."
            ]
            return JurisdictionClassification(
                primary=JurisdictionChoice.INDIA.value,
                secondary=None,
                mixed=False,
                confidence=0.95,
                signals=india_signals,
                explanation=explanations
            )

        # Case 3: International-exclusive
        if has_intl and not has_india:
            explanations = [
                f"Detected International jurisdiction signals: {', '.join(intl_signals)}.",
                "Retaining strict International-only legal scope."
            ]
            return JurisdictionClassification(
                primary=JurisdictionChoice.INTERNATIONAL.value,
                secondary=None,
                mixed=False,
                confidence=0.95,
                signals=intl_signals,
                explanation=explanations
            )

        # Case 4: Unspecified Jurisdiction
        # Never silently assume Indian law. Low confidence signals need clarification.
        explanations = [
            "No explicit jurisdiction signals detected in user query.",
            "Jurisdiction remains UNSPECIFIED; do not default to Indian or International law."
        ]
        return JurisdictionClassification(
            primary=JurisdictionChoice.UNSPECIFIED.value,
            secondary=None,
            mixed=False,
            confidence=0.20,
            signals=[],
            explanation=explanations
        )


# Singleton classifier
jurisdiction_classifier = JurisdictionClassifier()
