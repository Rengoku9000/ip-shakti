"""
30-Case Multilingual Benchmark Test Suite for Phase 2C (Sections 29-31)
Evaluates:
- 10 English cases (MB01 - MB10)
- 10 Hindi cases (MB11 - MB20)
- 10 Kannada cases (MB21 - MB30)

Measures:
- Language Detection Accuracy
- Classification Accuracy (Intent & Jurisdiction)
- Required Citation Anchor Hit Rate
- Status Preservation Accuracy
- Unsupported Claim Rate (Target: 0%)
- Forbidden Verdict Violations (Target: 0)
- Citation Provenance Immutability
"""
import unittest
import json
import logging
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "drugvista" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import config
from multilingual.query_normalizer import query_normalizer
from multilingual.answer_localizer import answer_localizer
from classification import query_classifier, retrieval_router
from retriever import retriever
from reasoning import reasoning_engine
from reasoning.answer_validator import answer_validator

logging.basicConfig(level=logging.WARNING)


class TestMultilingualBenchmark(unittest.TestCase):
    """30-Case Multilingual Reasoning Benchmark."""

    @classmethod
    def setUpClass(cls):
        bm_path = config.MULTILINGUAL_BENCHMARK_PATH
        if not bm_path.exists():
            bm_path = Path(__file__).resolve().parent.parent / "drugvista" / "data" / "knowledge" / "multilingual_benchmark_30.json"
        with open(bm_path, "r", encoding="utf-8") as f:
            cls.benchmark_cases = json.load(f)

    def test_run_30_case_multilingual_benchmark(self):
        """Execute full 30-case multilingual benchmark and assert all quality metrics."""
        total = len(self.benchmark_cases)
        self.assertEqual(total, 30, f"Expected 30 cases, found {total}")

        lang_correct = 0
        intent_correct = 0
        jur_correct = 0
        status_correct = 0
        anchor_hits = 0
        forbidden_violations = 0
        unsupported_claims_total = 0
        total_claims_generated = 0
        citation_errors = 0
        jurisdiction_errors = 0
        legal_status_errors = 0

        mismatches = []

        for case in self.benchmark_cases:
            cid = case["id"]
            query = case["query"]
            exp_lang = case["language"]
            exp_intent = case["expected_intent"]
            exp_jur = case["expected_jurisdiction"]
            req_anchors = case.get("required_anchors", [])
            exp_status = case["expected_status"]
            forbidden = case.get("forbidden_claims", [])

            # 1. Normalization & Detection
            ml_query = query_normalizer.normalize(query)
            if ml_query.detected_language == exp_lang:
                lang_correct += 1
            else:
                mismatches.append(f"[{cid}] LANG mismatch: got '{ml_query.detected_language}', exp '{exp_lang}'")

            # 2. Classification
            classification = query_classifier.classify(ml_query.normalized_text)
            if classification.intent == exp_intent:
                intent_correct += 1
            else:
                mismatches.append(f"[{cid}] INTENT mismatch: got '{classification.intent}', exp '{exp_intent}'")

            if classification.jurisdiction.primary == exp_jur:
                jur_correct += 1
            else:
                mismatches.append(f"[{cid}] JURISDICTION mismatch: got '{classification.jurisdiction.primary}', exp '{exp_jur}'")

            # 3. Routing & Retrieval
            routing_plan = retrieval_router.create_routing_plan(classification)
            retrieved = retrieval_router.execute_routing(routing_plan, retriever, top_k=5)

            # 4. Canonical Evidence Reasoning
            canon_res = reasoning_engine.reason(
                query=ml_query.normalized_text,
                classification=classification,
                routing_plan=routing_plan,
                retrieved_by_track=retrieved
            )

            # 5. Localization
            target_lang = exp_lang if exp_lang in {"HINDI", "KANNADA"} else "ENGLISH"
            loc_res, loc_meta = answer_localizer.localize(canon_res, target_language=target_lang)

            # Check Status
            if loc_res.status == exp_status:
                status_correct += 1
            else:
                mismatches.append(f"[{cid}] STATUS mismatch: got '{loc_res.status}', exp '{exp_status}'")

            # Check Forbidden Claims
            all_text = (
                loc_res.summary + " " +
                " ".join(f.text for f in loc_res.source_facts) + " " +
                " ".join(i.text for i in loc_res.interpretations)
            ).lower()

            for forb in forbidden:
                if forb.lower() in all_text:
                    forbidden_violations += 1
                    mismatches.append(f"[{cid}] FORBIDDEN CLAIM detected: '{forb}' in answer text!")

            # Check Required Anchors (if non-abstention)
            if req_anchors and loc_res.status == "EVIDENCE_SUPPORTED":
                retrieved_anchors = [e.citation_anchor.lower() for e in loc_res.evidence_items]
                hit = any(
                    any(ra.lower() in anch for anch in retrieved_anchors)
                    for ra in req_anchors
                )
                if hit:
                    anchor_hits += 1
                else:
                    mismatches.append(f"[{cid}] ANCHOR MISS: none of {req_anchors} in retrieved {retrieved_anchors}")
            else:
                anchor_hits += 1

            # Check Claim Provenance & Unsupported Claims via AnswerValidator
            all_claims = canon_res.source_facts + canon_res.interpretations
            total_claims_generated += len(all_claims)
            _, val_report = answer_validator.validate_claims(
                claims=all_claims,
                evidence_items=canon_res.evidence_items
            )
            unsupported_claims_total += len(val_report.unsupported_claims)

            # Check Citation Immutability between Canonical and Localized
            for ce, le in zip(canon_res.evidence_items, loc_res.evidence_items):
                if ce.citation_anchor != le.citation_anchor:
                    citation_errors += 1
                if ce.jurisdiction != le.jurisdiction:
                    jurisdiction_errors += 1
                if ce.legal_status != le.legal_status:
                    legal_status_errors += 1

        lang_acc = (lang_correct / total) * 100.0
        intent_acc = (intent_correct / total) * 100.0
        jur_acc = (jur_correct / total) * 100.0
        status_acc = (status_correct / total) * 100.0
        anchor_hit_rate = (anchor_hits / total) * 100.0
        unsupported_rate = (unsupported_claims_total / max(total_claims_generated, 1)) * 100.0

        print("\n" + "=" * 65)
        print("  PHASE 2C — 30-CASE MULTILINGUAL BENCHMARK REPORT")
        print("=" * 65)
        print(f"Total Benchmark Cases Evaluated:   {total} (10 EN, 10 HI, 10 KN)")
        print(f"Language Detection Accuracy:       {lang_acc:.1f}% ({lang_correct}/{total})")
        print(f"Intent Classification Accuracy:    {intent_acc:.1f}% ({intent_correct}/{total})")
        print(f"Jurisdiction Detection Accuracy:   {jur_acc:.1f}% ({jur_correct}/{total})")
        print(f"Reasoning Status Accuracy:         {status_acc:.1f}% ({status_correct}/{total})")
        print(f"Required Citation Anchor Hit Rate: {anchor_hit_rate:.1f}% ({anchor_hits}/{total})")
        print(f"Total Substantive Claims Audited:  {total_claims_generated}")
        print(f"Unsupported Claim Rate:            {unsupported_rate:.2f}% ({unsupported_claims_total} unsupported)")
        print(f"Forbidden Legal Verdict Violations:{forbidden_violations}")
        print(f"Citation Anchor Mutations:         {citation_errors}")
        print(f"Jurisdiction Mutations:            {jurisdiction_errors}")
        print(f"Legal Status Mutations:            {legal_status_errors}")
        print("=" * 65)

        if mismatches:
            print("\nMismatches detail:")
            for m in mismatches:
                print(" -", m)

        # Strict Quality Assertions
        self.assertGreaterEqual(lang_acc, 95.0, f"Language detection accuracy {lang_acc:.1f}% below 95%")
        self.assertGreaterEqual(intent_acc, 90.0, f"Intent classification accuracy {intent_acc:.1f}% below 90%")
        self.assertGreaterEqual(jur_acc, 90.0, f"Jurisdiction detection accuracy {jur_acc:.1f}% below 90%")
        self.assertGreaterEqual(status_acc, 90.0, f"Reasoning status accuracy {status_acc:.1f}% below 90%")
        self.assertGreaterEqual(anchor_hit_rate, 90.0, f"Anchor hit rate {anchor_hit_rate:.1f}% below 90%")
        self.assertEqual(unsupported_claims_total, 0, f"Found {unsupported_claims_total} unsupported claims! Must be 0.0%")
        self.assertEqual(forbidden_violations, 0, f"Found {forbidden_violations} forbidden verdict claims! Must be 0")
        self.assertEqual(citation_errors, 0, f"Found {citation_errors} citation mutations!")
        self.assertEqual(jurisdiction_errors, 0, f"Found {jurisdiction_errors} jurisdiction mutations!")
        self.assertEqual(legal_status_errors, 0, f"Found {legal_status_errors} legal status mutations!")


if __name__ == "__main__":
    unittest.main()
