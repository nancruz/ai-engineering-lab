"""Lab 3 — chunking.  Run: python3 -m unittest -v tests.test_lab3_chunking"""
import unittest

from minirag.chunking import (STRATEGIES, chunk_document, fixed_spans, pack_spans, paragraph_spans,
                              section_spans)

from .helpers import corpus, doc

MARKDOWN = """# Title

Intro paragraph.

## Setup

```bash
# not a heading, just a comment in code
make setup
```

## Usage
### Basic

Run it.

### Empty

## Last

Done.
"""


class FixedWindows(unittest.TestCase):
    def test_windows_step_by_size_minus_overlap(self):
        self.assertEqual(fixed_spans("x" * 25, 0, 25, 10, 3), [(0, 10), (7, 17), (14, 24), (21, 25)])

    def test_no_overlap_covers_the_text_exactly_once(self):
        self.assertEqual(fixed_spans("x" * 25, 0, 25, 10, 0), [(0, 10), (10, 20), (20, 25)])

    def test_respects_start_and_end(self):
        self.assertEqual(fixed_spans("x" * 30, 5, 20, 10, 0), [(5, 15), (15, 20)])

    def test_skips_whitespace_only_windows(self):
        self.assertEqual(fixed_spans("abc" + " " * 10 + "def", 0, 16, 5, 0), [(0, 5), (10, 15), (15, 16)])

    def test_invalid_settings(self):
        for size, overlap in [(0, 0), (10, 10), (10, -1)]:
            with self.assertRaises(ValueError):
                fixed_spans("text", 0, 4, size, overlap)


class Paragraphs(unittest.TestCase):
    TEXT = "First one.\n\nSecond\nstill second.\n   \n\n\nThird.  \n"

    def test_split_on_blank_lines_and_strip(self):
        spans = paragraph_spans(self.TEXT, 0, len(self.TEXT))
        self.assertEqual([self.TEXT[s:e] for s, e in spans], ["First one.", "Second\nstill second.", "Third."])

    def test_offsets_are_absolute(self):
        text = "IGNORED\n\n" + self.TEXT
        spans = paragraph_spans(text, 9, len(text))
        self.assertEqual(text[spans[0][0]:spans[0][1]], "First one.")

    def test_pack_merges_while_it_fits(self):
        text = "aaaa\n\nbbbb\n\ncccc"
        spans = paragraph_spans(text, 0, len(text))
        self.assertEqual([text[s:e] for s, e in pack_spans(text, spans, 10)], ["aaaa\n\nbbbb", "cccc"])
        self.assertEqual(len(pack_spans(text, spans, 4)), 3)

    def test_pack_cuts_oversized_paragraphs_into_windows(self):
        text = "short\n\n" + "y" * 25
        spans = paragraph_spans(text, 0, len(text))
        self.assertEqual(pack_spans(text, spans, 10), [(0, 5), (7, 17), (17, 27), (27, 32)])


class Sections(unittest.TestCase):
    def test_sections_follow_headings_and_ignore_code_fences(self):
        sections = section_spans(MARKDOWN)
        self.assertEqual([path for _, _, path in sections], ["", "Setup", "Usage > Basic", "Last"])
        setup = next(MARKDOWN[s:e] for s, e, p in sections if p == "Setup")
        self.assertIn("make setup", setup)
        self.assertTrue(setup.startswith("## Setup"))

    def test_heading_only_sections_are_dropped(self):
        self.assertNotIn("Usage > Empty", [p for _, _, p in section_spans(MARKDOWN)])
        self.assertNotIn("Usage", [p for _, _, p in section_spans(MARKDOWN)])


class Documents(unittest.TestCase):
    def test_every_chunk_points_back_to_its_exact_text(self):
        for d in corpus():
            for strategy in STRATEGIES:
                for c in chunk_document(d, strategy, size=300, overlap=50 if strategy == "fixed" else 0):
                    self.assertEqual(d.body[c.start:c.end], c.text, (d.id, strategy, c.id))

    def test_chunks_respect_the_size_limit(self):
        for d in corpus():
            for strategy in ("fixed", "paragraph", "headings"):
                for c in chunk_document(d, strategy, size=400):
                    self.assertLessEqual(len(c.text), 400, (d.id, strategy))

    def test_ids_are_unique_and_stable(self):
        d = next(x for x in corpus() if x.id == "on-call-handbook")
        first = [c.id for c in chunk_document(d, "headings", 400)]
        self.assertEqual(len(first), len(set(first)))
        self.assertEqual(first, [c.id for c in chunk_document(d, "headings", 400)])

    def test_heading_chunks_keep_the_eu_condition_with_its_instruction(self):
        runbook = next(x for x in corpus() if x.id == "playback-rollback-runbook")
        holder = next(c for c in chunk_document(runbook, "headings", 800) if "If the check fails" in c.text)
        self.assertIn("If the check fails, do not roll back in the EU region.", holder.text)
        self.assertEqual(holder.heading, "EU production")
        self.assertIn("EU production", holder.search_text())

    def test_chunks_carry_document_metadata(self):
        c = chunk_document(doc("d", "# D\n\nText.", access="sre"), "headings")[0]
        self.assertEqual((c.doc_id, c.meta["access"]), ("d", "sre"))


if __name__ == "__main__":
    unittest.main()
