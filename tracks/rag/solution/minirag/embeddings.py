"""Embeddings: turn text into vectors whose angle reflects similarity. (Lab 2.)

An embedder has a `name` and two methods:
    embed_documents(texts) -> list of vectors
    embed_query(text)      -> one vector
Some models expect different prefixes for queries and documents, which is why
they are separate.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import zlib

from .net import post_json
from .text import tokenize


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def norm(v):
    return math.sqrt(dot(v, v))


def cosine(a, b):
    """Cosine similarity: dot(a, b) / (|a| * |b|). Return 0.0 if either vector is all zeros."""
    # LAB2-BEGIN
    # Task: Use dot() and norm(). Guard against division by zero.
    na, nb = norm(a), norm(b)
    return dot(a, b) / (na * nb) if na and nb else 0.0
    # LAB2-END


def normalize(v):
    """Scale v to length 1 (a zero vector stays zero). Normalized vectors: dot == cosine."""
    # LAB2-BEGIN
    # Task: Divide every component by norm(v); return a new list.
    n = norm(v)
    return [x / n for x in v] if n else list(v)
    # LAB2-END


class CachedEmbedder:
    """Wrap an embedder and remember vectors on disk, keyed by model name + text.

    Embedding is the slow, sometimes paid, part of indexing. Re-running an
    experiment should only embed text the cache has not seen.
    """

    def __init__(self, inner, path):
        self.inner, self.path = inner, Path(path)
        self.name = inner.name
        self.cache = json.loads(self.path.read_text()) if self.path.exists() else {}

    def key(self, kind, text):
        return hashlib.sha256(f"{self.inner.name}\n{kind}\n{text}".encode()).hexdigest()

    def embed_documents(self, texts):
        # LAB2-BEGIN
        # Task: Compute a key per text (kind "doc"). Send only the texts missing from
        #       self.cache to self.inner.embed_documents in ONE call, store the results,
        #       save with self.save() if anything was added, then return vectors in input order.
        keys = [self.key("doc", t) for t in texts]
        missing = list(dict.fromkeys(t for t, k in zip(texts, keys) if k not in self.cache))
        if missing:
            for text, vector in zip(missing, self.inner.embed_documents(missing)):
                self.cache[self.key("doc", text)] = vector
            self.save()
        return [self.cache[k] for k in keys]
        # LAB2-END

    def embed_query(self, text):
        k = self.key("query", text)
        if k not in self.cache:
            self.cache[k] = self.inner.embed_query(text)
            self.save()
        return self.cache[k]

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.cache))


# ---------------------------------------------------------------- supplied embedders

class HashingEmbedder:
    """Offline stand-in for an embedding model: hashes words and character trigrams.

    It is NOT semantic: "undo" and "roll back" share nothing. It does match word
    variants ("release", "releases") and makes the vector pipeline runnable and
    testable without downloads. Swap in a real model to see what meaning buys you.
    """

    def __init__(self, dim=512):
        self.dim, self.name = dim, f"hashing-{dim}"

    def features(self, text):
        for term in tokenize(text):
            yield "w:" + term
            padded = f"#{term}#"
            for i in range(len(padded) - 2):
                yield "c:" + padded[i:i + 3]

    def embed_query(self, text):
        v = [0.0] * self.dim
        for feature in self.features(text):
            h = zlib.crc32(feature.encode())
            v[h % self.dim] += 1.0 if (h >> 16) & 1 else -1.0
        return normalize(v)

    def embed_documents(self, texts):
        return [self.embed_query(t) for t in texts]


class OllamaEmbedder:
    """Embeddings from a local Ollama server, e.g. `ollama pull nomic-embed-text`."""

    PREFIXES = {"nomic-embed-text": ("search_document: ", "search_query: ")}

    def __init__(self, model="nomic-embed-text", host=None, batch=32):
        self.model, self.batch = model, batch
        self.host = (host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
        self.name = f"ollama:{model}"
        self.doc_prefix, self.query_prefix = self.PREFIXES.get(model.split(":")[0], ("", ""))

    def _embed(self, texts):
        vectors = []
        for i in range(0, len(texts), self.batch):
            reply = post_json(f"{self.host}/api/embed", {"model": self.model, "input": texts[i:i + self.batch]}, timeout=120)
            vectors += reply["embeddings"]
        return [normalize(v) for v in vectors]

    def embed_documents(self, texts):
        return self._embed([self.doc_prefix + t for t in texts])

    def embed_query(self, text):
        return self._embed([self.query_prefix + text])[0]


class SentenceTransformerEmbedder:
    """Local Hugging Face model via `pip install sentence-transformers`."""

    def __init__(self, model="sentence-transformers/all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer  # optional dependency
        self.model = SentenceTransformer(model)
        self.name = f"st:{model}"

    def embed_documents(self, texts):
        return self.model.encode(list(texts), normalize_embeddings=True).tolist()

    def embed_query(self, text):
        return self.embed_documents([text])[0]


class OpenAIEmbedder:
    """Any OpenAI-compatible /embeddings endpoint. Needs OPENAI_API_KEY (and OPENAI_BASE_URL if not OpenAI)."""

    def __init__(self, model, base_url=None, api_key=None):
        self.model, self.name = model, f"openai:{model}"
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")

    def embed_documents(self, texts):
        reply = post_json(f"{self.base_url}/embeddings", {"model": self.model, "input": list(texts)},
                          headers={"Authorization": f"Bearer {self.api_key}"}, timeout=120)
        return [normalize(item["embedding"]) for item in sorted(reply["data"], key=lambda d: d["index"])]

    def embed_query(self, text):
        return self.embed_documents([text])[0]


def make_embedder(spec="hashing", cache_dir=".minirag/cache"):
    """'hashing', 'ollama:<model>', 'st:<model>' or 'openai:<model>'. Real models are cached on disk."""
    kind, _, model = spec.partition(":")
    if kind == "hashing":
        return HashingEmbedder(int(model) if model else 512)
    if kind == "ollama":
        inner = OllamaEmbedder(model or "nomic-embed-text")
    elif kind == "st":
        inner = SentenceTransformerEmbedder(model or "sentence-transformers/all-MiniLM-L6-v2")
    elif kind == "openai":
        inner = OpenAIEmbedder(model)
    else:
        raise ValueError(f"unknown embedder {spec!r}")
    safe = "".join(c if c.isalnum() else "-" for c in inner.name)
    return CachedEmbedder(inner, Path(cache_dir) / f"embeddings-{safe}.json")
