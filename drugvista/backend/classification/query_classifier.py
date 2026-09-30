"""
Query Classifier for IP-SAKTI Sahayak
Phase 2B.1 — Formulation & Query Classification + Jurisdiction Routing.

Orchestrates deterministic intent classification, topic categorization,
entity/botanical extraction, formulation classification, jurisdiction detection,
and evidence requirements derivation.
Follows strict rule: Structured Understanding, NOT Legal Conclusions.
"""
import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict

import config
from .vocabularies import QueryIntent, Topic, JurisdictionChoice, EntityType
from .entity_extractor import (
    Entity,
    normalize_query,
    entity_extractor,
    BOTANICAL_KNOWLEDGE_BASE,
    FORMULATION_SIGNALS
)
from .formulation_classifier import (
    FormulationClassification,
    formulation_classifier
)
from .jurisdiction_classifier import (
    JurisdictionClassification,
    jurisdiction_classifier
)

logger = logging.getLogger(__name__)


@dataclass
class QueryClassification:
    """Structured understanding of the user's query."""
    original_query: str
    normalized_query: str
    intent: str
    topics: List[str]
    formulation: FormulationClassification
    entities: List[Entity]
    jurisdiction: JurisdictionClassification
    confidence: float
    evidence_requirements: List[str]
    explanation: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_query": self.original_query,
            "normalized_query": self.normalized_query,
            "intent": self.intent,
            "topics": self.topics,
            "formulation": self.formulation.to_dict(),
            "entities": [e.to_dict() for e in self.entities],
            "jurisdiction": self.jurisdiction.to_dict(),
            "confidence": round(self.confidence, 4),
            "evidence_requirements": self.evidence_requirements,
            "explanation": self.explanation
        }


