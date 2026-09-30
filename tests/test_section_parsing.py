"""
Test Suite: Structure-Aware Section Parsing
Verifies that statutory, regulatory, and treaty structural boundaries
(sections, articles, rules, schedules) are accurately detected and preserved.
"""
import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "drugvista" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from structure_parser import structure_parser
from models import SectionType, AuthorityLevel, Jurisdiction


class TestSectionParsing(unittest.TestCase):
    def test_parse_statutory_sections(self):
        """Verify statutory section detection in Patents Act text"""
        sample_legal_text = """
The Patents Act, 1970
Chapter II: Inventions Not Patentable

Section 3 - What are not inventions
The following are not inventions within the meaning of this Act:

(a) an invention which is frivolous or which claims anything obvious;
(d) the mere discovery of a new form of a known substance which does not result in the enhancement of the known efficacy of that substance;
(p) an invention which in effect is traditional knowledge or which is an aggregation or duplication of known properties of traditionally known component or components.

Section 10 - Contents of specifications
(4) Every complete specification shall:
(d) disclose the source and geographical origin of the biological material in the specification, when used in an invention.
"""
        parsed = structure_parser.parse_text(
            text=sample_legal_text,
            doc_title="Patents Act, 1970",
            source_id="patents_act_1970",
            source_type="STATUTE",
            jurisdiction="INDIA",
            authority_level="PRIMARY"
        )

        labels = [s.section_label for s in parsed.sections]
        self.assertTrue(any("Section 3" in l for l in labels), "Section 3 not detected")
        self.assertTrue(any("Section 10" in l for l in labels), "Section 10 not detected")

    def test_parse_treaty_articles(self):
        """Verify treaty article detection in WIPO GRATK Treaty text"""
        sample_treaty_text = """
WIPO Treaty on Intellectual Property, Genetic Resources and Associated Traditional Knowledge (2024)

Article 1 - Objectives
The objectives of this Treaty are to:
(a) enhance the efficacy, transparency and quality of the patent system;

Article 3 - Mandatory Disclosure Requirement
1. Where the claimed invention in a patent application is based on genetic resources, each Contracting Party shall require applicants to disclose the country of origin of the genetic resources.
2. Where the claimed invention in a patent application is based on traditional knowledge associated with genetic resources, each Contracting Party shall require applicants to disclose the Indigenous Peoples or local community who provided the traditional knowledge.
"""
        parsed = structure_parser.parse_text(
            text=sample_treaty_text,
            doc_title="WIPO Treaty on GRATK",
            source_id="wipo_gratk_treaty_2024",
            source_type="TREATY",
            jurisdiction="INTERNATIONAL",
            authority_level="PRIMARY"
        )

        labels = [s.section_label for s in parsed.sections]
        self.assertTrue(any("Article 1" in l for l in labels), "Article 1 not detected")
        self.assertTrue(any("Article 3" in l for l in labels), "Article 3 not detected")

    def test_structure_bounded_chunking(self):
        """Verify chunks produced preserve section metadata and boundaries"""
        sample_text = """
Section 3(p) - Traditional Knowledge
An invention which in effect is traditional knowledge or which is an aggregation or duplication of known properties of traditionally known component or components is not patentable.
"""
        parsed = structure_parser.parse_text(
            text=sample_text,
            doc_title="Patents Act 1970",
            source_id="patents_act_1970",
            source_type="STATUTE",
            jurisdiction="INDIA",
            authority_level="PRIMARY"
        )
        chunks = structure_parser.create_structured_chunks(
            parsed_doc=parsed,
            document_id="doc_test_123",
            chunk_size=500,
            chunk_overlap=50
        )
        self.assertGreaterEqual(len(chunks), 1)
        chunk = chunks[0]
        self.assertIn("Section 3(p)", chunk.citation_anchor)
        self.assertIsNotNone(chunk.section_id)
        self.assertEqual(chunk.jurisdiction, "INDIA")
        self.assertEqual(chunk.authority_level, "PRIMARY")


if __name__ == "__main__":
    unittest.main()
