"""
Test Suite: Human Review Escalation (Phase 2B.2)
Verifies triggering of HUMAN_REVIEW_RECOMMENDED on legal guarantees,
statutory conflicts, and sensitive regulatory inquiries.
"""
import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "drugvista" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from classification import query_classifier, retrieval_router
from reasoning import (
    reasoning_engine,
    ReasoningStatus,
    EvidenceItem,
    evidence_sufficiency_evaluator
)


class TestHumanReview(unittest.TestCase):
    def test_human_review_on_definitive_legal_guarantee(self):
        """User asking for a legal guarantee triggers HUMAN_REVIEW_RECOMMENDED"""
        query = "Can you guarantee that my patent will be granted under Indian law?"
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
        self.assertGreater(len(res.human_review_reasons), 0)

    def test_human_review_on_statutory_conflict(self):
        """Conflicting or superseded statutory provisions flag human review"""
        item_in_force = EvidenceItem(
            chunk_id="c1", source_id="s1", source_version_id="2024",
            title="Current Provision", authority="Ministry", authority_level="PRIMARY",
            jurisdiction="INDIA", legal_status="IN_FORCE", verification_status="verified",
            citation_anchor="Act 2024", source_url="", text="Current text", retrieval_score=0.80
        )
        item_superseded = EvidenceItem(
            chunk_id="c2", source_id="s1_old", source_version_id="1970",
            title="Old Provision", authority="Ministry", authority_level="PRIMARY",
            jurisdiction="INDIA", legal_status="SUPERSEDED", verification_status="superseded",
            citation_anchor="Act 1970", source_url="", text="Old text", retrieval_score=0.75
        )

        eval_res = evidence_sufficiency_evaluator.evaluate([item_in_force, item_superseded], target_jurisdiction="INDIA")
        self.assertTrue(eval_res.has_potential_conflict)


if __name__ == "__main__":
    unittest.main()
