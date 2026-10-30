"""Retrievers: one interface over keyword, vector, hybrid and reranked search.

    retriever.retrieve(query, k=5, role="engineer", include_archived=False) -> list[Hit]

Access and freshness rules are applied *before* ranking, so a chunk the user may
not read can never reach the prompt. (Filtering is Lab 4; the rest is supplied
and extended in Lab 6.)
"""
from dataclasses import dataclass

from .hybrid import rrf
from .lexical import BM25Index
from .vectors import VectorIndex

# Which document `access` levels each role may read.
ROLE_ACCESS = {"engineer": {"all"}, "sre": {"all", "sre"}}


@dataclass
class Hit:
    chunk: object
    score: float
    source: str = ""


def allowed(chunk, role, include_archived=False):
    """May `role` see this chunk?

    - The chunk's meta["access"] must be one of ROLE_ACCESS[role]; unknown roles see nothing.
    - Chunks with meta["status"] == "archived" are hidden unless include_archived is True.
    """
    # LAB4-BEGIN
    # Task: Look up the role's access levels (empty set for unknown roles), check
    #       chunk.meta.get("access", "all"), then the archived rule.
    if chunk.meta.get("access", "all") not in ROLE_ACCESS.get(role, set()):
        return False
    return include_archived or chunk.meta.get("status", "current") != "archived"
    # LAB4-END


class LexicalRetriever:
    name = "bm25"

    def __init__(self, chunks, k1=1.5, b=0.75):
        self.index = BM25Index(chunks, k1=k1, b=b)

    def retrieve(self, query, k=5, role="engineer", include_archived=False):
        found = self.index.search(query, k, allow=lambda c: allowed(c, role, include_archived))
        return [Hit(chunk, score, self.name) for chunk, score in found]


class DenseRetriever:
    name = "dense"

    def __init__(self, chunks, embedder, vectors=None):
        self.index = VectorIndex(chunks, embedder, vectors)

    def retrieve(self, query, k=5, role="engineer", include_archived=False):
        found = self.index.search(query, k, allow=lambda c: allowed(c, role, include_archived))
        return [Hit(chunk, score, self.name) for chunk, score in found]


class HybridRetriever:
    """Run several retrievers and merge their rankings with reciprocal rank fusion (Lab 6)."""
    name = "hybrid"

    def __init__(self, retrievers, depth=20, c=60):
        self.retrievers, self.depth, self.c = retrievers, depth, c

    def retrieve(self, query, k=5, role="engineer", include_archived=False):
        by_id, rankings = {}, []
        for retriever in self.retrievers:
            hits = retriever.retrieve(query, self.depth, role, include_archived)
            rankings.append([h.chunk.id for h in hits])
            for h in hits:
                by_id.setdefault(h.chunk.id, h.chunk)
        return [Hit(by_id[cid], score, self.name) for cid, score in rrf(rankings, self.c)[:k]]


class RerankRetriever:
    """Fetch a wider shortlist, then reorder it with a slower, more precise scorer (Lab 6)."""

    def __init__(self, base, reranker, depth=20):
        self.base, self.reranker, self.depth = base, reranker, depth
        self.name = f"{base.name}+rerank"

    def retrieve(self, query, k=5, role="engineer", include_archived=False):
        from .rerank import rerank
        return rerank(query, self.base.retrieve(query, self.depth, role, include_archived), self.reranker, k)


class MultiQueryRetriever:
    """Ask the LLM for rephrasings, retrieve for each, fuse with RRF (Lab 6)."""

    def __init__(self, base, llm, n=3, depth=20, c=60):
        self.base, self.llm, self.n, self.depth, self.c = base, llm, n, depth, c
        self.name = f"{base.name}+multiquery"

    def retrieve(self, query, k=5, role="engineer", include_archived=False):
        from .query import expand_query
        by_id, rankings = {}, []
        for q in expand_query(query, self.llm, self.n):
            hits = self.base.retrieve(q, self.depth, role, include_archived)
            rankings.append([h.chunk.id for h in hits])
            for h in hits:
                by_id.setdefault(h.chunk.id, h.chunk)
        return [Hit(by_id[cid], score, self.name) for cid, score in rrf(rankings, self.c)[:k]]


def build_retriever(spec, chunks, embedder=None, llm=None, reranker=None, vectors=None, k1=1.5, b=0.75):
    """spec: bm25 | dense | hybrid, optionally followed by +rerank and/or +multiquery."""
    base, *extras = spec.split("+")
    if base == "bm25":
        retriever = LexicalRetriever(chunks, k1, b)
    elif base in ("dense", "hybrid"):
        if embedder is None:
            from .embeddings import HashingEmbedder
            embedder = HashingEmbedder()
        dense = DenseRetriever(chunks, embedder, vectors)
        retriever = dense if base == "dense" else HybridRetriever([LexicalRetriever(chunks, k1, b), dense])
    else:
        raise ValueError(f"unknown retriever {spec!r}")
    for extra in extras:
        if extra == "rerank":
            if reranker is None:
                from .rerank import OverlapReranker
                reranker = OverlapReranker()
            retriever = RerankRetriever(retriever, reranker)
        elif extra == "multiquery":
            if llm is None:
                raise ValueError("+multiquery needs an LLM (--llm)")
            retriever = MultiQueryRetriever(retriever, llm)
        else:
            raise ValueError(f"unknown retriever option +{extra}")
    return retriever


def unique_docs(hits):
    """Document IDs in first-seen order: what document-level metrics compare."""
    return list(dict.fromkeys(h.chunk.doc_id for h in hits))
