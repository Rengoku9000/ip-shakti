"""
Test Suite: Claim Support & Unsupported Claim Detection (Phase 2B.2)
Verifies that generated claims are strictly grounded in retrieved evidence,
and that unsupported statutory claims are rejected with Unsupported Claim Rate = 0%.
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


class TestClaimSupport(unittest.TestCase):
    def setUp(self):
        self.evidence = [
            EvidenceItem(
                chunk_id="chunk_sec3p",
                source_id="patents_act_1970",
                source_version_id="2024.1",
                title="Patents Act, 1970",
                authority="IP India",
                authority_level="PRIMARY",
                jurisdiction="INDIA",
                legal_status="IN_FORCE",
                verification_status="verified",
                citation_anchor="Patents Act, 1970 — Section 3(p)",
                source_url="https://ipindia.gov.in",
                text="Section 3(p) an invention which in effect, is traditional knowledge is not an invention.",
                retrieval_score=0.88
            )
        ]

    def test_valid_claims_pass_validation(self):
        """Claims referencing genuine evidence and matching provisions pass validation"""
        claim = Claim(
            text="According to Patents Act, 1970 — Section 3(p), traditional knowledge is excluded from patentability.",
            supporting_evidence=["chunk_sec3p"],
            type=ClaimType.SOURCE_FACT.value,
            support_nature=SupportNature.DIRECT.value,
            citations=["Patents Act, 1970 — Section 3(p)"],
            jurisdiction="INDIA"
        )
        validated, report = answer_validator.validate_claims([claim], self.evidence, target_jurisdiction="INDIA")
        self.assertEqual(len(validated), 1)
        self.assertEqual(report.unsupported_claim_rate, 0.0)
        self.assertTrue(report.passed)

    def test_unsupported_statutory_section_rejected(self):
        """Claims citing a hallucinated statutory section (e.g. Section 3(z)) are rejected"""
        hallucinated_claim = Claim(
            text="Under Section 3(z), herbal products are strictly prohibited from patent grant.",
            supporting_evidence=["chunk_sec3p"],
            type=ClaimType.SOURCE_FACT.value,
            support_nature=SupportNature.DIRECT.value,
            citations=["Patents Act, 1970 — Section 3(p)"],
            jurisdiction="INDIA"
        )
        validated, report = answer_validator.validate_claims([hallucinated_claim], self.evidence, target_jurisdiction="INDIA")
        self.assertEqual(len(validated), 0, "Hallucinated provision Section 3(z) must be rejected!")
        self.assertEqual(len(report.unsupported_claims), 1)
        self.assertFalse(report.passed)

    def test_unsupported_chunk_id_rejected(self):
        """Claims with unknown chunk IDs not present in evidence pool are rejected"""
        unsupported_claim = Claim(
            text="Some general claim without supporting evidence.",
            supporting_evidence=["non_existent_chunk_999"],
            type=ClaimType.SOURCE_FACT.value,
            support_nature=SupportNature.DIRECT.value,
            citations=["Unknown Anchor"],
            jurisdiction="INDIA"
        )
        validated, report = answer_validator.validate_claims([unsupported_claim], self.evidence, target_jurisdiction="INDIA")
        self.assertEqual(len(validated), 0)
        self.assertEqual(len(report.unsupported_claims), 1)
        self.assertFalse(report.passed)

    def test_forbidden_definitive_verdict_qualified(self):
        """Definitive legal guarantees are modified and qualified instead of asserted as absolute"""
        claim_with_verdict = Claim(
            text="Your patent will be granted under Section 3(p) of the Patents Act.",
            supporting_evidence=["chunk_sec3p"],
            type=ClaimType.INTERPRETATION.value,
            support_nature=SupportNature.INFERRED.value,
            citations=["Patents Act, 1970 — Section 3(p)"],
            jurisdiction="INDIA"
        )
        validated, report = answer_validator.validate_claims([claim_with_verdict], self.evidence, target_jurisdiction="INDIA")
        self.assertEqual(len(validated), 1)
        self.assertGreater(report.forbidden_verdicts_caught, 0)
        self.assertNotIn("will be granted", validated[0].text.lower())
        self.assertIsNotNone(validated[0].qualification)


if __name__ == "__main__":
    unittest.main()
