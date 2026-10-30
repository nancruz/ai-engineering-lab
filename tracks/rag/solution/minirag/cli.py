"""Command line for every lab. Run `python -m minirag --help`. (Supplied.)"""
import argparse
import json
from pathlib import Path
import sys
import textwrap
import unittest

from .chunking import chunk_document
from .documents import data_dir, load_documents, load_questions
from .pipeline import Settings, build_system

LABS = [(1, "Keyword search (BM25)"), (2, "Embeddings & vector search"), (3, "Chunking"),
        (4, "Grounded generation"), (5, "Evaluation"), (6, "Better retrieval"), (7, "Ship it")]


def settings_from(args):
    return Settings(**{f: getattr(args, f) for f in Settings.__dataclass_fields__ if hasattr(args, f)})


def short(text, width=90):
    text = " ".join(text.split())
    return text if len(text) <= width else text[: width - 1] + "…"


def cmd_search(args):
    system = build_system(settings_from(args))
    hits = system.retriever.retrieve(args.query, k=args.k, role=args.role, include_archived=args.archived)
    print(f"{system.retriever.name} · {len(system.chunks)} chunks ({args.chunks}) · role={args.role}\n")
    if not hits:
        print("no results")
    for rank, hit in enumerate(hits, 1):
        c = hit.chunk
        print(f"{rank:>2}. {hit.score:7.3f}  {c.id}" + (f"  [{c.heading}]" if c.heading else ""))
        print(f"           {short(c.text)}")
        if args.explain and hasattr(system.retriever, "index") and hasattr(system.retriever.index, "explain"):
            terms = system.retriever.index.explain(args.query, c.id)
            print("           " + "  ".join(f"{t}={v:.2f}" for t, v in sorted(terms.items(), key=lambda x: -x[1])))
    return 0


def cmd_chunks(args):
    docs = {d.id: d for d in load_documents(args.docs or None)}
    if args.doc not in docs:
        print(f"unknown document {args.doc!r}. Available:\n  " + "\n  ".join(sorted(docs)), file=sys.stderr)
        return 2
    chunks = chunk_document(docs[args.doc], args.chunks, args.size, args.overlap)
    print(f"{args.doc}: {len(chunks)} chunks · strategy={args.chunks} size={args.size} overlap={args.overlap}\n")
    for c in chunks:
        print(f"── {c.id}  [{c.start}:{c.end}]  {c.end - c.start} chars" + (f"  · {c.heading}" if c.heading else ""))
        print(textwrap.indent(c.text if args.full else short(c.text, 300), "   "))
        print()
    return 0


def cmd_ask(args):
    from .generation import ask
    system = build_system(settings_from(args))
    result = ask(args.question, system.retriever, system.llm, role=args.role, k=args.k,
                 budget_tokens=args.budget, include_archived=args.archived)
    if args.show_prompt:
        for m in result.messages:
            print(f"──── {m['role']} ────\n{m['content']}\n")
    print(f"──── answer ({system.llm.name}) ────")
    print(textwrap.fill(result.answer.text, 100) if "\n" not in result.answer.text else result.answer.text)
    print()
    for c in result.answer.citations:
        print(f"  [{c['label']}] {c['doc_id']}" + (f" › {c['heading']}" if c["heading"] else ""))
    if result.answer.unknown:
        print(f"  ! cites sources that do not exist: {', '.join(result.answer.unknown)}")
    if result.dropped:
        print(f"  · {len(result.dropped)} retrieved chunk(s) did not fit the {args.budget}-token budget")
    print(f"\n  retrieved {len(result.hits)} · in prompt {len(result.selected)} · "
          + " · ".join(f"{k} {v:.0f} ms" for k, v in result.timings.items()))
    return 0


def fmt(value):
    return "  –  " if value is None else f"{value:5.2f}"


