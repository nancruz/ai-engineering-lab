"""Keyword search with an inverted index and BM25 scoring. (Lab 1.)

BM25 score of item d for query terms q1..qn:

    score(d) = sum_i  idf(qi) * tf(qi,d) * (k1 + 1) / (tf(qi,d) + k1 * (1 - b + b * len(d) / avgdl))
    idf(t)   = ln(1 + (N - df(t) + 0.5) / (df(t) + 0.5))

tf = how often the term occurs in d, df = how many items contain it, N = number of
items, len(d) = number of terms in d, avgdl = average len over all items.
"""
from collections import Counter
import math

from .text import tokenize


class BM25Index:
    """Index any items that have an `id` and a `search_text()` (documents or chunks)."""

    def __init__(self, items, k1=1.5, b=0.75):
        if k1 < 0 or not 0 <= b <= 1:
            raise ValueError("BM25 needs k1 >= 0 and 0 <= b <= 1")
        self.items = list(items)
        self.k1, self.b = k1, b
        self.tf = []          # one Counter of term -> count per item
        self.lengths = []     # number of terms per item
        self.df = Counter()   # term -> number of items containing it
        self.postings = {}    # inverted index: term -> list of item positions
        # TODO (Lab 1): For each item, tokenize item.search_text(), store Counter(terms) in
        #       self.tf and len(terms) in self.lengths. Then fill self.df (count each
        #       term once per item) and self.postings (term -> item positions).
        raise NotImplementedError("Lab 1: write BM25Index.__init__() in minirag/lexical.py")
        self.avgdl = sum(self.lengths) / len(self.lengths) if self.lengths else 0.0

    def idf(self, term):
        """Inverse document frequency: rare terms count more. Never negative."""
        # TODO (Lab 1): Implement ln(1 + (N - df + 0.5) / (df + 0.5)) with N = len(self.items).
        raise NotImplementedError("Lab 1: write BM25Index.idf() in minirag/lexical.py")

    def term_scores(self, query_terms, position):
        """BM25 contribution of each distinct query term to the item at `position`."""
        # TODO (Lab 1): For each distinct term in query_terms (keep first-seen order), compute
        #       idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * length / avgdl)).
        #       Skip terms with tf == 0. Return a dict term -> contribution.
        raise NotImplementedError("Lab 1: write BM25Index.term_scores() in minirag/lexical.py")

    def search(self, query, k=5, allow=None):
        """Return up to k (item, score) pairs, best first.

        Only items containing at least one query term are candidates (use the
        postings). Skip items for which allow(item) is False. Sort by score
        descending, then by item id so ties are deterministic.
        """
        # TODO (Lab 1): Tokenize the query, collect candidate positions from self.postings,
        #       score each allowed candidate with sum(self.term_scores(...).values()),
        #       sort by (-score, item.id) and return the first k.
        raise NotImplementedError("Lab 1: write BM25Index.search() in minirag/lexical.py")

    def explain(self, query, item_id):
        """Per-term contributions for one item: useful to see *why* it ranked. (Supplied.)"""
        for position, item in enumerate(self.items):
            if item.id == item_id:
                return self.term_scores(tokenize(query), position)
        raise KeyError(item_id)
