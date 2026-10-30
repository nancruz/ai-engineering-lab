"""Small fixtures shared by the lab tests."""
from dataclasses import dataclass, field
from functools import lru_cache

from minirag.chunking import Chunk
from minirag.documents import Document, load_documents


@dataclass
class Item:
    """Anything with an id and search_text() can be indexed."""
    id: str
    text: str
    meta: dict = field(default_factory=dict)

    def search_text(self):
        return self.text


def chunk(cid, text, doc_id=None, access="all", status="current", heading=""):
    return Chunk(cid, doc_id or cid.split("#")[0], f"Title of {doc_id or cid}", heading, text, 0, len(text),
                 {"access": access, "status": status, "updated": "2026-01-01"})


def doc(doc_id, body, **meta):
    return Document(doc_id, meta.get("title", doc_id), body, {"status": "current", "access": "all", **meta})


@lru_cache(maxsize=1)
def corpus():
    return tuple(load_documents())


class FakeEmbedder:
    """Looks vectors up in a dict, counts how many texts it was asked to embed."""
    def __init__(self, table, name="fake"):
        self.table, self.name, self.embedded = table, name, []

    def embed_documents(self, texts):
        self.embedded += list(texts)
        return [list(self.table[t]) for t in texts]

    def embed_query(self, text):
        self.embedded.append(text)
        return list(self.table[text])
