"""
Test Suite: Strict Jurisdiction Filtering
Verifies that query retrieval strictly isolates INDIA and INTERNATIONAL regimes
with ZERO cross-jurisdiction leakage, fulfilling SIH26045 core requirements.
"""
import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "drugvista" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from retriever import retriever


class TestJurisdictionFilter(unittest.TestCase):
    def test_india_filter_zero_international_leakage(self):
        """When jurisdiction is set to INDIA, no international sources can be returned"""
        queries = [
            "What are the requirements for genetic resources and patent disclosure?",
            "traditional knowledge and benefit sharing access",
            "patentability of biological resources",
            "intellectual property and customary laws"
        ]

        for q in queries:
            results = retriever.retrieve(query=q, jurisdiction="INDIA", top_k=10)
            self.assertGreater(len(results), 0, f"Expected results for query '{q}'")
            for chunk in results:
                # If chunk has jurisdiction metadata, it MUST be INDIA
                if chunk.jurisdiction:
                    self.assertEqual(
                        chunk.jurisdiction, "INDIA",
                        f"Leakage detected! Query '{q}' with jurisdiction=INDIA returned chunk with jurisdiction '{chunk.jurisdiction}' (Source: {chunk.source_id})"
                    )
                self.assertNotIn(
                    chunk.source_id, ["wipo_gratk_treaty_2024", "nagoya_protocol_abs"],
                    f"International source '{chunk.source_id}' leaked into INDIA results for query '{q}'"
                )

    def test_international_filter_zero_india_leakage(self):
        """When jurisdiction is set to INTERNATIONAL, no Indian statutory sources can be returned"""
        queries = [
            "mandatory patent disclosure of country of origin of genetic resources",
            "fair and equitable sharing of benefits arising from genetic resources",
            "compliance measures for traditional knowledge associated with genetic resources"
        ]

        for q in queries:
            results = retriever.retrieve(query=q, jurisdiction="INTERNATIONAL", top_k=10)
            self.assertGreater(len(results), 0, f"Expected results for query '{q}'")
            for chunk in results:
                if chunk.jurisdiction:
                    self.assertEqual(
                        chunk.jurisdiction, "INTERNATIONAL",
                        f"Leakage detected! Query '{q}' with jurisdiction=INTERNATIONAL returned chunk with jurisdiction '{chunk.jurisdiction}' (Source: {chunk.source_id})"
                    )
                self.assertNotIn(
                    chunk.source_id,
                    ["patents_act_1970", "biological_diversity_act_2002", "drugs_cosmetics_act_asu_framework"],
                    f"Indian source '{chunk.source_id}' leaked into INTERNATIONAL results for query '{q}'"
                )


if __name__ == "__main__":
    unittest.main()
