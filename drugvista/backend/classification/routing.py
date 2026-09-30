"""
Retrieval Routing Engine for IP-SAKTI Sahayak
Phase 2B.1 — Formulation & Query Classification + Jurisdiction Routing.

Generates structured retrieval routing plans from query classifications.
Maps intents and topics to preferred source types, authority levels, and jurisdictions.
Generates isolated dual evidence tracks for mixed queries to guarantee 0% leakage.
Identifies unspecified queries requiring clarification without assuming India.
Executes retrieval directly over the existing FAISS + SQLite knowledge layer.
"""
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict

from models import RetrievedChunk, SourceType, AuthorityLevel, Jurisdiction
from .vocabularies import QueryIntent, Topic, JurisdictionChoice
from .query_classifier import QueryClassification

logger = logging.getLogger(__name__)


@dataclass
class EvidenceTrack:
    """A distinct retrieval execution track scoped to a specific jurisdiction and source set."""
    track_name: str
    jurisdiction: str
    source_types: List[str]
    authority_levels: List[str]
    topics: List[str]
    query_text: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RetrievalRoutingPlan:
    """Complete retrieval routing plan specifying evidence tracks and filtering parameters."""
    tracks: List[EvidenceTrack]
    jurisdictions: List[str]
    source_types: List[str]
    authority_levels: List[str]
    topics: List[str]
    requires_clarification: bool = False
    clarification_reason: Optional[str] = None
    explanation: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tracks": [t.to_dict() for t in self.tracks],
            "jurisdictions": self.jurisdictions,
            "source_types": self.source_types,
            "authority_levels": self.authority_levels,
            "topics": self.topics,
            "requires_clarification": self.requires_clarification,
            "clarification_reason": self.clarification_reason,
            "explanation": self.explanation
        }


# Source type preferences by intent
INTENT_SOURCE_TYPE_MAP: Dict[str, List[str]] = {
    QueryIntent.PATENTABILITY.value: [
        SourceType.STATUTE.value,
        SourceType.REGULATION.value,
        SourceType.OFFICIAL_GUIDANCE.value,
    ],
    QueryIntent.REGULATORY_COMPLIANCE.value: [
        SourceType.STATUTE.value,
        SourceType.REGULATION.value,
        SourceType.PHARMACOPOEIA.value,
        SourceType.FORMULARY.value,
        SourceType.OFFICIAL_GUIDANCE.value,
    ],
    QueryIntent.PHARMACOPOEIA.value: [
        SourceType.PHARMACOPOEIA.value,
        SourceType.FORMULARY.value,
        SourceType.OFFICIAL_GUIDANCE.value,
    ],
    QueryIntent.ABS.value: [
        SourceType.STATUTE.value,
        SourceType.TREATY.value,
        SourceType.REGULATION.value,
        SourceType.OFFICIAL_GUIDANCE.value,
    ],
    QueryIntent.INTERNATIONAL_IP.value: [
        SourceType.TREATY.value,
        SourceType.OFFICIAL_GUIDANCE.value,
    ],
    QueryIntent.TRADITIONAL_KNOWLEDGE.value: [
        SourceType.STATUTE.value,
        SourceType.OFFICIAL_GUIDANCE.value,
        SourceType.CLASSICAL_TEXT.value,
    ],
    QueryIntent.FORMULATION_CLASSIFICATION.value: [
        SourceType.STATUTE.value,
        SourceType.REGULATION.value,
        SourceType.OFFICIAL_GUIDANCE.value,
        SourceType.FORMULARY.value,
    ],
    QueryIntent.FORMULATION_INFORMATION.value: [
        SourceType.PHARMACOPOEIA.value,
        SourceType.FORMULARY.value,
        SourceType.OFFICIAL_GUIDANCE.value,
    ],
    QueryIntent.SOURCE_LOOKUP.value: [
        SourceType.STATUTE.value,
        SourceType.TREATY.value,
        SourceType.REGULATION.value,
    ],
    QueryIntent.GENERAL_INFORMATION.value: [
        SourceType.STATUTE.value,
        SourceType.TREATY.value,
        SourceType.OFFICIAL_GUIDANCE.value,
    ],
    QueryIntent.UNKNOWN.value: [
        SourceType.STATUTE.value,
        SourceType.OFFICIAL_GUIDANCE.value,
    ]
}

