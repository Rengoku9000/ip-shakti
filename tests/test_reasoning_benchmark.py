"""
Test Suite: 30-Case Evidence Reasoning Benchmark (Phase 2B.2)
Evaluates status accuracy, citation fidelity, unsupported claim rate (must be 0.0%),
forbidden verdict elimination, jurisdiction isolation, and abstention handling
across the 30-case manually curated reasoning benchmark dataset.
"""
import sys
import json
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "drugvista" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import config
from retriever import retriever
from classification import query_classifier, retrieval_router
from reasoning import reasoning_engine, answer_validator


class TestReasoningBenchmark(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        benchmark_path = config.REASONING_BENCHMARK_PATH
        if not benchmark_path.exists():
            raise FileNotFoundError(f"Reasoning benchmark not found at {benchmark_path}")

        with open(benchmark_path, "r", encoding="utf-8") as f:
            cls.benchmark_cases = json.load(f)

    def test_run_30_case_reasoning_benchmark(self):
        """Execute full 30-case reasoning benchmark and assert all quality metrics"""
        total = len(self.benchmark_cases)
        self.assertEqual(total, 30, f"Expected 30 cases, found {total}")

        status_correct = 0
        anchor_hits = 0
        forbidden_violations = 0
        unsupported_claims_total = 0
        total_claims_generated = 0
        jurisdiction_preservations = 0

        mismatches = []

        for case in self.benchmark_cases:
            cid = case["id"]
            query = case["query"]
            exp_status = case["expected_status"]
            exp_jur = case["expected_jurisdiction"]
            req_anchors = case.get("required_anchors", [])
            forbidden = case.get("forbidden_claims", [])
            is_mixed = case.get("is_mixed", False)

            # 1. Classification & Routing
            classification = query_classifier.classify(query)
            routing_plan = retrieval_router.create_routing_plan(classification)
            retrieved = retrieval_router.execute_routing(routing_plan, retriever, top_k=5)

            # 2. Evidence-Based Reasoning
            res = reasoning_engine.reason(
                query=query,
                classification=classification,
                routing_plan=routing_plan,
                retrieved_by_track=retrieved
            )

            # Check Status
            if res.status == exp_status:
                status_correct += 1
            else:
                mismatches.append(f"[{cid}] STATUS mismatch: got '{res.status}', exp '{exp_status}'")

            # Check Forbidden Claims
            all_text = (
                res.summary + " " +
                " ".join(f.text for f in res.source_facts) + " " +
                " ".join(i.text for i in res.interpretations)
            ).lower()

            for forb in forbidden:
                if forb.lower() in all_text:
                    forbidden_violations += 1
                    mismatches.append(f"[{cid}] FORBIDDEN CLAIM detected: '{forb}' in answer text!")

            # Check Required Anchors (if non-abstention)
            if req_anchors and res.status == "EVIDENCE_SUPPORTED":
                retrieved_anchors = [e.citation_anchor.lower() for e in res.evidence_items]
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

            # Check Unsupported Claims via AnswerValidator
            all_claims = res.source_facts + res.interpretations
            total_claims_generated += len(all_claims)
            _, val_report = answer_validator.validate_claims(
                claims=all_claims,
                evidence_items=res.evidence_items,
                target_jurisdiction=exp_jur if not is_mixed else None
            )
            unsupported_claims_total += len(val_report.unsupported_claims)

            # Check Jurisdiction Preservation
            if not is_mixed and exp_jur != "UNSPECIFIED":
                jur_clean = all(e.jurisdiction == exp_jur for e in res.evidence_items)
                if jur_clean:
                    jurisdiction_preservations += 1
                else:
                    mismatches.append(f"[{cid}] JURISDICTION LEAKAGE detected for expected {exp_jur}")
            else:
                jurisdiction_preservations += 1

        status_acc = (status_correct / total) * 100
        anchor_acc = (anchor_hits / total) * 100
        unsupported_rate = (unsupported_claims_total / max(total_claims_generated, 1)) * 100
        jur_pres_rate = (jurisdiction_preservations / total) * 100

        print("\n" + "=" * 65)
        print("  PHASE 2B.2 — 30-CASE EVIDENCE REASONING BENCHMARK REPORT")
        print("=" * 65)
        print(f"Total Benchmark Cases Evaluated:   {total}")
        print(f"Reasoning Status Accuracy:         {status_acc:.1f}% ({status_correct}/{total})")
        print(f"Required Citation Anchor Hit Rate: {anchor_acc:.1f}% ({anchor_hits}/{total})")
        print(f"Total Substantive Claims Audited:  {total_claims_generated}")
        print(f"Unsupported Claim Rate:            {unsupported_rate:.2f}% ({unsupported_claims_total} unsupported)")
        print(f"Forbidden Legal Verdict Violations:{forbidden_violations}")
        print(f"Jurisdiction Isolation Rate:       {jur_pres_rate:.1f}%")
        print("=" * 65)

        if mismatches:
            print("\nMismatches detail:")
            for m in mismatches[:10]:
                print(f" - {m}")

        # Assert Phase 2B.2 Criteria
        self.assertGreaterEqual(status_acc, 90.0, f"Status accuracy below target: {status_acc:.1f}%")
        self.assertGreaterEqual(anchor_acc, 90.0, f"Anchor hit rate below target: {anchor_acc:.1f}%")
        self.assertEqual(unsupported_rate, 0.0, f"Unsupported Claim Rate must be 0.0%: {unsupported_rate:.2f}%")
        self.assertEqual(forbidden_violations, 0, f"Forbidden claims must be 0: {forbidden_violations}")
        self.assertEqual(jur_pres_rate, 100.0, f"Jurisdiction preservation must be 100%: {jur_pres_rate:.1f}%")


if __name__ == "__main__":
    unittest.main()
