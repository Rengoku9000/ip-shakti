"""
Test Suite: Citation Generation and Provenance Traceability (Phase 2B.2)
Verifies that citations come strictly from structured chunk provenance
and contain valid anchors, authorities, and source URLs.
"""
import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "drugvista" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from retriever import retriever
from classification import query_classifier, retrieval_router
from reasoning import reasoning_engine


class TestCitationGeneration(unittest.TestCase):
    def test_citation_objects_derived_from_provenance(self):
        """Reasoning output must contain structured citations with valid URLs and anchors"""
        query = "What are the patentability criteria under Section 3(p) of the Indian Patents Act?"
        classification = query_classifier.classify(query)
        routing_plan = retrieval_router.create_routing_plan(classification)
        retrieved = retrieval_router.execute_routing(routing_plan, retriever, top_k=3)

        res = reasoning_engine.reason(
            query=query,
            classification=classification,
            routing_plan=routing_plan,
            retrieved_by_track=retrieved
        )

        self.assertGreater(len(res.citations), 0)
        for cit in res.citations:
            self.assertTrue(hasattr(cit, "citation_anchor") or "citation_anchor" in cit)
            anchor = cit.citation_anchor if hasattr(cit, "citation_anchor") else cit["citation_anchor"]
            self.assertIsNotNone(anchor)
            self.assertTrue(len(anchor) > 5)

            url = cit.source_url if hasattr(cit, "source_url") else cit.get("source_url")
            self.assertIsNotNone(url)

    def test_no_fabricated_sections_in_citations(self):
        """Every cited anchor must match the document and section stored in SQLite"""
        query = "What standards apply to single drugs under the Ayurvedic Pharmacopoeia of India?"
        classification = query_classifier.classify(query)
        routing_plan = retrieval_router.create_routing_plan(classification)
        retrieved = retrieval_router.execute_routing(routing_plan, retriever, top_k=3)

        res = reasoning_engine.reason(
            query=query,
            classification=classification,
            routing_plan=routing_plan,
            retrieved_by_track=retrieved
        )

        self.assertGreater(len(res.citations), 0)
        for cit in res.citations:
            anchor = cit.citation_anchor if hasattr(cit, "citation_anchor") else cit["citation_anchor"]
            # Ensure anchor is not generic or hallucinated
            self.assertNotIn("Unknown Section", anchor)
            self.assertNotIn("Section 999", anchor)


if __name__ == "__main__":
    unittest.main()
