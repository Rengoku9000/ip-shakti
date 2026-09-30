"""
Test Suite: Source Versioning
Verifies that versions are tracked properly in SQLite, distinct versions are preserved,
and superseded versions are not silently overwritten.
"""
import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "drugvista" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from db import db
from models import VerificationStatus, SourceVersionRecord


class TestSourceVersioning(unittest.TestCase):
    def test_sources_and_versions_in_database(self):
        """Verify sources and source_versions are populated in SQLite"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, jurisdiction, authority_level FROM sources")
            sources = cursor.fetchall()

            cursor.execute("SELECT id, source_id, version, content_hash, verification_status FROM source_versions")
            versions = cursor.fetchall()

        self.assertGreaterEqual(len(sources), 7, "Expected at least 7 sources in database")
        self.assertGreaterEqual(len(versions), 7, "Expected at least 7 source versions in database")

        # Check foreign key link
        source_ids = {s[0] for s in sources}
        valid_statuses = {
            VerificationStatus.VERIFIED.value,
            VerificationStatus.VERIFIED_CURRENT.value,
            VerificationStatus.OFFICIAL_SECONDARY.value
        }
        for v in versions:
            ver_id, src_id, ver, chash, status = v
            self.assertIn(src_id, source_ids, f"Version {ver_id} references non-existent source {src_id}")
            self.assertIn(status, valid_statuses)
            self.assertEqual(len(chash), 64)

    def test_version_immutability_and_superseding(self):
        """Verify that inserting a new version for an existing source does not overwrite the old one"""
        test_source_id = "test_version_act"
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO sources (id, name, authority, source_type, jurisdiction, authority_level, official_url, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (test_source_id, "Test Act", "Govt", "STATUTE", "INDIA", "PRIMARY", "https://example.gov.in"))

            # Version 1 (superseded)
            cursor.execute("""
                INSERT OR REPLACE INTO source_versions (id, source_id, version, content_hash, verification_status, retrieved_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            """, ("ver_1", test_source_id, "2020.1", "hash1111111111111111111111111111111111111111111111111111111111111111", "superseded"))

            # Version 2 (current)
            cursor.execute("""
                INSERT OR REPLACE INTO source_versions (id, source_id, version, content_hash, verification_status, retrieved_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            """, ("ver_2", test_source_id, "2024.1", "hash2222222222222222222222222222222222222222222222222222222222222222", "verified"))
            conn.commit()

            # Retrieve both versions
            cursor.execute("SELECT id, version, verification_status FROM source_versions WHERE source_id = ? ORDER BY id", (test_source_id,))
            rows = cursor.fetchall()

            self.assertEqual(len(rows), 2, "Both versions must be retained in history")
            self.assertEqual(rows[0][0], "ver_1")
            self.assertEqual(rows[0][2], "superseded")
            self.assertEqual(rows[1][0], "ver_2")
            self.assertEqual(rows[1][2], "verified")

            # Clean up test rows
            cursor.execute("DELETE FROM source_versions WHERE source_id = ?", (test_source_id,))
            cursor.execute("DELETE FROM sources WHERE id = ?", (test_source_id,))
            conn.commit()


if __name__ == "__main__":
    unittest.main()
