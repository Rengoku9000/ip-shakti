"""
Document Embedding and Index Creation CLI
Uses centralized paths and IngestionService with chunking and SQLite metadata.
"""
import sys
import logging
from pathlib import Path

# Add backend directory to sys.path to allow standalone invocation
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import config
from migration import run_migration
from vector_store import vector_store
from retriever import retriever

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_vector_index() -> bool:
    """Create vector index and SQLite metadata from documents"""
    logger.info("Initializing vector index and SQLite database")
    try:
        summary = run_migration(force_clean=True)
        stats = vector_store.get_stats()
        logger.info(f"Vector index created successfully: {stats['total_documents']} documents, {stats['total_chunks']} chunks, {stats['total_vectors']} vectors")
        return stats['total_documents'] > 0
    except Exception as e:
        logger.error(f"Failed to create vector index: {e}", exc_info=True)
        return False


def test_search():
    """Test search functionality across migrated chunks"""
    logger.info("Testing semantic search across chunks...")
    test_queries = [
        "Alzheimer's disease treatment",
        "cancer immunotherapy",
        "drug toxicity",
        "clinical trial results",
        "market analysis"
    ]

    for q in test_queries:
        results = retriever.retrieve(q, top_k=3)
        logger.info(f"Query: '{q}' -> {len(results)} chunks")
        for i, r in enumerate(results):
            logger.info(f"  {i+1}. {r.filename} [Chunk {r.chunk_index}] (score: {r.score:.3f})")


if __name__ == "__main__":
    success = create_vector_index()
    if success:
        test_search()
        logger.info("Setup complete! Knowledge base is ready.")
    else:
        logger.error("Setup failed. Please check the data folder and try again.")
        sys.exit(1)