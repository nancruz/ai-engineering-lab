"""Rerankers: score (query, passage) pairs more carefully than the first-stage retriever. (Lab 6.)

A bi-encoder (Lab 2) embeds query and passage separately; a cross-encoder or an
LLM reads them together, which is slower but more precise. So: retrieve ~20
candidates cheaply, rerank them, keep the top k.

    reranker.score(query, texts) -> list of floats (higher = more relevant)
"""
import re

from .text import tokenize

RERANK_PROMPT = """Rate how well the passage answers the question, from 0 (unrelated) to 10 (fully answers it).
Reply with the number only.

Question: {question}

Passage:
{passage}"""


def rerank(query, hits, reranker, top_n=5):
    """Rescore hits with reranker.score(query, [chunk.search_text() ...]).

    Return the top_n hits sorted by new score (descending). Keep the original
    order for ties. The returned hits carry the new score.
    """
    from .retrieval import Hit
    if not hits:
        return []
    # TODO (Lab 6): Score all texts in ONE call, then sort by (-new_score, original_position).
    raise NotImplementedError("Lab 6: write rerank() in minirag/rerank.py")


def parse_score(text):
    """First number in an LLM reply, clamped to 0..10. No number -> 0.0.

    >>> parse_score("Score: 7/10")
    7.0
    """
    # TODO (Lab 6): Find the first number (allow decimals) with a regex; clamp to [0, 10].
    raise NotImplementedError("Lab 6: write parse_score() in minirag/rerank.py")


class LLMReranker:
    """Ask a language model to grade each passage. One call per passage: simple, not cheap."""

    def __init__(self, llm):
        self.llm = llm

    def score(self, query, texts):
        return [parse_score(self.llm.complete([{"role": "user", "content": RERANK_PROMPT.format(question=query, passage=t)}],
                                              max_tokens=5)) for t in texts]


class CrossEncoderReranker:
    """A trained cross-encoder via `pip install sentence-transformers`. (Supplied.)"""

    def __init__(self, model="cross-encoder/ms-marco-MiniLM-L6-v2"):
        from sentence_transformers import CrossEncoder  # optional dependency
        self.model = CrossEncoder(model)

    def score(self, query, texts):
        return [float(s) for s in self.model.predict([(query, t) for t in texts])]


class OverlapReranker:
    """Offline toy: share of query terms present, plus a bonus for adjacent query-term pairs.

    It only exists so the rerank stage runs without a model. Expect a real
    cross-encoder or LLM to do much better.
    """

    def score(self, query, texts):
        q = tokenize(query)
        wanted, pairs = set(q), set(zip(q, q[1:]))
        out = []
        for text in texts:
            t = tokenize(text)
            have, have_pairs = set(t), set(zip(t, t[1:]))
            share = len(wanted & have) / len(wanted) if wanted else 0.0
            bonus = len(pairs & have_pairs) / len(pairs) if pairs else 0.0
            out.append(round(share + 0.5 * bonus, 6))
        return out


def make_reranker(spec, llm=None):
    """'overlap', 'cross-encoder[:model]' or 'llm' (uses --llm)."""
    kind, _, model = spec.partition(":")
    if kind == "overlap":
        return OverlapReranker()
    if kind == "cross-encoder":
        return CrossEncoderReranker(model or "cross-encoder/ms-marco-MiniLM-L6-v2")
    if kind == "llm":
        if llm is None:
            raise ValueError("the llm reranker needs --llm")
        return LLMReranker(llm)
    raise ValueError(f"unknown reranker {spec!r}")
