"""
Domain-Agnostic and Knowledge-Layer Models for DrugVista / IP-SAKTI Sahayak
Phase 2A: Authority, Versioning, Controlled Vocabularies, and Structured Provenance.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


# ---------------------------------------------------------------------------
# Controlled Vocabularies (Phase 2A)
# ---------------------------------------------------------------------------

class SourceType(str, Enum):
    STATUTE = "STATUTE"
    RULE = "RULE"
    REGULATION = "REGULATION"
    TREATY = "TREATY"
    PHARMACOPOEIA = "PHARMACOPOEIA"
    FORMULARY = "FORMULARY"
    OFFICIAL_GUIDANCE = "OFFICIAL_GUIDANCE"
    REGISTRY = "REGISTRY"
    CASE_LAW = "CASE_LAW"
    CLASSICAL_TEXT = "CLASSICAL_TEXT"
    GOVERNMENT_PUBLICATION = "GOVERNMENT_PUBLICATION"
    # Backward compatibility with Phase 1
    PAPER = "paper"
    CLINICAL_TRIAL = "clinical_trial"
    MARKET = "market"
    PATIENT_DATA = "patient_data"
    DOCUMENT = "document"


class AuthorityLevel(str, Enum):
    PRIMARY = "PRIMARY"                    # Legislation, rules, treaties, regulations
    OFFICIAL_SECONDARY = "OFFICIAL_SECONDARY"  # Ministry guidance, explanatory manuals
    REFERENCE = "REFERENCE"                # Supporting literature, academic papers


class Jurisdiction(str, Enum):
    INDIA = "INDIA"
    INTERNATIONAL = "INTERNATIONAL"


class LegalStatus(str, Enum):
    IN_FORCE = "IN_FORCE"
    NOT_IN_FORCE = "NOT_IN_FORCE"
    ADOPTED = "ADOPTED"
    SIGNED = "SIGNED"
    RATIFIED = "RATIFIED"
    SUPERSEDED = "SUPERSEDED"
    UNKNOWN = "UNKNOWN"


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    VERIFIED_CURRENT = "verified_current"
    VERIFIED_HISTORICAL = "verified_historical"
    OFFICIAL_SECONDARY = "official_secondary"
    SUPERSEDED = "superseded"
    REQUIRES_REVIEW = "requires_review"
    REJECTED = "rejected"
    UNVERIFIED = "unverified"


class SectionType(str, Enum):
    SECTION = "SECTION"
    SUBSECTION = "SUBSECTION"
    CLAUSE = "CLAUSE"
    ARTICLE = "ARTICLE"
    CHAPTER = "CHAPTER"
    RULE = "RULE"
    SCHEDULE = "SCHEDULE"
    VERSE = "VERSE"
    PART = "PART"


# ---------------------------------------------------------------------------
# Retrieval and Provenance Objects
# ---------------------------------------------------------------------------

@dataclass
class RetrievedChunk:
    """Represents a retrieved chunk with rich provenance metadata and citation anchors"""
    chunk_id: str
    document_id: str
    content: str
    score: float
    filename: str
    source_type: str
    chunk_index: int
    start_offset: int
    end_offset: int
    title: Optional[str] = None
    section_id: Optional[str] = None
    section_label: Optional[str] = None
    citation_anchor: Optional[str] = None
    authority: Optional[str] = None
    authority_level: Optional[str] = None
    jurisdiction: Optional[str] = None
    source_url: Optional[str] = None
    source_id: Optional[str] = None
    source_version_id: Optional[str] = None
    legal_status: Optional[str] = None
    verification_status: Optional[str] = None
    publication_date: Optional[str] = None
    effective_from: Optional[str] = None
    effective_until: Optional[str] = None
    entry_into_force_date: Optional[str] = None
    status_checked_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def id(self) -> str:
        return self.chunk_id

    @property
    def text(self) -> str:
        return self.content

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "content": self.content,
            "score": round(self.score, 4),
            "filename": self.filename,
            "source_type": self.source_type,
            "chunk_index": self.chunk_index,
            "start_offset": self.start_offset,
            "end_offset": self.end_offset,
            "title": self.title,
            "section_id": self.section_id,
            "section_label": self.section_label,
            "citation_anchor": self.citation_anchor,
            "authority": self.authority,
            "authority_level": self.authority_level,
            "jurisdiction": self.jurisdiction,
            "source_url": self.source_url,
            "source_id": self.source_id,
            "source_version_id": self.source_version_id,
            "legal_status": self.legal_status,
            "verification_status": self.verification_status,
            "publication_date": self.publication_date,
            "effective_from": self.effective_from,
            "effective_until": self.effective_until,
            "entry_into_force_date": self.entry_into_force_date,
            "status_checked_at": self.status_checked_at,
            "metadata": self.metadata
        }


class CitationSource(BaseModel):
    """Structured citation item linking to a specific chunk and document"""
    source_id: str
    document_id: str
    chunk_id: str
    chunk_index: int
    filename: str
    source_type: str
    score: float
    text_preview: str
    citation_anchor: Optional[str] = None
    authority: Optional[str] = None
    authority_level: Optional[str] = None
    jurisdiction: Optional[str] = None
    source_url: Optional[str] = None


class KnowledgeEvidenceItem(BaseModel):
    """Pure legal/regulatory evidence item for Phase 2A retrieval output"""
    citation_anchor: str
    source_name: str
    authority: str
    authority_level: str
    jurisdiction: str
    section_label: Optional[str] = None
    source_url: str
    score: float
    content: str
    chunk_id: str
    document_id: str


# ---------------------------------------------------------------------------
# Knowledge Layer Relational Records
# ---------------------------------------------------------------------------

class SourceRecord(BaseModel):
    """Top-level authoritative source metadata"""
    id: str
    name: str
    authority: str
    source_type: str
    jurisdiction: str
    authority_level: str
    official_url: str
    legal_status: Optional[str] = LegalStatus.IN_FORCE.value
    effective_status: Optional[str] = None
    description: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class SourceVersionRecord(BaseModel):
    """Specific versioned release of an authoritative source"""
    id: str
    source_id: str
    version: str
    publication_date: Optional[str] = None
    effective_from: Optional[str] = None
    effective_until: Optional[str] = None
    entry_into_force_date: Optional[str] = None
    legal_status: Optional[str] = LegalStatus.IN_FORCE.value
    effective_status: Optional[str] = None
    status_checked_at: Optional[str] = None
    retrieved_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    content_hash: str
    local_path: Optional[str] = None
    verification_status: str = VerificationStatus.VERIFIED.value


class DocumentSection(BaseModel):
    """Structural unit within a legal or classical text (Section, Article, Rule, Verse)"""
    id: str
    document_id: str
    parent_id: Optional[str] = None
    section_type: str
    section_label: str
    section_title: Optional[str] = None
    sequence: int = 0


# ---------------------------------------------------------------------------
# Document & Chunk Persistence Records
# ---------------------------------------------------------------------------

class DocumentMetadata(BaseModel):
    """Domain-agnostic document metadata with Phase 2A knowledge extensions"""
    id: str
    content_hash: str
    filename: str
    source_type: str
    source_uri: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    publication_date: Optional[str] = None
    ingested_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    language: str = "en"
    jurisdiction: Optional[str] = None
    version: str = "1.0"
    raw_content: Optional[str] = None
    source_id: Optional[str] = None
    source_version_id: Optional[str] = None
    authority_level: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChunkMetadata(BaseModel):
    """Domain-agnostic chunk metadata with structural anchors and provenance"""
    id: str
    document_id: str
    chunk_index: int
    content: str
    start_offset: int
    end_offset: int
    token_count: int
    content_hash: str
    section_id: Optional[str] = None
    citation_anchor: Optional[str] = None
    authority_level: Optional[str] = None
    jurisdiction: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# API Contract Models
# ---------------------------------------------------------------------------

class AnalysisRequest(BaseModel):
    """Request payload for query analysis"""
    query: str
    jurisdiction: Optional[str] = None
    source_type: Optional[str] = None
    authority_level: Optional[str] = None
    language: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Response payload preserved for backward compatibility with enriched provenance"""
    clinical_viability: str
    key_evidence: List[str]
    major_risks: List[str]
    market_signal: str
    recommendation: str
    confidence_score: float
    explanation: str
    sources: Optional[List[CitationSource]] = None
    query_classification: Optional[Dict[str, Any]] = None
    routing_plan: Optional[Dict[str, Any]] = None
    reasoning: Optional[Dict[str, Any]] = None
    evidence: Optional[List[Dict[str, Any]]] = None
    citations: Optional[List[Dict[str, Any]]] = None
    language: Optional[Dict[str, Any]] = None
    normalized_query: Optional[str] = None
    localization: Optional[Dict[str, Any]] = None


class IngestResponse(BaseModel):
    """Response payload for document ingestion with duplicate handling"""
    success: bool
    status: str = "success"  # "success", "duplicate", "error"
    message: str
    document_id: Optional[str] = None
    documents_added: int = 0
    chunks_added: int = 0
