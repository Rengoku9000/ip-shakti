"""
Test Suite: Jurisdiction Detection and Retrieval Routing (Phase 2B.1)
Verifies strict isolation of India vs International jurisdictions,
dual-track routing for comparative mixed queries, and honest handling of
unspecified queries without silent assumptions.
"""
import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "drugvista" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from retriever import retriever
from classification import (
    query_classifier,
    retrieval_router,
    jurisdiction_classifier,
    JurisdictionChoice
)


class TestJurisdictionRouting(unittest.TestCase):
    def test_single_jurisdiction_india_routing(self):
        """India queries route strictly to India evidence track with zero international leakage"""
        query = "What are the patentability criteria under Section 3(p) of the Indian Patents Act?"
        res = query_classifier.classify(query)
        self.assertEqual(res.jurisdiction.primary, JurisdictionChoice.INDIA.value)
        self.assertFalse(res.jurisdiction.mixed)

        plan = retrieval_router.create_routing_plan(res)
        self.assertEqual(len(plan.tracks), 1)
        self.assertEqual(plan.tracks[0].jurisdiction, "INDIA")
        self.assertFalse(plan.requires_clarification)

        # Execute retrieval via existing FAISS/SQLite retriever
        results = retrieval_router.execute_routing(plan, retriever, top_k=5)
        self.assertIn("INDIA", results)
        india_chunks = results["INDIA"]
        self.assertGreater(len(india_chunks), 0)

        for chunk in india_chunks:
            self.assertEqual(
                chunk.jurisdiction, "INDIA",
                f"Leakage detected! Chunk from '{chunk.source_id}' has jurisdiction {chunk.jurisdiction}"
            )
            self.assertNotIn(chunk.source_id, ["wipo_gratk_treaty_2024", "nagoya_protocol_abs"])

    def test_single_jurisdiction_international_routing(self):
        """International queries route strictly to International track with zero India leakage"""
        query = "What does Article 5 of the Nagoya Protocol state regarding benefit sharing?"
        res = query_classifier.classify(query)
        self.assertEqual(res.jurisdiction.primary, JurisdictionChoice.INTERNATIONAL.value)
        self.assertFalse(res.jurisdiction.mixed)

        plan = retrieval_router.create_routing_plan(res)
        self.assertEqual(len(plan.tracks), 1)
        self.assertEqual(plan.tracks[0].jurisdiction, "INTERNATIONAL")
        self.assertFalse(plan.requires_clarification)

        # Execute retrieval
        results = retrieval_router.execute_routing(plan, retriever, top_k=5)
        self.assertIn("INTERNATIONAL", results)
        intl_chunks = results["INTERNATIONAL"]
        self.assertGreater(len(intl_chunks), 0)

        for chunk in intl_chunks:
            self.assertEqual(
                chunk.jurisdiction, "INTERNATIONAL",
                f"Leakage detected! Chunk from '{chunk.source_id}' has jurisdiction {chunk.jurisdiction}"
            )
            self.assertNotIn(
                chunk.source_id,
                ["patents_act_1970", "biological_diversity_act_2002", "drugs_cosmetics_act_asu_framework"]
            )

    def test_mixed_jurisdiction_dual_track_routing(self):
        """
        Mixed comparative queries produce TWO isolated evidence tracks (INDIA and INTERNATIONAL)
        with zero cross-leakage between tracks.
        """
        query = "Compare Indian ABS requirements under the Biological Diversity Act with the Nagoya Protocol."
        res = query_classifier.classify(query)

        self.assertTrue(res.jurisdiction.mixed, "Query must be classified as mixed jurisdiction")
        self.assertEqual(res.jurisdiction.primary, JurisdictionChoice.INDIA.value)
        self.assertEqual(res.jurisdiction.secondary, JurisdictionChoice.INTERNATIONAL.value)

        plan = retrieval_router.create_routing_plan(res)
        self.assertEqual(len(plan.tracks), 2, "Mixed query must produce exactly two evidence tracks")

        track_names = [t.track_name for t in plan.tracks]
        self.assertIn("INDIA", track_names)
        self.assertIn("INTERNATIONAL", track_names)

        # Execute dual-track retrieval
        results = retrieval_router.execute_routing(plan, retriever, top_k=5)

        # Track 1: INDIA results
        self.assertIn("INDIA", results)
        india_chunks = results["INDIA"]
        self.assertGreater(len(india_chunks), 0)
        for chunk in india_chunks:
            self.assertEqual(
                chunk.jurisdiction, "INDIA",
                f"Leakage in INDIA track: {chunk.source_id} has jurisdiction {chunk.jurisdiction}"
            )

        # Track 2: INTERNATIONAL results
        self.assertIn("INTERNATIONAL", results)
        intl_chunks = results["INTERNATIONAL"]
        self.assertGreater(len(intl_chunks), 0)
        for chunk in intl_chunks:
            self.assertEqual(
                chunk.jurisdiction, "INTERNATIONAL",
                f"Leakage in INTERNATIONAL track: {chunk.source_id} has jurisdiction {chunk.jurisdiction}"
            )

    def test_unspecified_jurisdiction_does_not_assume_india(self):
        """
        Unspecified jurisdiction queries must NOT silently assume India.
        Must set requires_clarification=True.
        """
        unspecified_queries = [
            "Is this formulation patentable?",
            "Can I patent an herbal extract?",
            "What are the regulatory requirements for selling herbal tea?"
        ]

        for q in unspecified_queries:
            res = query_classifier.classify(q)
            self.assertEqual(
                res.jurisdiction.primary, JurisdictionChoice.UNSPECIFIED.value,
                f"Query '{q}' should have UNSPECIFIED jurisdiction"
            )
            self.assertLessEqual(res.jurisdiction.confidence, 0.35)

            plan = retrieval_router.create_routing_plan(res)
            self.assertTrue(
                plan.requires_clarification,
                f"Query '{q}' must require jurisdiction clarification"
            )
            self.assertIsNotNone(plan.clarification_reason)
            self.assertIn("UNSPECIFIED", plan.jurisdictions)


if __name__ == "__main__":
    unittest.main()
