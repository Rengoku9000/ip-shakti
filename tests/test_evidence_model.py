"""
Test Suite: Evidence Data Models (Phase 2B.2)
Verifies EvidenceItem, Claim, EvidenceChainItem, and StructuredReasoningResult
data representations, conversions from RetrievedChunk, and serializations.
"""
import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "drugvista" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from models import RetrievedChunk, AuthorityLevel, LegalStatus, VerificationStatus
from reasoning import (
    EvidenceItem,
    Claim,
    ClaimType,
    SupportNature,
    EvidenceChainItem,
    StructuredReasoningResult,
    ReasoningStatus,
    SufficiencyState
)


class TestEvidenceModel(unittest.TestCase):
    def setUp(self):
        self.chunk = RetrievedChunk(
            chunk_id="chunk_patents_sec3p_01",
            document_id="doc_patents_act_1970",
            content="Section 3(p) an invention which in effect, is traditional knowledge is not an invention.",
            score=0.88,
            filename="patents_act_1970.txt",
            source_type="STATUTE",
            chunk_index=3,
            start_offset=120,
            end_offset=215,
            title="Patents Act, 1970",
            section_id="sec_3_p",
            section_label="Section 3(p)",
            citation_anchor="Patents Act, 1970 — Section 3(p)",
            authority="Intellectual Property India",
            authority_level=AuthorityLevel.PRIMARY.value,
            jurisdiction="INDIA",
            source_url="https://ipindia.gov.in/patents-act.htm",
            source_id="patents_act_1970",
            source_version_id="2024.1",
            legal_status=LegalStatus.IN_FORCE.value,
            verification_status=VerificationStatus.VERIFIED.value
        )

    def test_evidence_item_from_chunk(self):
        """Verify seamless conversion from RetrievedChunk to EvidenceItem without loss"""
        item = EvidenceItem.from_chunk(self.chunk, relevance_reason="Direct match for Section 3(p)")
        self.assertEqual(item.chunk_id, "chunk_patents_sec3p_01")
        self.assertEqual(item.source_id, "patents_act_1970")
        self.assertEqual(item.authority_level, "PRIMARY")
        self.assertEqual(item.jurisdiction, "INDIA")
        self.assertEqual(item.legal_status, "IN_FORCE")
        self.assertEqual(item.citation_anchor, "Patents Act, 1970 — Section 3(p)")
        self.assertEqual(item.relevance_reason, "Direct match for Section 3(p)")
        self.assertIn("Section 3(p)", item.text)

        d = item.to_dict()
        self.assertEqual(d["chunk_id"], "chunk_patents_sec3p_01")
        self.assertEqual(d["retrieval_score"], 0.88)

    def test_claim_structure_and_serialization(self):
        """Verify Claim model distinguishes SOURCE_FACT from INTERPRETATION"""
        fact = Claim(
            text="Section 3(p) excludes traditional knowledge from patentability.",
            supporting_evidence=["chunk_patents_sec3p_01"],
            type=ClaimType.SOURCE_FACT.value,
            support_nature=SupportNature.DIRECT.value,
            citations=["Patents Act, 1970 — Section 3(p)"],
            jurisdiction="INDIA"
        )
        self.assertEqual(fact.type, "SOURCE_FACT")
        self.assertEqual(fact.support_nature, "DIRECT")

        interp = Claim(
            text="The applicant's formulation may encounter Section 3(p) objections if documented in TKDL.",
            supporting_evidence=["chunk_patents_sec3p_01"],
            type=ClaimType.INTERPRETATION.value,
            support_nature=SupportNature.INFERRED.value,
            citations=["Patents Act, 1970 — Section 3(p)"],
            jurisdiction="INDIA"
        )
        self.assertEqual(interp.type, "INTERPRETATION")
        self.assertEqual(interp.support_nature, "INFERRED")

        d_interp = interp.to_dict()
        self.assertEqual(d_interp["type"], "INTERPRETATION")

    def test_structured_reasoning_result_serialization(self):
        """Verify complete StructuredReasoningResult structure"""
        res = StructuredReasoningResult(
            status=ReasoningStatus.EVIDENCE_SUPPORTED.value,
            sufficiency=SufficiencyState.STRONG.value,
            summary="Section 3(p) governs traditional knowledge patentability under Indian law.",
            source_facts=[],
            interpretations=[],
            uncertainties=["Requires verification against TKDL records"],
            clarification_needed=[],
            human_review=False
        )
        d = res.to_dict()
        self.assertEqual(d["status"], "EVIDENCE_SUPPORTED")
        self.assertEqual(d["sufficiency"], "STRONG")
        self.assertFalse(d["human_review"])


if __name__ == "__main__":
    unittest.main()
