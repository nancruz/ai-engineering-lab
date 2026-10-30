"""Exact (brute-force) vector search. (Lab 2.)

Vector databases (pgvector, Qdrant, Chroma, OpenSearch...) do the same job at
scale with approximate indexes such as HNSW. On a few hundred chunks, exact
search is fast and gives the true nearest neighbours to compare against.
"""
from .embeddings import dot, normalize


class VectorIndex:
    def __init__(self, items, embedder, vectors=None):
        """Embed every item's search_text() once (or reuse precomputed `vectors`)."""
        self.items, self.embedder = list(items), embedder
        raw = vectors if vectors is not None else embedder.embed_documents([i.search_text() for i in self.items])
        self.vectors = [normalize(v) for v in raw]

    def search(self, query, k=5, allow=None):
        """Return up to k (item, cosine) pairs, most similar first.

        Embed the query with embedder.embed_query, compare with every allowed item,
        sort by (-score, item.id), return the first k.
        """
        # LAB2-BEGIN
        # Task: Normalize the query vector so dot() equals cosine (stored vectors are
        #       already normalized). Score every item where allow is None or allow(item).
        q = normalize(self.embedder.embed_query(query))
        scored = [(item, dot(q, v)) for item, v in zip(self.items, self.vectors) if allow is None or allow(item)]
        scored.sort(key=lambda pair: (-pair[1], pair[0].id))
        return scored[:k]
        # LAB2-END
