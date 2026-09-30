"""
Reasoning Engine for IP-SAKTI Sahayak
Phase 2B.2 — Evidence-Based Reasoning & Cited Answer Generation.

Orchestrates multi-track evidence reasoning, claim extraction, sufficiency audit,
unsupported claim filtering, formulation verification, and human-review escalation.
Integrates LLM reasoning with seamless, deterministic offline fallback.
"""
import logging
from typing import List, Dict, Any, Optional

from models import RetrievedChunk, CitationSource, AuthorityLevel, LegalStatus, VerificationStatus
from classification import QueryClassification, RetrievalRoutingPlan
from llm_provider import get_llm_provider, LLMProvider
from .evidence_model import (
    EvidenceItem,
    Claim,
    ClaimType,
    SupportNature,
    EvidenceChainItem,
    StructuredReasoningResult,
    ReasoningStatus,
    SufficiencyState
)
from .evidence_sufficiency import evidence_sufficiency_evaluator, SufficiencyEvaluation
from .abstention import abstention_guard, AbstentionDecision
from .claim_mapper import claim_mapper
from .answer_validator import answer_validator
from .prompts import SYSTEM_REASONING_PROMPT, format_evidence_context, build_offline_summary

logger = logging.getLogger(__name__)


class ReasoningEngine:
    """
    Executes evidence-bounded reasoning over authoritative retrieved chunks,
    strictly separating source facts from interpretations and maintaining 0%
    cross-jurisdiction leakage.
    """

    def __init__(self, llm: Optional[LLMProvider] = None):
        self.llm = llm or get_llm_provider()

    def reason(
        self,
        query: str,
        classification: QueryClassification,
        routing_plan: RetrievalRoutingPlan,
        retrieved_by_track: Dict[str, List[RetrievedChunk]]
    ) -> StructuredReasoningResult:
        """
        Execute full evidence-based reasoning pipeline.
        """
        logger.info(f"Starting reasoning for query: '{query[:50]}' (Intent: {classification.intent})")

        # 1. Pre-retrieval guardrails (TKDL confidentiality, missing jurisdiction, definitive guarantees)
        pre_abstention = abstention_guard.evaluate_pre_retrieval(classification)
        if pre_abstention.should_divert:
            return self._build_diverted_result(pre_abstention, classification)

        # 2. Flatten and convert retrieved chunks into structured EvidenceItems per track
        evidence_items_all: List[EvidenceItem] = []
        evidence_by_track: Dict[str, List[EvidenceItem]] = {}
        citations_all: List[CitationSource] = []

        for track_name, chunks in retrieved_by_track.items():
            track_items: List[EvidenceItem] = []
            for ch in chunks:
                item = EvidenceItem.from_chunk(ch, relevance_reason=f"Retrieved in {track_name} track (Score: {ch.score:.2f})")
                track_items.append(item)
                evidence_items_all.append(item)

                # Build citation source
                preview = ch.content[:150] + ("..." if len(ch.content) > 150 else "")
                citations_all.append(
                    CitationSource(
                        source_id=ch.source_id or ch.chunk_id,
                        document_id=ch.document_id,
                        chunk_id=ch.chunk_id,
                        chunk_index=ch.chunk_index,
                        filename=ch.filename,
                        source_type=ch.source_type,
                        score=round(ch.score, 4),
                        text_preview=preview,
                        citation_anchor=item.citation_anchor,
                        authority=item.authority,
                        authority_level=item.authority_level,
                        jurisdiction=item.jurisdiction,
                        source_url=item.source_url
                    )
                )
            evidence_by_track[track_name] = track_items

        # 3. Evidence Sufficiency Evaluation
        target_jur = classification.jurisdiction.primary
        sufficiency = evidence_sufficiency_evaluator.evaluate(evidence_items_all, target_jurisdiction=target_jur)
        logger.info(f"Evidence sufficiency: {sufficiency.state} (Score: {sufficiency.score:.2f})")

        # 4. Post-retrieval guardrails (low evidence, material conflicts)
        post_abstention = abstention_guard.evaluate_post_retrieval(classification, evidence_items_all, sufficiency)
        if post_abstention.should_divert:
            return self._build_diverted_result(post_abstention, classification, evidence_items_all, citations_all, sufficiency)

        # 5. Formulation Verification (Section 10 & 11)
        formulation_verification = self._verify_formulation(classification, evidence_items_all)

        # 6. Structured Claim Mapping
        source_facts, interpretations, evidence_chain = claim_mapper.map_claims(
            query=query,
            classification=classification,
            evidence_items=evidence_items_all
        )

        # 7. Answer Validation & Unsupported Claim Elimination (Section 13)
        validated_facts, facts_report = answer_validator.validate_claims(
            claims=source_facts,
            evidence_items=evidence_items_all,
            target_jurisdiction=target_jur if not classification.jurisdiction.mixed else None
        )
        validated_interps, interps_report = answer_validator.validate_claims(
            claims=interpretations,
            evidence_items=evidence_items_all,
            target_jurisdiction=target_jur if not classification.jurisdiction.mixed else None
        )

        logger.info(
            f"Validated {len(validated_facts)} source facts and {len(validated_interps)} interpretations. "
            f"Unsupported claim rate: {facts_report.unsupported_claim_rate:.1f}%"
        )

        # 8. Multi-Track Jurisdiction Breakdown for Mixed Queries (Section 9)
        jurisdiction_breakdown = {}
        if classification.jurisdiction.mixed:
            jurisdiction_breakdown = self._build_mixed_breakdown(
                evidence_by_track, validated_facts, validated_interps
            )

        # 9. Summary Synthesis (LLM or Offline Fallback)
        summary = self._synthesize_summary(
            query=query,
            classification=classification,
            validated_facts=validated_facts,
            validated_interps=validated_interps,
            evidence_items=evidence_items_all,
            sufficiency=sufficiency
        )

        # Determine final status
        final_status = ReasoningStatus.EVIDENCE_SUPPORTED.value
        if sufficiency.state == SufficiencyState.PARTIAL.value:
            final_status = ReasoningStatus.PARTIALLY_SUPPORTED.value

        human_review_required = sufficiency.has_potential_conflict or sufficiency.is_not_in_force_treaty
        human_review_reasons = []
        if sufficiency.has_potential_conflict:
            human_review_reasons.append("Statutory conflict detected among provisions.")
        if sufficiency.is_not_in_force_treaty:
            human_review_reasons.append("Retrieved international treaty provisions are not yet in force.")

        uncertainties = []
        if classification.formulation.detected and formulation_verification.get("basis") == "USER_ASSERTED":
            uncertainties.append("Formulation type is user-asserted and lacks empirical monograph verification.")
        if sufficiency.is_not_in_force_treaty:
            uncertainties.append("Treaty provisions represent adopted multilateral standards, not binding domestic statutes.")

        return StructuredReasoningResult(
            status=final_status,
            sufficiency=sufficiency.state,
            summary=summary,
            source_facts=validated_facts,
            interpretations=validated_interps,
            uncertainties=uncertainties,
            clarification_needed=[],
            human_review=human_review_required,
            human_review_reasons=human_review_reasons,
            evidence_chain=evidence_chain,
            evidence_items=evidence_items_all,
            citations=citations_all,
            jurisdiction_breakdown=jurisdiction_breakdown,
            formulation_verification=formulation_verification
        )

    def _verify_formulation(
        self,
        classification: QueryClassification,
        evidence_items: List[EvidenceItem]
    ) -> Dict[str, Any]:
        """
        Verify user-asserted formulation against retrieved authoritative evidence.
        """
        if not classification.formulation.detected:
            return {
                "detected": False,
                "type": "NOT_APPLICABLE",
                "basis": "NOT_APPLICABLE",
                "explanation": "No formulation subject matter identified in query."
            }

        ingredients = classification.formulation.ingredients
        form_type = classification.formulation.type
        current_basis = classification.formulation.basis

        # Search retrieved text for mentions of the ingredients
        supported_ingredients = []
        for ing in ingredients:
            for item in evidence_items:
                if ing.lower() in item.text.lower():
                    supported_ingredients.append(ing)
                    break

        if supported_ingredients:
            return {
                "detected": True,
                "type": form_type,
                "basis": "EVIDENCE_SUPPORTED",
                "ingredients": ingredients,
                "verified_ingredients": supported_ingredients,
                "explanation": f"Ingredient(s) {', '.join(supported_ingredients)} verified in authoritative pharmacopoeial/statutory source."
            }

        return {
            "detected": True,
            "type": form_type,
            "basis": current_basis,
            "ingredients": ingredients,
            "verified_ingredients": [],
            "explanation": "Formulation details remain user-asserted; not explicitly indexed in retrieved statutory records."
        }

    def _build_mixed_breakdown(
        self,
        evidence_by_track: Dict[str, List[EvidenceItem]],
        facts: List[Claim],
        interps: List[Claim]
    ) -> Dict[str, Any]:
        """
        Construct completely isolated evidence breakdowns for mixed-jurisdiction queries.
        """
        india_items = evidence_by_track.get("INDIA", [])
        intl_items = evidence_by_track.get("INTERNATIONAL", [])

        india_facts = [f for f in facts if f.jurisdiction == "INDIA"]
        intl_facts = [f for f in facts if f.jurisdiction == "INTERNATIONAL"]

        return {
            "INDIA": {
                "evidence_count": len(india_items),
                "authorities": list(set(e.authority for e in india_items)),
                "source_facts": [f.to_dict() for f in india_facts],
                "regime": "Indian Domestic Law (Statutes & Rules)"
            },
            "INTERNATIONAL": {
                "evidence_count": len(intl_items),
                "authorities": list(set(e.authority for e in intl_items)),
                "source_facts": [f.to_dict() for f in intl_facts],
                "regime": "International Regimes & Multilateral Treaties"
            },
            "comparison": (
                "Indian law imposes domestic statutory controls under the Patents Act, 1970 and Biological "
                "Diversity Act, 2002, whereas international treaties (e.g., Nagoya Protocol, WIPO GRATK) provide "
                "multilateral frameworks for sovereign genetic resource rights and mandatory disclosure."
            )
        }

    def _synthesize_summary(
        self,
        query: str,
        classification: QueryClassification,
        validated_facts: List[Claim],
        validated_interps: List[Claim],
        evidence_items: List[EvidenceItem],
        sufficiency: SufficiencyEvaluation
    ) -> str:
        """
        Synthesizes final answer summary via online LLM if available,
        falling back deterministically to offline template synthesis.
        """
        target_jur = classification.jurisdiction.primary

        # If LLM is online, generate evidence-bound reasoning
        if self.llm and self.llm.is_online:
            try:
                context_str = format_evidence_context(evidence_items)
                prompt = (
                    f"{SYSTEM_REASONING_PROMPT}\n\n"
                    f"USER QUERY: {query}\n"
                    f"INTENT: {classification.intent}\n"
                    f"JURISDICTION: {target_jur}\n\n"
                    f"RETRIEVED AUTHORITATIVE EVIDENCE:\n{context_str}\n\n"
                    f"Provide an evidence-based summary explaining the relevant provisions without giving legal guarantees."
                )
                llm_response = self.llm.generate(prompt, temperature=0.2)
                if llm_response and len(llm_response.strip()) > 30:
                    return llm_response.strip()
            except Exception as e:
                logger.warning(f"Online LLM generation failed, falling back to offline mode: {e}")

        # Deterministic offline synthesis
        return build_offline_summary(
            classification=classification,
            source_facts=validated_facts,
            interpretations=validated_interps,
            sufficiency_state=sufficiency.state,
            target_jurisdiction=target_jur
        )

    def _build_diverted_result(
        self,
        decision: AbstentionDecision,
        classification: QueryClassification,
        evidence_items: Optional[List[EvidenceItem]] = None,
        citations: Optional[List[CitationSource]] = None,
        sufficiency: Optional[SufficiencyEvaluation] = None
    ) -> StructuredReasoningResult:
        """Construct a structured abstention or clarification response."""
        status = decision.status or ReasoningStatus.INSUFFICIENT_EVIDENCE.value
        suff_state = sufficiency.state if sufficiency else SufficiencyState.INSUFFICIENT.value

        summary = decision.reason
        if decision.explanation:
            summary += " " + " ".join(decision.explanation)

        is_human_review = (status == ReasoningStatus.HUMAN_REVIEW_RECOMMENDED.value)

        return StructuredReasoningResult(
            status=status,
            sufficiency=suff_state,
            summary=summary,
            source_facts=[],
            interpretations=[],
            uncertainties=decision.explanation,
            clarification_needed=decision.missing_information,
            human_review=is_human_review,
            human_review_reasons=decision.human_review_reasons,
            evidence_chain=[],
            evidence_items=evidence_items or [],
            citations=citations or [],
            jurisdiction_breakdown={},
            formulation_verification={}
        )


# Singleton reasoning engine
reasoning_engine = ReasoningEngine()
