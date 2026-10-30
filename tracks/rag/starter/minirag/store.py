"""A persistent index in SQLite with incremental re-indexing. (Lab 7.)

Production RAG keeps its chunks and vectors in a database (pgvector, OpenSearch,
a vector DB...). The hard part is not storing them; it is keeping them in sync
with the sources: re-embed only what changed, and make deletions disappear.
"""
import hashlib
import json
import sqlite3

from .chunking import Chunk, chunk_document

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    doc_id TEXT PRIMARY KEY,
    fingerprint TEXT NOT NULL,
    title TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS chunks (
    chunk_id TEXT PRIMARY KEY,
    doc_id TEXT NOT NULL REFERENCES documents(doc_id),
    ord INTEGER NOT NULL,
    title TEXT NOT NULL,
    heading TEXT NOT NULL,
    text TEXT NOT NULL,
    start INTEGER NOT NULL,
    end INTEGER NOT NULL,
    meta TEXT NOT NULL,
    embedding TEXT
);
CREATE INDEX IF NOT EXISTS chunks_by_doc ON chunks(doc_id);
"""


def fingerprint(doc, settings):
    """Changes whenever the document OR the way it is chunked/embedded changes. (Supplied.)"""
    payload = json.dumps([doc.body, doc.meta, settings], sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()


class IndexStore:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(str(path))
        self.db.executescript(SCHEMA)

    def sync(self, docs, strategy="headings", size=800, overlap=0, embedder=None):
        """Make the store match `docs` and return what changed.

        For each doc: compare fingerprint(doc, settings) with the stored one.
        - new doc       -> insert its chunks                      (counts as "added")
        - changed doc   -> delete its old chunks, insert new ones  ("updated")
        - same          -> do nothing                              ("unchanged")
        Docs in the store but no longer in `docs` are removed with their chunks ("deleted").
        Only chunks being inserted are embedded, in one embed_documents call.

        Returns {"added": [...ids], "updated": [...], "unchanged": [...], "deleted": [...], "embedded": n}.
        """
        settings = {"strategy": strategy, "size": size, "overlap": overlap,
                    "embedder": embedder.name if embedder else None}
        # TODO (Lab 7): Read existing {doc_id: fingerprint}. Classify each doc, collect the new
        #       chunks (chunk_document) of added/updated docs, embed their search_text()
        #       once if an embedder is given, then write everything in one transaction
        #       (with self.db: ...). Remember to delete chunks of updated and removed docs.
        raise NotImplementedError("Lab 7: write IndexStore.sync() in minirag/store.py")

    def chunks(self):
        """All stored chunks in a stable order. (Supplied.)"""
        rows = self.db.execute("SELECT chunk_id, doc_id, title, heading, text, start, end, meta FROM chunks ORDER BY doc_id, ord")
        return [Chunk(r[0], r[1], r[2], r[3], r[4], r[5], r[6], json.loads(r[7])) for r in rows]

    def vectors(self):
        """Stored vectors aligned with chunks(), or None if any chunk has no vector. (Supplied.)"""
        rows = [r[0] for r in self.db.execute("SELECT embedding FROM chunks ORDER BY doc_id, ord")]
        return None if any(r is None for r in rows) else [json.loads(r) for r in rows]

    def close(self):
        self.db.close()