class QueryClassifier:
    """
    Deterministic query classifier transforming natural language inquiries
    into structured intent, topics, entities, formulation classification,
    and jurisdiction scoping.
    """

    def __init__(self, confidence_threshold: Optional[float] = None):
        self.threshold = confidence_threshold or config.CLASSIFIER_CONFIDENCE_THRESHOLD

        # Intent patterns (compiled regex)
        self.patentability_pattern = re.compile(
            r"\b(patent|patents|patented|patenting|patentable|patentability|patent\s+application|patents\s+act|section\s+3\s*\(p\)|section\s+3\s*\(d\)|section\s+3\s*\(e\)|prior\s+art|novelty|inventive\s+step|evergreening)\b",
            re.IGNORECASE
        )
        self.abs_pattern = re.compile(
            r"\b(access\s+and\s+benefit\s+sharing|abs|benefit\s+sharing|biological\s+diversity|biodiversity\s+act|bda\s+2002|bda\b|nba\s+approval|national\s+biodiversity\s+authority|state\s+biodiversity\s+board|sbb\b|section\s+6\b|form\s+1|form\s+i\b|fair\s+and\s+equitable|nagoya\s+protocol|commercial\s+utilization|access\s+to\s+genetic\s+resources|article\s+15\b|convention\s+on\s+biological\s+diversity|cbd)\b",
            re.IGNORECASE
        )
        self.pharmacopoeia_pattern = re.compile(
            r"\b(pharmacopoeia|pharmacopoeial|ayurvedic\s+pharmacopoeia|api\s+part|monograph|physicochemical|standards\s+apply|testing\s+standards|quality\s+standards|pcim&h|pcimh|thin\s+layer\s+chromatography|heavy\s+metals\s+limit|microbial\s+load)\b",
            re.IGNORECASE
        )
        self.compliance_pattern = re.compile(
            r"\b(manufacturing\s+license|licensing|licensed|licenses?|gmp|schedule\s+t|rule\s+161|labeling\s+requirements|regulatory\s+compliance|cdsco|drugs\s+and\s+cosmetics|clinical\s+trials?|clinical\s+trial\s+exemption|approval\s+for\s+sale|ayush\s+license)\b",
            re.IGNORECASE
        )
        self.international_ip_pattern = re.compile(
            r"\b(wipo|wipo\s+gratk|gratk\s+treaty|gratk|mandatory\s+disclosure|mandatory\s+patent\s+disclosure|patent\s+cooperation\s+treaty|pct|foreign\s+patent|international\s+application|international\s+treaty|trips\s+agreement)\b",
            re.IGNORECASE
        )
        self.traditional_knowledge_pattern = re.compile(
            r"\b(traditional\s+knowledge|tkdl|shastric\s+text|classical\s+text|traditional\s+use|ancient\s+texts|documented\s+in\s+ayurveda|indigenous\s+knowledge)\b",
            re.IGNORECASE
        )
        self.formulation_classification_pattern = re.compile(
            r"\b(is\s+this\s+classical\s+or\s+proprietary|difference\s+between\s+classical\s+and\s+proprietary|how\s+to\s+classify\s+this\s+formulation|classify\s+this\s+formulation|classical\s+vs\s+proprietary)\b",
            re.IGNORECASE
        )
        self.source_lookup_pattern = re.compile(
            r"\b(what\s+does\s+(section|article|rule)\s+\w+\s+say|show\s+me\s+the\s+text\s+of|read\s+(section|article)|lookup\s+(section|article))\b",
            re.IGNORECASE
        )

        # Ambiguous / negative signals (queries devoid of IP/Ayush context)
        self.negative_patterns = re.compile(
            r"^(what\s+do\s+you\s+think(\s+about\s+this)?\??|tell\s+me\s+something\s+interesting\.?|is\s+this\s+good\??|hello(\s+there)?|hi|how\s+are\s+you\??|who\s+are\s+you\??)$",
            re.IGNORECASE
        )

    def classify(self, query: str) -> QueryClassification:
        """
        Classifies user query into structured intent, topics, entities,
        formulation classification, and jurisdiction.
        """
        orig_query = query.strip()
        norm_query = normalize_query(orig_query)
        explanations: List[str] = []

        # 1. Entity and signal extraction
        entities, entity_explanations = entity_extractor.extract_entities(orig_query)
        explanations.extend(entity_explanations)

        # 2. Formulation classification
        formulation = formulation_classifier.classify(orig_query, entities)
        explanations.extend(formulation.explanation)

        # 3. Jurisdiction classification
        jurisdiction = jurisdiction_classifier.classify(orig_query)
        explanations.extend(jurisdiction.explanation)

        # 4. Check negative / non-domain queries
        if self.negative_patterns.match(norm_query) or (len(norm_query) < 10 and not entities and not formulation.detected):
            return QueryClassification(
                original_query=orig_query,
                normalized_query=norm_query,
                intent=QueryIntent.UNKNOWN.value,
                topics=[Topic.UNKNOWN.value],
                formulation=formulation,
                entities=entities,
                jurisdiction=jurisdiction,
                confidence=0.10,
                evidence_requirements=[],
                explanation=["Query does not contain recognized IP, Ayush, regulatory, or botanical keywords."]
            )

        # 5. Intent and Topic Classification
        intent = QueryIntent.UNKNOWN.value
        topics: List[str] = []
        confidence = 0.50
        evidence_reqs: List[str] = []

        # Priority 1: Formulation Classification inquiry
        if self.formulation_classification_pattern.search(norm_query):
            intent = QueryIntent.FORMULATION_CLASSIFICATION.value
            topics.extend([Topic.AYURVEDA_REGULATION.value, Topic.FORMULARY.value, Topic.ASU_MEDICINE.value])
            evidence_reqs.extend([Topic.AYURVEDA_REGULATION.value, Topic.FORMULARY.value])
            confidence = 0.95
            explanations.append("Detected explicit request to classify formulation category.")

        # Priority 2: Source Lookup
        elif self.source_lookup_pattern.search(norm_query):
            intent = QueryIntent.SOURCE_LOOKUP.value
            confidence = 0.92
            if "article" in norm_query or jurisdiction.primary == JurisdictionChoice.INTERNATIONAL.value:
                topics.extend([Topic.INTERNATIONAL_TREATY.value])
                evidence_reqs.append(Topic.INTERNATIONAL_TREATY.value)
            else:
                topics.extend([Topic.PATENT_LAW.value, Topic.AYURVEDA_REGULATION.value])
                evidence_reqs.append(Topic.PATENT_LAW.value)
            explanations.append("Detected statutory/treaty provision citation lookup.")

        # Priority 3: Access and Benefit Sharing (ABS) & Biodiversity
        elif self.abs_pattern.search(norm_query):
            intent = QueryIntent.ABS.value
            topics.extend([Topic.ABS.value, Topic.BIOLOGICAL_RESOURCES.value])
            evidence_reqs.extend([Topic.ABS.value, Topic.BIOLOGICAL_RESOURCES.value])
            confidence = 0.95

            if jurisdiction.primary == JurisdictionChoice.INTERNATIONAL.value or jurisdiction.mixed:
                topics.append(Topic.INTERNATIONAL_TREATY.value)
                topics.append(Topic.GENETIC_RESOURCES.value)
                evidence_reqs.append(Topic.INTERNATIONAL_TREATY.value)

            explanations.append("Detected Access and Benefit Sharing (ABS) / Biodiversity regulatory inquiry.")

        # Priority 4: Explicit Patentability / Patents Act inquiries
        elif self.patentability_pattern.search(norm_query) and any(kw in norm_query for kw in ["section 3", "patentable", "patenting", "patents act", "patentability"]):
            intent = QueryIntent.PATENTABILITY.value
            topics.append(Topic.PATENT_LAW.value)
            evidence_reqs.append(Topic.PATENT_LAW.value)
            confidence = 0.94

            if self.traditional_knowledge_pattern.search(norm_query) or formulation.detected:
                topics.append(Topic.TRADITIONAL_KNOWLEDGE.value)
                evidence_reqs.append(Topic.TRADITIONAL_KNOWLEDGE.value)

            if jurisdiction.primary == JurisdictionChoice.INTERNATIONAL.value or jurisdiction.mixed:
                topics.append(Topic.INTERNATIONAL_TREATY.value)

            explanations.append("Detected patentability / patent law inquiry.")

        # Priority 5: International IP Treaties (WIPO, GRATK, PCT)
        elif self.international_ip_pattern.search(norm_query):
            intent = QueryIntent.INTERNATIONAL_IP.value
            topics.extend([Topic.INTERNATIONAL_TREATY.value, Topic.PATENT_LAW.value])
            evidence_reqs.extend([Topic.INTERNATIONAL_TREATY.value, Topic.PATENT_LAW.value])
            confidence = 0.92
            explanations.append("Detected multilateral / international IP treaty inquiry.")

        # Priority 5: Pharmacopoeia & Testing Standards
        elif self.pharmacopoeia_pattern.search(norm_query):
            intent = QueryIntent.PHARMACOPOEIA.value
            topics.extend([Topic.PHARMACOPOEIA.value, Topic.AYURVEDA_REGULATION.value, Topic.ASU_MEDICINE.value])
            evidence_reqs.extend([Topic.PHARMACOPOEIA.value, Topic.ASU_MEDICINE.value])
            confidence = 0.94
            explanations.append("Detected Pharmacopoeia / ASU quality standards inquiry.")

        # Priority 6: Regulatory Compliance / Licensing
        elif self.compliance_pattern.search(norm_query):
            intent = QueryIntent.REGULATORY_COMPLIANCE.value
            topics.extend([Topic.AYURVEDA_REGULATION.value, Topic.LICENSING.value])
            evidence_reqs.extend([Topic.AYURVEDA_REGULATION.value, Topic.LICENSING.value])
            if "gmp" in norm_query or "schedule t" in norm_query:
                topics.append(Topic.GMP.value)
            confidence = 0.92
            explanations.append("Detected ASU manufacturing licensing / regulatory compliance inquiry.")

        # Priority 7: Patentability & Patent Law
        elif self.patentability_pattern.search(norm_query):
            intent = QueryIntent.PATENTABILITY.value
            topics.append(Topic.PATENT_LAW.value)
            evidence_reqs.append(Topic.PATENT_LAW.value)
            confidence = 0.94

            if self.traditional_knowledge_pattern.search(norm_query) or formulation.detected:
                topics.append(Topic.TRADITIONAL_KNOWLEDGE.value)
                evidence_reqs.append(Topic.TRADITIONAL_KNOWLEDGE.value)

            if jurisdiction.primary == JurisdictionChoice.INTERNATIONAL.value or jurisdiction.mixed:
                topics.append(Topic.INTERNATIONAL_TREATY.value)

            explanations.append("Detected patentability / patent law inquiry.")

        # Priority 8: Traditional Knowledge & TKDL
        elif self.traditional_knowledge_pattern.search(norm_query):
            intent = QueryIntent.TRADITIONAL_KNOWLEDGE.value
            topics.extend([Topic.TRADITIONAL_KNOWLEDGE.value, Topic.ASU_MEDICINE.value])
            evidence_reqs.append(Topic.TRADITIONAL_KNOWLEDGE.value)
            confidence = 0.90
            explanations.append("Detected Traditional Knowledge / TKDL inquiry.")

        # Priority 9: Formulation Information
        elif formulation.detected:
            intent = QueryIntent.FORMULATION_INFORMATION.value
            topics.extend([Topic.ASU_MEDICINE.value, Topic.FORMULARY.value])
            evidence_reqs.append(Topic.FORMULARY.value)
            confidence = 0.85
            explanations.append("Detected Ayurvedic formulation inquiry without specific patent or licensing question.")

        # Priority 10: General Information fallback
        elif any(e.entity_type in {EntityType.STATUTE.value, EntityType.REGULATORY_BODY.value} for e in entities):
            intent = QueryIntent.GENERAL_INFORMATION.value
            topics.append(Topic.AYURVEDA_REGULATION.value)
            evidence_reqs.append(Topic.AYURVEDA_REGULATION.value)
            confidence = 0.70
            explanations.append("Detected general legal/statutory inquiry.")

        else:
            intent = QueryIntent.UNKNOWN.value
            topics.append(Topic.UNKNOWN.value)
            confidence = 0.20
            explanations.append("Query lacks identifiable intent under controlled IP/Ayush taxonomy.")

        # Enforce threshold
        if confidence < self.threshold:
            intent = QueryIntent.UNKNOWN.value
            if not topics or topics == [Topic.UNKNOWN.value]:
                topics = [Topic.UNKNOWN.value]

        # De-duplicate topics and evidence requirements
        unique_topics = []
        for t in topics:
            if t not in unique_topics:
                unique_topics.append(t)

        unique_evidence_reqs = []
        for er in evidence_reqs:
            if er not in unique_evidence_reqs:
                unique_evidence_reqs.append(er)

        logger.debug(
            f"Classified query: '{orig_query[:40]}' -> Intent: {intent}, "
            f"Topics: {unique_topics}, Jur: {jurisdiction.primary}, Conf: {confidence:.2f}"
        )

        return QueryClassification(
            original_query=orig_query,
            normalized_query=norm_query,
            intent=intent,
            topics=unique_topics,
            formulation=formulation,
            entities=entities,
            jurisdiction=jurisdiction,
            confidence=confidence,
            evidence_requirements=unique_evidence_reqs,
            explanation=explanations
        )


# Singleton classifier
query_classifier = QueryClassifier()
