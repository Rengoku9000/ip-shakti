"""
Knowledge Base Management & Ingestion Service for IP-SAKTI Sahayak
Manages authoritative legal and regulatory corpus ingestion, version verification,
and structural section indexing into SQLite and FAISS.
"""
import os
import json
import uuid
import hashlib
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import config
from db import db
from models import (
    SourceRecord, SourceVersionRecord, DocumentSection,
    DocumentMetadata, ChunkMetadata, VerificationStatus
)
from structure_parser import structure_parser
from embedding_service import embedding_service
from vector_store import vector_store

logger = logging.getLogger(__name__)


class KnowledgeService:
    def __init__(self, manifest_path: Optional[Path] = None):
        self.manifest_path = Path(manifest_path or config.MANIFEST_PATH)

    def load_manifest(self) -> Dict[str, Any]:
        """Load source manifest from disk"""
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Source manifest not found at {self.manifest_path}")
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def verify_sources(self) -> List[Dict[str, Any]]:
        """
        Verify all sources in manifest against on-disk files and SHA-256 hashes.
        Returns list of verification results.
        """
        manifest = self.load_manifest()
        results = []

        for src in manifest.get("sources", []):
            src_id = src["source_id"]
            local_rel_path = src.get("local_path")
            expected_hash = src.get("content_hash")
            
            full_path = config.BASE_DIR / local_rel_path
            
            if not full_path.exists():
                results.append({
                    "source_id": src_id,
                    "status": "missing_file",
                    "path": str(full_path),
                    "valid": False
                })
                continue

            content = full_path.read_bytes()
            actual_hash = hashlib.sha256(content).hexdigest()

            if actual_hash != expected_hash:
                results.append({
                    "source_id": src_id,
                    "status": "hash_mismatch",
                    "expected": expected_hash,
                    "actual": actual_hash,
                    "valid": False
                })
            else:
                results.append({
                    "source_id": src_id,
                    "status": "verified",
                    "hash": actual_hash,
                    "valid": True
                })

        return results

    def ingest_knowledge_corpus(self, force_rebuild: bool = False) -> Dict[str, Any]:
        """
        Ingest all verified sources from manifest into SQLite and FAISS.
        Applies structure-aware sectioning, deduplication, and deterministic citation anchors.
        """
        manifest = self.load_manifest()
        sources_list = manifest.get("sources", [])

        summary = {
            "total_manifest_sources": len(sources_list),
            "sources_ingested": 0,
            "sections_created": 0,
            "chunks_created": 0,
            "skipped_duplicates": 0,
            "errors": 0,
            "details": []
        }

        for src in sources_list:
            src_id = src["source_id"]
            status = src.get("status", "unverified")

            # Only ingest verified production sources
            valid_ingest_statuses = {
                VerificationStatus.VERIFIED.value,
                VerificationStatus.VERIFIED_CURRENT.value,
                VerificationStatus.OFFICIAL_SECONDARY.value
            }
            if status not in valid_ingest_statuses:
                logger.warning(f"Skipping source '{src_id}' with status '{status}'")
                continue

            local_rel = src.get("local_path")
            file_path = config.BASE_DIR / local_rel
            if not file_path.exists():
                logger.error(f"Cannot ingest {src_id}: file not found at {file_path}")
                summary["errors"] += 1
                continue

            try:
                raw_bytes = file_path.read_bytes()
                content_hash = hashlib.sha256(raw_bytes).hexdigest()
                raw_text = raw_bytes.decode("utf-8")

                # Check if document already exists
                existing_doc = db.get_document_by_hash(content_hash)
                if existing_doc and not force_rebuild:
                    logger.info(f"Source '{src_id}' already indexed (hash {content_hash[:8]}). Skipping duplicate.")
                    summary["skipped_duplicates"] += 1
                    continue

                # 1. Insert or update SourceRecord
                source_record = SourceRecord(
                    id=src_id,
                    name=src["name"],
                    authority=src["authority"],
                    source_type=src["source_type"],
                    jurisdiction=src["jurisdiction"],
                    authority_level=src["authority_level"],
                    official_url=src["source_url"],
                    legal_status=src.get("legal_status", "IN_FORCE"),
                    effective_status=src.get("effective_status"),
                    description=src.get("description", "")
                )
                db.insert_source(source_record)

                # 2. Insert SourceVersionRecord
                safe_ver = (src.get('version') or 'current').replace(' ', '_')[:30]
                version_id = f"{src_id}_v{safe_ver}"
                version_record = SourceVersionRecord(
                    id=version_id,
                    source_id=src_id,
                    version=src.get("version", "current"),
                    publication_date=src.get("publication_date"),
                    effective_from=src.get("effective_from"),
                    effective_until=src.get("effective_until"),
                    entry_into_force_date=src.get("entry_into_force_date"),
                    legal_status=src.get("legal_status", "IN_FORCE"),
                    effective_status=src.get("effective_status"),
                    status_checked_at=src.get("status_checked_at"),
                    content_hash=content_hash,
                    local_path=str(local_rel),
                    verification_status=status
                )
                db.insert_source_version(version_record)

                # 3. Parse structural sections
                doc_id = str(uuid.uuid4())
                parsed = structure_parser.parse_text(raw_text, document_id=doc_id)

                # 4. Insert DocumentMetadata
                doc_meta = DocumentMetadata(
                    id=doc_id,
                    content_hash=content_hash,
                    filename=file_path.name,
                    source_type=src["source_type"],
                    source_uri=str(src["source_url"]),
                    title=src.get("title", src["name"]),
                    authority_level=src["authority_level"],
                    jurisdiction=src["jurisdiction"],
                    version=src.get("version", "1.0"),
                    raw_content=parsed.clean_full_text,
                    source_id=src_id,
                    source_version_id=version_id,
                    metadata={
                        "short_title": src.get("short_title", src["name"]),
                        "authority": src["authority"],
                        "source_url": src["source_url"]
                    }
                )
                db.insert_document(doc_meta)

                # 5. Insert DocumentSections
                if parsed.sections:
                    db.insert_document_sections(parsed.sections)
                    summary["sections_created"] += len(parsed.sections)

                # 6. Generate structure-bounded chunks
                chunks = structure_parser.create_structured_chunks(
                    parsed_doc=parsed,
                    document_id=doc_id,
                    chunk_size=config.CHUNK_SIZE,
                    chunk_overlap=config.CHUNK_OVERLAP
                )

                if chunks:
                    db.insert_chunks(chunks)
                    summary["chunks_created"] += len(chunks)

                    # 7. Generate embeddings and store in FAISS
                    chunk_texts = [c.content for c in chunks]
                    vectors = embedding_service.embed_texts(chunk_texts)
                    chunk_ids = [c.id for c in chunks]
                    vector_store.add_vectors(vectors, chunk_ids)

                summary["sources_ingested"] += 1
                summary["details"].append({
                    "source_id": src_id,
                    "sections": len(parsed.sections),
                    "chunks": len(chunks),
                    "hash": content_hash[:12]
                })

            except Exception as e:
                logger.error(f"Failed to ingest source {src_id}: {e}", exc_info=True)
                summary["errors"] += 1

        logger.info(f"Knowledge corpus ingestion complete: {summary}")
        return summary


# Singleton instance
knowledge_service = KnowledgeService()
