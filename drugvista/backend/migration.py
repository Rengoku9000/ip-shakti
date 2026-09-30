"""
Migration Utility for DrugVista
Extracts legacy pickle records, restores missing paper files to data/papers/,
and performs clean, chunked, deduplicated re-indexing into SQLite and FAISS.
"""
import os
import pickle
import logging
from pathlib import Path
from typing import Dict, Any

import config
from db import db
from vector_store import vector_store
from ingestion_service import ingestion_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def restore_legacy_papers_to_disk() -> int:
    """
    Recover missing paper documents stored only in legacy vector_metadata.pkl
    and write them to data/papers/ so repository dataset on disk is complete.
    """
    legacy_pkl = config.LEGACY_METADATA_PATH
    if not legacy_pkl.exists():
        logger.info(f"No legacy pickle file found at {legacy_pkl}")
        return 0

    papers_dir = config.DATA_DIR / "papers"
    papers_dir.mkdir(parents=True, exist_ok=True)

    recovered = 0
    try:
        with open(legacy_pkl, "rb") as f:
            data = pickle.load(f)
            metadata = data.get("metadata", [])

        # Find documents of type 'paper' with .txt extension
        for item in metadata:
            fname = item.get("filename", "")
            ftype = item.get("type", "")
            content = item.get("content", "")

            if ftype == "paper" and fname.endswith(".txt") and len(content) > 10:
                target_file = papers_dir / fname
                if not target_file.exists():
                    with open(target_file, "w", encoding="utf-8") as out_f:
                        out_f.write(content)
                    logger.info(f"Restored legacy paper to disk: {target_file}")
                    recovered += 1

    except Exception as e:
        logger.error(f"Error reading legacy pickle: {e}")

    return recovered


def run_migration(force_clean: bool = False) -> Dict[str, Any]:
    """
    Run full migration:
    1. Restore missing papers to disk.
    2. Optionally clean database & FAISS if force_clean=True.
    3. Ingest data/papers, data/clinical_trials, and data/market.
    """
    logger.info("Starting DrugVista Phase 1 Migration...")

    # Step 1: Restore papers from legacy pickle if needed
    restored = restore_legacy_papers_to_disk()
    if restored > 0:
        logger.info(f"Restored {restored} paper(s) to data/papers/")

    if force_clean:
        logger.info("force_clean requested: Clearing existing SQLite tables and FAISS index")
        db.clear_all()
        vector_store.clear()

    # Step 2: Ingest all folders
    summary = {
        "restored_papers": restored,
        "papers": {"total_files": 0, "ingested": 0, "duplicates": 0, "chunks": 0},
        "clinical_trials": {"total_files": 0, "ingested": 0, "duplicates": 0, "chunks": 0},
        "market": {"total_files": 0, "ingested": 0, "duplicates": 0, "chunks": 0},
    }

    folders = [
        ("papers", "paper"),
        ("clinical_trials", "clinical_trial"),
        ("market", "market")
    ]

    for sub_dir, doc_type in folders:
        target_dir = config.DATA_DIR / sub_dir
        if target_dir.exists():
            res = ingestion_service.ingest_directory(target_dir, doc_type=doc_type)
            summary[sub_dir] = res
            logger.info(f"Directory {sub_dir}: {res['ingested']} ingested, {res['duplicates']} duplicates, {res['chunks']} chunks")

    stats = vector_store.get_stats()
    summary["final_stats"] = stats
    logger.info(f"Migration complete! Final stats: {stats}")
    return summary


if __name__ == "__main__":
    import sys
    force = "--clean" in sys.argv
    run_migration(force_clean=force)
