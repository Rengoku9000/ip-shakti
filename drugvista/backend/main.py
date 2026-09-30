"""
FastAPI Backend for DRUGVISTA
Serves RAG analysis, multi-format document ingestion, and vector store statistics.
"""
import os
import sys
import logging
from pathlib import Path
from typing import Optional

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import config
from models import AnalysisRequest, AnalysisResponse, IngestResponse
from rag_pipeline import rag
from ingestion_service import ingestion_service
from vector_store import vector_store
from retriever import retriever
from classification import query_classifier, retrieval_router
from reasoning import reasoning_engine
from multilingual import query_normalizer, answer_localizer, SupportedLanguage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="DRUGVISTA API", version="2.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "service": "DRUGVISTA API",
        "version": "2.0 (Phase 1 Refactor)",
        "status": "operational",
        "storage": str(config.STORAGE_DIR)
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "rag_initialized": rag is not None,
        "database_connected": config.DATABASE_PATH.exists()
    }


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest):
    """
    Main analysis endpoint with multi-step reasoning over retrieved chunks.
    """
    if not rag:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")

    if not request.query or len(request.query.strip()) < 3:
        raise HTTPException(status_code=400, detail="Query too short (minimum 3 characters required)")

    try:
        # 1. Multilingual Query Normalization (Phase 2C)
        ml_query = query_normalizer.normalize(request.query, explicit_language=request.language)

        # 2. Classification & Routing (Phase 2B.1) on canonical normalized query
        classification = query_classifier.classify(ml_query.normalized_text)
        routing_plan = retrieval_router.create_routing_plan(classification)

        # 3. Multi-track Retrieval (Phase 2A & 2B.1)
        retrieved_by_track = retrieval_router.execute_routing(routing_plan, retriever, top_k=5)

        # 4. Evidence-Based Reasoning (Phase 2B.2) over authoritative evidence
        reasoning_result = reasoning_engine.reason(
            query=ml_query.normalized_text,
            classification=classification,
            routing_plan=routing_plan,
            retrieved_by_track=retrieved_by_track
        )

        # 5. Answer Localization (Phase 2C)
        target_lang = (request.language or ml_query.detected_language or SupportedLanguage.ENGLISH.value).upper()
        if target_lang not in {SupportedLanguage.HINDI.value, SupportedLanguage.KANNADA.value}:
            target_lang = SupportedLanguage.ENGLISH.value

        localized_reasoning, localization_meta = answer_localizer.localize(
            reasoning=reasoning_result,
            target_language=target_lang
        )

        # 6. Pharmaceutical baseline analyze (preserved 100% backward compatible)
        result = rag.analyze(ml_query.normalized_text)

        # 7. Add additive classification, routing, evidence, reasoning, and multilingual fields
        result["query_classification"] = classification.to_dict()
        result["routing_plan"] = routing_plan.to_dict()
        result["reasoning"] = localized_reasoning.to_dict()
        result["evidence"] = [e.to_dict() for e in localized_reasoning.evidence_items]
        result["citations"] = [c.dict() if hasattr(c, "dict") else c for c in localized_reasoning.citations]
        result["language"] = {
            "detected": ml_query.detected_language,
            "confidence": ml_query.confidence,
            "script": ml_query.script,
            "is_mixed": ml_query.is_mixed
        }
        result["normalized_query"] = ml_query.normalized_text
        result["localization"] = localization_meta

        logger.info(f"Analysis completed successfully (lang: {ml_query.detected_language} -> {target_lang})")
        return result
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    file: UploadFile = File(...),
    doc_type: str = Form(default="document"),
    description: Optional[str] = Form(default=None)
):
    """
    Ingest multi-format document (.txt, .csv, .json, .pdf, .docx)
    with content hashing, deduplication, chunking, and SQLite+FAISS persistence.
    """
    file_ext = os.path.splitext(file.filename)[1].lower()
    allowed_exts = {'.txt', '.csv', '.json', '.pdf', '.docx'}
    if file_ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file_ext}' not supported. Allowed: {', '.join(allowed_exts)}"
        )

    try:
        content = await file.read()
        res = ingestion_service.ingest_bytes(
            content=content,
            filename=file.filename,
            doc_type=doc_type,
            description=description
        )

        if not res.success and res.status == "error":
            raise HTTPException(status_code=400, detail=res.message)

        return res

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ingest failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


class TextIngestRequest(BaseModel):
    content: str
    doc_type: str = "text_note"
    title: Optional[str] = None


@app.post("/ingest-text", response_model=IngestResponse)
async def ingest_text(request: TextIngestRequest):
    """
    Ingest direct text entry with deduplication and chunking.
    """
    if len(request.content.strip()) < 10:
        raise HTTPException(status_code=400, detail="Content too short (minimum 10 characters required)")

    try:
        res = ingestion_service.ingest_text(
            content=request.content,
            title=request.title,
            doc_type=request.doc_type
        )
        if not res.success and res.status == "error":
            raise HTTPException(status_code=400, detail=res.message)
        return res
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text ingest failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
def get_stats():
    """Get vector store and SQLite metadata statistics"""
    return vector_store.get_stats()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=config.API_HOST, port=config.API_PORT, reload=False)
