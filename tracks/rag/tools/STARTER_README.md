# minirag: your RAG system (starter)

Copy this folder once, then do every lab in your copy:

```bash
cp -r tracks/rag/starter projects/knowledge-assistant
cd projects/knowledge-assistant
python3 -m minirag doctor        # lab progress, data location, optional tools
```

Everything runs on the Python standard library (3.10+). Real models are optional
and plug in with a flag (`--embedder ollama:nomic-embed-text`, `--llm ollama:llama3.2:3b`, ...).

## Labs

Each lab replaces `raise NotImplementedError(...)` stubs (marked `TODO (Lab n)`) in one
or two files. The lab's tests tell you when you are done.

| Lab | Course page | You write | Done when this passes |
| --- | --- | --- | --- |
| 1 | Keyword search | `minirag/text.py`, `minirag/lexical.py` | `python3 -m unittest -v tests.test_lab1_search` |
| 2 | Embeddings & vector search | `minirag/embeddings.py`, `minirag/vectors.py` | `python3 -m unittest -v tests.test_lab2_vectors` |
| 3 | Chunking | `minirag/chunking.py` | `python3 -m unittest -v tests.test_lab3_chunking` |
| 4 | Grounded generation | `minirag/retrieval.py` (`allowed`), `minirag/generation.py` | `python3 -m unittest -v tests.test_lab4_generation` |
| 5 | Evaluation | `minirag/evaluation.py` | `python3 -m unittest -v tests.test_lab5_evaluation` |
| 6 | Better retrieval | `minirag/hybrid.py`, `minirag/rerank.py`, `minirag/query.py` | `python3 -m unittest -v tests.test_lab6_retrieval` |
| 7 | Ship it | `minirag/store.py`, `minirag/service.py` | `python3 -m unittest -v tests.test_lab7_ship` |

The course pages live in `docs/rag/` (open `docs/rag/index.html`). Labs build on each
other: Lab 4 uses your BM25 from Lab 1 and your chunker from Lab 3.

Stuck? The reference solution is in `tracks/rag/solution/` with the same layout. Try
first, then compare: the comparison teaches more than the copy.

## Commands

```bash
python3 -m minirag search "PLAY-4012" --explain          # Lab 1
python3 -m minirag search "undo a bad release" --retriever dense
python3 -m minirag chunks playback-rollback-runbook --chunks fixed --size 300
python3 -m minirag ask "How do I roll back playback?" --show-prompt
python3 -m minirag eval --compare bm25,dense,hybrid --answers
python3 -m minirag index --db .minirag/index.sqlite
python3 -m minirag serve
```
