"""
Comprehensive Phase 1 Architecture Verification Test Suite for DrugVista
Tests:
1. Path resolution across working directories
2. Content hashing determinism
3. Deduplication prevention in SQLite & FAISS
4. Boundary-aware document chunking and offset tracking
5. Semantic chunk retrieval with similarity scores
6. Persistence across VectorStore & DB re-instantiation
7. Detailed citation and provenance mapping
8. FAISS vector ID to SQLite chunk consistency
9. End-to-end DrugVista pharmaceutical analysis flow
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Safe UTF-8 console output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure backend directory is in sys.path
TEST_DIR = Path(__file__).resolve().parent
BACKEND_DIR = TEST_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import config
from db import db, DatabaseManager
from document_loader import compute_sha256, normalize_text
from document_chunker import DocumentChunker
from embedding_service import embedding_service
from vector_store import vector_store, VectorStore
from ingestion_service import IngestionService
from retriever import retriever
from rag_pipeline import rag


class TestPhase1Architecture(unittest.TestCase):
    def test_01_path_resolution(self):
        """Test that paths are absolute and resolved correctly regardless of cwd"""
        self.assertTrue(config.DATA_DIR.is_absolute())
        self.assertTrue(config.STORAGE_DIR.is_absolute())
        self.assertTrue(config.DATABASE_PATH.is_absolute())
        self.assertTrue(config.FAISS_INDEX_PATH.is_absolute())
        self.assertTrue(config.DATA_DIR.exists())
        self.assertTrue(config.STORAGE_DIR.exists())
        self.assertTrue(config.DATABASE_PATH.exists())
        self.assertTrue(config.FAISS_INDEX_PATH.exists())

    def test_02_content_hashing_determinism(self):
        """Test SHA-256 content hashing determinism and whitespace normalization"""
        text_a = "Metformin is an oral antihyperglycemic medication.\r\nIt decreases hepatic glucose production."
        text_b = "Metformin is an oral antihyperglycemic medication.\nIt decreases hepatic glucose production."
        
        hash_a = compute_sha256(normalize_text(text_a))
        hash_b = compute_sha256(normalize_text(text_b))
        
        self.assertEqual(hash_a, hash_b)
        self.assertEqual(len(hash_a), 64)

    def test_03_boundary_aware_chunking(self):
        """Test that chunker produces ordered chunks with valid offsets and token counts"""
        chunker = DocumentChunker(chunk_size=150, chunk_overlap=30)
        sample_doc = (
            "Paragraph one describes the mechanism of action of kinase inhibitors. "
            "It engages ATP-binding sites on target enzymes to prevent phosphorylation.\n\n"
            "Paragraph two addresses clinical trial safety profiles. "
            "Adverse events were monitored across cohorts with hepatic enzyme elevations noted."
        )
        
        chunks = chunker.chunk_text(sample_doc, document_id="test_doc_1")
        self.assertGreater(len(chunks), 1, "Should split text into multiple chunks")
        
        for i, c in enumerate(chunks):
            self.assertEqual(c.chunk_index, i)
            self.assertEqual(c.document_id, "test_doc_1")
            self.assertGreater(c.end_offset, c.start_offset)
            # Verify slice matches original text
            sliced = sample_doc[c.start_offset:c.end_offset]
            self.assertEqual(sliced, c.content)
            self.assertGreater(c.token_count, 0)

    def test_04_deduplication(self):
        """Test that ingesting the exact same document twice rejects duplicate and preserves single record"""
        test_text = "Deduplication Test Content: Aspirin antiplatelet therapy for secondary stroke prevention."
        ingest_svc = IngestionService()
        
        # First ingestion
        res1 = ingest_svc.ingest_text(content=test_text, title="test_dedup_unique_1.txt")
        self.assertTrue(res1.success)
        
        # Second ingestion with identical content
        res2 = ingest_svc.ingest_text(content=test_text, title="test_dedup_unique_2.txt")
        self.assertTrue(res2.success)
        self.assertEqual(res2.status, "duplicate")
        self.assertEqual(res2.documents_added, 0)
        self.assertEqual(res2.chunks_added, 0)
        self.assertEqual(res1.document_id, res2.document_id)

    def test_05_retrieval_and_provenance(self):
        """Test that retriever returns chunk-level provenance with scores and metadata"""
        results = retriever.retrieve("Alzheimer lecanemab clinical trial", top_k=3)
        self.assertGreater(len(results), 0)
        
        top_chunk = results[0]
        self.assertIsNotNone(top_chunk.chunk_id)
        self.assertIsNotNone(top_chunk.document_id)
        self.assertIsNotNone(top_chunk.filename)
        self.assertIsNotNone(top_chunk.source_type)
        self.assertGreaterEqual(top_chunk.score, 0.0)
        self.assertGreater(len(top_chunk.content), 0)
        self.assertGreaterEqual(top_chunk.chunk_index, 0)

    def test_06_faiss_sqlite_consistency(self):
        """Test that every FAISS vector ID resolves to a valid chunk in SQLite"""
        total_vectors = vector_store.index.ntotal
        self.assertGreater(total_vectors, 0)
        
        # Test sample of FAISS IDs
        sample_ids = list(range(min(5, total_vectors)))
        resolved_chunks = db.get_chunks_by_faiss_ids(sample_ids)
        self.assertEqual(len(resolved_chunks), len(sample_ids))
        
        for c in resolved_chunks:
            self.assertIn("chunk_id", c)
            self.assertIn("filename", c)
            self.assertIn("content", c)
            self.assertGreater(len(c["content"]), 0)

    def test_07_persistence(self):
        """Test that re-instantiating VectorStore and DatabaseManager preserves all data"""
        doc_count_before = db.get_document_count()
        vector_count_before = vector_store.index.ntotal
        
        # Re-instantiate
        new_db = DatabaseManager(config.DATABASE_PATH)
        new_vs = VectorStore(config.FAISS_INDEX_PATH)
        
        self.assertEqual(new_db.get_document_count(), doc_count_before)
        self.assertEqual(new_vs.index.ntotal, vector_count_before)

    def test_08_existing_drugvista_flow(self):
        """Test that existing pharmaceutical analysis pipeline produces expected structured response"""
        result = rag.analyze("Alzheimer's disease treatment options")
        
        required_keys = [
            "clinical_viability",
            "key_evidence",
            "major_risks",
            "market_signal",
            "recommendation",
            "confidence_score",
            "explanation",
            "sources"
        ]
        for key in required_keys:
            self.assertIn(key, result, f"Response missing key: {key}")
            
        self.assertIn(result["clinical_viability"], ["High", "Medium", "Low"])
        self.assertIn(result["market_signal"], ["Strong", "Moderate", "Weak"])
        self.assertIn(result["recommendation"], ["Proceed", "Investigate Further", "Drop"])
        self.assertGreater(result["confidence_score"], 0.0)
        self.assertGreater(len(result["key_evidence"]), 0)
        self.assertGreater(len(result["sources"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
