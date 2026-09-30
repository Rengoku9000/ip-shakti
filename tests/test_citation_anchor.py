"""
Test Suite: Deterministic Citation Anchor Generation
Verifies that citation anchors are deterministic, structured, never hallucinated by LLM,
and accurately identify legal and regulatory structural positions.
"""
import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "drugvista" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from db import db
from structure_parser import structure_parser
from models import DocumentSection, SectionType


class TestCitationAnchor(unittest.TestCase):
    def test_anchor_generation_formats(self):
        """Test deterministic string formatting for various legal structures"""
        # Section anchor
        sec = DocumentSection(
            id="s1",
            document_id="doc1",
            section_type=SectionType.SECTION,
            section_label="Section 3(p)",
            section_title="Traditional Knowledge Exclusion",
            sequence=1
        )
        anchor_sec = structure_parser.generate_citation_anchor("Patents Act, 1970", sec)
        self.assertEqual(anchor_sec, "Patents Act, 1970 — Section 3(p)")

        # Article anchor
        art = DocumentSection(
            id="s2",
            document_id="doc2",
            section_type=SectionType.ARTICLE,
            section_label="Article 3",
            section_title="Mandatory Disclosure Requirement",
            sequence=2
        )
        anchor_art = structure_parser.generate_citation_anchor("WIPO Treaty on GRATK (2024)", art)
        self.assertEqual(anchor_art, "WIPO Treaty on GRATK (2024) — Article 3")

        # Rule anchor
        rule = DocumentSection(
            id="s3",
            document_id="doc3",
            section_type=SectionType.RULE,
            section_label="Rule 158-B",
            section_title="Ayurveda Proprietary Medicines",
            sequence=3
        )
        anchor_rule = structure_parser.generate_citation_anchor("Drugs and Cosmetics Rules, 1945", rule)
        self.assertEqual(anchor_rule, "Drugs and Cosmetics Rules, 1945 — Rule 158-B")

    def test_database_chunks_have_valid_citation_anchors(self):
        """Verify that all knowledge chunks stored in SQLite have valid citation anchors"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.id, c.citation_anchor, d.source_id, c.content AS text
                FROM chunks c
                JOIN documents d ON c.document_id = d.id
                WHERE d.source_id IS NOT NULL
            """)
            rows = cursor.fetchall()

        self.assertGreater(len(rows), 0, "No knowledge chunks found in database")
        for chunk_id, anchor, source_id, text in rows:
            self.assertIsNotNone(anchor, f"Chunk {chunk_id} has null citation_anchor")
            self.assertGreater(len(anchor), 5, f"Chunk {chunk_id} anchor is suspiciously short: '{anchor}'")
            self.assertIn("—", anchor, f"Chunk {chunk_id} anchor '{anchor}' missing em-dash separator")
            self.assertGreater(len(text), 10, f"Chunk {chunk_id} has empty or trivial text")


if __name__ == "__main__":
    unittest.main()
