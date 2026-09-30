"""
RAG Pipeline Façade for DrugVista
Maintains 100% backward compatibility with existing callers while delegating
to the modular domain-agnostic RAGEngine and PharmaceuticalAnalyzer.
"""
import logging
from typing import Dict, Any, Optional

import config
from vector_store import vector_store, VectorStore
from rag_engine import rag_engine, RAGEngine
from domain.pharmaceutical import PharmaceuticalAnalyzer
from prompts import PromptTemplates

logger = logging.getLogger(__name__)


class RAGPipeline:
    def __init__(self, engine: Optional[RAGEngine] = None):
        """Initialize RAG pipeline façade with underlying modular services"""
        self.rag_engine = engine or rag_engine
        self.vector_store = self.rag_engine.retriever.vector_store if hasattr(self.rag_engine.retriever, "vector_store") else vector_store
        self.analyzer = PharmaceuticalAnalyzer(self.rag_engine)
        self.prompts = PromptTemplates()
        logger.info("RAGPipeline initialized with domain-agnostic engine")

    def analyze(self, query: str) -> Dict[str, Any]:
        """Execute query analysis via the pharmaceutical domain analyzer"""
        return self.analyzer.analyze(query)


# Default pipeline instance
rag = RAGPipeline()