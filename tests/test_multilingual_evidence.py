"""
Unit Tests for Evidence Preservation across Localization (Phase 2C - Section 27)
Verifies that translation into Hindi/Kannada cannot:
- create a new citation
- change a statutory section number
- change legal status
- change jurisdiction
- change source authority
- change evidence classification (SOURCE_FACT vs INTERPRETATION)
"""
import unittest
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "drugvista" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from reasoning.evidence_model import (
    StructuredReasoningResult,
    EvidenceItem,
    Claim
)
from models import CitationSource
from multilingual.answer_localizer import answer_localizer


class TestMultilingualEvidence(unittest.TestCase):
    """Test suite ensuring evidence preservation across localization."""

    def setUp(self):
        self.evidence = [
            EvidenceItem(
                chunk_id="chunk_1",
                source_id="patents_act_1970",
                source_version_id="patents_act_1970_v2005",
                title="Patents Act, 1970",
                authority="Intellectual Property India",
                authority_level="PRIMARY",
                jurisdiction="INDIA",
                legal_status="IN_FORCE",
                verification_status="OFFICIAL_VERIFIED",
                citation_anchor="Patents Act 1970 — Section 3(d)",
                source_url="https://ipindia.gov.in/patents-act.htm",
                text="Section 3(d) requires demonstration of enhanced therapeutic efficacy.",
                retrieval_score=0.91,
                relevance_reason="Direct provision on efficacy"
            )
        ]
        self.citations = [
            CitationSource(
                source_id="patents_act_1970",
                document_id="doc_1",
                chunk_id="chunk_1",
                chunk_index=0,
                filename="patents_act_1970.txt",
                source_type="STATUTE",
                score=0.91,
                text_preview="Section 3(d) requires...",
                citation_anchor="Patents Act 1970 — Section 3(d)",
                authority="Intellectual Property India",
                authority_level="PRIMARY",
                jurisdiction="INDIA",
                source_url="https://ipindia.gov.in/patents-act.htm"
            )
        ]
        self.canonical = StructuredReasoningResult(
            status="EVIDENCE_SUPPORTED",
            sufficiency="STRONG",
            summary="Section 3(d) mandates enhanced efficacy for derivatives in India.",
            source_facts=[
                Claim(
                    text="Section 3(d) requires demonstration of enhanced efficacy.",
                    type="SOURCE_FACT",
                    citations=["Patents Act 1970 — Section 3(d)"],
                    supporting_evidence=["chunk_1"],
                    jurisdiction="INDIA",
                    legal_status="IN_FORCE"
                )
            ],
            interpretations=[
                Claim(
                    text="Because this is a known derivative, Section 3(d) may apply.",
                    type="INTERPRETATION",
                    citations=["Patents Act 1970 — Section 3(d)"],
                    supporting_evidence=["chunk_1"],
                    jurisdiction="INDIA",
                    legal_status="IN_FORCE",
                    qualification="Therapeutic efficacy data required."
                )
            ],
            evidence_items=self.evidence,
            citations=self.citations
        )

    def test_no_spurious_citations_in_hindi(self):
        """Hindi localization must not add or remove citation links."""
        loc_res, _ = answer_localizer.localize(self.canonical, target_language="HINDI")

        # Citation count must match exactly
        self.assertEqual(len(loc_res.citations), len(self.canonical.citations))
        self.assertEqual(len(loc_res.evidence_items), len(self.canonical.evidence_items))

        # Citation anchors in claims must remain identical
        self.assertEqual(loc_res.source_facts[0].citations, self.canonical.source_facts[0].citations)
        self.assertEqual(loc_res.interpretations[0].citations, self.canonical.interpretations[0].citations)

    def test_statutory_sections_preserved_in_kannada(self):
        """Kannada localization must not alter statutory section identifiers."""
        loc_res, _ = answer_localizer.localize(self.canonical, target_language="KANNADA")

        # Section 3(d) anchor must be identical
        self.assertEqual(loc_res.evidence_items[0].citation_anchor, "Patents Act 1970 — Section 3(d)")
        self.assertEqual(loc_res.citations[0].citation_anchor, "Patents Act 1970 — Section 3(d)")

    def test_legal_status_and_jurisdiction_preserved(self):
        """Legal status and jurisdiction must remain strictly invariant across localization."""
        for lang in ["HINDI", "KANNADA"]:
            loc_res, _ = answer_localizer.localize(self.canonical, target_language=lang)

            self.assertEqual(loc_res.evidence_items[0].legal_status, "IN_FORCE")
            self.assertEqual(loc_res.evidence_items[0].jurisdiction, "INDIA")
            self.assertEqual(loc_res.evidence_items[0].authority_level, "PRIMARY")
            self.assertEqual(loc_res.source_facts[0].type, "SOURCE_FACT")
            self.assertEqual(loc_res.interpretations[0].type, "INTERPRETATION")


if __name__ == "__main__":
    unittest.main()
