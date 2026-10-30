"""Split documents into retrievable chunks that keep their provenance. (Lab 3.)

Every chunk remembers where it came from: `doc.body[chunk.start:chunk.end] == chunk.text`.
That is what lets you cite a source, show the exact passage, and re-index only
what changed.

Strategies:
- "document"  — the whole document is one chunk (what Labs 1 and 2 use)
- "fixed"     — windows of `size` characters, each starting `size - overlap` after the last
- "paragraph" — whole paragraphs packed greedily into chunks of at most `size` characters
- "headings"  — one chunk per Markdown section; long sections are packed by paragraph
"""
from dataclasses import dataclass, field
import re

STRATEGIES = ("document", "fixed", "paragraph", "headings")
HEADING = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t#]*$")
PARAGRAPH_BREAK = re.compile(r"\n(?:[ \t]*\n)+")


@dataclass
class Chunk:
    id: str
    doc_id: str
    title: str
    heading: str
    text: str
    start: int
    end: int
    meta: dict = field(default_factory=dict)

    def search_text(self):
        """What the indexes see: title and section heading give the chunk context."""
        label = f"{self.title} > {self.heading}" if self.heading else self.title
        return f"{label}\n{self.text}"


def strip_span(text, start, end):
    """Shrink [start, end) so it excludes leading and trailing whitespace. (Supplied.)"""
    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    return start, end


def headings(body):
    """List (offset, level, path) for each Markdown heading outside code fences. (Supplied.)

    The path joins headings from level 2 down, e.g. "When to roll back" or
    "Week 1 > Setup". The level-1 heading is the document title, so it is left out.
    """
    found, stack, offset, in_fence = [], [], 0, False
    for line in body.splitlines(keepends=True):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        match = None if in_fence else HEADING.match(line.rstrip("\n"))
        if match:
            level = len(match.group(1))
            stack = [(lvl, name) for lvl, name in stack if lvl < level] + [(level, match.group(2))]
            found.append((offset, level, " > ".join(name for lvl, name in stack if lvl >= 2)))
        offset += len(line)
    return found


def heading_at(body, offset, marks=None):
    """The heading path in effect at `offset`. (Supplied.)"""
    path = ""
    for start, _level, name in marks if marks is not None else headings(body):
        if start > offset:
            break
        path = name
    return path


def fixed_spans(text, start, end, size, overlap):
    """Character windows over text[start:end]. Returns a list of (start, end)."""
    if size <= 0 or not 0 <= overlap < size:
        raise ValueError("need size > 0 and 0 <= overlap < size")
    # TODO (Lab 3): Step through [start, end) in steps of size - overlap. Each window is
    #       (pos, min(pos + size, end)). Stop after the window that reaches `end`.
    #       Skip windows that contain only whitespace.
    raise NotImplementedError("Lab 3: write fixed_spans() in minirag/chunking.py")


def paragraph_spans(text, start, end):
    """Non-empty paragraphs of text[start:end], separated by blank lines, whitespace stripped."""
    # TODO (Lab 3): Use PARAGRAPH_BREAK.finditer on text[start:end] to find the blank-line
    #       separators. The pieces between them are paragraphs. Convert them back
    #       to offsets in `text`, strip them with strip_span and drop empty ones.
    raise NotImplementedError("Lab 3: write paragraph_spans() in minirag/chunking.py")


def pack_spans(text, spans, size, overlap=0):
    """Merge consecutive spans while the merged span stays within `size` characters.

    A single span longer than `size` is cut into fixed windows instead.
    """
    # TODO (Lab 3): Walk the spans in order keeping a current (start, end). Extend it while
    #       next_end - current_start <= size; otherwise emit it and start a new one.
    #       Spans longer than size: emit the current one, then fixed_spans(...) of it.
    raise NotImplementedError("Lab 3: write pack_spans() in minirag/chunking.py")


def section_spans(body):
    """One (start, end, heading_path) per Markdown section that has content."""
    # TODO (Lab 3): A section runs from one heading's offset to the next heading's offset
    #       (the first starts at 0, the last ends at len(body)). Strip each span.
    #       Drop sections whose only content is the heading line itself.
    raise NotImplementedError("Lab 3: write section_spans() in minirag/chunking.py")


def chunk_document(doc, strategy="headings", size=800, overlap=0):
    """Split one Document into Chunks. (Supplied: wires the functions above together.)"""
    body = doc.body
    if strategy == "document":
        s, e = strip_span(body, 0, len(body))
        return [Chunk(doc.id, doc.id, doc.title, "", body[s:e], s, e, dict(doc.meta))]
    marks = headings(body)
    if strategy == "fixed":
        spans = [(s, e, heading_at(body, s, marks)) for s, e in fixed_spans(body, 0, len(body), size, overlap)]
    elif strategy == "paragraph":
        spans = [(s, e, heading_at(body, s, marks)) for s, e in pack_spans(body, paragraph_spans(body, 0, len(body)), size, overlap)]
    elif strategy == "headings":
        spans = []
        for s, e, path in section_spans(body):
            parts = [(s, e)] if e - s <= size else pack_spans(body, paragraph_spans(body, s, e), size, overlap)
            spans += [(ps, pe, path) for ps, pe in parts]
    else:
        raise ValueError(f"unknown strategy {strategy!r}; choose from {STRATEGIES}")
    return [Chunk(f"{doc.id}#{i}", doc.id, doc.title, path, body[s:e], s, e, dict(doc.meta))
            for i, (s, e, path) in enumerate(spans)]


def chunk_documents(docs, strategy="headings", size=800, overlap=0):
    return [chunk for doc in docs for chunk in chunk_document(doc, strategy, size, overlap)]
