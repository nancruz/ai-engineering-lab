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
        # LAB7-BEGIN
        # Task: Read existing {doc_id: fingerprint}. Classify each doc, collect the new
        #       chunks (chunk_document) of added/updated docs, embed their search_text()
        #       once if an embedder is given, then write everything in one transaction
        #       (with self.db: ...). Remember to delete chunks of updated and removed docs.
        stored = dict(self.db.execute("SELECT doc_id, fingerprint FROM documents"))
        report = {"added": [], "updated": [], "unchanged": [], "deleted": [], "embedded": 0}
        changed, new_chunks = [], []
        for doc in docs:
            fp = fingerprint(doc, settings)
            if doc.id not in stored:
                report["added"].append(doc.id)
            elif stored[doc.id] != fp:
                report["updated"].append(doc.id)
            else:
                report["unchanged"].append(doc.id)
                continue
            changed.append((doc, fp))
            new_chunks += list(enumerate(chunk_document(doc, strategy, size, overlap)))
        current = {doc.id for doc in docs}
        report["deleted"] = sorted(set(stored) - current)
        texts = [chunk.search_text() for _, chunk in new_chunks]
        vectors = embedder.embed_documents(texts) if embedder and texts else [None] * len(texts)
        report["embedded"] = len(new_chunks) if embedder else 0
        with self.db:
            for doc_id in report["deleted"] + [doc.id for doc, _ in changed]:
                self.db.execute("DELETE FROM chunks WHERE doc_id = ?", (doc_id,))
            for doc_id in report["deleted"]:
                self.db.execute("DELETE FROM documents WHERE doc_id = ?", (doc_id,))
            for doc, fp in changed:
                self.db.execute("INSERT OR REPLACE INTO documents VALUES (?, ?, ?)", (doc.id, fp, doc.title))
            for (ord_, chunk), vector in zip(new_chunks, vectors):
                self.db.execute("INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                (chunk.id, chunk.doc_id, ord_, chunk.title, chunk.heading, chunk.text, chunk.start,
                                 chunk.end, json.dumps(chunk.meta), json.dumps(vector) if vector is not None else None))
        return report
        # LAB7-END

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
