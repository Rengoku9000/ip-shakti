"""
Evidence Sufficiency Evaluator for IP-SAKTI Sahayak
Phase 2B.2 — Evidence-Based Reasoning & Cited Answer Generation.

Evaluates retrieval quality, authority hierarchy, verification status,
jurisdiction alignment, legal status, and potential statutory conflicts.
Prevents hallucination by rejecting insufficient or unverified evidence pools.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from models import RetrievedChunk, AuthorityLevel, LegalStatus, VerificationStatus
from .evidence_model import SufficiencyState, EvidenceItem


@dataclass
class SufficiencyEvaluation:
    """Detailed evaluation of the retrieved evidence sufficiency."""
    state: str
    score: float
    reasons: List[str] = field(default_factory=list)
    has_primary_authority: bool = False
    has_in_force_statute: bool = False
    is_not_in_force_treaty: bool = False
    is_historical_only: bool = False
    has_potential_conflict: bool = False
    conflicting_sources: List[str] = field(default_factory=list)
    total_evidence_count: int = 0
    top_score: float = 0.0


class EvidenceSufficiencyEvaluator:
    """
    Evaluates evidence sufficiency across authority level, semantic relevance,
    legal status, and provenance completeness without computing arbitrary probabilities.
    """

    def evaluate(
        self,
        evidence_items: List[EvidenceItem],
        target_jurisdiction: Optional[str] = None
    ) -> SufficiencyEvaluation:
        """
        Evaluate an evidence pool against strict legal and regulatory criteria.
        """
        if not evidence_items:
            return SufficiencyEvaluation(
                state=SufficiencyState.NONE.value,
                score=0.0,
                reasons=["No authoritative evidence retrieved."],
                total_evidence_count=0,
                top_score=0.0
            )

        total_count = len(evidence_items)
        scores = [item.retrieval_score for item in evidence_items]
        top_score = max(scores)
        reasons: List[str] = []

        # 1. Authority Level Analysis
        primary_items = [e for e in evidence_items if e.authority_level == AuthorityLevel.PRIMARY.value]
        secondary_items = [e for e in evidence_items if e.authority_level == AuthorityLevel.OFFICIAL_SECONDARY.value]
        has_primary = len(primary_items) > 0

        # 2. Legal Status and Verification Analysis
        in_force_items = [e for e in evidence_items if e.legal_status == LegalStatus.IN_FORCE.value]
        not_in_force_treaties = [
            e for e in evidence_items
            if e.legal_status in {LegalStatus.ADOPTED.value, LegalStatus.NOT_IN_FORCE.value}
        ]
        historical_items = [
            e for e in evidence_items
            if e.verification_status == VerificationStatus.VERIFIED_HISTORICAL.value or
               (e.effective_until is not None and e.effective_until != "")
        ]

        has_in_force = len(in_force_items) > 0
        is_not_in_force_treaty = len(not_in_force_treaties) > 0 and len(in_force_items) == 0
        is_historical_only = len(historical_items) == total_count

        # 3. Jurisdiction Consistency
        if target_jurisdiction and target_jurisdiction != "UNSPECIFIED":
            mismatched_jur = [e for e in evidence_items if e.jurisdiction != target_jurisdiction]
            if len(mismatched_jur) == total_count:
                return SufficiencyEvaluation(
                    state=SufficiencyState.INSUFFICIENT.value,
                    score=0.1,
                    reasons=[f"All retrieved evidence belongs to mismatched jurisdiction (expected: {target_jurisdiction})."],
                    total_evidence_count=total_count,
                    top_score=top_score
                )

        # 4. Conflict and Superseded Detection
        has_conflict = False
        conflicting_sources: List[str] = []
        superseded_items = [e for e in evidence_items if e.legal_status == LegalStatus.SUPERSEDED.value]
        if superseded_items and in_force_items:
            has_conflict = True
            conflicting_sources = [e.source_id for e in superseded_items]
            reasons.append("Evidence contains both in-force provisions and superseded historical versions.")

        # 5. Composite Sufficiency Determination
        # High relevance top score with in-force primary/secondary source
        if top_score >= 0.35 and (has_primary or len(secondary_items) > 0) and (has_in_force or len(not_in_force_treaties) > 0):
            if total_count >= 2 and has_primary and has_in_force:
                state = SufficiencyState.STRONG.value
                score = 0.95
                reasons.append("Strong multi-source authoritative evidence with PRIMARY in-force provisions.")
            else:
                state = SufficiencyState.ADEQUATE.value
                score = 0.85
                reasons.append("Adequate authoritative evidence supporting the requested inquiry.")
        elif top_score >= 0.22 and total_count >= 1:
            state = SufficiencyState.PARTIAL.value
            score = 0.60
            reasons.append("Partial evidence retrieved; relevant concepts present but authority or coverage is limited.")
        else:
            state = SufficiencyState.INSUFFICIENT.value
            score = 0.25
            reasons.append("Retrieval scores below minimum authoritative threshold; evidence is insufficient to reason safely.")

        if is_not_in_force_treaty:
            reasons.append("Notice: Retrieved treaty provisions are ADOPTED but NOT IN FORCE as binding domestic law.")

        if is_historical_only:
            reasons.append("Notice: All retrieved provisions are historical records and do not reflect current law.")

        return SufficiencyEvaluation(
            state=state,
            score=score,
            reasons=reasons,
            has_primary_authority=has_primary,
            has_in_force_statute=has_in_force,
            is_not_in_force_treaty=is_not_in_force_treaty,
            is_historical_only=is_historical_only,
            has_potential_conflict=has_conflict,
            conflicting_sources=conflicting_sources,
            total_evidence_count=total_count,
            top_score=top_score
        )


# Singleton evaluator
evidence_sufficiency_evaluator = EvidenceSufficiencyEvaluator()
