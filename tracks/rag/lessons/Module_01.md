# Module 01 — From source documents to a running local RAG service

Weeks 1–6 · 3 hours per week · one evolving knowledge-assistant project.

## Start here

Finished the introduction? Start Week 1 below. Already completed evidence labeling or baseline runs? Reuse those files and skip only the steps you have actually completed.

**Working result:** A local CLI and HTTP API that retrieve evidence, call a real model, return citations and record failures.

Read only the current week's instructions. Use the reference section when a step points to a concept; there are no written theory answers or oral assessments. Demonstrate progress through working code, saved runs, tests and short observations attached to a change.

All shell commands start at the repository root. Paths beginning with `app/`, `tests/`, `artifacts/`, `data/` or `infra/` below mean files **inside** `projects/knowledge-assistant/`. You create these project files as the course progresses; the supplied baseline remains under `tracks/rag/lab/`. See the [project contract](../guides/project-contract.md) for the directory map, interfaces and commands.


## Week 01 — Run and inspect the supplied search

Start with evidence selection. No implementation or model setup is required this week.

### Session A — Start and inspect (60 minutes)

1. If you already read the [introduction](00-rag-introduction.md), count it as completed reading.
2. Open the repository locally and create `projects/knowledge-assistant/experiments/module-01/`.
3. Display the six practice questions without exposing their reference labels:

```bash
python3 tracks/rag/tools/practice.py
```

Read the `query`, reader role and current-only setting. The original questions live in [dev.json](../lab/data/dev.json); source documents live in [corpus.json](../lab/data/corpus.json).

### Session B — Build or change (60 minutes)

1. Start with q02: “What is the current production catalog timeout?” Find the two catalog-timeout documents in the corpus.
2. Worked example: accept `timeout-v2` (800 milliseconds, current, engineer access). Reject `timeout-v1` (3,000 milliseconds, archived).
3. Create `experiments/module-01/evidence.md` with columns `question_id`, `accepted IDs`, `supported answer or abstention`, `reason`. Try q03 next, then q13, q14, q16 and q17 as time permits.
4. Reveal the supplied labels only after your attempt: `python3 tracks/rag/tools/practice.py --check`. Note disagreements beside the affected row. Labels already seen are guided practice, not independent assessment.

### Session C — Run and verify (60 minutes)

Run the deliberately faulty retriever after labeling:

```bash
python3 tracks/rag/lab/evaluate.py --mode faulty --out projects/knowledge-assistant/experiments/module-01/faulty.json
```

Open `rows`, find q02, and copy its `retrieved` IDs in rank order into your table. Look up their text in the corpus. Repeat for your other labeled rows. Mark missing, archived or unauthorized evidence, or “no observed issue.” Ignore the metric summary this week. A trace here is simply the saved record of what search returned.

**Save:** `evidence.md` and `faulty.json`. No workflow essay, incident memo or release decision is due.

**Move on when:** you can reproduce the run and match its document IDs to source text. Complete unfinished rows before their search outputs are inspected; two careful rows are enough to start. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 02 — Put useful checks around retrieval

Turn the observations from week one into executable checks.

### Session A — Start and inspect (60 minutes)

Read the ranked-list example in this module's reference section. Open [retrieval.py](../lab/retrieval.py) at `metrics` and [test_retrieval.py](../lab/test_retrieval.py). Run the existing tests:

```bash
python3 -m unittest discover -s tracks/rag/lab -p 'test*.py' -v
```

Inspect how `rr` on a row becomes `mrr` in the aggregate. No separate written derivation is required.

### Session B — Build or change (60 minutes)

Create `tracks/rag/lab/test_my_metrics.py`. Add table-driven cases with gold `[A,B]` and rankings `[X,A,Y]`, `[A,B,X]` and `[X,Y,Z]`. Their `(recall, hit, rr, complete)` expectations at k=3 are `(0.5,1,0.5,0)`, `(1,1,1,1)` and `(0,0,0,0)`. Add duplicate-ID and empty-gold cases. Empty gold should produce null metrics, not a manufactured zero recall.

### Session C — Run and verify (60 minutes)

Run discovery again. Temporarily change an expected value and verify the test fails, then restore it. Add q13's actual retrieved list as another example and independently confirm its expected values from the evidence IDs. Keep each calculation beside its test as a short comment.

**Save:** Your metric test file and passing test output.

**Move on when:** tests distinguish a single hit from complete evidence and catch a deliberately incorrect expectation. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 03 — Repair source eligibility

