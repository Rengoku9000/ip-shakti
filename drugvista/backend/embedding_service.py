"""
Embedding Service for DrugVista
Wraps SentenceTransformer with lazy model loading, L2-normalization, and thread safety.
"""
import threading
import logging
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
import config

logger = logging.getLogger(__name__)


class EmbeddingService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EmbeddingService, cls).__new__(cls)
                cls._instance._model = None
            return cls._instance

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            with self._lock:
                if self._model is None:
                    logger.info(f"Loading embedding model: {config.EMBEDDING_MODEL}")
                    self._model = SentenceTransformer(config.EMBEDDING_MODEL)
                    logger.info("Embedding model loaded successfully")
        return self._model

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generate normalized float32 embeddings for a list of texts"""
        if not texts:
            return np.empty((0, config.EMBEDDING_DIMENSION), dtype=np.float32)
        embeddings = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return np.asarray(embeddings, dtype=np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        """Generate normalized float32 embedding for a single query"""
        return self.embed_texts([query])[0]


# Singleton instance
embedding_service = EmbeddingService()