# Preferred authority levels: PRIMARY and OFFICIAL_SECONDARY
DEFAULT_AUTHORITY_LEVELS = [
    AuthorityLevel.PRIMARY.value,
    AuthorityLevel.OFFICIAL_SECONDARY.value
]


class RetrievalRouter:
    """
    Creates evidence-routing plans based on query classification and
    routes retrieval to the existing FAISS + SQLite knowledge layer.
    """

    def create_routing_plan(self, classification: QueryClassification) -> RetrievalRoutingPlan:
        """
        Builds a RetrievalRoutingPlan. Handles isolated single jurisdictions,
        dual tracks for mixed queries, and clarification flags for unspecified queries.
        """
        intent = classification.intent
        jur_info = classification.jurisdiction
        query_text = classification.original_query
        topics = classification.topics

        # Determine source types based on intent
        preferred_source_types = INTENT_SOURCE_TYPE_MAP.get(
            intent,
            [SourceType.STATUTE.value, SourceType.OFFICIAL_GUIDANCE.value]
        )

        tracks: List[EvidenceTrack] = []
        explanations: List[str] = []
        requires_clarification = False
        clarification_reason = None

        # Case 1: Unspecified Jurisdiction
        if jur_info.primary == JurisdictionChoice.UNSPECIFIED.value:
            requires_clarification = True
            clarification_reason = (
                "The query does not specify a legal jurisdiction (e.g., Indian Law vs International Treaty). "
                "Retrieval requires jurisdiction clarification to prevent cross-regime assumptions."
            )
            explanations.append(
                "Unspecified jurisdiction: Marked for clarification. "
                "Retrieval track configured with neutral reference parameters."
            )
            # Universal/neutral track
            tracks.append(
                EvidenceTrack(
                    track_name="UNSPECIFIED",
                    jurisdiction="UNSPECIFIED",
                    source_types=preferred_source_types,
                    authority_levels=DEFAULT_AUTHORITY_LEVELS,
                    topics=topics,
                    query_text=query_text
                )
            )
            return RetrievalRoutingPlan(
                tracks=tracks,
                jurisdictions=["UNSPECIFIED"],
                source_types=preferred_source_types,
                authority_levels=DEFAULT_AUTHORITY_LEVELS,
                topics=topics,
                requires_clarification=requires_clarification,
                clarification_reason=clarification_reason,
                explanation=explanations
            )

        # Case 2: Mixed Jurisdiction (India + International)
        if jur_info.mixed:
            explanations.append(
                "Mixed jurisdiction detected: Creating two separate isolated evidence tracks "
                "(Track 1: INDIA, Track 2: INTERNATIONAL) to prevent cross-jurisdiction leakage."
            )

            # Track 1: India (Statutes, Regulations, Guidelines under Indian Law)
            india_source_types = [st for st in preferred_source_types if st != SourceType.TREATY.value]
            if not india_source_types:
                india_source_types = [SourceType.STATUTE.value, SourceType.OFFICIAL_GUIDANCE.value]

            tracks.append(
                EvidenceTrack(
                    track_name="INDIA",
                    jurisdiction=Jurisdiction.INDIA.value,
                    source_types=india_source_types,
                    authority_levels=DEFAULT_AUTHORITY_LEVELS,
                    topics=[t for t in topics if t != Topic.INTERNATIONAL_TREATY.value] or [Topic.ABS.value],
                    query_text=query_text
                )
            )

            # Track 2: International (Treaties, International Guidelines)
            intl_source_types = [SourceType.TREATY.value, SourceType.OFFICIAL_GUIDANCE.value]
            tracks.append(
                EvidenceTrack(
                    track_name="INTERNATIONAL",
                    jurisdiction=Jurisdiction.INTERNATIONAL.value,
                    source_types=intl_source_types,
                    authority_levels=DEFAULT_AUTHORITY_LEVELS,
                    topics=[Topic.INTERNATIONAL_TREATY.value, Topic.ABS.value, Topic.GENETIC_RESOURCES.value],
                    query_text=query_text
                )
            )

            return RetrievalRoutingPlan(
                tracks=tracks,
                jurisdictions=[Jurisdiction.INDIA.value, Jurisdiction.INTERNATIONAL.value],
                source_types=preferred_source_types,
                authority_levels=DEFAULT_AUTHORITY_LEVELS,
                topics=topics,
                requires_clarification=False,
                clarification_reason=None,
                explanation=explanations
            )

        # Case 3: Single Jurisdiction (INDIA)
        if jur_info.primary == JurisdictionChoice.INDIA.value:
            explanations.append("Routing retrieval exclusively to INDIA authoritative sources.")
            tracks.append(
                EvidenceTrack(
                    track_name="INDIA",
                    jurisdiction=Jurisdiction.INDIA.value,
                    source_types=preferred_source_types,
                    authority_levels=DEFAULT_AUTHORITY_LEVELS,
                    topics=topics,
                    query_text=query_text
                )
            )
            return RetrievalRoutingPlan(
                tracks=tracks,
                jurisdictions=[Jurisdiction.INDIA.value],
                source_types=preferred_source_types,
                authority_levels=DEFAULT_AUTHORITY_LEVELS,
                topics=topics,
                requires_clarification=False,
                clarification_reason=None,
                explanation=explanations
            )

        # Case 4: Single Jurisdiction (INTERNATIONAL)
        if jur_info.primary == JurisdictionChoice.INTERNATIONAL.value:
            explanations.append("Routing retrieval exclusively to INTERNATIONAL treaties and guidance.")
            # For international, ensure TREATY is preferred
            intl_source_types = [st for st in preferred_source_types if st in {SourceType.TREATY.value, SourceType.OFFICIAL_GUIDANCE.value}]
            if not intl_source_types:
                intl_source_types = [SourceType.TREATY.value, SourceType.OFFICIAL_GUIDANCE.value]

            tracks.append(
                EvidenceTrack(
                    track_name="INTERNATIONAL",
                    jurisdiction=Jurisdiction.INTERNATIONAL.value,
                    source_types=intl_source_types,
                    authority_levels=DEFAULT_AUTHORITY_LEVELS,
                    topics=topics,
                    query_text=query_text
                )
            )
            return RetrievalRoutingPlan(
                tracks=tracks,
                jurisdictions=[Jurisdiction.INTERNATIONAL.value],
                source_types=intl_source_types,
                authority_levels=DEFAULT_AUTHORITY_LEVELS,
                topics=topics,
                requires_clarification=False,
                clarification_reason=None,
                explanation=explanations
            )

        # Fallback
        tracks.append(
            EvidenceTrack(
                track_name="DEFAULT",
                jurisdiction="UNSPECIFIED",
                source_types=preferred_source_types,
                authority_levels=DEFAULT_AUTHORITY_LEVELS,
                topics=topics,
                query_text=query_text
            )
        )
        return RetrievalRoutingPlan(
            tracks=tracks,
            jurisdictions=["UNSPECIFIED"],
            source_types=preferred_source_types,
            authority_levels=DEFAULT_AUTHORITY_LEVELS,
            topics=topics,
            requires_clarification=True,
            clarification_reason="Unrecognized jurisdiction.",
            explanation=["Fallback routing applied."]
        )

    def execute_routing(
        self,
        plan: RetrievalRoutingPlan,
        retriever_instance: Any,
        top_k: int = 5
    ) -> Dict[str, List[RetrievedChunk]]:
        """
        Executes retrieval for each evidence track in the routing plan using the existing
        FAISS + SQLite retriever.
        Maintains 100% strict jurisdiction isolation per track.
        """
        results_by_track: Dict[str, List[RetrievedChunk]] = {}

        for track in plan.tracks:
            # If track is UNSPECIFIED and marked for clarification, don't execute or retrieve neutral
            if track.jurisdiction == "UNSPECIFIED":
                results_by_track[track.track_name] = []
                continue

            # Execute retrieval with strict jurisdiction filter
            chunks = retriever_instance.retrieve(
                query=track.query_text,
                top_k=top_k,
                jurisdiction=track.jurisdiction,
                apply_authority_weight=True
            )
            results_by_track[track.track_name] = chunks
            logger.info(
                f"Track '{track.track_name}' (Jur: {track.jurisdiction}) retrieved {len(chunks)} chunk(s)"
            )

        return results_by_track


# Singleton router
retrieval_router = RetrievalRouter()
