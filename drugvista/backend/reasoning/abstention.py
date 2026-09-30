"""
Abstention, Clarification, and Human Review Guardrails for IP-SAKTI Sahayak
Phase 2B.2 — Evidence-Based Reasoning & Cited Answer Generation.

Implements principled abstention, structured clarification generation,
and human-review escalation. Guarantees zero fabrication on confidential
TKDL queries, missing jurisdictions, and low-evidence situations.
"""
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

from classification.vocabularies import QueryIntent, JurisdictionChoice
from classification import QueryClassification
from .evidence_model import ReasoningStatus, SufficiencyState, EvidenceItem
from .evidence_sufficiency import SufficiencyEvaluation


@dataclass
class AbstentionDecision:
    """Decision indicating whether to abstain, seek clarification, or escalate."""
    should_divert: bool
    status: Optional[str] = None  # ReasoningStatus enum value if diverting
    reason: str = ""
    missing_information: List[str] = field(default_factory=list)
    human_review_reasons: List[str] = field(default_factory=list)
    explanation: List[str] = field(default_factory=list)


class AbstentionGuard:
    """
    Evaluates queries and evidence pools against strict regulatory guardrails
    to trigger safe abstention, clarification requests, or human escalation.
    """

    def __init__(self):
        # Confidential TKDL search regex
        self.tkdl_confidential_pattern = re.compile(
            r"\b(search\s+tkdl|look\s+up\s+in\s+tkdl|find\s+in\s+tkdl|is\s+this\s+in\s+tkdl|check\s+tkdl\s+database|does\s+this\s+exact\s+formulation\s+appear\s+in\s+tkdl|tkdl\s+access)\b",
            re.IGNORECASE
        )
        # Definitive legal opinion / guarantee regex
        self.definitive_legal_pattern = re.compile(
            r"\b(guarantee|definitely\s+patentable|guaranteed\s+to\s+pass|binding\s+legal\s+opinion|guarantee\s+approval|will\s+my\s+patent\s+be\s+granted)\b",
            re.IGNORECASE
        )

    def evaluate_pre_retrieval(self, classification: QueryClassification) -> AbstentionDecision:
        """
        Check guardrails that can be determined from the query classification alone
        prior to or in parallel with retrieval.
        """
        query = classification.original_query
        norm_query = classification.normalized_query
        missing_info: List[str] = []
        human_reasons: List[str] = []

        # 1. TKDL Confidential Records Guardrail (Section 30)
        if self.tkdl_confidential_pattern.search(norm_query):
            human_reasons.append(
                "User requested search of confidential TKDL internal database records. "
                "The system corpus contains only public advisory/guideline documents."
            )
            return AbstentionDecision(
                should_divert=True,
                status=ReasoningStatus.HUMAN_REVIEW_RECOMMENDED.value,
                reason="Direct searches of confidential TKDL database records cannot be performed by this public system.",
                human_review_reasons=human_reasons,
                explanation=[
                    "The system knowledge corpus contains only public statutory texts and general TKDL advisory guidelines.",
                    "Confidential TKDL formulation records are restricted to official patent offices under non-disclosure agreements.",
                    "Please submit an official search inquiry through the Indian Patent Office or authorized CSIR-TKDL institutional channels."
                ]
            )

        # 2. Missing Jurisdiction for Jurisdiction-Specific Legal Query (Section 10, 18, 35)
        if classification.jurisdiction.primary == JurisdictionChoice.UNSPECIFIED.value:
            if classification.intent in {
                QueryIntent.PATENTABILITY.value,
                QueryIntent.REGULATORY_COMPLIANCE.value,
                QueryIntent.ABS.value
            }:
                missing_info.append("Jurisdiction specification (e.g., Indian Patents Act vs. International Treaties)")
                return AbstentionDecision(
                    should_divert=True,
                    status=ReasoningStatus.CLARIFICATION_REQUIRED.value,
                    reason="Legal analysis requires specifying the applicable legal jurisdiction to avoid cross-regime assumptions.",
                    missing_information=missing_info,
                    explanation=[
                        "Patentability and regulatory compliance standards differ fundamentally across jurisdictions.",
                        "Please specify whether your inquiry concerns Indian domestic law (e.g., Patents Act, 1970) or an international framework."
                    ]
                )

        # 3. Definitive Legal Guarantee / Verdict Guardrail (Section 19, 20)
        if self.definitive_legal_pattern.search(norm_query):
            human_reasons.append("Query requests a definitive legal ruling or commercial guarantee.")
            return AbstentionDecision(
                should_divert=True,
                status=ReasoningStatus.HUMAN_REVIEW_RECOMMENDED.value,
                reason="This AI assistant provides evidence-based regulatory guidance and cannot issue binding legal guarantees.",
                human_review_reasons=human_reasons,
                explanation=[
                    "Patent grant decisions are exercised solely by the Controller General of Patents under statutory discretion.",
                    "Formal consultation with a registered Patent Agent or legal counsel is strongly recommended."
                ]
            )

        return AbstentionDecision(should_divert=False)

    def evaluate_post_retrieval(
        self,
        classification: QueryClassification,
        evidence_items: List[EvidenceItem],
        sufficiency: SufficiencyEvaluation
    ) -> AbstentionDecision:
        """
        Evaluate guardrails that depend on the retrieved evidence pool and sufficiency metrics.
        """
        # 1. Total lack of evidence or insufficient relevance (Section 17, 23)
        if sufficiency.state in {SufficiencyState.NONE.value, SufficiencyState.INSUFFICIENT.value}:
            return AbstentionDecision(
                should_divert=True,
                status=ReasoningStatus.INSUFFICIENT_EVIDENCE.value,
                reason="Available authoritative knowledge base contains insufficient evidence to safely address this inquiry.",
                explanation=[
                    "No authoritative statutory provisions or official guidelines met the relevance threshold for this query.",
                    "Abstaining from speculation to prevent legal hallucinations."
                ]
            )

        # 2. Material Statutory or Temporal Conflict (Section 28)
        if sufficiency.has_potential_conflict:
            return AbstentionDecision(
                should_divert=True,
                status=ReasoningStatus.HUMAN_REVIEW_RECOMMENDED.value,
                reason="Retrieved evidence contains potentially conflicting or superseded statutory provisions.",
                human_review_reasons=[
                    f"Conflict detected involving sources: {', '.join(sufficiency.conflicting_sources)}."
                ],
                explanation=[
                    "Multiple statutory versions with differing legal status (in-force vs. superseded) were retrieved.",
                    "Professional legal review is required to resolve temporal applicability."
                ]
            )

        return AbstentionDecision(should_divert=False)


# Singleton guard
abstention_guard = AbstentionGuard()
