"""
Test Suite: Knowledge Schema & Database Architecture
Verifies that SQLite tables, columns, foreign keys, and controlled vocabularies
for Phase 2A comply strictly with IP-SAKTI Sahayak specifications.
"""
import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "drugvista" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import config
from db import db
from models import (
    SourceType, AuthorityLevel, Jurisdiction, VerificationStatus, SectionType,
    SourceRecord, SourceVersionRecord, DocumentSection
)


class TestKnowledgeSchema(unittest.TestCase):
    def test_controlled_vocabularies(self):
        """Test controlled enum values defined for Phase 2A"""
        self.assertEqual(SourceType.STATUTE.value, "STATUTE")
        self.assertEqual(SourceType.RULE.value, "RULE")
        self.assertEqual(SourceType.REGULATION.value, "REGULATION")
        self.assertEqual(SourceType.TREATY.value, "TREATY")
        self.assertEqual(SourceType.PHARMACOPOEIA.value, "PHARMACOPOEIA")
        self.assertEqual(SourceType.FORMULARY.value, "FORMULARY")
        self.assertEqual(SourceType.OFFICIAL_GUIDANCE.value, "OFFICIAL_GUIDANCE")
        self.assertEqual(SourceType.REGISTRY.value, "REGISTRY")
        self.assertEqual(SourceType.CASE_LAW.value, "CASE_LAW")
        self.assertEqual(SourceType.CLASSICAL_TEXT.value, "CLASSICAL_TEXT")
        self.assertEqual(SourceType.GOVERNMENT_PUBLICATION.value, "GOVERNMENT_PUBLICATION")

        # Authority levels
        self.assertEqual(AuthorityLevel.PRIMARY.value, "PRIMARY")
        self.assertEqual(AuthorityLevel.OFFICIAL_SECONDARY.value, "OFFICIAL_SECONDARY")
        self.assertEqual(AuthorityLevel.REFERENCE.value, "REFERENCE")

        # Jurisdictions
        self.assertEqual(Jurisdiction.INDIA.value, "INDIA")
        self.assertEqual(Jurisdiction.INTERNATIONAL.value, "INTERNATIONAL")

        # Verification statuses
        self.assertEqual(VerificationStatus.VERIFIED.value, "verified")
        self.assertEqual(VerificationStatus.UNVERIFIED.value, "unverified")
        self.assertEqual(VerificationStatus.SUPERSEDED.value, "superseded")
        self.assertEqual(VerificationStatus.REJECTED.value, "rejected")

        # Section types
        self.assertEqual(SectionType.SECTION.value, "SECTION")
        self.assertEqual(SectionType.ARTICLE.value, "ARTICLE")
        self.assertEqual(SectionType.CHAPTER.value, "CHAPTER")
        self.assertEqual(SectionType.RULE.value, "RULE")
        self.assertEqual(SectionType.CLAUSE.value, "CLAUSE")
        self.assertEqual(SectionType.SCHEDULE.value, "SCHEDULE")

    def test_database_tables_exist(self):
        """Verify all Phase 2A tables exist in SQLite"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = {row[0] for row in cursor.fetchall()}

        required_tables = {
            "documents", "chunks", "vector_mapping",
            "sources", "source_versions", "document_sections"
        }
        for table in required_tables:
            self.assertIn(table, tables, f"Expected table '{table}' not found in database.")

    def test_documents_table_has_provenance_columns(self):
        """Verify documents table contains Phase 2A provenance columns"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(documents);")
            cols = {row[1] for row in cursor.fetchall()}

        for col in ["source_id", "source_version_id", "authority_level", "jurisdiction"]:
            self.assertIn(col, cols, f"Column '{col}' missing from documents table.")

    def test_chunks_table_has_citation_columns(self):
        """Verify chunks table contains Phase 2A citation anchor columns"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(chunks);")
            cols = {row[1] for row in cursor.fetchall()}

        for col in ["section_id", "citation_anchor", "source_id", "source_version_id", "authority_level", "jurisdiction"]:
            self.assertIn(col, cols, f"Column '{col}' missing from chunks table.")

    def test_source_and_version_models(self):
        """Verify Pydantic models validate correctly"""
        src = SourceRecord(
            id="test_src",
            name="Test Source",
            authority="Government of India",
            source_type=SourceType.STATUTE,
            jurisdiction=Jurisdiction.INDIA,
            authority_level=AuthorityLevel.PRIMARY,
            official_url="https://example.gov.in"
        )
        self.assertEqual(src.id, "test_src")
        self.assertEqual(src.authority_level, AuthorityLevel.PRIMARY)

        ver = SourceVersionRecord(
            id="ver_01",
            source_id="test_src",
            version="1.0",
            content_hash="abc123hash",
            verification_status=VerificationStatus.VERIFIED
        )
        self.assertEqual(ver.verification_status, VerificationStatus.VERIFIED)


if __name__ == "__main__":
    unittest.main()
