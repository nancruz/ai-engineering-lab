"""Lab 5 — evaluation.  Run: python3 -m unittest -v tests.test_lab5_evaluation"""
import math
import unittest

from minirag.evaluation import (check_answer, evaluate_retrieval, evidence_recall, hit_at_k, ndcg_at_k,
                                parse_judgement, recall_at_k, reciprocal_rank)
from minirag.generation import Answer
from minirag.retrieval import Hit

from .helpers import chunk


class RankingMetrics(unittest.TestCase):
    def test_one_of_two_relevant_found_at_position_two(self):
        ranked, gold = ["X", "A", "Y"], ["A", "B"]
        self.assertEqual(hit_at_k(ranked, gold, 3), 1.0)
        self.assertEqual(recall_at_k(ranked, gold, 3), 0.5)
        self.assertEqual(reciprocal_rank(ranked, gold, 3), 0.5)
        expected = (1 / math.log2(3)) / (1 + 1 / math.log2(3))
        self.assertAlmostEqual(ndcg_at_k(ranked, gold, 3), expected)

    def test_perfect_and_empty_rankings(self):
        self.assertEqual([m(["A", "B", "X"], ["A", "B"], 3) for m in (hit_at_k, recall_at_k, reciprocal_rank, ndcg_at_k)],
                         [1.0, 1.0, 1.0, 1.0])
        self.assertEqual([m(["X", "Y"], ["A"], 3) for m in (hit_at_k, recall_at_k, reciprocal_rank, ndcg_at_k)],
                         [0.0, 0.0, 0.0, 0.0])

    def test_only_the_top_k_counts(self):
        self.assertEqual(hit_at_k(["X", "Y", "A"], ["A"], 2), 0.0)
        self.assertEqual(reciprocal_rank(["X", "Y", "A"], ["A"], 3), 1 / 3)

    def test_duplicates_in_the_ranking_are_ignored(self):
        self.assertEqual(recall_at_k(["A", "A", "B"], ["A", "B"], 2), 1.0)

    def test_questions_without_relevant_documents_are_not_scored(self):
        self.assertEqual([m(["A"], [], 3) for m in (hit_at_k, recall_at_k, reciprocal_rank, ndcg_at_k)], [None] * 4)

    def test_k_must_be_positive(self):
        with self.assertRaises(ValueError):
            recall_at_k(["A"], ["A"], 0)


class Evidence(unittest.TestCase):
    def test_counts_evidence_found_inside_a_single_chunk(self):
        texts = ["The deadline is 800 MS total.", "Retry once."]
        self.assertEqual(evidence_recall(texts, ["800 ms total", "retry once"]), 1.0)
        self.assertEqual(evidence_recall(texts, ["800 ms total", "circuit breaker"]), 0.5)
        self.assertEqual(evidence_recall(texts, ["total.\nretry"]), 0.0)   # split across chunks: not found
        self.assertIsNone(evidence_recall(texts, []))


class FakeRetriever:
    def __init__(self, results):
        self.results = results

    def retrieve(self, query, k=5, role="engineer", include_archived=False):
        return [Hit(c, 1.0) for c in self.results[query]][:k]


class Harness(unittest.TestCase):
    def test_rows_summary_and_leaks(self):
        a, b, secret = chunk("a#0", "alpha fact"), chunk("b#0", "beta"), chunk("s#0", "secret", access="sre")
        retriever = FakeRetriever({"q1": [b, a], "q2": [secret], "q3": [b]})
        questions = [
            {"id": "1", "question": "q1", "role": "engineer", "relevant": ["a"], "evidence": ["alpha fact"], "type": "t1"},
            {"id": "2", "question": "q2", "role": "engineer", "relevant": [], "type": "t2"},
            {"id": "3", "question": "q3", "role": "engineer", "relevant": ["a"], "evidence": ["alpha"], "type": "t1"},
        ]
        report = evaluate_retrieval(retriever, questions, k=5)
        rows = {r["id"]: r for r in report["rows"]}
        self.assertEqual(rows["1"]["retrieved"], ["b", "a"])
        self.assertEqual((rows["1"]["mrr"], rows["1"]["evidence"]), (0.5, 1.0))
        self.assertIsNone(rows["2"]["recall"])
        self.assertEqual(rows["2"]["leaks"], ["s"])
        self.assertEqual(report["summary"]["recall"], 0.5)        # mean of 1.0 and 0.0; q2 not counted
        self.assertEqual(report["summary"]["n"], 3)
        self.assertEqual(report["by_type"]["t1"]["mrr"], 0.25)
        self.assertGreater(rows["1"]["tokens"], 0)


class AnswerChecks(unittest.TestCase):
    Q = {"expected": "answer", "must_include": ["800"], "must_not_include": ["3000"]}

    def test_passes_when_required_facts_are_present(self):
        self.assertTrue(check_answer(Answer("The deadline is 800 ms [S1]."), self.Q)["ok"])

    def test_reports_missing_and_forbidden_text(self):
        result = check_answer(Answer("It used to be 3000 ms."), self.Q)
        self.assertEqual((result["ok"], result["missing"], result["forbidden"]), (False, ["800"], ["3000"]))

    def test_abstention_is_right_only_when_expected(self):
        abstain = Answer("I don't know based on the available documents.", abstained=True)
        self.assertTrue(check_answer(abstain, {"expected": "abstain"})["ok"])
        wrong = check_answer(abstain, self.Q)
        self.assertEqual((wrong["ok"], wrong["abstain_ok"], wrong["missing"]), (False, False, []))
        self.assertFalse(check_answer(Answer("It is 720 workers."), {"expected": "abstain"})["ok"])


class Judge(unittest.TestCase):
    def test_reads_json_wrapped_in_text(self):
        reply = 'Sure!\n```json\n{"claims": [{"claim": "a", "supported": true}, {"claim": "b", "supported": false}]}\n```'
        result = parse_judgement(reply)
        self.assertEqual((len(result["claims"]), result["faithfulness"]), (2, 0.5))

    def test_no_claims_means_no_score(self):
        self.assertIsNone(parse_judgement('{"claims": []}')["faithfulness"])

    def test_invalid_replies_raise(self):
        for reply in ["no json here", "{not json}"]:
            with self.assertRaises(ValueError):
                parse_judgement(reply)


if __name__ == "__main__":
    unittest.main()
