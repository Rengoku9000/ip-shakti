"""
Test Suite: 50-Query Classification Benchmark (Phase 2B.1)
Evaluates query intent accuracy, jurisdiction accuracy, formulation accuracy,
topic matching, mixed-jurisdiction routing, and cross-jurisdiction leakage
against the 50-query manually defined ground truth dataset.
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


class TestClassificationBenchmark(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        benchmark_path = config.CLASSIFICATION_BENCHMARK_PATH
        if not benchmark_path.exists():
            raise FileNotFoundError(f"Benchmark dataset not found at {benchmark_path}")

        with open(benchmark_path, "r", encoding="utf-8") as f:
            cls.benchmark_data = json.load(f)

    def test_run_50_query_classification_benchmark(self):
        """Run full 50-query classification and routing benchmark and verify all metric thresholds"""
        total = len(self.benchmark_data)
        self.assertEqual(total, 50, f"Expected exactly 50 benchmark queries, found {total}")

        intent_correct = 0
        jurisdiction_correct = 0
        topic_match_count = 0
        formulation_correct = 0
        mixed_correct = 0
        clarification_correct = 0
        leakage_chunks = 0
        total_retrieved_chunks = 0

        mismatches = []

        for item in self.benchmark_data:
            qid = item["id"]
            query = item["query"]
            exp_intent = item["expected_intent"]
            exp_jur = item["expected_jurisdiction"]
            exp_topics = set(item["expected_topics"])
            exp_form_type = item["expected_formulation_type"]
            is_mixed = item["is_mixed"]
            exp_clarification = item["requires_clarification"]

            # 1. Run classifier
            classification = query_classifier.classify(query)
            plan = retrieval_router.create_routing_plan(classification)

            # Check intent
            if classification.intent == exp_intent:
                intent_correct += 1
            else:
                mismatches.append(f"[{qid}] INTENT mismatch: got '{classification.intent}', exp '{exp_intent}'")

            # Check jurisdiction
            if classification.jurisdiction.primary == exp_jur:
                jurisdiction_correct += 1
            else:
                mismatches.append(f"[{qid}] JURISDICTION mismatch: got '{classification.jurisdiction.primary}', exp '{exp_jur}'")

            # Check mixed
            if classification.jurisdiction.mixed == is_mixed:
                mixed_correct += 1
            else:
                mismatches.append(f"[{qid}] MIXED mismatch: got {classification.jurisdiction.mixed}, exp {is_mixed}")

            # Check topics (any overlap with expected topics)
            detected_topics = set(classification.topics)
            if detected_topics.intersection(exp_topics) or (not exp_topics and not detected_topics):
                topic_match_count += 1
            else:
                mismatches.append(f"[{qid}] TOPIC mismatch: got {detected_topics}, exp {exp_topics}")

            # Check formulation type
            if classification.formulation.type == exp_form_type:
                formulation_correct += 1
            else:
                mismatches.append(f"[{qid}] FORMULATION mismatch: got '{classification.formulation.type}', exp '{exp_form_type}'")

            # Check clarification requirement
            if plan.requires_clarification == exp_clarification:
                clarification_correct += 1

            # Check retrieval leakage if non-unspecified
            if not plan.requires_clarification:
                results = retrieval_router.execute_routing(plan, retriever, top_k=3)
                for track_name, chunks in results.items():
                    target_jur = "INDIA" if track_name == "INDIA" else "INTERNATIONAL"
                    for ch in chunks:
                        total_retrieved_chunks += 1
                        if ch.jurisdiction and ch.jurisdiction != target_jur:
                            leakage_chunks += 1
                            mismatches.append(
                                f"[{qid}] LEAKAGE in track {track_name}: chunk {ch.source_id} has {ch.jurisdiction}"
                            )

        intent_acc = (intent_correct / total) * 100
        jur_acc = (jurisdiction_correct / total) * 100
        topic_acc = (topic_match_count / total) * 100
        form_acc = (formulation_correct / total) * 100
        mixed_acc = (mixed_correct / total) * 100
        clarif_acc = (clarification_correct / total) * 100
        leakage_rate = (leakage_chunks / max(total_retrieved_chunks, 1)) * 100

        print("\n" + "=" * 60)
        print("  PHASE 2B.1 — 50-QUERY CLASSIFICATION BENCHMARK REPORT")
        print("=" * 60)
        print(f"Total Benchmark Queries:           {total}")
        print(f"Intent Classification Accuracy:    {intent_acc:.1f}% ({intent_correct}/{total})")
        print(f"Jurisdiction Detection Accuracy:   {jur_acc:.1f}% ({jurisdiction_correct}/{total})")
        print(f"Topic Match Rate:                  {topic_acc:.1f}% ({topic_match_count}/{total})")
        print(f"Formulation Category Accuracy:     {form_acc:.1f}% ({formulation_correct}/{total})")
        print(f"Mixed Jurisdiction Accuracy:       {mixed_acc:.1f}% ({mixed_correct}/{total})")
        print(f"Clarification Handling Accuracy:   {clarif_acc:.1f}% ({clarification_correct}/{total})")
        print(f"Total Chunks Retrieved in Routing: {total_retrieved_chunks}")
        print(f"Cross-Jurisdiction Leakage Rate:   {leakage_rate:.2f}% ({leakage_chunks} leaked chunks)")
        print("=" * 60)

        if mismatches:
            print("\nMismatches detail:")
            for m in mismatches[:10]:
                print(f" - {m}")
            if len(mismatches) > 10:
                print(f" ... and {len(mismatches) - 10} more")

        # Strict acceptance criteria
        self.assertGreaterEqual(intent_acc, 90.0, f"Intent accuracy below threshold: {intent_acc:.1f}%")
        self.assertGreaterEqual(jur_acc, 90.0, f"Jurisdiction accuracy below threshold: {jur_acc:.1f}%")
        self.assertGreaterEqual(topic_acc, 85.0, f"Topic match rate below threshold: {topic_acc:.1f}%")
        self.assertGreaterEqual(form_acc, 80.0, f"Formulation accuracy below threshold: {form_acc:.1f}%")
        self.assertEqual(mixed_acc, 100.0, f"Mixed jurisdiction accuracy must be 100%: {mixed_acc:.1f}%")
        self.assertEqual(leakage_rate, 0.0, f"Cross-jurisdiction leakage must be 0%: {leakage_rate:.2f}%")


if __name__ == "__main__":
    unittest.main()
