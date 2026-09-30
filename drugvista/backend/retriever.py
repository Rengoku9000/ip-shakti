"""
Retriever Service for DrugVista / IP-SAKTI Sahayak
Executes semantic vector search and resolves matches against SQLite
to produce structured, provenance-rich RetrievedChunk records.
Supports Phase 2A: Jurisdiction filtering, Authority-level weighting, and Citation Anchors.
"""
import logging
import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from typing import List, Optional
import config
from db import db
from models import RetrievedChunk, AuthorityLevel, Jurisdiction
from embedding_service import embedding_service
from vector_store import vector_store

logger = logging.getLogger(__name__)


class Retriever:
    def __init__(self, top_k: Optional[int] = None, threshold: Optional[float] = None):
        self.top_k = top_k or config.TOP_K
        self.threshold = threshold or config.SIMILARITY_THRESHOLD

    @staticmethod
    def _apply_authority_boost(chunk: RetrievedChunk) -> RetrievedChunk:
        """Apply configured authority boost to chunk score (PRIMARY > OFFICIAL_SECONDARY > REFERENCE)"""
        score = chunk.score
        if chunk.authority_level == AuthorityLevel.PRIMARY.value:
            score += config.AUTHORITY_WEIGHT_PRIMARY
        elif chunk.authority_level == AuthorityLevel.OFFICIAL_SECONDARY.value:
            score += config.AUTHORITY_WEIGHT_SECONDARY
        chunk.score = min(1.0, round(score, 4))
        return chunk

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None,
        jurisdiction: Optional[str] = None,
        source_type: Optional[str] = None,
        authority_level: Optional[str] = None,
        apply_authority_weight: bool = True
    ) -> List[RetrievedChunk]:
        """
        Embed query, execute FAISS similarity search, and map FAISS IDs
        to rich SQLite chunk, document, section, and source provenance records.
        Supports strict jurisdiction filtering and configurable authority weighting.
        """
        k = top_k or self.top_k
        min_score = threshold if threshold is not None else self.threshold

        if not query or len(query.strip()) == 0:
            return []

        # Generate query vector
        query_vector = embedding_service.embed_query(query)

        # Retrieve a broad candidate pool from FAISS to allow for post-filtering
        candidate_k = max(k * 20, 300)
        vector_results = vector_store.search_vectors(query_vector, top_k=candidate_k)
        if not vector_results:
            return []

        faiss_ids = [fid for fid, _ in vector_results]
        score_map = {fid: score for fid, score in vector_results}

        # Resolve chunks and document metadata from SQLite
        chunk_records = db.get_chunks_by_faiss_ids(faiss_ids)

        retrieved: List[RetrievedChunk] = []
        for rec in chunk_records:
            fid = rec["faiss_id"]
            base_score = score_map.get(fid, 0.0)

            # 1. Similarity threshold filter
            if base_score < min_score:
                continue

            chunk_jurisdiction = (rec.get("jurisdiction") or "INDIA").upper()
            chunk_source_type = (rec.get("source_type") or "").upper()
            chunk_authority_level = (rec.get("authority_level") or AuthorityLevel.REFERENCE.value).upper()

            # 2. Jurisdiction Filter (Strict separation: INDIA vs INTERNATIONAL)
            if jurisdiction:
                target_jur = jurisdiction.upper()
                if chunk_jurisdiction != target_jur:
                    continue

            # 3. Source Type Filter
            if source_type:
                target_type = source_type.upper()
                if chunk_source_type != target_type:
                    continue

            # 4. Authority Level Filter
            if authority_level:
                target_auth = authority_level.upper()
                if chunk_authority_level != target_auth:
                    continue

            # 5. Authority Weighting Adjustment (PRIMARY > OFFICIAL_SECONDARY > REFERENCE)
            weighted_score = base_score
            if apply_authority_weight:
                if chunk_authority_level == AuthorityLevel.PRIMARY.value:
                    weighted_score += config.AUTHORITY_WEIGHT_PRIMARY
                elif chunk_authority_level == AuthorityLevel.OFFICIAL_SECONDARY.value:
                    weighted_score += config.AUTHORITY_WEIGHT_SECONDARY

            # 6. Exact Provision / Citation Anchor Match Boost
            query_norm = query.lower()
            sec_lbl = rec.get("section_label") or ""
            anchor_text = rec.get("citation_anchor") or ""
            doc_title = rec.get("source_name") or rec.get("document_title") or ""

            # Statute title relevance
            if "patent" in query_norm and "patent" in anchor_text.lower():
                weighted_score += 0.08
            elif "biodiversity" in query_norm and "diversity" in anchor_text.lower():
                weighted_score += 0.08
            elif ("drugs and cosmetics" in query_norm or "drugs & cosmetics" in query_norm or "schedule t" in query_norm or "asu" in query_norm) and "cosmetics" in anchor_text.lower():
                weighted_score += 0.08
            elif ("pharmacopoeia" in query_norm or "pcim&h" in query_norm or "testing standards" in query_norm) and "pharmacopoeial" in anchor_text.lower():
                weighted_score += 0.08

            # Specific section / article / rule label match
            import re
            anchor_lower = anchor_text.lower()
            sec_match = re.search(r'(?:section|rule|article|schedule)\s*[\d]+(?:\([a-z0-9]+\))?|(?:schedule\s+[a-z]+)', query_norm)
            if sec_match:
                matched_sec = sec_match.group(0).strip()
                if matched_sec in anchor_lower or (sec_lbl and matched_sec in sec_lbl.lower()):
                    weighted_score += 0.25
            elif sec_lbl and sec_lbl.lower() in query_norm:
                weighted_score += 0.15
            elif anchor_text and any(part.strip().lower() in query_norm for part in anchor_text.split("—") if len(part.strip()) > 6):
                weighted_score += 0.05

            # Determine citation anchor fallback if not explicitly indexed
            citation_anchor = rec.get("citation_anchor")
            if not citation_anchor:
                sec_lbl = rec.get("section_label")
                doc_title = rec.get("source_name") or rec.get("document_title") or rec.get("filename")
                citation_anchor = f"{doc_title} — {sec_lbl}" if sec_lbl else f"{doc_title} (Chunk {rec.get('chunk_index')})"

            retrieved.append(
                RetrievedChunk(
                    chunk_id=rec["chunk_id"],
                    document_id=rec["document_id"],
                    content=rec["content"],
                    score=weighted_score,
                    filename=rec["filename"],
                    source_type=rec["source_type"],
                    chunk_index=rec["chunk_index"],
                    start_offset=rec["start_offset"],
                    end_offset=rec["end_offset"],
                    title=rec.get("document_title") or rec.get("filename"),
                    section_id=rec.get("section_id"),
                    section_label=rec.get("section_label"),
                    citation_anchor=citation_anchor,
                    authority=rec.get("authority"),
                    authority_level=chunk_authority_level,
                    jurisdiction=chunk_jurisdiction,
                    source_url=rec.get("source_url"),
                    source_id=rec.get("source_id"),
                    source_version_id=rec.get("source_version_id"),
                    legal_status=rec.get("legal_status"),
                    verification_status=rec.get("verification_status"),
                    publication_date=rec.get("publication_date"),
                    effective_from=rec.get("effective_from"),
                    effective_until=rec.get("effective_until"),
                    entry_into_force_date=rec.get("entry_into_force_date"),
                    status_checked_at=rec.get("status_checked_at"),
                    metadata={
                        **rec.get("doc_metadata", {}),
                        **rec.get("chunk_metadata", {})
                    }
                )
            )

        # Re-sort by weighted score descending and trim to top_k
        retrieved.sort(key=lambda x: x.score, reverse=True)
        final_results = retrieved[:k]

        logger.info(
            f"Retrieved {len(final_results)} chunk(s) for query: '{query[:50]}' "
            f"(jur: {jurisdiction or 'ALL'}, auth_weight: {apply_authority_weight})"
        )
        return final_results


# Singleton instance
retriever = Retriever()
