"""Build a configured RAG system from settings. Used by the CLI, the service and the labs. (Supplied.)"""
from dataclasses import dataclass, field, asdict
from pathlib import Path

from .chunking import chunk_documents
from .documents import load_documents
from .embeddings import make_embedder
from .llm import make_llm
from .rerank import make_reranker
from .retrieval import build_retriever


@dataclass
class Settings:
    retriever: str = "bm25"        # bm25 | dense | hybrid, plus +rerank / +multiquery
    chunks: str = "headings"       # document | fixed | paragraph | headings
    size: int = 800
    overlap: int = 0
    k: int = 5
    k1: float = 1.5                # BM25 term-frequency saturation
    b: float = 0.75                # BM25 length normalization
    embedder: str = "hashing"      # hashing | ollama:<model> | st:<model> | openai:<model>
    reranker: str = "overlap"      # overlap | cross-encoder[:model] | llm
    llm: str = "extractive"        # extractive | ollama:<model> | openai:<model> | anthropic:<model>
    budget: int = 1500             # context budget in (estimated) tokens
    db: str = ""                   # SQLite index path; empty = rebuild in memory
    docs: str = ""                 # folder of Markdown docs; empty = course data

    def as_dict(self):
        return asdict(self)


@dataclass
class System:
    settings: Settings
    chunks: list
    retriever: object
    llm: object
    sync_report: dict = field(default_factory=dict)


def build_system(settings, docs=None, llm=None):
    docs = docs if docs is not None else load_documents(settings.docs or None)
    llm = llm or make_llm(settings.llm)
    needs_vectors = settings.retriever.split("+")[0] in ("dense", "hybrid")
    embedder = make_embedder(settings.embedder) if needs_vectors else None
    vectors, report = None, {}
    if settings.db:
        from .store import IndexStore
        Path(settings.db).parent.mkdir(parents=True, exist_ok=True)
        store = IndexStore(settings.db)
        report = store.sync(docs, settings.chunks, settings.size, settings.overlap, embedder)
        chunks = store.chunks()
        vectors = store.vectors() if embedder else None
        store.close()
    else:
        chunks = chunk_documents(docs, settings.chunks, settings.size, settings.overlap)
    reranker = make_reranker(settings.reranker, llm) if "rerank" in settings.retriever else None
    retriever = build_retriever(settings.retriever, chunks, embedder=embedder, llm=llm, reranker=reranker,
                                vectors=vectors, k1=settings.k1, b=settings.b)
    return System(settings, chunks, retriever, llm, report)