def cmd_eval(args):
    from .evaluation import evaluate_answers, evaluate_retrieval, judge_faithfulness
    from .generation import ask
    from .llm import make_llm
    questions = load_questions(args.questions, split=args.split)
    if args.type:
        questions = [q for q in questions if q.get("type") == args.type]
    specs = args.compare.split(",") if args.compare else [args.retriever]
    output = {}
    print(f"{len(questions)} questions · split={args.split} · k={args.k} · chunks={args.chunks}\n")
    print(f"{'retriever':<22}{'hit@k':>7}{'recall':>8}{'MRR':>7}{'nDCG':>7}{'evidence':>10}{'tokens':>8}   leaks")
    runs = {}
    for spec in specs:
        args.retriever = spec
        system = build_system(settings_from(args))
        report = evaluate_retrieval(system.retriever, questions, args.k)
        runs[spec] = (system, report)
        s = report["summary"]
        leaks = sum(bool(r["leaks"]) for r in report["rows"])
        print(f"{spec:<22}{fmt(s['hit']):>7}{fmt(s['recall']):>8}{fmt(s['mrr']):>7}{fmt(s['ndcg']):>7}{fmt(s['evidence']):>10}{s['tokens']:>8.0f}   {leaks}")
        output[spec] = {"retrieval": report}
    print("\nevidence found, by question type")
    types = sorted({q.get("type", "") for q in questions})
    print(f"{'':<22}" + "".join(f"{t[:10]:>11}" for t in types))
    for spec, (_, report) in runs.items():
        print(f"{spec:<22}" + "".join(f"{fmt(report['by_type'][t]['evidence']):>11}" for t in types))
    if args.show_failures:
        for spec, (_, report) in runs.items():
            misses = [r for r in report["rows"] if r["evidence"] is not None and r["evidence"] < 1]
            print(f"\n{spec}: {len(misses)} question(s) where the answering passage was not retrieved")
            for r in misses:
                print(f"  {r['id']} [{r['type']}] wanted {r['relevant']} got {r['retrieved']}")
    if args.answers:
        judge = make_llm(args.judge) if args.judge else None
        print(f"\nanswers ({args.llm})")
        print(f"{'retriever':<22}{'pass':>7}{'abstain':>9}{'cites':>7}" + ("  faithful" if judge else ""))
        for spec, (system, _) in runs.items():
            results = {}

            def run(q):
                results[q["id"]] = ask(q["question"], system.retriever, system.llm, role=q["role"], k=args.k,
                                       budget_tokens=args.budget)
                return results[q["id"]]
            report = evaluate_answers(run, questions)
            line = f"{spec:<22}{fmt(report['summary']['pass']):>7}{fmt(report['summary']['abstain_ok']):>9}{fmt(report['summary']['cites_relevant']):>7}"
            if judge:
                scores = [judge_faithfulness(results[r["id"]], judge)["faithfulness"] for r in report["rows"]]
                for r, f in zip(report["rows"], scores):
                    r["faithfulness"] = f
                vals = [f for f in scores if f is not None]
                line += f"  {fmt(sum(vals) / len(vals) if vals else None)}"
            print(line)
            output[spec]["answers"] = report
            if args.show_failures:
                for r in report["rows"]:
                    if not r["pass"]:
                        why = (["should abstain" if r["abstained"] is False else "should answer"] if not r["abstain_ok"] else []) \
                            + [f"missing {m!r}" for m in r["missing"]] + [f"contains {f!r}" for f in r["forbidden"]]
                        print(f"  ✗ {r['id']} [{r['type']}] {', '.join(why)}: {short(r['answer'], 70)}")
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps({"settings": settings_from(args).as_dict(), "runs": output}, indent=2, default=str))
        print(f"\nsaved {args.out}")
    return 0


def cmd_index(args):
    if not args.db:
        args.db = ".minirag/index.sqlite"
    system = build_system(settings_from(args))
    r = system.sync_report
    print(f"{args.db}: {len(system.chunks)} chunks")
    for key in ("added", "updated", "unchanged", "deleted"):
        print(f"  {key:<9} {len(r[key]):>3}  {' '.join(r[key][:6])}{' …' if len(r[key]) > 6 else ''}")
    print(f"  embedded  {r['embedded']:>3} chunk(s)")
    return 0


def cmd_serve(args):
    from .service import RagService, serve
    system = build_system(settings_from(args))
    serve(RagService(system), args.host, args.port)
    return 0


def cmd_doctor(args):
    import importlib.util
    import os
    print(f"python {sys.version.split()[0]} · data {data_dir()}")
    tests = Path(__file__).resolve().parent.parent / "tests"
    print(f"\n{'lab':<34}tests passing")

    class Result(unittest.TestResult):
        def __init__(self):
            super().__init__()
            self.passed = 0

        def addSuccess(self, test):
            self.passed += 1

    for number, title in LABS:
        files = sorted(tests.glob(f"test_lab{number}_*.py"))
        if not files:
            print(f"  {number}. {title:<29}(no test file)")
            continue
        suite = unittest.defaultTestLoader.discover(str(tests), pattern=files[0].name, top_level_dir=str(tests.parent))
        result = Result()
        suite.run(result)
        total = suite.countTestCases()
        problems = result.failures + result.errors
        if result.passed == total:
            state = "done ✓"
        elif all("NotImplementedError" in tb for _, tb in problems):
            state = "TODOs left"
        else:
            state = "failing tests"
        print(f"  {number}. {title:<29}{result.passed:>3}/{total:<4} {state}")
    print("\noptional")
    for module, use in [("sentence_transformers", "local embeddings / cross-encoder (Labs 2, 6)"),
                        ("fastapi", "HTTP API (Lab 7)"), ("uvicorn", "HTTP server (Lab 7)")]:
        print(f"  {'✓' if importlib.util.find_spec(module) else '·'} {module:<22}{use}")
    for var in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
        print(f"  {'✓' if os.environ.get(var) else '·'} {var:<22}hosted models")
    try:
        import urllib.request
        host = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
        with urllib.request.urlopen(f"{host}/api/tags", timeout=1) as r:
            models = [m["name"] for m in json.loads(r.read()).get("models", [])]
        print(f"  ✓ ollama                {', '.join(models) or 'running, no models pulled'}")
    except Exception:
        print("  · ollama                not running (optional: local models)")
    return 0


