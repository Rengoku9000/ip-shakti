"""
SQLite Metadata and Provenance Storage for DrugVista / IP-SAKTI Sahayak
Phase 2A Knowledge Layer: Authoritative sources, version tracking, legal sections,
and deterministic citation anchors.
"""
import sqlite3
import json
import logging
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime

import config
from models import DocumentMetadata, ChunkMetadata, SourceRecord, SourceVersionRecord, DocumentSection

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path or config.DATABASE_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        return conn

    def get_connection(self) -> sqlite3.Connection:
        """Public alias to get SQLite connection context manager"""
        return self._get_connection()

    def _init_db(self):
        """Initialize database schema with Phase 1 & Phase 2A tables and columns"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # ---------------------------------------------------------------
            # 1. Authoritative Sources Table (Phase 2A)
            # ---------------------------------------------------------------
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                authority TEXT NOT NULL,
                source_type TEXT NOT NULL,
                jurisdiction TEXT NOT NULL,
                authority_level TEXT NOT NULL,
                official_url TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL
            );
            """)

            # ---------------------------------------------------------------
            # 2. Source Versions Table (Phase 2A)
            # ---------------------------------------------------------------
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS source_versions (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                version TEXT NOT NULL,
                publication_date TEXT,
                effective_from TEXT,
                effective_until TEXT,
                retrieved_at TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                local_path TEXT,
                verification_status TEXT NOT NULL DEFAULT 'verified',
                FOREIGN KEY (source_id) REFERENCES sources (id) ON DELETE CASCADE
            );
            """)

            # ---------------------------------------------------------------
            # 3. Documents Table (Phase 1 Baseline)
            # ---------------------------------------------------------------
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                content_hash TEXT UNIQUE NOT NULL,
                filename TEXT NOT NULL,
                source_type TEXT NOT NULL,
                source_uri TEXT,
                title TEXT,
                author TEXT,
                publication_date TEXT,
                ingested_at TEXT NOT NULL,
                language TEXT DEFAULT 'en',
                jurisdiction TEXT,
                version TEXT DEFAULT '1.0',
                raw_content TEXT,
                metadata_json TEXT
            );
            """)

            # ---------------------------------------------------------------
            # 4. Document Sections Table (Phase 2A)
            # ---------------------------------------------------------------
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_sections (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                parent_id TEXT,
                section_type TEXT NOT NULL,
                section_label TEXT NOT NULL,
                section_title TEXT,
                sequence INTEGER NOT NULL,
                FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE,
                FOREIGN KEY (parent_id) REFERENCES document_sections (id) ON DELETE CASCADE
            );
            """)

            # ---------------------------------------------------------------
            # 5. Chunks Table (Phase 1 Baseline)
            # ---------------------------------------------------------------
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                start_offset INTEGER NOT NULL,
                end_offset INTEGER NOT NULL,
                token_count INTEGER NOT NULL,
                content_hash TEXT NOT NULL,
                metadata_json TEXT,
                FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
            );
            """)

            # ---------------------------------------------------------------
            # 6. Vector Mapping Table (Phase 1 Baseline)
            # ---------------------------------------------------------------
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS vector_mapping (
                faiss_id INTEGER PRIMARY KEY,
                chunk_id TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                FOREIGN KEY (chunk_id) REFERENCES chunks (id) ON DELETE CASCADE
            );
            """)

            # ---------------------------------------------------------------
            # Dynamic Column Migration for Phase 2A Extensions
            # ---------------------------------------------------------------
            cursor.execute("PRAGMA table_info(documents);")
            doc_cols = {row[1] for row in cursor.fetchall()}
            if "source_id" not in doc_cols:
                cursor.execute("ALTER TABLE documents ADD COLUMN source_id TEXT REFERENCES sources (id);")
            if "source_version_id" not in doc_cols:
                cursor.execute("ALTER TABLE documents ADD COLUMN source_version_id TEXT REFERENCES source_versions (id);")
            if "authority_level" not in doc_cols:
                cursor.execute("ALTER TABLE documents ADD COLUMN authority_level TEXT;")

            cursor.execute("PRAGMA table_info(chunks);")
            chunk_cols = {row[1] for row in cursor.fetchall()}
            if "section_id" not in chunk_cols:
                cursor.execute("ALTER TABLE chunks ADD COLUMN section_id TEXT REFERENCES document_sections (id);")
            if "citation_anchor" not in chunk_cols:
                cursor.execute("ALTER TABLE chunks ADD COLUMN citation_anchor TEXT;")
            if "authority_level" not in chunk_cols:
                cursor.execute("ALTER TABLE chunks ADD COLUMN authority_level TEXT;")
            if "jurisdiction" not in chunk_cols:
                cursor.execute("ALTER TABLE chunks ADD COLUMN jurisdiction TEXT;")
            if "source_id" not in chunk_cols:
                cursor.execute("ALTER TABLE chunks ADD COLUMN source_id TEXT REFERENCES sources (id);")
            if "source_version_id" not in chunk_cols:
                cursor.execute("ALTER TABLE chunks ADD COLUMN source_version_id TEXT REFERENCES source_versions (id);")

            # Source status migrations for Phase 2A.1
            cursor.execute("PRAGMA table_info(sources);")
            source_cols = {row[1] for row in cursor.fetchall()}
            if "legal_status" not in source_cols:
                cursor.execute("ALTER TABLE sources ADD COLUMN legal_status TEXT DEFAULT 'IN_FORCE';")
            if "effective_status" not in source_cols:
                cursor.execute("ALTER TABLE sources ADD COLUMN effective_status TEXT;")
            if "status_checked_at" not in source_cols:
                cursor.execute("ALTER TABLE sources ADD COLUMN status_checked_at TEXT;")

            cursor.execute("PRAGMA table_info(source_versions);")
            ver_cols = {row[1] for row in cursor.fetchall()}
            if "legal_status" not in ver_cols:
                cursor.execute("ALTER TABLE source_versions ADD COLUMN legal_status TEXT DEFAULT 'IN_FORCE';")
            if "effective_status" not in ver_cols:
                cursor.execute("ALTER TABLE source_versions ADD COLUMN effective_status TEXT;")
            if "entry_into_force_date" not in ver_cols:
                cursor.execute("ALTER TABLE source_versions ADD COLUMN entry_into_force_date TEXT;")
            if "status_checked_at" not in ver_cols:
                cursor.execute("ALTER TABLE source_versions ADD COLUMN status_checked_at TEXT;")

            # ---------------------------------------------------------------
            # Indexes
            # ---------------------------------------------------------------
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_hash ON documents (content_hash);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_source ON documents (source_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_doc ON chunks (document_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_hash ON chunks (content_hash);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_section ON chunks (section_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_jurisdiction ON chunks (jurisdiction);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_authority ON chunks (authority_level);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_vector_chunk ON vector_mapping (chunk_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sources_jurisdiction ON sources (jurisdiction);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sources_type ON sources (source_type);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_versions_source ON source_versions (source_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sections_doc ON document_sections (document_id);")

            conn.commit()

    # -----------------------------------------------------------------------
    # Authoritative Source CRUD (Phase 2A)
    # -----------------------------------------------------------------------

    def insert_source(self, source: SourceRecord) -> str:
        """Insert or replace an authoritative source record"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO sources (
                id, name, authority, source_type, jurisdiction,
                authority_level, official_url, legal_status, effective_status,
                description, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                source.id, source.name, source.authority, source.source_type,
                source.jurisdiction, source.authority_level, source.official_url,
                getattr(source, "legal_status", "IN_FORCE"),
                getattr(source, "effective_status", None),
                source.description, source.created_at
            ))
            conn.commit()
            return source.id

    def get_source(self, source_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve source by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sources WHERE id = ? LIMIT 1;", (source_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_sources(self, jurisdiction: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve all sources with optional jurisdiction filter"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if jurisdiction:
                cursor.execute("SELECT * FROM sources WHERE jurisdiction = ? ORDER BY name ASC;", (jurisdiction,))
            else:
                cursor.execute("SELECT * FROM sources ORDER BY name ASC;")
            return [dict(r) for r in cursor.fetchall()]

    # -----------------------------------------------------------------------
    # Source Version CRUD (Phase 2A)
    # -----------------------------------------------------------------------

    def insert_source_version(self, version: SourceVersionRecord) -> str:
        """Insert or replace a source version record"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO source_versions (
                id, source_id, version, publication_date, effective_from,
                effective_until, entry_into_force_date, legal_status, effective_status,
                status_checked_at, retrieved_at, content_hash, local_path, verification_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                version.id, version.source_id, version.version, version.publication_date,
                version.effective_from, version.effective_until,
                getattr(version, "entry_into_force_date", None),
                getattr(version, "legal_status", "IN_FORCE"),
                getattr(version, "effective_status", None),
                getattr(version, "status_checked_at", None),
                version.retrieved_at, version.content_hash, version.local_path, version.verification_status
            ))
            conn.commit()
            return version.id

    def get_source_version(self, version_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve specific source version record"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM source_versions WHERE id = ? LIMIT 1;", (version_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_versions_for_source(self, source_id: str) -> List[Dict[str, Any]]:
        """Retrieve all versions of a source"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM source_versions WHERE source_id = ? ORDER BY retrieved_at DESC;", (source_id,))
            return [dict(r) for r in cursor.fetchall()]

    # -----------------------------------------------------------------------
    # Document Sections CRUD (Phase 2A)
    # -----------------------------------------------------------------------

    def insert_document_sections(self, sections: List[DocumentSection]) -> List[str]:
        """Insert structural sections of a legal document"""
        if not sections:
            return []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
            INSERT OR REPLACE INTO document_sections (
                id, document_id, parent_id, section_type, section_label,
                section_title, sequence
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
            """, [
                (
                    s.id, s.document_id, s.parent_id, s.section_type,
                    s.section_label, s.section_title, s.sequence
                ) for s in sections
            ])
            conn.commit()
            return [s.id for s in sections]

    def get_sections_for_document(self, document_id: str) -> List[Dict[str, Any]]:
        """Retrieve all structural sections for a document"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM document_sections WHERE document_id = ? ORDER BY sequence ASC;", (document_id,))
            return [dict(r) for r in cursor.fetchall()]

    def get_section(self, section_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific section by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM document_sections WHERE id = ? LIMIT 1;", (section_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    # -----------------------------------------------------------------------
    # Document & Chunk CRUD (Phase 1 Baseline + Phase 2A extensions)
    # -----------------------------------------------------------------------

    def get_document_by_hash(self, content_hash: str) -> Optional[Dict[str, Any]]:
        """Check if a document with this content hash already exists (deduplication)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM documents WHERE content_hash = ? LIMIT 1;", (content_hash,))
            row = cursor.fetchone()
            if row:
                data = dict(row)
                data['metadata'] = json.loads(data.get('metadata_json') or '{}')
                return data
            return None

    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve document record by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM documents WHERE id = ? LIMIT 1;", (doc_id,))
            row = cursor.fetchone()
            if row:
                data = dict(row)
                data['metadata'] = json.loads(data.get('metadata_json') or '{}')
                return data
            return None

    def insert_document(self, doc: DocumentMetadata) -> str:
        """Insert a document record into SQLite"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO documents (
                id, content_hash, filename, source_type, source_uri,
                title, author, publication_date, ingested_at,
                language, jurisdiction, version, raw_content,
                source_id, source_version_id, authority_level, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                doc.id, doc.content_hash, doc.filename, doc.source_type, doc.source_uri,
                doc.title, doc.author, doc.publication_date, doc.ingested_at,
                doc.language, doc.jurisdiction, doc.version, doc.raw_content,
                doc.source_id, doc.source_version_id, doc.authority_level,
                json.dumps(doc.metadata)
            ))
            conn.commit()
            return doc.id

    def insert_chunks(self, chunks: List[ChunkMetadata]) -> List[str]:
        """Insert a batch of chunk records into SQLite"""
        if not chunks:
            return []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
            INSERT OR REPLACE INTO chunks (
                id, document_id, chunk_index, content, start_offset,
                end_offset, token_count, content_hash, section_id,
                citation_anchor, authority_level, jurisdiction, source_id,
                source_version_id, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, [
                (
                    c.id, c.document_id, c.chunk_index, c.content, c.start_offset,
                    c.end_offset, c.token_count, c.content_hash, c.section_id,
                    c.citation_anchor, c.authority_level, c.jurisdiction,
                    getattr(c, "source_id", None) or c.metadata.get("source_id"),
                    getattr(c, "source_version_id", None) or c.metadata.get("source_version_id"),
                    json.dumps(c.metadata)
                ) for c in chunks
            ])
            conn.commit()
            return [c.id for c in chunks]

    def insert_vector_mappings(self, mappings: List[Tuple[int, str]]) -> None:
        """Insert mappings between FAISS integer IDs and chunk string IDs"""
        if not mappings:
            return
        now = datetime.utcnow().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
            INSERT OR REPLACE INTO vector_mapping (faiss_id, chunk_id, created_at)
            VALUES (?, ?, ?);
            """, [(faiss_id, chunk_id, now) for faiss_id, chunk_id in mappings])
            conn.commit()

    def get_chunks_by_faiss_ids(self, faiss_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Resolve FAISS integer IDs to enriched chunk, document, section, and source metadata.
        Preserves the order of input faiss_ids.
        """
        if not faiss_ids:
            return []

        placeholders = ",".join("?" for _ in faiss_ids)
        query = f"""
        SELECT 
            vm.faiss_id,
            c.id AS chunk_id,
            c.document_id,
            c.chunk_index,
            c.content,
            c.start_offset,
            c.end_offset,
            c.token_count,
            c.section_id,
            c.citation_anchor,
            COALESCE(c.authority_level, d.authority_level, s.authority_level, 'REFERENCE') AS authority_level,
            COALESCE(c.jurisdiction, d.jurisdiction, s.jurisdiction, 'INDIA') AS jurisdiction,
            c.metadata_json AS chunk_metadata_json,
            d.filename,
            d.source_type,
            d.title AS document_title,
            d.publication_date,
            d.language,
            d.source_id,
            d.source_version_id,
            d.metadata_json AS doc_metadata_json,
            s.name AS source_name,
            s.authority AS authority,
            s.official_url AS source_url,
            COALESCE(sv.legal_status, s.legal_status, 'IN_FORCE') AS legal_status,
            COALESCE(sv.effective_status, s.effective_status, 'IN_FORCE') AS effective_status,
            COALESCE(sv.verification_status, 'verified') AS verification_status,
            sv.effective_from,
            sv.effective_until,
            sv.entry_into_force_date,
            sv.status_checked_at,
            sec.section_label,
            sec.section_title
        FROM vector_mapping vm
        JOIN chunks c ON vm.chunk_id = c.id
        JOIN documents d ON c.document_id = d.id
        LEFT JOIN sources s ON d.source_id = s.id
        LEFT JOIN source_versions sv ON d.source_version_id = sv.id
        LEFT JOIN document_sections sec ON c.section_id = sec.id
        WHERE vm.faiss_id IN ({placeholders});
        """

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, faiss_ids)
            rows = cursor.fetchall()

            by_id = {}
            for r in rows:
                item = dict(r)
                item['chunk_metadata'] = json.loads(item.pop('chunk_metadata_json') or '{}')
                item['doc_metadata'] = json.loads(item.pop('doc_metadata_json') or '{}')
                by_id[item['faiss_id']] = item

            ordered = []
            for fid in faiss_ids:
                if fid in by_id:
                    ordered.append(by_id[fid])
            return ordered

    def get_document_count(self) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM documents;")
            return cursor.fetchone()[0]

    def get_chunk_count(self) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM chunks;")
            return cursor.fetchone()[0]

    def get_all_documents(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, filename, source_type, title, ingested_at, content_hash,
                   source_id, jurisdiction, authority_level
            FROM documents ORDER BY ingested_at DESC;
            """)
            return [dict(r) for r in cursor.fetchall()]

    def clear_knowledge_corpus(self):
        """Remove Phase 2 knowledge sources, sections, and chunks, preserving Phase 1 baseline"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = OFF;")
            cursor.execute("DELETE FROM vector_mapping WHERE chunk_id IN (SELECT id FROM chunks WHERE source_id IS NOT NULL OR section_id IS NOT NULL);")
            cursor.execute("DELETE FROM chunks WHERE source_id IS NOT NULL OR section_id IS NOT NULL;")
            cursor.execute("DELETE FROM document_sections;")
            cursor.execute("DELETE FROM documents WHERE source_id IS NOT NULL;")
            cursor.execute("DELETE FROM source_versions;")
            cursor.execute("DELETE FROM sources;")
            cursor.execute("PRAGMA foreign_keys = ON;")
            conn.commit()

    def clear_all(self):
        """Clear all tables (for testing or clean re-indexing)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vector_mapping;")
            cursor.execute("DELETE FROM chunks;")
            cursor.execute("DELETE FROM document_sections;")
            cursor.execute("DELETE FROM documents;")
            cursor.execute("DELETE FROM source_versions;")
            cursor.execute("DELETE FROM sources;")
            conn.commit()


# Singleton instance
db = DatabaseManager()
