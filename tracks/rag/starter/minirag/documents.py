"""Load the knowledge base: Markdown files with a small front-matter header. (Supplied.)

    ---
    id: playback-rollback-runbook
    title: Playback rollback runbook
    status: current        # current | archived
    access: all            # all | sre
    updated: 2026-06-12
    ---
    # Playback rollback runbook
    ...
"""
from dataclasses import dataclass, field
import json
import os
from pathlib import Path


@dataclass
class Document:
    id: str
    title: str
    body: str
    meta: dict = field(default_factory=dict)
    path: str = ""


def parse_front_matter(raw):
    """Split '---' header lines from the Markdown body. Returns (meta, body)."""
    if not raw.startswith("---\n"):
        return {}, raw
    header, sep, body = raw[4:].partition("\n---\n")
    if not sep:
        return {}, raw
    meta = {}
    for line in header.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip().strip('"')
    return meta, body


def load_document(path):
    path = Path(path)
    raw = path.read_text(encoding="utf-8")
    meta, body = parse_front_matter(raw)
    meta.setdefault("status", "current")
    meta.setdefault("access", "all")
    doc_id = meta.get("id") or path.stem
    return Document(id=doc_id, title=meta.get("title", doc_id), body=body, meta=meta, path=str(path))


def load_documents(folder=None):
    folder = Path(folder) if folder else data_dir() / "docs"
    docs = [load_document(p) for p in sorted(folder.glob("*.md"))]
    if not docs:
        raise FileNotFoundError(f"No Markdown documents found in {folder}")
    return docs


def load_questions(path=None, split=None):
    path = Path(path) if path else data_dir() / "questions.json"
    questions = json.loads(path.read_text(encoding="utf-8"))
    for q in questions:
        q.setdefault("role", "engineer")
        q.setdefault("relevant", [])
        q.setdefault("expected", "abstain" if not q["relevant"] else "answer")
        q.setdefault("type", "general")
        q.setdefault("split", "dev")
    return [q for q in questions if split in (None, "all") or q.get("split") == split]


def data_dir():
    """Find the course data: $MINIRAG_DATA, ./data, or tracks/rag/data above this package."""
    if os.environ.get("MINIRAG_DATA"):
        return Path(os.environ["MINIRAG_DATA"])
    here = Path(__file__).resolve()
    for base in [Path.cwd(), *Path.cwd().parents, *here.parents]:
        for candidate in (base / "data", base / "tracks" / "rag" / "data"):
            if (candidate / "docs").is_dir() and (candidate / "questions.json").is_file():
                return candidate
    raise FileNotFoundError("Course data not found. Set MINIRAG_DATA to the folder holding docs/ and questions.json.")
