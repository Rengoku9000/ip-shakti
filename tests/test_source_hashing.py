"""
Test Suite: Source Hashing and Integrity
Verifies SHA-256 calculation determinism, tamper-detection, and exact match
between files on disk and manifest content_hash values.
"""
import hashlib
import json
import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "drugvista" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import config
from knowledge_service import knowledge_service


class TestSourceHashing(unittest.TestCase):
    def test_all_manifest_sources_match_disk_hashes(self):
        """Every file in raw knowledge corpus must match its manifest content_hash"""
        with open(config.MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        for src in manifest["sources"]:
            src_id = src["source_id"]
            file_path = config.BASE_DIR / src["local_path"]
            self.assertTrue(file_path.exists(), f"Source file {file_path} not found")

            computed_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
            expected_hash = src["content_hash"]
            self.assertEqual(
                computed_hash, expected_hash,
                f"Hash mismatch for {src_id}: computed {computed_hash} != expected {expected_hash}"
            )

    def test_knowledge_service_verification(self):
        """Knowledge service verify_sources method should report all sources as valid"""
        results = knowledge_service.verify_sources()
        self.assertGreater(len(results), 0)
        for res in results:
            self.assertTrue(res["valid"], f"Source verification failed for {res.get('source_id')}: {res}")
            self.assertEqual(res["status"], "verified")

    def test_tamper_detection(self):
        """Modifying even 1 byte must produce a completely different SHA-256 hash"""
        sample_text = "Patents Act, 1970 - Section 3(p)"
        hash_orig = hashlib.sha256(sample_text.encode("utf-8")).hexdigest()

        # Mutate 1 character
        tampered_text = "Patents Act, 1970 - Section 3(q)"
        hash_tampered = hashlib.sha256(tampered_text.encode("utf-8")).hexdigest()

        self.assertNotEqual(hash_orig, hash_tampered)


if __name__ == "__main__":
    unittest.main()
