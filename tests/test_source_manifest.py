"""
Test Suite: Source Manifest Validation
Verifies that sources.json is valid, comprehensive, adheres to schema constraints,
and contains all required metadata fields for legal/regulatory sources.
"""
import json
import re
import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "drugvista" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import config
from models import SourceType, AuthorityLevel, Jurisdiction, VerificationStatus


class TestSourceManifest(unittest.TestCase):
    def setUp(self):
        self.manifest_path = config.MANIFEST_PATH
        self.assertTrue(self.manifest_path.exists(), f"Manifest file missing: {self.manifest_path}")
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            self.manifest = json.load(f)

    def test_manifest_top_level_fields(self):
        """Verify manifest root structure"""
        self.assertIn("manifest_version", self.manifest)
        self.assertIn("corpus_name", self.manifest)
        self.assertIn("sources", self.manifest)
        self.assertIsInstance(self.manifest["sources"], list)
        self.assertGreater(len(self.manifest["sources"]), 0)

    def test_each_source_has_required_fields(self):
        """Verify all sources possess required fields with non-empty values"""
        required_fields = [
            "source_id", "title", "source_type", "authority",
            "authority_level", "jurisdiction", "language",
            "version", "source_url", "content_hash", "status", "local_path"
        ]
        valid_types = {t.value for t in SourceType}
        valid_authorities = {a.value for a in AuthorityLevel}
        valid_jurisdictions = {j.value for j in Jurisdiction}
        valid_statuses = {s.value for s in VerificationStatus}

        sha256_pattern = re.compile(r"^[a-f0-9]{64}$")

        for src in self.manifest["sources"]:
            src_id = src.get("source_id", "UNKNOWN")
            for field in required_fields:
                self.assertIn(field, src, f"Source '{src_id}' missing field '{field}'")
                self.assertIsNotNone(src[field], f"Source '{src_id}' field '{field}' is None")
                self.assertTrue(str(src[field]).strip(), f"Source '{src_id}' field '{field}' is empty")

            # Validate enum values
            self.assertIn(src["source_type"], valid_types, f"Invalid source_type in {src_id}")
            self.assertIn(src["authority_level"], valid_authorities, f"Invalid authority_level in {src_id}")
            self.assertIn(src["jurisdiction"], valid_jurisdictions, f"Invalid jurisdiction in {src_id}")
            self.assertIn(src["status"], valid_statuses, f"Invalid status in {src_id}")

            # Validate SHA-256 pattern
            self.assertTrue(
                sha256_pattern.match(src["content_hash"]),
                f"Source '{src_id}' content_hash is not a valid 64-character lowercase SHA-256 hex string"
            )

            # Validate URL format
            self.assertTrue(
                src["source_url"].startswith("http://") or src["source_url"].startswith("https://"),
                f"Source '{src_id}' source_url must start with http:// or https://"
            )

            # Validate local file exists
            file_path = config.BASE_DIR / src["local_path"]
            self.assertTrue(file_path.exists(), f"Source file does not exist at {file_path}")

    def test_no_cross_jurisdiction_in_sources(self):
        """Verify sources strictly specify either INDIA or INTERNATIONAL, never both or ambiguous"""
        for src in self.manifest["sources"]:
            self.assertIn(src["jurisdiction"], ["INDIA", "INTERNATIONAL"])


if __name__ == "__main__":
    unittest.main()
