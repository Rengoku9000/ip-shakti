"""
Test Suite: Evidence Sufficiency Evaluator (Phase 2B.2)
Verifies sufficiency evaluation across authority levels, relevance scores,
legal status, and conflict detection.
"""
import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "drugvista" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from reasoning import (
    EvidenceItem,
    SufficiencyState,
    evidence_sufficiency_evaluator
)


class TestEvidenceSufficiency(unittest.TestCase):
    def test_empty_evidence_yields_none(self):
        """Zero evidence items must return NONE sufficiency"""
        eval_res = evidence_sufficiency_evaluator.evaluate([], target_jurisdiction="INDIA")
        self.assertEqual(eval_res.state, SufficiencyState.NONE.value)
        self.assertEqual(eval_res.score, 0.0)

    def test_strong_evidence_with_primary_in_force(self):
        """High score primary in-force items yield STRONG sufficiency"""
        item1 = EvidenceItem(
            chunk_id="c1", source_id="s1", source_version_id="v1",
            title="Patents Act", authority="IP India", authority_level="PRIMARY",
            jurisdiction="INDIA", legal_status="IN_FORCE", verification_status="verified",
            citation_anchor="Patents Act — Section 3(p)", source_url="https://ipindia.gov.in",
            text="Section 3(p) details...", retrieval_score=0.85
        )
        item2 = EvidenceItem(
            chunk_id="c2", source_id="s2", source_version_id="v1",
            title="Biological Diversity Act", authority="NBA", authority_level="PRIMARY",
            jurisdiction="INDIA", legal_status="IN_FORCE", verification_status="verified",
            citation_anchor="Biological Diversity Act — Section 6", source_url="https://nbaindia.org",
            text="Section 6 details...", retrieval_score=0.75
        )
        eval_res = evidence_sufficiency_evaluator.evaluate([item1, item2], target_jurisdiction="INDIA")
        self.assertEqual(eval_res.state, SufficiencyState.STRONG.value)
        self.assertTrue(eval_res.has_primary_authority)
        self.assertTrue(eval_res.has_in_force_statute)

    def test_low_score_yields_insufficient(self):
        """Scores below threshold yield INSUFFICIENT sufficiency"""
        item = EvidenceItem(
            chunk_id="c1", source_id="s1", source_version_id="v1",
            title="Reference Article", authority="Academic", authority_level="REFERENCE",
            jurisdiction="INDIA", legal_status="IN_FORCE", verification_status="verified",
            citation_anchor="Reference", source_url="",
            text="General remarks...", retrieval_score=0.15
        )
        eval_res = evidence_sufficiency_evaluator.evaluate([item], target_jurisdiction="INDIA")
        self.assertEqual(eval_res.state, SufficiencyState.INSUFFICIENT.value)

    def test_potential_conflict_detection(self):
        """Mixing in-force and superseded items flags conflict"""
        item_current = EvidenceItem(
            chunk_id="c1", source_id="s1", source_version_id="v2",
            title="Current Rules", authority="Ministry", authority_level="PRIMARY",
            jurisdiction="INDIA", legal_status="IN_FORCE", verification_status="verified",
            citation_anchor="Rules 2024", source_url="", text="Current text", retrieval_score=0.70
        )
        item_superseded = EvidenceItem(
            chunk_id="c2", source_id="s1_old", source_version_id="v1",
            title="Old Rules", authority="Ministry", authority_level="PRIMARY",
            jurisdiction="INDIA", legal_status="SUPERSEDED", verification_status="superseded",
            citation_anchor="Rules 1990", source_url="", text="Old text", retrieval_score=0.65
        )
        eval_res = evidence_sufficiency_evaluator.evaluate([item_current, item_superseded], target_jurisdiction="INDIA")
        self.assertTrue(eval_res.has_potential_conflict)
        self.assertIn("s1_old", eval_res.conflicting_sources)

    def test_not_in_force_treaty_flag(self):
        """Treaties adopted but not in force are explicitly flagged"""
        treaty_item = EvidenceItem(
            chunk_id="c1", source_id="wipo_gratk", source_version_id="2024",
            title="WIPO GRATK Treaty", authority="WIPO", authority_level="PRIMARY",
            jurisdiction="INTERNATIONAL", legal_status="ADOPTED", verification_status="verified",
            citation_anchor="WIPO GRATK Treaty — Article 3", source_url="",
            text="Mandatory disclosure...", retrieval_score=0.80
        )
        eval_res = evidence_sufficiency_evaluator.evaluate([treaty_item], target_jurisdiction="INTERNATIONAL")
        self.assertTrue(eval_res.is_not_in_force_treaty)


if __name__ == "__main__":
    unittest.main()
