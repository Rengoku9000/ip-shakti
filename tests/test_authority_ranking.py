"""
Test Suite: Authority Level Ranking & Weighting
Verifies that PRIMARY sources receive configured authority boosts
(PRIMARY > OFFICIAL_SECONDARY > REFERENCE) and that authority-level filtering works.
"""
import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "drugvista" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import config
from retriever import retriever
from models import AuthorityLevel, RetrievedChunk


class TestAuthorityRanking(unittest.TestCase):
    def test_authority_boost_weighting(self):
        """Verify that score adjustment applies authority bonus correctly"""
        base_score = 0.75

        # Primary chunk
        chunk_primary = RetrievedChunk(
            chunk_id="c1", document_id="d1", content="Content", score=base_score,
            filename="act.txt", source_type="STATUTE", chunk_index=0, start_offset=0, end_offset=7,
            title="Patents Act", section_label="Section 3", authority_level="PRIMARY"
        )
        boosted_primary = retriever._apply_authority_boost(chunk_primary)
        expected_primary = min(1.0, round(base_score + config.AUTHORITY_WEIGHT_PRIMARY, 4))
        self.assertEqual(boosted_primary.score, expected_primary)

        # Official secondary chunk
        chunk_sec = RetrievedChunk(
            chunk_id="c2", document_id="d2", content="Content", score=base_score,
            filename="guidance.txt", source_type="OFFICIAL_GUIDANCE", chunk_index=0, start_offset=0, end_offset=7,
            title="Ayush Guidance", section_label="Standards", authority_level="OFFICIAL_SECONDARY"
        )
        boosted_sec = retriever._apply_authority_boost(chunk_sec)
        expected_sec = min(1.0, round(base_score + config.AUTHORITY_WEIGHT_SECONDARY, 4))
        self.assertEqual(boosted_sec.score, expected_sec)

        # Reference chunk
        chunk_ref = RetrievedChunk(
            chunk_id="c3", document_id="d3", content="Content", score=base_score,
            filename="tkdl.txt", source_type="GOVERNMENT_PUBLICATION", chunk_index=0, start_offset=0, end_offset=7,
            title="TKDL Reference", section_label="Scope", authority_level="REFERENCE"
        )
        boosted_ref = retriever._apply_authority_boost(chunk_ref)
        self.assertEqual(boosted_ref.score, base_score)

    def test_authority_level_filter(self):
        """When authority_level=PRIMARY is specified, only PRIMARY chunks are returned"""
        results = retriever.retrieve(
            query="traditional knowledge ayurveda patent",
            authority_level="PRIMARY",
            top_k=5
        )
        self.assertGreater(len(results), 0)
        for chunk in results:
            if chunk.authority_level:
                self.assertEqual(
                    chunk.authority_level, "PRIMARY",
                    f"Chunk {chunk.id} with authority_level '{chunk.authority_level}' returned despite PRIMARY filter"
                )


if __name__ == "__main__":
    unittest.main()