Isolate metadata filtering from ranking changes.

### Session A — Start and inspect (60 minutes)

Open `eligible` and `retrieve` in the baseline. Trace q02's current-only filter and the role difference between q14 and q15. Keep corpus and question labels unchanged. Create a results table with rows for faulty and filtered keyword modes and columns for recall, MRR, unauthorized-query count and stale-query count.

### Session B — Build or change (60 minutes)

Run the filtered keyword baseline:

```bash
python3 tracks/rag/lab/evaluate.py --mode keyword --out projects/knowledge-assistant/experiments/module-01/keyword.json
```

Populate the table from the two saved runs. Add regression tests asserting that returned sources permit the request role and obey current-only intent. The fixture role is a teaching input, not production authentication.

### Session C — Run and verify (60 minutes)

Run tests and inspect q17 and q18 after filtering. Record unchanged scores as well as improvements. Keep any unresolved paraphrase miss as an issue linked to the exact question and returned IDs. Do not change labels to improve the result.

**Save:** `keyword.json`, a compact before/after table and eligibility regression tests.

**Move on when:** the filtered baseline passes defined access/freshness cases and remaining relevance misses are visible. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 04 — Run your first real RAG answer

Use supplied retrieval and a local model to see the complete retrieve→context→generate loop early.

### Session A — Start and inspect (60 minutes)

Follow [Run the first model](../guides/first-model.md): install/start Ollama, pull `llama3.2:3b`, and verify the model responds. This is the one-time setup session. If hardware is unsuitable, use the documented Bedrock adapter route and carry setup into the next session; do not substitute a fake generated answer.

### Session B — Build or change (60 minutes)

Run the provided local RAG command:

```bash
python3 tracks/rag/lab/answer.py --question-id q02 --model llama3.2:3b --out projects/knowledge-assistant/experiments/module-01/answer-q02.json
```

Open `evidence`, `system_prompt`, `answer` and `provider_response`. The exact context and raw model response are saved. Look up each citation; confirm the timeout value against its source, regardless of whether output validation passed.

### Session C — Run and verify (60 minutes)

Run q13 (multiple evidence) and q16 (no known supporting evidence). Save separate outputs. Mark each factual claim supported, contradicted or unsupported in a small CSV. A lexical match for q16 is not proof an answer exists. If JSON validation fails, open `validation_error` and `provider_response` in the saved run and fix the model/prompt configuration before retrying; never silently turn an error into a success.

**Save:** Three real-model run records, actual model tag/digest from Ollama, and claim-review rows.

**Move on when:** at least one real answer has been traced from retrieved text through the model output, including an abstention attempt. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 05 — Build your own callable RAG pipeline

Move from supplied scripts to the project you will keep deploying.

### Session A — Start and inspect (60 minutes)

Create the package layout in [project contract](../guides/project-contract.md). Implement a development-document loader and copy the baseline retrieval algorithm into `app/retrieval.py` with attribution. Keep reference data read-only and put project data snapshots under `data/`. Create a typed result containing answer, citations, abstention and request ID.

### Session B — Build or change (60 minutes)

Implement `app/pipeline.py` with `answer(question, principal, config)` and `app/generation.py` with the local model adapter from week four. Add `app/cli.py` so `python -m app.cli --question-id q02` works from the project directory. Inject the generator dependency: unit tests use labeled test doubles, interactive runs use the real model. Fixture roles remain local-only.

### Session C — Run and verify (60 minutes)

Add end-to-end tests for q02, no evidence, unknown citation ID and model timeout. Unit-test failure behavior with doubles; separately save one real CLI run. Return a controlled error or abstention for insufficient evidence, without inventing an answer. Confirm the full source text can be traced by evidence ID.

**Save:** `app/` package, tests, dependency record and one saved CLI run.

**Move on when:** a single command runs your own pipeline and failure tests exercise the actual boundary used by it. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 06 — Add a local HTTP endpoint

Create the interface used by later evaluation and deployment work.

### Session A — Start and inspect (60 minutes)

Install FastAPI, Uvicorn and pytest in the project environment. Implement `POST /answer` in `app/api.py` using the contract guide. Bind only to loopback. For now the development principal comes from local configuration; reject a role supplied in the request body. Production token validation is added in Module 7.

### Session B — Build or change (60 minutes)

Add `GET /health/live` and `GET /health/ready`. Live means the process responds; ready means the required active index/config has loaded. Start the service:

