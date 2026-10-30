"""Lab 4 — grounded generation.  Run: python3 -m unittest -v tests.test_lab4_generation"""
import unittest

from minirag.chunking import chunk_documents
from minirag.generation import (ABSTAIN, SYSTEM_PROMPT, ask, build_messages, count_tokens, format_source,
                                pack_context, parse_answer)
from minirag.llm import ExtractiveLLM, ScriptedLLM
from minirag.retrieval import Hit, LexicalRetriever, allowed

from .helpers import chunk, corpus


def hits(*chunks):
    return [Hit(c, 1.0 / (i + 1)) for i, c in enumerate(chunks)]


class AccessRules(unittest.TestCase):
    def test_roles_see_their_access_levels(self):
        public, restricted = chunk("p", "x"), chunk("r", "x", access="sre")
        self.assertTrue(allowed(public, "engineer"))
        self.assertFalse(allowed(restricted, "engineer"))
        self.assertTrue(allowed(restricted, "sre"))

    def test_archived_chunks_are_hidden_unless_asked_for(self):
        old = chunk("o", "x", status="archived")
        self.assertFalse(allowed(old, "engineer"))
        self.assertTrue(allowed(old, "engineer", include_archived=True))

    def test_unknown_roles_see_nothing(self):
        self.assertFalse(allowed(chunk("p", "x"), "intern"))


class FilteredRetrieval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retriever = LexicalRetriever(chunk_documents(corpus(), "headings"))

    def docs(self, query, role="engineer", **kw):
        return {h.chunk.doc_id for h in self.retriever.retrieve(query, k=10, role=role, **kw)}

    def test_restricted_documents_never_reach_engineers(self):
        self.assertNotIn("emergency-capacity-settings", self.docs("playback emergency worker count"))
        self.assertIn("emergency-capacity-settings", self.docs("playback emergency worker count", role="sre"))

    def test_archived_documents_are_filtered_by_default(self):
        self.assertNotIn("catalog-api-timeouts-2023", self.docs("catalog timeout retries"))
        self.assertIn("catalog-api-timeouts-2023", self.docs("catalog timeout retries", include_archived=True))


class PackContext(unittest.TestCase):
    def setUp(self):
        self.a, self.b, self.c = chunk("a#0", "A" * 400), chunk("b#0", "B" * 400), chunk("c#0", "C" * 40)

    def cost(self, n, c):
        return count_tokens(format_source(n, c))

    def test_keeps_rank_order_within_budget(self):
        selected, dropped = pack_context(hits(self.a, self.c), budget_tokens=1000)
        self.assertEqual([h.chunk.id for h in selected], ["a#0", "c#0"])
        self.assertEqual(dropped, [])

    def test_drops_what_does_not_fit_and_keeps_trying_smaller_chunks(self):
        budget = self.cost(1, self.a) + self.cost(2, self.c)
        selected, dropped = pack_context(hits(self.a, self.b, self.c), budget)
        self.assertEqual([h.chunk.id for h in selected], ["a#0", "c#0"])
        self.assertEqual([h.chunk.id for h in dropped], ["b#0"])

    def test_skips_duplicates(self):
        twin = chunk("twin#0", "A" * 400)
        selected, dropped = pack_context(hits(self.a, self.a, twin, self.c), 10_000)
        self.assertEqual([h.chunk.id for h in selected], ["a#0", "c#0"])
        self.assertEqual(dropped, [])

    def test_zero_budget_selects_nothing(self):
        selected, dropped = pack_context(hits(self.a), 0)
        self.assertEqual((selected, len(dropped)), ([], 1))


class Messages(unittest.TestCase):
    def test_system_rules_then_numbered_sources_then_question(self):
        a, b = chunk("a#0", "Alpha text."), chunk("b#0", "Beta text.")
        messages = build_messages("What is alpha?", hits(a, b))
        self.assertEqual([m["role"] for m in messages], ["system", "user"])
        self.assertEqual(messages[0]["content"], SYSTEM_PROMPT)
        user = messages[1]["content"]
        self.assertTrue(user.startswith("Sources:\n\n[S1] "))
        self.assertLess(user.index("Alpha text."), user.index("[S2]"))
        self.assertTrue(user.endswith("\n\nQuestion: What is alpha?"))
        self.assertIn(format_source(2, b), user)


class ParseAnswer(unittest.TestCase):
    def setUp(self):
        self.hits = hits(chunk("a#0", "x", doc_id="doc-a"), chunk("b#3", "y", doc_id="doc-b", heading="Steps"))

    def test_maps_labels_to_sources(self):
        answer = parse_answer("Do X [S2]. Then Y [S1][S2].", self.hits)
        self.assertEqual([c["label"] for c in answer.citations], ["S2", "S1"])
        self.assertEqual(answer.citations[0], {"label": "S2", "chunk_id": "b#3", "doc_id": "doc-b",
                                               "title": "Title of doc-b", "heading": "Steps"})
        self.assertEqual(answer.unknown, [])
        self.assertFalse(answer.abstained)

    def test_reports_citations_to_sources_that_do_not_exist(self):
        answer = parse_answer("Something [S1] and [S7] and [S7].", self.hits)
        self.assertEqual(answer.unknown, ["S7"])

    def test_detects_abstention(self):
        self.assertTrue(parse_answer(ABSTAIN, self.hits).abstained)
        self.assertTrue(parse_answer("Sorry, I do not know.", self.hits).abstained)
        self.assertFalse(parse_answer("The deadline is 800 ms [S1].", self.hits).abstained)


class Pipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retriever = LexicalRetriever(chunk_documents(corpus(), "headings"))

    def test_no_evidence_means_no_model_call(self):
        llm = ScriptedLLM(["should not be used"])
        result = ask("parental sabbatical", self.retriever, llm)
        self.assertTrue(result.answer.abstained)
        self.assertEqual(llm.calls, [])

    def test_the_model_sees_the_sources_and_its_citations_are_parsed(self):
        llm = ScriptedLLM(["The deadline is 800 ms [S1]."])
        result = ask("catalog request deadline", self.retriever, llm, k=3)
        prompt = llm.calls[0][-1]["content"]
        self.assertIn("Question: catalog request deadline", prompt)
        self.assertIn(result.selected[0].chunk.text, prompt)
        self.assertEqual(result.answer.citations[0]["chunk_id"], result.selected[0].chunk.id)
        self.assertEqual(set(result.timings), {"retrieve", "generate", "total"})

    def test_end_to_end_offline_answer_uses_the_current_document(self):
        result = ask("What is the current production timeout for catalog API requests?", self.retriever, ExtractiveLLM())
        self.assertIn("800", result.answer.text)
        self.assertNotIn("3000", result.answer.text)
        self.assertTrue(result.answer.citations)


if __name__ == "__main__":
    unittest.main()
