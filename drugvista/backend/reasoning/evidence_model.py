"""
Evidence Data Models for IP-SAKTI Sahayak
Phase 2B.2 — Evidence-Based Reasoning & Cited Answer Generation.

Defines structured evidence representations, claims, evidence chains,
and reasoning results. Implements strict separation of source facts
from model interpretations.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

from models import RetrievedChunk, CitationSource, AuthorityLevel, LegalStatus, VerificationStatus


class ReasoningStatus(str, Enum):
    """Controlled answer classifications reflecting evidentiary state (not legal verdicts)."""
    EVIDENCE_SUPPORTED = "EVIDENCE_SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
    HUMAN_REVIEW_RECOMMENDED = "HUMAN_REVIEW_RECOMMENDED"


class SufficiencyState(str, Enum):
    """Evaluated sufficiency of the retrieved evidence pool."""
    STRONG = "STRONG"
    ADEQUATE = "ADEQUATE"
    PARTIAL = "PARTIAL"
    INSUFFICIENT = "INSUFFICIENT"
    NONE = "NONE"


class ClaimType(str, Enum):
    """Categorization of individual claims in generated reasoning."""
    SOURCE_FACT = "SOURCE_FACT"
    INTERPRETATION = "INTERPRETATION"
    UNCERTAINTY = "UNCERTAINTY"
    RECOMMENDATION = "RECOMMENDATION"


class SupportNature(str, Enum):
    """Whether evidence directly states the fact or requires inference."""
    DIRECT = "DIRECT"
    INFERRED = "INFERRED"


@dataclass
class EvidenceItem:
    """Structured representation of an authoritative evidence unit used in reasoning."""
    chunk_id: str
    source_id: str
    source_version_id: str
    title: str
    authority: str
    authority_level: str
    jurisdiction: str
    legal_status: str
    verification_status: str
    citation_anchor: str
    source_url: str
    text: str
    retrieval_score: float
    relevance_reason: str = ""
    effective_from: Optional[str] = None
    effective_until: Optional[str] = None
    entry_into_force_date: Optional[str] = None

    @classmethod
    def from_chunk(cls, chunk: RetrievedChunk, relevance_reason: str = "") -> "EvidenceItem":
        """Instantiate an EvidenceItem from an existing RetrievedChunk without redundant data loss."""
        anchor = chunk.citation_anchor or f"{chunk.title or chunk.filename} — Section {chunk.section_label or chunk.chunk_index}"
        return cls(
            chunk_id=chunk.chunk_id,
            source_id=chunk.source_id or "unknown_source",
            source_version_id=chunk.source_version_id or "v1.0",
            title=chunk.title or chunk.filename,
            authority=chunk.authority or "Authoritative Body",
            authority_level=chunk.authority_level or AuthorityLevel.REFERENCE.value,
            jurisdiction=chunk.jurisdiction or "INDIA",
            legal_status=chunk.legal_status or LegalStatus.IN_FORCE.value,
            verification_status=chunk.verification_status or VerificationStatus.VERIFIED.value,
            citation_anchor=anchor,
            source_url=chunk.source_url or "",
            text=chunk.content,
            retrieval_score=round(chunk.score, 4),
            relevance_reason=relevance_reason,
            effective_from=chunk.effective_from,
            effective_until=chunk.effective_until,
            entry_into_force_date=chunk.entry_into_force_date
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Claim:
    """An individual structured claim tied to verified supporting evidence."""
    text: str
    supporting_evidence: List[str] = field(default_factory=list)  # chunk_ids or citation_anchors
    type: str = ClaimType.SOURCE_FACT.value
    support_nature: str = SupportNature.DIRECT.value
    citations: List[str] = field(default_factory=list)
    jurisdiction: str = "INDIA"
    legal_status: str = "IN_FORCE"
    qualification: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceChainItem:
    """Inspectable step in the evidence reasoning chain."""
    claim: str
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    interpretation: str = ""
    support_level: str = ReasoningStatus.EVIDENCE_SUPPORTED.value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StructuredReasoningResult:
    """Complete, cited reasoning output with honest uncertainty and clear provenance."""
    status: str
    sufficiency: str
    summary: str
    source_facts: List[Claim] = field(default_factory=list)
    interpretations: List[Claim] = field(default_factory=list)
    uncertainties: List[str] = field(default_factory=list)
    clarification_needed: List[str] = field(default_factory=list)
    human_review: bool = False
    human_review_reasons: List[str] = field(default_factory=list)
    evidence_chain: List[EvidenceChainItem] = field(default_factory=list)
    evidence_items: List[EvidenceItem] = field(default_factory=list)
    citations: List[CitationSource] = field(default_factory=list)
    jurisdiction_breakdown: Dict[str, Any] = field(default_factory=dict)
    formulation_verification: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "sufficiency": self.sufficiency,
            "summary": self.summary,
            "source_facts": [c.to_dict() for c in self.source_facts],
            "interpretations": [c.to_dict() for c in self.interpretations],
            "uncertainties": self.uncertainties,
            "clarification_needed": self.clarification_needed,
            "human_review": self.human_review,
            "human_review_reasons": self.human_review_reasons,
            "evidence_chain": [ec.to_dict() for ec in self.evidence_chain],
            "evidence_items": [ei.to_dict() for ei in self.evidence_items],
            "citations": [c.dict() if hasattr(c, "dict") else c for c in self.citations],
            "jurisdiction_breakdown": self.jurisdiction_breakdown,
            "formulation_verification": self.formulation_verification
        }
