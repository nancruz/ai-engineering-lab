"""Lab 7 — persistent index and HTTP service.  Run: python3 -m unittest -v tests.test_lab7_ship"""
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from minirag.chunking import chunk_documents
from minirag.llm import ExtractiveLLM, ScriptedLLM
from minirag.net import ModelError
from minirag.pipeline import Settings, build_system
from minirag.service import ListLog, RagService, make_stdlib_server
from minirag.store import IndexStore

from .helpers import FakeEmbedder, corpus, doc


class CountingEmbedder(FakeEmbedder):
    def __init__(self):
        super().__init__({}, name="counting")

    def embed_documents(self, texts):
        self.embedded += list(texts)
        return [[float(len(t)), 1.0] for t in texts]


class Store(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.store = IndexStore(Path(self.folder.name) / "index.sqlite")
        self.docs = [doc("a", "# A\n\nAlpha.\n\n## Part\n\nMore alpha."), doc("b", "# B\n\nBeta."), doc("c", "# C\n\nGamma.")]

    def tearDown(self):
        self.store.close()
        self.folder.cleanup()

    def test_first_sync_adds_everything(self):
        report = self.store.sync(self.docs)
        self.assertEqual((report["added"], report["updated"], report["unchanged"], report["deleted"]),
                         (["a", "b", "c"], [], [], []))
        self.assertEqual([c.id for c in self.store.chunks()], [c.id for c in chunk_documents(self.docs)])

    def test_second_sync_changes_nothing(self):
        self.store.sync(self.docs)
        report = self.store.sync(self.docs)
        self.assertEqual(report["unchanged"], ["a", "b", "c"])
        self.assertEqual(report["added"] + report["updated"] + report["deleted"], [])

    def test_edited_documents_are_replaced(self):
        self.store.sync(self.docs)
        self.docs[1] = doc("b", "# B\n\nBeta, revised.")
        report = self.store.sync(self.docs)
        self.assertEqual(report["updated"], ["b"])
        texts = [c.text for c in self.store.chunks() if c.doc_id == "b"]
        self.assertEqual(texts, ["# B\n\nBeta, revised."])

    def test_removed_documents_disappear_with_their_chunks(self):
        self.store.sync(self.docs)
        report = self.store.sync(self.docs[:2])
        self.assertEqual(report["deleted"], ["c"])
        self.assertNotIn("c", {c.doc_id for c in self.store.chunks()})

    def test_only_new_or_changed_chunks_are_embedded(self):
        embedder = CountingEmbedder()
        self.store.sync(self.docs, embedder=embedder)
        first = len(embedder.embedded)
        self.docs[0] = doc("a", "# A\n\nAlpha, edited.")
        report = self.store.sync(self.docs, embedder=embedder)
        self.assertEqual(len(embedder.embedded) - first, 1)
        self.assertEqual(report["embedded"], 1)
        self.assertEqual(len(self.store.vectors()), len(self.store.chunks()))

    def test_changing_the_chunking_reindexes_everything(self):
        self.store.sync(self.docs, size=800)
        self.assertEqual(self.store.sync(self.docs, size=400)["updated"], ["a", "b", "c"])


class Service(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.system = build_system(Settings(), docs=list(corpus()), llm=ExtractiveLLM())

    def setUp(self):
        self.log = ListLog()
        self.service = RagService(self.system, log=self.log)

    def ask(self, payload, role="engineer"):
        return self.service.handle_ask(payload, {"X-User-Role": role} if role else {})

    def test_answers_with_citations_and_timings(self):
        status, body = self.ask({"question": "What is the current production timeout for catalog API requests?"})
        self.assertEqual(status, 200)
        self.assertIn("800", body["answer"])
        self.assertEqual(set(body["citations"][0]), {"label", "doc_id", "title", "heading"})
        self.assertIn("total", body["timings_ms"])
        self.assertEqual(len(body["request_id"]), 16)

    def test_rejects_bad_requests(self):
        for payload in [None, [], {}, {"question": "   "}, {"question": 42}, {"question": "x" * 1001},
                        {"question": "ok", "k": 0}, {"question": "ok", "k": "3"}, {"question": "ok", "k": True}]:
            status, body = self.ask(payload)
            self.assertEqual(status, 400, payload)
            self.assertIn("error", body)
            self.assertIn("request_id", body)

    def test_requires_a_known_role(self):
        self.assertEqual(self.ask({"question": "hi"}, role=None)[0], 401)
        self.assertEqual(self.ask({"question": "hi"}, role="admin")[0], 401)

    def test_restricted_values_never_reach_engineers(self):
        status, body = self.ask({"question": "What is the playback emergency worker count?"})
        self.assertEqual(status, 200)
        self.assertNotIn("720", json.dumps(body))
        status, body = self.ask({"question": "What is the playback emergency worker count?"}, role="sre")
        self.assertIn("720", body["answer"])

    def test_model_failures_become_502_without_details(self):
        class Down:
            name = "down"

            def complete(self, *a, **kw):
                raise ModelError("connection refused to http://secret-host:11434")
        service = RagService(build_system(Settings(), docs=list(corpus()), llm=Down()), log=self.log)
        status, body = service.handle_ask({"question": "catalog timeout"}, {"x-user-role": "engineer"})
        self.assertEqual(status, 502)
        self.assertNotIn("secret-host", json.dumps(body))

    def test_unexpected_errors_become_500(self):
        service = RagService(build_system(Settings(), docs=list(corpus()), llm=ScriptedLLM([])), log=self.log)
        service.system.llm = type("Broken", (), {"name": "broken", "complete": lambda *a, **k: 1 / 0})()
        status, body = service.handle_ask({"question": "catalog timeout"}, {"x-user-role": "engineer"})
        self.assertEqual((status, body["error"]), (500, "internal error"))

    def test_every_request_is_traced(self):
        self.ask({"question": "catalog timeout"})
        self.ask({})
        statuses = [r["status"] for r in self.log.records]
        self.assertEqual(statuses, [200, 400])
        first = self.log.records[0]
        self.assertTrue({"request_id", "role", "retrieved", "abstained", "timings"} <= set(first))
        self.assertNotIn("question", first)   # log the length, not the text


class Http(unittest.TestCase):
    def test_stdlib_server_round_trip(self):
        system = build_system(Settings(), docs=list(corpus()), llm=ExtractiveLLM())
        server = make_stdlib_server(RagService(system, log=ListLog()), port=0)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_address[1]}"
        try:
            with urllib.request.urlopen(f"{base}/health") as r:
                self.assertEqual(json.loads(r.read())["status"], "ok")
            request = urllib.request.Request(f"{base}/ask", data=json.dumps({"question": "kill switch naming"}).encode(),
                                             headers={"X-User-Role": "engineer", "Content-Type": "application/json"})
            with urllib.request.urlopen(request) as r:
                self.assertIn("answer", json.loads(r.read()))
            bad = urllib.request.Request(f"{base}/ask", data=b"{oops", headers={"X-User-Role": "engineer"})
            with self.assertRaises(urllib.error.HTTPError) as err:
                urllib.request.urlopen(bad)
            self.assertEqual(err.exception.code, 400)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
