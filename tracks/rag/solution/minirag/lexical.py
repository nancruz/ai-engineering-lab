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
        # LAB1-BEGIN
        # Task: For each item, tokenize item.search_text(), store Counter(terms) in
        #       self.tf and len(terms) in self.lengths. Then fill self.df (count each
        #       term once per item) and self.postings (term -> item positions).
        for position, item in enumerate(self.items):
            counts = Counter(tokenize(item.search_text()))
            self.tf.append(counts)
            self.lengths.append(sum(counts.values()))
            for term in counts:
                self.df[term] += 1
                self.postings.setdefault(term, []).append(position)
        # LAB1-END
        self.avgdl = sum(self.lengths) / len(self.lengths) if self.lengths else 0.0

    def idf(self, term):
        """Inverse document frequency: rare terms count more. Never negative."""
        # LAB1-BEGIN
        # Task: Implement ln(1 + (N - df + 0.5) / (df + 0.5)) with N = len(self.items).
        n, df = len(self.items), self.df.get(term, 0)
        return math.log(1 + (n - df + 0.5) / (df + 0.5))
        # LAB1-END

    def term_scores(self, query_terms, position):
        """BM25 contribution of each distinct query term to the item at `position`."""
        # LAB1-BEGIN
        # Task: For each distinct term in query_terms (keep first-seen order), compute
        #       idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * length / avgdl)).
        #       Skip terms with tf == 0. Return a dict term -> contribution.
        counts, length = self.tf[position], self.lengths[position]
        norm = 1 - self.b + self.b * length / self.avgdl if self.avgdl else 1.0
        scores = {}
        for term in dict.fromkeys(query_terms):
            f = counts.get(term, 0)
            if f:
                scores[term] = self.idf(term) * f * (self.k1 + 1) / (f + self.k1 * norm)
        return scores
        # LAB1-END

    def search(self, query, k=5, allow=None):
        """Return up to k (item, score) pairs, best first.

        Only items containing at least one query term are candidates (use the
        postings). Skip items for which allow(item) is False. Sort by score
        descending, then by item id so ties are deterministic.
        """
        # LAB1-BEGIN
        # Task: Tokenize the query, collect candidate positions from self.postings,
        #       score each allowed candidate with sum(self.term_scores(...).values()),
        #       sort by (-score, item.id) and return the first k.
        terms = tokenize(query)
        candidates = sorted({p for t in dict.fromkeys(terms) for p in self.postings.get(t, [])})
        results = []
        for position in candidates:
            item = self.items[position]
            if allow is not None and not allow(item):
                continue
            score = sum(self.term_scores(terms, position).values())
            if score > 0:
                results.append((item, score))
        results.sort(key=lambda pair: (-pair[1], pair[0].id))
        return results[:k]
        # LAB1-END

    def explain(self, query, item_id):
        """Per-term contributions for one item: useful to see *why* it ranked. (Supplied.)"""
        for position, item in enumerate(self.items):
            if item.id == item_id:
                return self.term_scores(tokenize(query), position)
        raise KeyError(item_id)
