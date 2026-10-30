"""Serve the RAG pipeline over HTTP with validation, error mapping and tracing. (Lab 7.)

The request handling lives in RagService.handle_ask(), a plain function from
(payload, headers) to (status, body). That makes it testable without a web
framework; FastAPI (or the standard library) is only a thin adapter around it.
"""
import json
import sys
import time
import traceback
import uuid
from pathlib import Path

from .generation import ask
from .net import ModelError
from .retrieval import ROLE_ACCESS

MAX_QUESTION_CHARS = 1000


class RagService:
    def __init__(self, system, log=None):
        self.system = system
        self.log = log or JsonlLog(".minirag/traces.jsonl")

    def health(self):
        s = self.system.settings
        return 200, {"status": "ok", "chunks": len(self.system.chunks), "retriever": s.retriever, "llm": s.llm}

    def handle_ask(self, payload, headers):
        """POST /ask. Returns (status, body).

        Request:  {"question": str, "k": optional int 1..10}; header X-User-Role: engineer | sre
                  (A real deployment gets the role from a verified token, never from a plain header.)
        Responses:
          400 {"error", "request_id"}  payload not an object, question missing/blank/too long, bad k
          401 {"error", "request_id"}  missing or unknown role
          502 {"error", "request_id"}  the model provider failed (ModelError)
          500 {"error", "request_id"}  anything else; never include the exception text
          200 {"request_id", "answer", "abstained", "citations", "unknown_citations", "timings_ms"}
        Every request, including failures, writes one trace with self.log.write(dict).
        """
        request_id = uuid.uuid4().hex[:16]
        started = time.perf_counter()
        trace = {"request_id": request_id, "llm": self.system.settings.llm, "retriever": self.system.settings.retriever}
        # TODO (Lab 7): Validate in the order listed above, call ask(...) with the system's
        #       retriever/llm/settings, map exceptions to statuses, build the 200 body,
        #       and always write the trace (status, role, question length, retrieved
        #       chunk ids, cited doc ids, abstained, timings) before returning.
        raise NotImplementedError("Lab 7: write RagService.handle_ask() in minirag/service.py")


class JsonlLog:
    """Append one JSON object per line. Point log shippers (CloudWatch, Loki...) at the file. (Supplied.)"""

    def __init__(self, path):
        self.path = Path(path)

    def write(self, record):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a") as f:
            f.write(json.dumps(record) + "\n")


class ListLog:
    """In-memory log for tests."""

    def __init__(self):
        self.records = []

    def write(self, record):
        self.records.append(record)


# ---------------------------------------------------------------- HTTP adapters (supplied)

def create_fastapi_app(service):
    """FastAPI adapter: `pip install fastapi uvicorn`. Interactive docs at /docs."""
    from fastapi import Body, FastAPI, Header
    from fastapi.responses import JSONResponse

    app = FastAPI(title="minirag", description="Lumen engineering knowledge assistant")

    @app.get("/health")
    def health():
        status, body = service.health()
        return JSONResponse(body, status_code=status)

    @app.post("/ask")
    def ask_endpoint(payload: dict = Body(...), x_user_role: str = Header(default="")):
        status, body = service.handle_ask(payload, {"x-user-role": x_user_role})
        return JSONResponse(body, status_code=status)

    return app


def make_stdlib_server(service, host="127.0.0.1", port=8000):
    """Standard-library adapter, so the service runs with no installs at all."""
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class Handler(BaseHTTPRequestHandler):
        def _send(self, status, body):
            data = json.dumps(body).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            self._send(*service.health()) if self.path == "/health" else self._send(404, {"error": "not found"})

        def do_POST(self):
            if self.path != "/ask":
                return self._send(404, {"error": "not found"})
            raw = self.rfile.read(int(self.headers.get("Content-Length") or 0))
            try:
                payload = json.loads(raw or b"null")
            except json.JSONDecodeError:
                payload = None
            self._send(*service.handle_ask(payload, dict(self.headers.items())))

        def log_message(self, *args):
            pass

    return ThreadingHTTPServer((host, port), Handler)


def serve(service, host="127.0.0.1", port=8000):
    try:
        import uvicorn
        app = create_fastapi_app(service)
    except ImportError:
        print("FastAPI/uvicorn not installed: using the standard-library server. "
              "`pip install fastapi uvicorn` for /docs and production-grade serving.", file=sys.stderr)
        server = make_stdlib_server(service, host, port)
        print(f"minirag listening on http://{host}:{port}  (POST /ask, GET /health)", file=sys.stderr)
        server.serve_forever()
        return
    uvicorn.run(app, host=host, port=port)
