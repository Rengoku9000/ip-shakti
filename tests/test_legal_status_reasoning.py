"""
Test Suite: Legal Status Reasoning (Phase 2B.2)
Verifies that ADOPTED treaties not in force are NOT presented as binding domestic law,
and historical sources are appropriately qualified.
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
    answer_validator,
    claim_mapper
)
from classification import query_classifier


class TestLegalStatusReasoning(unittest.TestCase):
    def test_adopted_treaty_not_in_force_is_qualified(self):
        """WIPO GRATK Treaty (ADOPTED / NOT_IN_FORCE) must be qualified and not called binding Indian law"""
        treaty_evidence = [
            EvidenceItem(
                chunk_id="chunk_gratk_01",
                source_id="wipo_gratk_treaty_2024",
                source_version_id="2024.1",
                title="WIPO GRATK Treaty, 2024",
                authority="WIPO",
                authority_level="PRIMARY",
                jurisdiction="INTERNATIONAL",
                legal_status="ADOPTED",
                verification_status="verified",
                citation_anchor="WIPO GRATK Treaty, 2024 — Article 3",
                source_url="https://www.wipo.int/gratk",
                text="Article 3 establishes mandatory patent disclosure of country of origin of genetic resources.",
                retrieval_score=0.89
            )
        ]

        claim = Claim(
            text="According to WIPO GRATK Treaty, 2024 — Article 3, binding Indian law mandates patent disclosure.",
            supporting_evidence=["chunk_gratk_01"],
            type=ClaimType.SOURCE_FACT.value,
            support_nature=SupportNature.DIRECT.value,
            citations=["WIPO GRATK Treaty, 2024 — Article 3"],
            jurisdiction="INTERNATIONAL",
            legal_status="ADOPTED"
        )

        validated, report = answer_validator.validate_claims([claim], treaty_evidence, target_jurisdiction="INTERNATIONAL")
        self.assertEqual(len(validated), 1)
        self.assertNotIn("binding indian law", validated[0].text.lower())
        self.assertIn("adopted international treaty", validated[0].text.lower())
        self.assertIsNotNone(validated[0].qualification)

    def test_historical_source_is_qualified(self):
        """Historical source claims cannot be described as currently applicable without qualification"""
        historical_evidence = [
            EvidenceItem(
                chunk_id="chunk_hist_01",
                source_id="old_rules_1945",
                source_version_id="1945.1",
                title="Old Rules 1945",
                authority="Historical Authority",
                authority_level="PRIMARY",
                jurisdiction="INDIA",
                legal_status="SUPERSEDED",
                verification_status="verified_historical",
                citation_anchor="Old Rules 1945 — Rule 1",
                source_url="",
                text="Rule 1 prescribes historical licensing terms.",
                retrieval_score=0.72
            )
        ]

        claim = Claim(
            text="Under current law, Old Rules 1945 — Rule 1 governs licensing.",
            supporting_evidence=["chunk_hist_01"],
            type=ClaimType.SOURCE_FACT.value,
            support_nature=SupportNature.DIRECT.value,
            citations=["Old Rules 1945 — Rule 1"],
            jurisdiction="INDIA",
            legal_status="SUPERSEDED"
        )

        validated, report = answer_validator.validate_claims([claim], historical_evidence, target_jurisdiction="INDIA")
        self.assertEqual(len(validated), 1)
        self.assertNotIn("under current law", validated[0].text.lower())
        self.assertIn("historical", validated[0].text.lower())


if __name__ == "__main__":
    unittest.main()
