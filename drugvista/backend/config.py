"""
Centralized Configuration for DrugVista
Resolves all filesystem paths relative to this module, ensuring consistent
behavior regardless of the working directory from which the application is launched.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from either backend dir or project root if present
load_dotenv()

# Base directories
BACKEND_DIR = Path(__file__).resolve().parent
BASE_DIR = BACKEND_DIR.parent
PROJECT_ROOT = BASE_DIR.parent

DATA_DIR = Path(os.getenv("DRUGVISTA_DATA_DIR", str(BASE_DIR / "data")))
STORAGE_DIR = Path(os.getenv("DRUGVISTA_STORAGE_DIR", str(BASE_DIR / "storage")))
LEGACY_DIR = BACKEND_DIR

# Ensure storage directory exists
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Knowledge Base Paths (Phase 2A)
KNOWLEDGE_DIR = DATA_DIR / "knowledge"
KNOWLEDGE_MANIFESTS_DIR = KNOWLEDGE_DIR / "manifests"
KNOWLEDGE_RAW_DIR = KNOWLEDGE_DIR / "raw"
KNOWLEDGE_PROCESSED_DIR = KNOWLEDGE_DIR / "processed"
MANIFEST_PATH = KNOWLEDGE_MANIFESTS_DIR / "sources.json"
CLASSIFICATION_BENCHMARK_PATH = KNOWLEDGE_DIR / "classification_benchmark_50.json"
REASONING_BENCHMARK_PATH = KNOWLEDGE_DIR / "reasoning_benchmark_30.json"
MULTILINGUAL_BENCHMARK_PATH = KNOWLEDGE_DIR / "multilingual_benchmark_30.json"

KNOWLEDGE_MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)
KNOWLEDGE_RAW_DIR.mkdir(parents=True, exist_ok=True)
KNOWLEDGE_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Database and Vector Store paths
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(STORAGE_DIR / "metadata.db")))
FAISS_INDEX_PATH = Path(os.getenv("FAISS_INDEX_PATH", str(STORAGE_DIR / "vector_index.faiss")))

# Legacy paths (for migration)
LEGACY_FAISS_PATH = BACKEND_DIR / "vector_index.faiss"
LEGACY_METADATA_PATH = BACKEND_DIR / "vector_metadata.pkl"

# Embedding Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "384"))

# Chunking Configuration
# Default target ~500-600 characters with 100 character overlap
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "600"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

# Retrieval Configuration
TOP_K = int(os.getenv("TOP_K", "5"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.20"))
AUTHORITY_WEIGHT_PRIMARY = float(os.getenv("AUTHORITY_WEIGHT_PRIMARY", "0.08"))
AUTHORITY_WEIGHT_SECONDARY = float(os.getenv("AUTHORITY_WEIGHT_SECONDARY", "0.04"))

# Classification Configuration (Phase 2B.1)
CLASSIFIER_CONFIDENCE_THRESHOLD = float(os.getenv("CLASSIFIER_CONFIDENCE_THRESHOLD", "0.50"))
JURISDICTION_CONFIDENCE_THRESHOLD = float(os.getenv("JURISDICTION_CONFIDENCE_THRESHOLD", "0.60"))
FORMULATION_CONFIDENCE_THRESHOLD = float(os.getenv("FORMULATION_CONFIDENCE_THRESHOLD", "0.50"))

# LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo").strip()

# Server Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
BACKEND_URL = os.getenv("BACKEND_URL", f"http://localhost:{API_PORT}").strip()
