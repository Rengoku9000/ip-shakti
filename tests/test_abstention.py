"""
Test Suite: Safe Abstention and Clarification (Phase 2B.2)
Verifies safe abstention on insufficient evidence, missing jurisdiction,
and confidential TKDL search queries.
"""
import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "drugvista" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from classification import query_classifier, retrieval_router
from reasoning import reasoning_engine, ReasoningStatus


class TestAbstention(unittest.TestCase):
    def test_abstention_on_unspecified_jurisdiction(self):
        """A jurisdiction-specific question without jurisdiction triggers CLARIFICATION_REQUIRED"""
        query = "Is this formulation patentable?"
        classification = query_classifier.classify(query)
        routing_plan = retrieval_router.create_routing_plan(classification)

        res = reasoning_engine.reason(
            query=query,
            classification=classification,
            routing_plan=routing_plan,
            retrieved_by_track={}
        )

        self.assertEqual(res.status, ReasoningStatus.CLARIFICATION_REQUIRED.value)
        self.assertGreater(len(res.clarification_needed), 0)
        self.assertTrue(any("jurisdiction" in c.lower() for c in res.clarification_needed))

    def test_abstention_on_confidential_tkdl_search(self):
        """A request to search confidential TKDL records does NOT fabricate a result"""
        query = "Search TKDL database and tell me whether this exact formulation appears in the confidential records."
        classification = query_classifier.classify(query)
        routing_plan = retrieval_router.create_routing_plan(classification)

        res = reasoning_engine.reason(
            query=query,
            classification=classification,
            routing_plan=routing_plan,
            retrieved_by_track={}
        )

        self.assertEqual(res.status, ReasoningStatus.HUMAN_REVIEW_RECOMMENDED.value)
        self.assertTrue(res.human_review)
        summary_text = res.summary.lower()
        self.assertIn("tkdl", summary_text)
        self.assertIn("confidential", summary_text)
        self.assertNotIn("formulation found in tkdl", summary_text)

    def test_abstention_on_zero_evidence(self):
        """Query with zero retrieved chunks returns INSUFFICIENT_EVIDENCE"""
        query = "Under Indian law, what are the patent rules for quantum supercomputers in Ayush?"
        classification = query_classifier.classify(query)
        routing_plan = retrieval_router.create_routing_plan(classification)

        # Empty retrieval result
        res = reasoning_engine.reason(
            query=query,
            classification=classification,
            routing_plan=routing_plan,
            retrieved_by_track={"INDIA": []}
        )

        self.assertEqual(res.status, ReasoningStatus.INSUFFICIENT_EVIDENCE.value)
        self.assertIn("insufficient", res.summary.lower())


if __name__ == "__main__":
    unittest.main()