```bash
cd projects/knowledge-assistant
python -m uvicorn app.api:app --host 127.0.0.1 --port 8000
```

From another terminal run the curl example in the contract guide. Save the response and a request trace with the same request ID.

### Session C — Run and verify (60 minutes)

Add HTTP tests for a valid request, oversized question, missing index and generator timeout. Ensure errors are non-200 and carry a request ID without raw stack traces. Stop and restart the server, then rerun one real query. Update the project README with the commands that actually worked.

**Save:** Local API, HTTP tests and reproducible startup/query commands.

**Move on when:** your own service answers a real request locally and its failure responses are tested. Continue to Module 2; no final oral or written exam. If the hour ends first, keep your current work and resume the unfinished step next session.

## Next step

Open [Module 2](Module_02.md), Week 7. Your existing local API is the system you will improve.

## Reference — evidence and retrieval metrics

A RAG system has separable failure boundaries: source data, ingestion, representation, retrieval, context selection, generation and output validation. An answer can be fluent and cite a real document while still being wrong. A citation identifier proves where text came from; it does not prove that the cited passage entails the claim, is current, or is authorized for this user.

Begin by specifying the unit of truth. A question may need one passage, several jointly sufficient passages, a time-specific policy or an explicit refusal. Label supporting evidence independently from the system's retrieved results. Otherwise the benchmark rewards whichever evidence the current retriever happens to find. In this course, document-level labels start the exercise; later you add passage offsets and claim-level support.

### Start with a ranked list

Ask: “How do I roll back staging and production?” Document A explains staging; document B explains production. Both are needed for this question. Documents X and Y are irrelevant.

Suppose the first three unique retrieved IDs are **X, A, Y**. We found one of the two supporting documents, and the first useful result is in position two.

| Metric | What it asks | Result |
| --- | --- | --- |
| Recall@3 | What fraction of the labeled relevant documents did we find? | 1 / 2 = 0.5 |
| Hit@3 | Did we find at least one relevant document? | 1, meaning yes |
| Reciprocal Rank@3 (RR@3) | How early is the first relevant result? | 1 / 2 = 0.5 |
| Complete labeled-set coverage@3 | Did we retrieve every labeled relevant document? | 0, meaning no |

Hit is perfect here even though the production instructions are missing. RR rewards finding the first useful item early; it does not measure whether the remaining evidence was found.

**MRR means mean reciprocal rank across queries.** If three answerable questions have RR values 1, 0.5 and 0, their MRR is (1 + 0.5 + 0) / 3 = 0.5. The per-query JSON uses `rr`; the aggregate summary uses `mrr`.

### The notation, after the example

For question q, G(q) is the set of labeled relevant document IDs. R_k(q) is the first k unique retrieved document IDs, in retrieval order. The intersection G ∩ R_k contains IDs appearing in both; vertical bars mean “number of items.”

- Recall@k = |G ∩ R_k| / |G|, for nonempty G.
- Hit@k = 1 when the intersection is nonempty, otherwise 0.
- RR@k = 1 / rank of the first relevant result within the top k, otherwise 0.
- MRR@k = the mean of RR@k over the declared evaluation population. This harness uses answerable questions.

The supplied `complete` field means every labeled relevant ID was retrieved. It is a diagnostic, not a general answerability score. Relevant documents can be redundant: finding one of two equivalent sources can be sufficient even with recall 0.5. In our staging/production example the documents are complementary, so both are required. Later benchmarks should label required facts and alternative supporting passages to measure evidence sufficiency directly.

Questions with no authorized supporting evidence have an empty G. Recall is undefined there, so report them in an abstention slice, not as failed retrieval. The same words can be answerable for one principal and unanswerable for another. Authorization belongs in the evaluation context.

The offline harness contains a deliberately weak keyword retriever and deterministic answer fixtures. The fixtures reproduce failure shapes; they are not calls to an LLM and cannot establish model quality. This separation lets you debug evidence selection cheaply before integrating a generator. The corpus is fictional engineering material, with conflicts, paraphrases and restricted notes. Its small size supports controlled experiments, not claims about enterprise search performance.

## Worked example

A user asks for the current playback rollback procedure. An archived runbook shares the exact words in the query and scores above a current runbook that says “restore the previous release.” The old document is a good lexical match but wrong evidence for a current-policy question. Three possible interventions are metadata-based current-version selection, semantic retrieval and prompt instructions. Test metadata first: a prompt cannot reliably repair an incorrect authoritative-source selection rule.
