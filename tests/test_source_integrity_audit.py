"""
Test Suite: Phase 2A.1 Authoritative Source Integrity Audit
Verifies:
1. Exact source fidelity and authority matching
2. Explicit separation of legal status (IN_FORCE vs ADOPTED / NOT_IN_FORCE)
3. Non-promotion of secondary material to PRIMARY
4. Negative tests (India vs International, confidential TKDL abstention, treaty status)
5. Comprehensive evaluation metrics: Top-1/Top-5 Hit Rates, 0% Leakage, 0% Invalid Citations
"""
import json
import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "drugvista" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import config
from db import db
from retriever import retriever
from models import LegalStatus, VerificationStatus, AuthorityLevel, Jurisdiction


class TestSourceIntegrityAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest_path = config.MANIFEST_PATH
        with open(cls.manifest_path, "r", encoding="utf-8") as f:
            cls.manifest = json.load(f)

        cls.eval_path = config.KNOWLEDGE_DIR / "evaluation_dataset.json"
        with open(cls.eval_path, "r", encoding="utf-8") as f:
            cls.eval_data = json.load(f)

        audit_rec_path = config.KNOWLEDGE_MANIFESTS_DIR / "source_audit_records.json"
        with open(audit_rec_path, "r", encoding="utf-8") as f:
            cls.audit_records = json.load(f)

    def test_01_all_audit_records_verified(self):
        """Verify each source has an audit record with 100% fidelity matches"""
        records = self.audit_records.get("records", [])
        self.assertEqual(len(records), 7)
        for rec in records:
            src_id = rec["source_id"]
            self.assertTrue(rec["authority_match"], f"{src_id} authority match failed")
            self.assertTrue(rec["version_match"], f"{src_id} version match failed")
            self.assertTrue(rec["content_fidelity"], f"{src_id} content fidelity failed")
            self.assertTrue(rec["structural_fidelity"], f"{src_id} structural fidelity failed")
            self.assertTrue(rec["citation_fidelity"], f"{src_id} citation fidelity failed")
            self.assertTrue(rec["legal_status_verified"], f"{src_id} legal status verification failed")

    def test_02_treaty_legal_status_distinction(self):
        """Verify WIPO GRATK Treaty is ADOPTED / NOT_IN_FORCE while Nagoya Protocol is IN_FORCE"""
        results_wipo = retriever.retrieve(
            query="mandatory patent disclosure requirement genetic resources",
            jurisdiction="INTERNATIONAL",
            top_k=5
        )
        self.assertGreater(len(results_wipo), 0)
        wipo_chunks = [c for c in results_wipo if c.source_id == "wipo_gratk_treaty_2024"]
        self.assertGreater(len(wipo_chunks), 0)
        top_wipo = wipo_chunks[0]
        self.assertEqual(top_wipo.legal_status, "ADOPTED")
        self.assertIsNone(top_wipo.entry_into_force_date)

        results_nagoya = retriever.retrieve(
            query="fair and equitable sharing of benefits genetic resources",
            jurisdiction="INTERNATIONAL",
            top_k=5
        )
        nagoya_chunks = [c for c in results_nagoya if c.source_id == "nagoya_protocol_abs"]
        self.assertGreater(len(nagoya_chunks), 0)
        top_nagoya = nagoya_chunks[0]
        self.assertEqual(top_nagoya.legal_status, "IN_FORCE")
        self.assertEqual(top_nagoya.entry_into_force_date, "2014-10-12")

    def test_03_authority_level_integrity(self):
        """Verify secondary/guidance materials are strictly OFFICIAL_SECONDARY, not PRIMARY"""
        sources_by_id = {s["source_id"]: s for s in self.manifest["sources"]}
        
        # Primary statutory authorities
        self.assertEqual(sources_by_id["patents_act_1970"]["authority_level"], "PRIMARY")
        self.assertEqual(sources_by_id["biological_diversity_act_2002"]["authority_level"], "PRIMARY")
        self.assertEqual(sources_by_id["drugs_cosmetics_act_asu_framework"]["authority_level"], "PRIMARY")
        self.assertEqual(sources_by_id["wipo_gratk_treaty_2024"]["authority_level"], "PRIMARY")
        self.assertEqual(sources_by_id["nagoya_protocol_abs"]["authority_level"], "PRIMARY")

        # Explanatory and guidance materials MUST be OFFICIAL_SECONDARY
        self.assertEqual(sources_by_id["ayush_pharmacopoeial_standards_guidance"]["authority_level"], "OFFICIAL_SECONDARY")
        self.assertEqual(sources_by_id["tkdl_public_scope_and_defensive_prior_art_advisory"]["authority_level"], "OFFICIAL_SECONDARY")

    def test_04_negative_test_jurisdiction_leakage(self):
        """NEGATIVE TEST 1: Indian patent law queries restricted to INTERNATIONAL must return 0 Indian results"""
        queries = [
            "Section 3(p) traditional knowledge exclusion Patents Act",
            "Section 33EEB patent proprietary ASU medicines",
            "National Biodiversity Authority Section 6 approval"
        ]
        for q in queries:
            results = retriever.retrieve(query=q, jurisdiction="INTERNATIONAL", top_k=10)
            for chunk in results:
                self.assertNotEqual(
                    chunk.jurisdiction, "INDIA",
                    f"Leakage detected! Indian chunk {chunk.chunk_id} returned for international query: {q}"
                )
                self.assertNotIn(
                    chunk.source_id,
                    ["patents_act_1970", "biological_diversity_act_2002", "drugs_cosmetics_act_asu_framework"]
                )

    def test_05_negative_test_tkdl_safe_abstention(self):
        """NEGATIVE TEST 2: Query for confidential TKDL search records returns defensive advisory with safe abstention"""
        query = "Show confidential TKDL transcription dossier and internal search transcripts"
        results = retriever.retrieve(query=query, jurisdiction="INDIA", top_k=5)
        self.assertGreater(len(results), 0)
        
        # Must retrieve the defensive advisory explaining database is non-public
        tkdl_results = [r for r in results if r.source_id == "tkdl_public_scope_and_defensive_prior_art_advisory"]
        self.assertGreater(len(tkdl_results), 0)
        
        # Verify content contains explicit abstention guardrail
        abstention_found = any("abstain" in r.content.lower() or "non-disclosure" in r.content.lower() for r in tkdl_results)
        self.assertTrue(abstention_found, "TKDL safe abstention guardrail not found in retrieved evidence")

    def test_06_benchmark_and_invalid_citation_rate(self):
        """Run all 25 benchmark queries and verify hit rates and 0% invalid citation rate"""
        queries = self.eval_data["queries"]
        total = len(queries)
        
        top1_source_hits = 0
        top5_source_hits = 0
        top1_anchor_hits = 0
        top5_anchor_hits = 0
        invalid_citations = 0
        leakage_count = 0

        for item in queries:
            q = item["query"]
            jur = item["jurisdiction"]
            expected_sources = item["expected_sources"]
            expected_anchor = item["expected_anchor_substring"]

            results = retriever.retrieve(query=q, jurisdiction=jur, top_k=5)
            self.assertGreater(len(results), 0, f"No results for {item['id']}")

            # Top-1 Source
            if results[0].source_id in expected_sources:
                top1_source_hits += 1

            # Top-5 Source
            if any(r.source_id in expected_sources for r in results):
                top5_source_hits += 1

            # Top-1 Anchor
            if results[0].citation_anchor and expected_anchor.lower() in results[0].citation_anchor.lower():
                top1_anchor_hits += 1

            # Top-5 Anchor
            if any(r.citation_anchor and expected_anchor.lower() in r.citation_anchor.lower() for r in results):
                top5_anchor_hits += 1

            # Citation Validity Check
            for r in results:
                # Check for empty, malformed, or hallucinated anchors
                if not r.citation_anchor or "—" not in r.citation_anchor or len(r.citation_anchor.strip()) < 8:
                    invalid_citations += 1
                if not r.source_url or not r.source_url.startswith("http"):
                    invalid_citations += 1
                # Check cross-jurisdiction leakage
                if jur and r.jurisdiction and r.jurisdiction != jur:
                    leakage_count += 1

        top1_source_rate = (top1_source_hits / total) * 100.0
        top5_source_rate = (top5_source_hits / total) * 100.0
        top1_anchor_rate = (top1_anchor_hits / total) * 100.0
        top5_anchor_rate = (top5_anchor_hits / total) * 100.0
        leakage_rate = (leakage_count / (total * 5)) * 100.0
        invalid_citation_rate = (invalid_citations / (total * 5)) * 100.0

        print(f"\n==========================================")
        print(f"PHASE 2A.1 RETRIEVAL & AUDIT BENCHMARK")
        print(f"==========================================")
        print(f"Total Benchmark Queries: {total}")
        print(f"Top-1 Source Hit Rate:   {top1_source_rate:.1f}% ({top1_source_hits}/{total})")
        print(f"Top-5 Source Hit Rate:   {top5_source_rate:.1f}% ({top5_source_hits}/{total})")
        print(f"Top-1 Anchor Hit Rate:   {top1_anchor_rate:.1f}% ({top1_anchor_hits}/{total})")
        print(f"Top-5 Anchor Hit Rate:   {top5_anchor_rate:.1f}% ({top5_anchor_hits}/{total})")
        print(f"Cross-Jurisdiction Leak: {leakage_rate:.1f}%")
        print(f"Invalid Citation Rate:   {invalid_citation_rate:.1f}%")
        print(f"==========================================")

        self.assertGreaterEqual(top1_source_rate, 80.0)
        self.assertEqual(top5_source_rate, 100.0)
        self.assertGreaterEqual(top1_anchor_rate, 75.0)
        self.assertEqual(top5_anchor_rate, 100.0)
        self.assertEqual(leakage_rate, 0.0, "Cross-jurisdiction leakage must be 0%")
        self.assertEqual(invalid_citation_rate, 0.0, "Invalid citation rate must be 0%")


if __name__ == "__main__":
    unittest.main()