def main(argv=None):
    import os
    common = argparse.ArgumentParser(add_help=False)
    env = {f: os.environ[f"MINIRAG_{f.upper()}"] for f in ("retriever", "embedder", "reranker", "llm", "db")
           if os.environ.get(f"MINIRAG_{f.upper()}")}
    defaults = Settings(**env)
    common.add_argument("--retriever", default=defaults.retriever, help="bm25 | dense | hybrid [+rerank] [+multiquery]")
    common.add_argument("--chunks", default=defaults.chunks, choices=["document", "fixed", "paragraph", "headings"])
    common.add_argument("--size", type=int, default=defaults.size, help="max chunk size in characters")
    common.add_argument("--overlap", type=int, default=defaults.overlap, help="overlap in characters (fixed/paragraph)")
    common.add_argument("--k", type=int, default=defaults.k, help="chunks to retrieve")
    common.add_argument("--k1", type=float, default=defaults.k1, help="BM25 saturation (Lab 1)")
    common.add_argument("--b", type=float, default=defaults.b, help="BM25 length normalization (Lab 1)")
    common.add_argument("--embedder", default=defaults.embedder, help="hashing | ollama:<model> | st:<model> | openai:<model>")
    common.add_argument("--reranker", default=defaults.reranker, help="overlap | cross-encoder[:model] | llm")
    common.add_argument("--llm", default=defaults.llm, help="extractive | ollama:<model> | openai:<model> | anthropic:<model>")
    common.add_argument("--budget", type=int, default=defaults.budget, help="context budget in estimated tokens")
    common.add_argument("--db", default=defaults.db, help="SQLite index (Lab 7); default: build in memory")
    common.add_argument("--docs", default=defaults.docs, help="folder of Markdown docs (capstone)")
    common.add_argument("--role", default="engineer", choices=["engineer", "sre"])
    common.add_argument("--archived", action="store_true", help="include archived documents")

    parser = argparse.ArgumentParser(prog="minirag", description="A RAG system you build lab by lab.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="show lab progress and optional tools").set_defaults(func=cmd_doctor)
    p = sub.add_parser("search", parents=[common], help="retrieve chunks for a query")
    p.add_argument("query")
    p.add_argument("--explain", action="store_true", help="show BM25 term contributions")
    p.set_defaults(func=cmd_search)
    p = sub.add_parser("chunks", parents=[common], help="show how a document is chunked")
    p.add_argument("doc")
    p.add_argument("--full", action="store_true")
    p.set_defaults(func=cmd_chunks)
    p = sub.add_parser("ask", parents=[common], help="answer a question with citations")
    p.add_argument("question")
    p.add_argument("--show-prompt", action="store_true")
    p.set_defaults(func=cmd_ask)
    p = sub.add_parser("eval", parents=[common], help="evaluate retrieval (and answers)")
    p.add_argument("--compare", help="comma-separated retrievers, e.g. bm25,dense,hybrid")
    p.add_argument("--split", default="dev", choices=["dev", "test", "all"])
    p.add_argument("--questions", help="questions JSON file (capstone); default: the course questions")
    p.add_argument("--type", help="only questions of this type, e.g. paraphrase")
    p.add_argument("--answers", action="store_true", help="also generate and check answers")
    p.add_argument("--judge", help="LLM for faithfulness judging, e.g. ollama:llama3.2:3b")
    p.add_argument("--show-failures", action="store_true")
    p.add_argument("--out", help="save the full results as JSON")
    p.set_defaults(func=cmd_eval)
    p = sub.add_parser("index", parents=[common], help="sync documents into the SQLite index (Lab 7)")
    p.set_defaults(func=cmd_index)
    p = sub.add_parser("serve", parents=[common], help="run the HTTP API (Lab 7)")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    p.set_defaults(func=cmd_serve)
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except NotImplementedError as err:
        print(f"\nNot built yet: {err}\nRun the lab's tests to see what to implement.", file=sys.stderr)
        return 1
    except BrokenPipeError:  # output piped into head/less that closed early
        return 0


if __name__ == "__main__":
    sys.exit(main())
