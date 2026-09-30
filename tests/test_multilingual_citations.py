"""
Unit Tests for Citation Immutability (Phase 2C - Section 26)
Verifies that localization into Hindi and Kannada NEVER alters:
- citation_anchor
- source_id
- source_version_id
- chunk_id
- jurisdiction
- legal_status
- verification_status
- source_url
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
from multilingual.language_policy import SupportedLanguage


class TestMultilingualCitations(unittest.TestCase):
    """Test suite ensuring absolute citation provenance immutability."""

    def setUp(self):
        self.evidence = [
            EvidenceItem(
                chunk_id="chunk_pat_3p",
                source_id="patents_act_1970",
                source_version_id="patents_act_1970_v2005",
                title="Patents Act, 1970",
                authority="Intellectual Property India",
                authority_level="PRIMARY",
                jurisdiction="INDIA",
                legal_status="IN_FORCE",
                verification_status="OFFICIAL_VERIFIED",
                citation_anchor="Patents Act 1970 — Section 3(p)",
                source_url="https://ipindia.gov.in/patents-act.htm",
                text="Section 3(p) excludes traditional knowledge from patentability.",
                retrieval_score=0.92,
                relevance_reason="Direct provision on traditional knowledge"
            ),
            EvidenceItem(
                chunk_id="chunk_bda_sec6",
                source_id="biological_diversity_act_2002",
                source_version_id="bda_2002_v1",
                title="Biological Diversity Act, 2002",
                authority="National Biodiversity Authority",
                authority_level="PRIMARY",
                jurisdiction="INDIA",
                legal_status="IN_FORCE",
                verification_status="OFFICIAL_VERIFIED",
                citation_anchor="Biological Diversity Act 2002 — Section 6",
                source_url="http://nbaindia.org/act",
                text="Section 6 requires prior approval from NBA before applying for IPR.",
                retrieval_score=0.88,
                relevance_reason="Mandatory prior approval for biological resources"
            )
        ]

        self.citations = [
            CitationSource(
                source_id="patents_act_1970",
                document_id="doc_patents",
                chunk_id="chunk_pat_3p",
                chunk_index=0,
                filename="patents_act_1970.txt",
                source_type="STATUTE",
                score=0.92,
                text_preview="Section 3(p) excludes...",
                citation_anchor="Patents Act 1970 — Section 3(p)",
                authority="Intellectual Property India",
                authority_level="PRIMARY",
                jurisdiction="INDIA",
                source_url="https://ipindia.gov.in/patents-act.htm"
            ),
            CitationSource(
                source_id="biological_diversity_act_2002",
                document_id="doc_bda",
                chunk_id="chunk_bda_sec6",
                chunk_index=1,
                filename="bda_2002.txt",
                source_type="STATUTE",
                score=0.88,
                text_preview="Section 6 requires prior approval...",
                citation_anchor="Biological Diversity Act 2002 — Section 6",
                authority="National Biodiversity Authority",
                authority_level="PRIMARY",
                jurisdiction="INDIA",
                source_url="http://nbaindia.org/act"
            )
        ]

        self.canonical = StructuredReasoningResult(
            status="EVIDENCE_SUPPORTED",
            sufficiency="STRONG",
            summary="Section 3(p) excludes traditional knowledge from patentability in India.",
            source_facts=[
                Claim(
                    text="Section 3(p) excludes traditional knowledge from patentability.",
                    type="SOURCE_FACT",
                    citations=["Patents Act 1970 — Section 3(p)"],
                    supporting_evidence=["chunk_pat_3p"]
                )
            ],
            interpretations=[
                Claim(
                    text="Because the formulation is based on traditionally known herbs, Section 3(p) may be relevant.",
                    type="INTERPRETATION",
                    citations=["Patents Act 1970 — Section 3(p)"],
                    supporting_evidence=["chunk_pat_3p"],
                    qualification="Applicability depends on proof of synergy."
                )
            ],
            evidence_items=self.evidence,
            citations=self.citations
        )

    def test_hindi_citation_immutability(self):
        """Hindi localization must not alter citation metadata or anchors."""
        loc_res, meta = answer_localizer.localize(self.canonical, target_language="HINDI")
        self.assertEqual(meta["answer_language"], "HINDI")
        self.assertTrue(meta["translation_used"])

        # Check evidence item immutability
        for orig, loc in zip(self.canonical.evidence_items, loc_res.evidence_items):
            self.assertEqual(orig.citation_anchor, loc.citation_anchor)
            self.assertEqual(orig.source_id, loc.source_id)
            self.assertEqual(orig.source_version_id, loc.source_version_id)
            self.assertEqual(orig.chunk_id, loc.chunk_id)
            self.assertEqual(orig.jurisdiction, loc.jurisdiction)
            self.assertEqual(orig.legal_status, loc.legal_status)
            self.assertEqual(orig.verification_status, loc.verification_status)
            self.assertEqual(orig.source_url, loc.source_url)

        # Check citation object immutability
        for orig_c, loc_c in zip(self.canonical.citations, loc_res.citations):
            self.assertEqual(orig_c.citation_anchor, loc_c.citation_anchor)
            self.assertEqual(orig_c.source_id, loc_c.source_id)
            self.assertEqual(orig_c.chunk_id, loc_c.chunk_id)

        # Check claim citations list preserved
        self.assertEqual(loc_res.source_facts[0].citations, ["Patents Act 1970 — Section 3(p)"])
        self.assertEqual(loc_res.source_facts[0].supporting_evidence, ["chunk_pat_3p"])

    def test_kannada_citation_immutability(self):
        """Kannada localization must not alter citation metadata or anchors."""
        loc_res, meta = answer_localizer.localize(self.canonical, target_language="KANNADA")
        self.assertEqual(meta["answer_language"], "KANNADA")
        self.assertTrue(meta["translation_used"])

        for orig, loc in zip(self.canonical.evidence_items, loc_res.evidence_items):
            self.assertEqual(orig.citation_anchor, loc.citation_anchor)
            self.assertEqual(orig.source_id, loc.source_id)
            self.assertEqual(orig.jurisdiction, loc.jurisdiction)
            self.assertEqual(orig.legal_status, loc.legal_status)

        for orig_c, loc_c in zip(self.canonical.citations, loc_res.citations):
            self.assertEqual(orig_c.citation_anchor, loc_c.citation_anchor)

        self.assertEqual(loc_res.source_facts[0].citations, ["Patents Act 1970 — Section 3(p)"])


if __name__ == "__main__":
    unittest.main()
