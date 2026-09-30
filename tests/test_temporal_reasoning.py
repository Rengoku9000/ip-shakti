"""
Test Suite: Temporal Reasoning (Phase 2B.2)
Verifies that current and historical legal regimes are never conflated,
and in-force statutes are distinguished from historical versions.
"""
import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "drugvista" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from reasoning import (
    EvidenceItem,
    Claim,
    ClaimType,
    SupportNature,
    evidence_sufficiency_evaluator,
    answer_validator
)


class TestTemporalReasoning(unittest.TestCase):
    def test_current_statute_preferred_over_historical(self):
        """Current in-force statute evaluated as in-force and not flagged as historical"""
        current_item = EvidenceItem(
            chunk_id="chunk_cur", source_id="patents_act_1970", source_version_id="2024.1",
            title="Patents Act, 1970", authority="IP India", authority_level="PRIMARY",
            jurisdiction="INDIA", legal_status="IN_FORCE", verification_status="verified",
            citation_anchor="Patents Act, 1970 — Section 3(p)", source_url="",
            text="Section 3(p) in force text", retrieval_score=0.88, effective_from="2005-01-01"
        )
        eval_res = evidence_sufficiency_evaluator.evaluate([current_item], target_jurisdiction="INDIA")
        self.assertTrue(eval_res.has_in_force_statute)
        self.assertFalse(eval_res.is_historical_only)

    def test_historical_only_pool_flagged(self):
        """Pool consisting entirely of historical records is flagged as historical only"""
        historical_item = EvidenceItem(
            chunk_id="chunk_hist", source_id="old_law", source_version_id="1911.1",
            title="Patents Act 1911", authority="Historical", authority_level="PRIMARY",
            jurisdiction="INDIA", legal_status="SUPERSEDED", verification_status="verified_historical",
            citation_anchor="Patents Act 1911 — Section 1", source_url="",
            text="Old law", retrieval_score=0.60, effective_until="1972-04-20"
        )
        eval_res = evidence_sufficiency_evaluator.evaluate([historical_item], target_jurisdiction="INDIA")
        self.assertTrue(eval_res.is_historical_only)


if __name__ == "__main__":
    unittest.main()
