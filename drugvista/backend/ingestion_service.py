"""
Ingestion Service for DrugVista
Orchestrates: Parse -> Normalize -> Hash -> Deduplicate -> Chunk -> Embed -> SQLite + FAISS
"""
import uuid
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

import config
from db import db
from models import DocumentMetadata, ChunkMetadata, IngestResponse
from document_loader import DocumentLoader, normalize_text, compute_sha256
from document_chunker import DocumentChunker
from embedding_service import embedding_service
from vector_store import vector_store

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self, chunker: Optional[DocumentChunker] = None):
        self.chunker = chunker or DocumentChunker()

    def ingest_bytes(
        self,
        content: bytes,
        filename: str,
        doc_type: str = "document",
        description: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Any]] = None
    ) -> IngestResponse:
        """
        Ingest document from bytes with content hashing, deduplication, chunking, and embedding.
        """
        parsed_records = DocumentLoader.load_from_bytes(
            content=content,
            filename=filename,
            doc_type=doc_type,
            description=description
        )

        if not parsed_records:
            return IngestResponse(
                success=False,
                status="error",
                message=f"No readable text extracted from {filename} (minimum 10 characters required)"
            )

        total_docs_added = 0
        total_chunks_added = 0
        last_doc_id = None
        has_duplicates = False

        for rec in parsed_records:
            content_hash = rec["content_hash"]
            clean_content = rec["content"]
            rec_filename = rec["filename"]

            # Deduplication check
            existing = db.get_document_by_hash(content_hash)
            if existing:
                logger.info(f"Duplicate detected: {rec_filename} matches existing document {existing['id']}")
                has_duplicates = True
                last_doc_id = existing['id']
                continue

            # Create document record
            doc_id = str(uuid.uuid4())
            last_doc_id = doc_id
            doc_meta = DocumentMetadata(
                id=doc_id,
                content_hash=content_hash,
                filename=rec_filename,
                source_type=rec["source_type"],
                source_uri=rec.get("source_uri"),
                title=rec.get("title", rec_filename),
                raw_content=clean_content,
                metadata={**(extra_metadata or {}), "description": rec.get("description", "")}
            )

            # Chunk document
            chunks = self.chunker.chunk_text(
                text=clean_content,
                document_id=doc_id,
                extra_metadata={"filename": rec_filename, "source_type": rec["source_type"]}
            )

            if not chunks:
                continue

            # Persist document and chunks to SQLite
            db.insert_document(doc_meta)
            db.insert_chunks(chunks)

            # Generate embeddings for chunks
            chunk_texts = [c.content for c in chunks]
            vectors = embedding_service.embed_texts(chunk_texts)

            # Add to FAISS and map IDs
            chunk_ids = [c.id for c in chunks]
            vector_store.add_vectors(vectors, chunk_ids)

            total_docs_added += 1
            total_chunks_added += len(chunks)

        if total_docs_added == 0 and has_duplicates:
            return IngestResponse(
                success=True,
                status="duplicate",
                message=f"Document '{filename}' already exists in knowledge base (deduplicated)",
                document_id=last_doc_id,
                documents_added=0,
                chunks_added=0
            )

        return IngestResponse(
            success=True,
            status="success",
            message=f"Successfully ingested {filename} ({total_docs_added} document(s), {total_chunks_added} chunk(s))",
            document_id=last_doc_id,
            documents_added=total_docs_added,
            chunks_added=total_chunks_added
        )

    def ingest_text(
        self,
        content: str,
        title: Optional[str] = None,
        doc_type: str = "text_note",
        extra_metadata: Optional[Dict[str, Any]] = None
    ) -> IngestResponse:
        """Ingest plain text note with deduplication and chunking"""
        clean_content = normalize_text(content)
        if len(clean_content) < 10:
            return IngestResponse(
                success=False,
                status="error",
                message="Content too short (minimum 10 characters required)"
            )

        filename = title or f"note_{clean_content[:20].replace(' ', '_')}.txt"
        return self.ingest_bytes(
            content=clean_content.encode("utf-8"),
            filename=filename,
            doc_type=doc_type,
            description=f"Direct text entry: {title or filename}",
            extra_metadata=extra_metadata
        )

    def ingest_file(self, file_path: Path, doc_type: str = "document") -> IngestResponse:
        """Ingest single file from disk"""
        path = Path(file_path)
        with open(path, "rb") as f:
            content = f.read()
        return self.ingest_bytes(content=content, filename=path.name, doc_type=doc_type, extra_metadata={"source_path": str(path)})

    def ingest_directory(self, dir_path: Path, doc_type: str = "document", pattern: str = "*.*") -> Dict[str, Any]:
        """Ingest all matching files in a directory"""
        path = Path(dir_path)
        if not path.exists():
            return {"total_files": 0, "ingested": 0, "duplicates": 0, "errors": 0}

        results = {"total_files": 0, "ingested": 0, "duplicates": 0, "errors": 0, "chunks": 0}
        for file_path in path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in DocumentLoader.ALLOWED_EXTENSIONS:
                results["total_files"] += 1
                try:
                    resp = self.ingest_file(file_path, doc_type=doc_type)
                    if resp.status == "success":
                        results["ingested"] += resp.documents_added
                        results["chunks"] += resp.chunks_added
                    elif resp.status == "duplicate":
                        results["duplicates"] += 1
                except Exception as e:
                    logger.error(f"Failed to ingest {file_path}: {e}")
                    results["errors"] += 1
        return results


# Singleton instance
ingestion_service = IngestionService()
