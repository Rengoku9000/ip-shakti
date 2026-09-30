"""
FAISS Vector Store Manager for DrugVista
Manages dense vector storage and similarity search.
Decoupled from metadata and document content: FAISS stores vectors and returns integer IDs,
while SQLite manages chunk content and provenance.
"""
import os
import threading
import logging
from typing import List, Tuple, Dict, Any, Union, Optional
from pathlib import Path
import numpy as np
import faiss

import config
from db import db
from embedding_service import embedding_service

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self, index_path: Optional[Path] = None, dimension: Optional[int] = None):
        self.index_path = Path(index_path or config.FAISS_INDEX_PATH)
        self.dimension = dimension or config.EMBEDDING_DIMENSION
        self.model_name = config.EMBEDDING_MODEL
        self._lock = threading.Lock()
        self.index: Optional[faiss.IndexFlatIP] = None
        self._load_or_create()

    def _load_or_create(self):
        """Load persistent FAISS index from disk or create empty IndexFlatIP"""
        with self._lock:
            if self.index_path.exists():
                try:
                    self.index = faiss.read_index(str(self.index_path))
                    logger.info(f"Loaded FAISS index from {self.index_path} with {self.index.ntotal} vectors")
                except Exception as e:
                    logger.warning(f"Failed to read FAISS index from {self.index_path}: {e}. Creating empty index.")
                    self._create_empty_index()
            else:
                logger.info(f"No FAISS index found at {self.index_path}. Creating new index.")
                self._create_empty_index()

    def _create_empty_index(self):
        """Create empty IndexFlatIP for cosine similarity with normalized vectors"""
        self.index = faiss.IndexFlatIP(self.dimension)

    def add_vectors(self, vectors: np.ndarray, chunk_ids: List[str]) -> List[int]:
        """
        Add batch of dense vectors to FAISS index and record integer ID mappings in SQLite.
        Returns the assigned FAISS integer IDs.
        """
        if len(vectors) == 0:
            return []
        if len(vectors) != len(chunk_ids):
            raise ValueError(f"Vector count ({len(vectors)}) must match chunk ID count ({len(chunk_ids)})")

        with self._lock:
            start_id = self.index.ntotal
            faiss_ids = list(range(start_id, start_id + len(chunk_ids)))
            
            # Record mapping in SQLite
            mappings = list(zip(faiss_ids, chunk_ids))
            db.insert_vector_mappings(mappings)
            
            # Add to FAISS index
            self.index.add(vectors.astype(np.float32))
            
            # Persist index
            self.save()
            
            logger.info(f"Added {len(chunk_ids)} vectors to FAISS index (total: {self.index.ntotal})")
            return faiss_ids

    def search_vectors(self, query_vector: np.ndarray, top_k: int = 5) -> List[Tuple[int, float]]:
        """
        Search FAISS index with a single query vector.
        Returns list of (faiss_id, similarity_score) tuples.
        """
        with self._lock:
            if self.index is None or self.index.ntotal == 0:
                return []
            
            q_vec = query_vector.reshape(1, -1).astype(np.float32)
            actual_k = min(top_k, self.index.ntotal)
            scores, indices = self.index.search(q_vec, actual_k)
            
            results: List[Tuple[int, float]] = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0:  # FAISS returns -1 for empty slots
                    results.append((int(idx), float(score)))
            return results

    def search(self, query: Union[str, np.ndarray], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search interface supporting both string query and numpy vector.
        Resolves FAISS IDs against SQLite metadata for backward compatibility.
        """
        if isinstance(query, str):
            query_vector = embedding_service.embed_query(query)
        else:
            query_vector = query

        vector_results = self.search_vectors(query_vector, top_k=top_k)
        if not vector_results:
            return []

        faiss_ids = [fid for fid, _ in vector_results]
        score_map = {fid: score for fid, score in vector_results}

        # Resolve via SQLite
        chunk_records = db.get_chunks_by_faiss_ids(faiss_ids)

        legacy_results: List[Dict[str, Any]] = []
        for rec in chunk_records:
            fid = rec['faiss_id']
            score = score_map.get(fid, 0.0)
            legacy_results.append({
                "chunk_id": rec['chunk_id'],
                "document_id": rec['document_id'],
                "filename": rec['filename'],
                "type": rec['source_type'],
                "title": rec['document_title'] or rec['filename'],
                "content": rec['content'],
                "similarity_score": score,
                "chunk_index": rec['chunk_index'],
                "start_offset": rec['start_offset'],
                "end_offset": rec['end_offset']
            })
        return legacy_results

    def save(self):
        """Save FAISS binary index to disk"""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))
        logger.debug(f"Saved FAISS index to {self.index_path}")

    def clear(self):
        """Reset index to empty state and persist"""
        with self._lock:
            self._create_empty_index()
            self.save()
            logger.info("Cleared FAISS index")

    def get_stats(self) -> Dict[str, Any]:
        """Return vector store statistics"""
        total = self.index.ntotal if self.index else 0
        return {
            "total_documents": db.get_document_count(),
            "total_chunks": db.get_chunk_count(),
            "total_vectors": total,
            "index_size": total,
            "embedding_dimension": self.dimension,
            "model_name": self.model_name,
            "index_path": str(self.index_path)
        }


# Singleton instance
vector_store = VectorStore()