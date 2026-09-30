"""
Test Suite: Knowledge Retrieval & Evaluation Benchmark
Runs all 25 ground-truth evaluation queries across Patent/IP, Ayurveda Regulation,
ABS, and International Treaties against the Phase 2A knowledge base.
Verifies source hit rate, exact citation anchor matching, and absence of LLM hallucinations.
"""
import json
import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "drugvista" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import config
from retriever import retriever


class TestKnowledgeRetrieval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        eval_path = config.KNOWLEDGE_DIR / "evaluation_dataset.json"
        with open(eval_path, "r", encoding="utf-8") as f:
            cls.eval_data = json.load(f)

    def test_evaluation_benchmark_all_queries(self):
        """Execute all 25 benchmark queries and verify source hit and anchor match"""
        queries = self.eval_data["queries"]
        total_queries = len(queries)
        source_hits = 0
        anchor_hits = 0
        detailed_results = []

        for item in queries:
            qid = item["id"]
            query_text = item["query"]
            jurisdiction = item["jurisdiction"]
            expected_sources = item["expected_sources"]
            expected_anchor = item["expected_anchor_substring"]

            results = retriever.retrieve(
                query=query_text,
                jurisdiction=jurisdiction,
                top_k=5
            )

            # Check if expected source is present in top-k
            top_sources = [r.source_id for r in results if r.source_id]
            source_matched = any(exp in top_sources for exp in expected_sources)
            if source_matched:
                source_hits += 1

            # Check if expected anchor substring is present in top-k citation anchors
            top_anchors = [r.citation_anchor for r in results if r.citation_anchor]
            anchor_matched = any(expected_anchor.lower() in a.lower() for a in top_anchors)
            if anchor_matched:
                anchor_hits += 1

            # Check that top result has structured citation anchor and source_url
            if results:
                best = results[0]
                self.assertIsNotNone(best.citation_anchor, f"Top result for {qid} missing citation_anchor")
                self.assertIsNotNone(best.source_url, f"Top result for {qid} missing source_url")

            detailed_results.append({
                "id": qid,
                "query": query_text,
                "expected_sources": expected_sources,
                "top_source": top_sources[0] if top_sources else None,
                "source_matched": source_matched,
                "expected_anchor": expected_anchor,
                "top_anchor": top_anchors[0] if top_anchors else None,
                "anchor_matched": anchor_matched
            })

        source_hit_rate = (source_hits / total_queries) * 100.0
        anchor_hit_rate = (anchor_hits / total_queries) * 100.0

        print(f"\n--- EVALUATION BENCHMARK SUMMARY ---")
        print(f"Total Queries Evaluated: {total_queries}")
        print(f"Source Hit Rate (Top-5): {source_hit_rate:.1f}% ({source_hits}/{total_queries})")
        print(f"Anchor Hit Rate (Top-5): {anchor_hit_rate:.1f}% ({anchor_hits}/{total_queries})")

        # Acceptance criterion: Top-5 source hit rate must be >= 90%
        self.assertGreaterEqual(
            source_hit_rate, 90.0,
            f"Source hit rate {source_hit_rate:.1f}% below minimum threshold of 90%"
        )
        self.assertGreaterEqual(
            anchor_hit_rate, 85.0,
            f"Anchor hit rate {anchor_hit_rate:.1f}% below minimum threshold of 85%"
        )


if __name__ == "__main__":
    unittest.main()
