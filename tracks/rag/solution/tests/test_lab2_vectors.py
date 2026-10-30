"""Lab 2 — embeddings and vector search.  Run: python3 -m unittest -v tests.test_lab2_vectors"""
import math
import tempfile
import unittest
from pathlib import Path

from minirag.chunking import chunk_documents
from minirag.embeddings import CachedEmbedder, HashingEmbedder, cosine, normalize
from minirag.vectors import VectorIndex

from .helpers import FakeEmbedder, Item, corpus


class Similarity(unittest.TestCase):
    def test_cosine_of_identical_orthogonal_and_opposite_vectors(self):
        self.assertAlmostEqual(cosine([1, 2, 3], [1, 2, 3]), 1.0)
        self.assertAlmostEqual(cosine([1, 0], [0, 5]), 0.0)
        self.assertAlmostEqual(cosine([1, 1], [-1, -1]), -1.0)

    def test_cosine_ignores_length(self):
        self.assertAlmostEqual(cosine([1, 2], [10, 20]), 1.0)
        self.assertAlmostEqual(cosine([1, 0], [1, 1]), 1 / math.sqrt(2))

    def test_cosine_with_a_zero_vector_is_zero(self):
        self.assertEqual(cosine([0, 0], [1, 2]), 0.0)

    def test_normalize_gives_unit_length(self):
        v = normalize([3, 4])
        self.assertAlmostEqual(v[0], 0.6)
        self.assertAlmostEqual(math.sqrt(sum(x * x for x in v)), 1.0)

    def test_normalize_keeps_zero_and_does_not_modify_input(self):
        original = [3.0, 4.0]
        normalize(original)
        self.assertEqual(original, [3.0, 4.0])
        self.assertEqual(normalize([0.0, 0.0]), [0.0, 0.0])


class VectorSearch(unittest.TestCase):
    def setUp(self):
        table = {"a": [1, 0], "b": [0.7, 0.7], "c": [0, 1], "q": [1, 0.1], "d": [0.7, 0.7]}
        self.embedder = FakeEmbedder(table)
        self.items = [Item("a", "a"), Item("b", "b"), Item("c", "c")]

    def test_ranks_by_cosine_similarity(self):
        index = VectorIndex(self.items, self.embedder)
        results = index.search("q", k=3)
        self.assertEqual([item.id for item, _ in results], ["a", "b", "c"])
        self.assertAlmostEqual(results[0][1], cosine([1, 0.1], [1, 0]))

    def test_respects_k_and_allow(self):
        index = VectorIndex(self.items, self.embedder)
        self.assertEqual(len(index.search("q", k=2)), 2)
        self.assertEqual([i.id for i, _ in index.search("q", k=3, allow=lambda i: i.id != "a")], ["b", "c"])

    def test_ties_are_broken_by_id(self):
        index = VectorIndex([Item("d", "d"), Item("b", "b")], self.embedder)
        self.assertEqual([i.id for i, _ in index.search("q", k=2)], ["b", "d"])

    def test_documents_are_embedded_once(self):
        index = VectorIndex(self.items, self.embedder)
        before = len(self.embedder.embedded)
        index.search("q")
        index.search("q")
        self.assertEqual(len(self.embedder.embedded) - before, 2)   # only the two queries


class Cache(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = Path(self.folder.name) / "cache.json"
        self.inner = FakeEmbedder({"x": [1, 0], "y": [0, 1], "z": [1, 1]})

    def tearDown(self):
        self.folder.cleanup()

    def test_only_missing_texts_reach_the_model(self):
        cached = CachedEmbedder(self.inner, self.path)
        self.assertEqual(cached.embed_documents(["x", "y"]), [[1, 0], [0, 1]])
        self.assertEqual(cached.embed_documents(["y", "z", "x"]), [[0, 1], [1, 1], [1, 0]])
        self.assertEqual(self.inner.embedded, ["x", "y", "z"])

    def test_cache_survives_a_restart(self):
        CachedEmbedder(self.inner, self.path).embed_documents(["x"])
        again = CachedEmbedder(self.inner, self.path)
        self.assertEqual(again.embed_documents(["x"]), [[1, 0]])
        self.assertEqual(self.inner.embedded, ["x"])

    def test_a_different_model_does_not_reuse_vectors(self):
        CachedEmbedder(self.inner, self.path).embed_documents(["x"])
        other = FakeEmbedder({"x": [0, 1]}, name="other-model")
        self.assertEqual(CachedEmbedder(other, self.path).embed_documents(["x"]), [[0, 1]])


class RealCorpus(unittest.TestCase):
    def test_dense_retrieval_runs_on_the_knowledge_base(self):
        index = VectorIndex(chunk_documents(corpus(), "document"), HashingEmbedder())
        top = [item.doc_id for item, _ in index.search("rolling back playback releases", k=3)]
        self.assertIn("playback-rollback-runbook", top)


if __name__ == "__main__":
    unittest.main()
