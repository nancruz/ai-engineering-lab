"""Lab 6 — hybrid search, reranking and query rewriting.  Run: python3 -m unittest -v tests.test_lab6_retrieval"""
import unittest

from minirag.chunking import chunk_documents
from minirag.embeddings import HashingEmbedder
from minirag.hybrid import rrf
from minirag.llm import ScriptedLLM
from minirag.query import parse_queries
from minirag.rerank import parse_score, rerank
from minirag.retrieval import DenseRetriever, Hit, HybridRetriever, LexicalRetriever, MultiQueryRetriever

from .helpers import chunk, corpus


class Fusion(unittest.TestCase):
    def test_worked_example(self):
        fused = rrf([["A", "B", "C"], ["C", "A", "D"]], c=60)
        self.assertEqual([i for i, _ in fused], ["A", "C", "B", "D"])
        self.assertAlmostEqual(dict(fused)["A"], 1 / 61 + 1 / 62)
        self.assertAlmostEqual(dict(fused)["D"], 1 / 63)

    def test_repeats_within_one_ranking_count_once(self):
        self.assertAlmostEqual(dict(rrf([["A", "A", "B"]], c=0))["B"], 1 / 2)
        self.assertAlmostEqual(dict(rrf([["A", "A", "B"]], c=0))["A"], 1.0)

    def test_ties_are_broken_by_id_and_empty_input_is_fine(self):
        self.assertEqual([i for i, _ in rrf([["b"], ["a"]])], ["a", "b"])
        self.assertEqual(rrf([]), [])

    def test_smaller_c_rewards_top_positions_more(self):
        lists = [["A", "B"], ["B", "C"], ["A", "C"]]
        self.assertGreater(dict(rrf(lists, 1))["A"] - dict(rrf(lists, 1))["C"],
                           dict(rrf(lists, 100))["A"] - dict(rrf(lists, 100))["C"])


class HybridOnTheCorpus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        chunks = chunk_documents(corpus(), "headings")
        cls.bm25, cls.dense = LexicalRetriever(chunks), DenseRetriever(chunks, HashingEmbedder())
        cls.hybrid = HybridRetriever([cls.bm25, cls.dense])

    def test_results_come_from_either_retriever_and_respect_access(self):
        query = "playback emergency worker count"
        fused = {h.chunk.id for h in self.hybrid.retrieve(query, k=5)}
        union = {h.chunk.id for r in (self.bm25, self.dense) for h in r.retrieve(query, k=20)}
        self.assertTrue(fused <= union)
        self.assertNotIn("emergency-capacity-settings", {cid.split("#")[0] for cid in fused})


class FixedScores:
    def __init__(self, scores):
        self.scores, self.calls = scores, 0

    def score(self, query, texts):
        self.calls += 1
        return [self.scores[t.split("\n", 1)[1]] for t in texts]


class Rerank(unittest.TestCase):
    def setUp(self):
        self.hits = [Hit(chunk(f"{n}#0", n), 1.0) for n in ["a", "b", "c", "d"]]

    def test_reorders_by_the_new_score_in_one_call(self):
        scorer = FixedScores({"a": 0.1, "b": 0.9, "c": 0.5, "d": 0.7})
        out = rerank("q", self.hits, scorer, top_n=3)
        self.assertEqual([h.chunk.id for h in out], ["b#0", "d#0", "c#0"])
        self.assertEqual(out[0].score, 0.9)
        self.assertEqual(scorer.calls, 1)

    def test_ties_keep_the_original_order(self):
        out = rerank("q", self.hits, FixedScores({"a": 1, "b": 2, "c": 2, "d": 1}), top_n=4)
        self.assertEqual([h.chunk.id for h in out], ["b#0", "c#0", "a#0", "d#0"])

    def test_empty_shortlist(self):
        self.assertEqual(rerank("q", [], FixedScores({}), 3), [])

    def test_parse_llm_scores(self):
        self.assertEqual(parse_score("8"), 8.0)
        self.assertEqual(parse_score("Score: 7/10"), 7.0)
        self.assertEqual(parse_score("about 6.5"), 6.5)
        self.assertEqual(parse_score("42"), 10.0)
        self.assertEqual(parse_score("not relevant at all"), 0.0)


class QueryRewriting(unittest.TestCase):
    def test_cleans_numbering_bullets_quotes_and_duplicates(self):
        reply = '1. roll back playback release\n2) "revert playback deploy"\n- How do I undo a bad playback release?\n\n* restore previous release\n- extra one'
        self.assertEqual(parse_queries(reply, "How do I undo a bad playback release?", n=3),
                         ["How do I undo a bad playback release?", "roll back playback release",
                          "revert playback deploy", "restore previous release"])

    def test_multiquery_retrieves_for_each_rewrite(self):
        seen = []

        class Base:
            name = "fake"

            def retrieve(self, query, k=5, role="engineer", include_archived=False):
                seen.append(query)
                return [Hit(chunk(f"{query}#0", query), 1.0)]

        llm = ScriptedLLM(["first rewrite\nsecond rewrite"])
        out = MultiQueryRetriever(Base(), llm, n=2).retrieve("original", k=5)
        self.assertEqual(seen, ["original", "first rewrite", "second rewrite"])
        self.assertEqual(len(out), 3)


if __name__ == "__main__":
    unittest.main()
