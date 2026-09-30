"""
Test Suite: Jurisdiction Reasoning Isolation (Phase 2B.2)
Verifies that Indian and International reasoning tracks are never silently merged,
and mixed queries produce isolated dual breakdowns.
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


class TestJurisdictionReasoning(unittest.TestCase):
    def test_india_reasoning_contains_only_india_evidence(self):
        """Pure India query reasons exclusively over Indian statutory evidence"""
        query = "What prior approval is mandated by Section 6 of the Biological Diversity Act in India?"
        classification = query_classifier.classify(query)
        routing_plan = retrieval_router.create_routing_plan(classification)
        retrieved = retrieval_router.execute_routing(routing_plan, retriever, top_k=5)

        res = reasoning_engine.reason(
            query=query,
            classification=classification,
            routing_plan=routing_plan,
            retrieved_by_track=retrieved
        )

        for item in res.evidence_items:
            self.assertEqual(item.jurisdiction, "INDIA")
        for fact in res.source_facts:
            self.assertEqual(fact.jurisdiction, "INDIA")

    def test_international_reasoning_contains_only_international_evidence(self):
        """Pure International query reasons exclusively over International treaties"""
        query = "What does Article 5 of the Nagoya Protocol state regarding benefit sharing?"
        classification = query_classifier.classify(query)
        routing_plan = retrieval_router.create_routing_plan(classification)
        retrieved = retrieval_router.execute_routing(routing_plan, retriever, top_k=5)

        res = reasoning_engine.reason(
            query=query,
            classification=classification,
            routing_plan=routing_plan,
            retrieved_by_track=retrieved
        )

        for item in res.evidence_items:
            self.assertEqual(item.jurisdiction, "INTERNATIONAL")
        for fact in res.source_facts:
            self.assertEqual(fact.jurisdiction, "INTERNATIONAL")

    def test_mixed_query_generates_isolated_jurisdiction_breakdown(self):
        """Mixed query produces explicit isolated breakdown for INDIA and INTERNATIONAL without blending"""
        query = "Compare Indian ABS requirements under the Biological Diversity Act with the Nagoya Protocol."
        classification = query_classifier.classify(query)
        self.assertTrue(classification.jurisdiction.mixed)

        routing_plan = retrieval_router.create_routing_plan(classification)
        retrieved = retrieval_router.execute_routing(routing_plan, retriever, top_k=5)

        res = reasoning_engine.reason(
            query=query,
            classification=classification,
            routing_plan=routing_plan,
            retrieved_by_track=retrieved
        )

        self.assertIn("INDIA", res.jurisdiction_breakdown)
        self.assertIn("INTERNATIONAL", res.jurisdiction_breakdown)
        self.assertIn("comparison", res.jurisdiction_breakdown)

        india_track = res.jurisdiction_breakdown["INDIA"]
        intl_track = res.jurisdiction_breakdown["INTERNATIONAL"]

        self.assertGreater(india_track["evidence_count"], 0)
        self.assertGreater(intl_track["evidence_count"], 0)


if __name__ == "__main__":
    unittest.main()
