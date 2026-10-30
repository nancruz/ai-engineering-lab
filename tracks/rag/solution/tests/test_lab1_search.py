"""Lab 1 — keyword search with BM25.  Run: python3 -m unittest -v tests.test_lab1_search"""
import unittest

from minirag.chunking import chunk_documents
from minirag.lexical import BM25Index
from minirag.text import tokenize

from .helpers import Item, corpus

TINY = [Item("A", "rollback playback release lumen"),
        Item("B", "playback timeout timeout timeout lumen"),
        Item("C", "catalog timeout lumen")]


class Tokenize(unittest.TestCase):
    def test_lowercases_and_splits_on_punctuation(self):
        self.assertEqual(tokenize("Catalog API: timeouts, retries!"), ["catalog", "api", "timeouts", "retries"])

    def test_keeps_compound_terms_whole_and_as_parts(self):
        self.assertEqual(tokenize("PLAY-4012 on eu-west-2"),
                         ["play-4012", "play", "4012", "eu-west-2", "eu", "west", "2"])
        self.assertEqual(tokenize("CATALOG_DEADLINE_MS=800"), ["catalog_deadline_ms", "catalog", "deadline", "ms", "800"])

    def test_removes_stopwords(self):
        self.assertEqual(tokenize("What is the rollback policy for the playback service?"),
                         ["rollback", "policy", "playback", "service"])

    def test_empty_text(self):
        self.assertEqual(tokenize("  ... !!"), [])


class BuildIndex(unittest.TestCase):
    def setUp(self):
        self.index = BM25Index(TINY)

    def test_term_frequencies_and_lengths(self):
        self.assertEqual(self.index.tf[1]["timeout"], 3)
        self.assertEqual(self.index.lengths, [4, 5, 3])
        self.assertEqual(self.index.avgdl, 4.0)

    def test_document_frequency_counts_each_item_once(self):
        self.assertEqual(self.index.df["timeout"], 2)
        self.assertEqual(self.index.df["lumen"], 3)

    def test_postings_list_items_containing_the_term(self):
        self.assertEqual(self.index.postings["timeout"], [1, 2])
        self.assertEqual(self.index.postings["rollback"], [0])


class Scoring(unittest.TestCase):
    def setUp(self):
        self.index = BM25Index(TINY)

    def test_idf_rewards_rare_terms_and_is_never_negative(self):
        self.assertAlmostEqual(self.index.idf("rollback"), 0.98083, places=4)
        self.assertAlmostEqual(self.index.idf("playback"), 0.47000, places=4)
        self.assertGreater(self.index.idf("lumen"), 0)          # in every item: small but positive
        self.assertGreater(self.index.idf("never-seen"), self.index.idf("rollback"))

    def test_term_scores_follow_the_formula(self):
        self.assertAlmostEqual(self.index.term_scores(["timeout"], 1)["timeout"], 0.73726, places=4)
        self.assertAlmostEqual(self.index.term_scores(["timeout"], 2)["timeout"], 0.52958, places=4)
        self.assertEqual(self.index.term_scores(["catalog"], 0), {})   # absent terms are skipped

    def test_repeated_query_terms_count_once(self):
        once = self.index.term_scores(["timeout"], 1)
        self.assertEqual(self.index.term_scores(["timeout", "timeout"], 1), once)

    def test_term_frequency_saturates(self):
        items = [Item("one", "timeout x x x x x x x x x"), Item("ten", " ".join(["timeout"] * 10)), Item("z", "other")]
        index = BM25Index(items, k1=1.5, b=0.0)
        ratio = index.term_scores(["timeout"], 1)["timeout"] / index.term_scores(["timeout"], 0)["timeout"]
        self.assertLess(ratio, 3)       # ten times the occurrences, nowhere near ten times the score
        flat = BM25Index(items, k1=0.0, b=0.0)
        self.assertAlmostEqual(flat.term_scores(["timeout"], 1)["timeout"], flat.term_scores(["timeout"], 0)["timeout"])

    def test_length_normalization(self):
        items = [Item("short", "timeout"), Item("long", "timeout " + "filler " * 20), Item("z", "other")]
        normalized = BM25Index(items, b=0.75)
        self.assertGreater(normalized.term_scores(["timeout"], 0)["timeout"], normalized.term_scores(["timeout"], 1)["timeout"])
        plain = BM25Index(items, b=0.0)
        self.assertAlmostEqual(plain.term_scores(["timeout"], 0)["timeout"], plain.term_scores(["timeout"], 1)["timeout"])


class Search(unittest.TestCase):
    def setUp(self):
        self.index = BM25Index(TINY)

    def test_returns_best_first_and_only_matching_items(self):
        results = self.index.search("timeout", k=5)
        self.assertEqual([item.id for item, _ in results], ["B", "C"])
        self.assertGreater(results[0][1], results[1][1])

    def test_respects_k_and_allow(self):
        self.assertEqual(len(self.index.search("lumen", k=2)), 2)
        allowed = self.index.search("timeout", k=5, allow=lambda item: item.id != "B")
        self.assertEqual([item.id for item, _ in allowed], ["C"])

    def test_ties_are_broken_by_id(self):
        index = BM25Index([Item("b", "same words"), Item("a", "same words"), Item("c", "other")])
        self.assertEqual([item.id for item, _ in index.search("same", k=3)], ["a", "b"])

    def test_no_match_returns_nothing(self):
        self.assertEqual(self.index.search("parental leave"), [])

    def test_explain_adds_up_to_the_score(self):
        (item, score), = self.index.search("rollback release", k=1)
        self.assertAlmostEqual(sum(self.index.explain("rollback release", item.id).values()), score)


class RealCorpus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = BM25Index(chunk_documents(corpus(), "document"))

    def top(self, query, k=3):
        return [item.id for item, _ in self.index.search(query, k)]

    def test_exact_error_code(self):
        self.assertEqual(self.top("PLAY-4012 device clock")[0], "playback-error-codes")

    def test_exact_phrase_terms(self):
        self.assertEqual(self.top("kill switch flag naming")[0], "feature-flags-policy")

    def test_finds_both_catalog_timeout_versions(self):
        # BM25 knows nothing about freshness: the archived doc ranks too (Lab 4 filters it).
        self.assertEqual(set(self.top("catalog timeout retries", 2)), {"catalog-api-timeouts", "catalog-api-timeouts-2023"})


if __name__ == "__main__":
    unittest.main()
