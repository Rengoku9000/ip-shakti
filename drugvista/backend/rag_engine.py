"""
Domain-Agnostic Generic RAG Engine for DrugVista
Decouples retrieval, context assembly, LLM prompting, and citation provenance
from domain-specific business rules.
"""
from typing import List, Dict, Any, Optional
import logging

from models import RetrievedChunk, CitationSource
from retriever import Retriever, retriever as default_retriever
from llm_provider import LLMProvider, get_llm_provider

logger = logging.getLogger(__name__)


class RAGEngine:
    def __init__(self, retriever: Optional[Retriever] = None, llm: Optional[LLMProvider] = None):
        self.retriever = retriever or default_retriever
        self.llm = llm or get_llm_provider()

    def retrieve(self, query: str, top_k: Optional[int] = None, threshold: Optional[float] = None) -> List[RetrievedChunk]:
        """Perform semantic retrieval and return structured chunk records with provenance"""
        return self.retriever.retrieve(query, top_k=top_k, threshold=threshold)

    def assemble_context(self, chunks: List[RetrievedChunk], max_chars_per_chunk: int = 800) -> str:
        """
        Assemble chunks into a structured prompt context block.
        Includes document filename, chunk index, and offsets.
        """
        if not chunks:
            return "No relevant context found in knowledge base."

        context_parts = []
        for i, chunk in enumerate(chunks):
            content_preview = chunk.content[:max_chars_per_chunk]
            context_parts.append(
                f"[Source {i+1} | File: {chunk.filename} | Chunk {chunk.chunk_index} | Sim: {chunk.score:.2f}]:\n{content_preview}"
            )
        return "\n\n".join(context_parts)

    def build_citations(self, chunks: List[RetrievedChunk]) -> List[CitationSource]:
        """
        Construct rich, structured citation records linking responses
        directly to exact chunks, documents, and similarity scores.
        """
        citations: List[CitationSource] = []
        for chunk in chunks:
            preview = chunk.content[:150] + ("..." if len(chunk.content) > 150 else "")
            citations.append(
                CitationSource(
                    source_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    chunk_id=chunk.chunk_id,
                    chunk_index=chunk.chunk_index,
                    filename=chunk.filename,
                    source_type=chunk.source_type,
                    score=round(chunk.score, 4),
                    text_preview=preview
                )
            )
        return citations

    def generate(self, prompt: str, temperature: float = 0.3) -> Optional[str]:
        """Generate response via configured LLM provider"""
        return self.llm.generate(prompt, temperature=temperature)

    @property
    def is_online(self) -> bool:
        return self.llm.is_online


# Singleton instance
rag_engine = RAGEngine()
