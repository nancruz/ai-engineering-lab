# One project, consistent commands

This is the implementation contract used throughout the lessons. It specifies the code you will build; it is not a claim that a complete application has already been supplied.

The supplied runnable code is in `tracks/rag/lab/` plus `tracks/rag/tools/practice.py`. Your application is in `projects/knowledge-assistant/`. Keep its commands, tests and artifacts together so deployment later uses the same pipeline you evaluated.

## Create only what the current session needs

| Project path | Created in | Responsibility |
| --- | --- | --- |
| `app/__init__.py`, `app/cli.py` | Week 5 | Importable package and local query command |
| `app/retrieval.py`, `app/generation.py`, `app/pipeline.py` | Week 5 | Retrieval, replaceable generation and orchestration |
| `app/api.py` | Week 6 | HTTP contracts and controlled errors |
| `app/embeddings.py`, `app/dense.py`, `app/hybrid.py`, `app/rerank.py` | Weeks 8–11 | Retrieval experiments behind shared interfaces |
| `app/evaluate.py` | Week 9 | Reproducible evaluation runner |
| `app/ingest.py`, `app/context.py` | Weeks 14–16 | Source preparation and context selection |
| `app/features.py`, `training/` | Weeks 27–38 | Reproducible training and inference features |
| `app/auth.py`, `app/store.py`, `app/ingestion_job.py` | Weeks 40–42 | Trusted identity, persistent retrieval and snapshot publication |
| `tests/`, `configs/`, `prompts/` | As first used | Executable checks and versioned behavior |
| `data/`, `artifacts/`, `experiments/` | As first used | Permitted inputs, outputs and comparisons |
| `Dockerfile`, `infra/terraform/`, `runbooks/` | Weeks 43–51 | Reproducible deployment and operation |

Initialize a project-local virtual environment and record resolved dependencies. Python basics are assumed; install only the packages required by the current module. Begin with the standard library, then FastAPI/Uvicorn/pytest; add numerical, model, database and AWS dependencies when introduced. Pin a tested compatible dependency set rather than installing an unspecified “latest” environment during deployment.

## Application interfaces

Implement these contracts in week five; typed dataclasses or Pydantic models are fine:

- `Principal`: subject ID, trusted roles/groups and access-scope version. During local work use explicit development configuration; never trust a user-supplied role in an exposed API.
- `retrieve(question, principal, config)`: ranked evidence items with stable document/chunk ID, source/version/snapshot, text, score and access metadata.
- `build_context(items, budget)`: selected passages and provenance, plus omitted IDs/reasons. Initially a bounded selection; Module 3 develops it.
- `generate(messages, settings)`: parsed answer plus raw provider/model/usage metadata. The pipeline owns deadlines and error mapping.
- `answer(question, principal, config)`: orchestrates eligibility, retrieval, context, optional quality gate and generation; assigns a request ID and effective configuration.

The generator does not decide permissions. A citation-membership check does not prove claim support. Unit-test doubles exercise control flow; real model runs evaluate generation. Reports must label which was used.

## HTTP contract

In week six, implement:

```http
POST /answer
Content-Type: application/json

{"question":"What is the current production catalog timeout?"}
```

Successful response shape (the text below is an illustration, not a measured model output):

```json
{
  "request_id": "generated-id",
  "answer": "The production deadline is 800 milliseconds.",
  "citations": [{"source_id": "timeout-v2", "chunk_id": "stable-chunk-id"}],
  "abstained": false,
  "release_id": "local-development"
}
```

Use 400/422 for invalid input, 401 for absent/invalid authentication once enabled, 403 for a forbidden operation, 429 for admission/rate limits and appropriate 5xx for dependency failure. A valid question with insufficient authorized evidence can return a normal response with `abstained: true`. Do not confuse dependency outage with proven absence of evidence. All paths carry a request ID; return no raw credentials, stack traces or hidden source text.

The early local API binds to loopback and uses a fixed development principal. Module 7 replaces it with JWT validation. An endpoint is not ready for internet exposure merely because the local curl works.

From a second terminal, at repository root:

```bash
curl --fail-with-body http://127.0.0.1:8000/answer \
  -H 'Content-Type: application/json' \
  -d '{"question":"What is the current production catalog timeout?"}'
```

Set an input-length bound, total request deadline and output-token limit. Configure them explicitly; measure a suitable value rather than inheriting unlimited defaults.

## Commands you implement progressively

Create a project `Makefile` by week 24 with these targets. They are project deliverables, not preinstalled course tools. Each should run from the project directory with the project environment active; use `make -C projects/knowledge-assistant <target>` from the repository root.

| Target | Behavior |
| --- | --- |
| `check` | Run deterministic unit/integration/security tests. No cloud/model calls. |
| `ingest` | Build a candidate index from a specified source manifest; do not auto-promote. |
| `serve` | Start the API using explicit local settings. |
| `eval` | Run a bounded development batch with named config, save run manifest/rows. |
| `compare` | Reject incompatible runs, then emit per-query/family comparisons. |
| `gate` | Read policy and saved results; exit nonzero when required checks fail. |
| `smoke` | Query a configured running endpoint; verify response/citation/auth behavior. |

Before these targets exist, use the actual Python/pytest commands from each lesson. Avoid maintaining a separate “demo” implementation that bypasses authentication, context or deployed retrieval.

## Data and result contracts

A benchmark row needs `id`, `family`, `query`, request role/scope, temporal intent, relevant source/passage IDs, answerability and slice. Preserve required facts and alternate supporting passages where sources are redundant. Ground truth is for evaluation only.

A run manifest needs Git SHA, corpus/benchmark hashes, effective model/embedding/reranker/gate revisions, prompt hash, chunking/retrieval config, k/candidate depth, environment and timestamp. Each row needs ranked IDs/scores, selected context IDs, metrics where defined, errors, timing and provider usage where available. Keep reviewer labels attached to that exact run.

Compatibility checks should reject changed questions/labels/corpus when estimating a single configuration's effect. A deliberate corpus update is a different experiment and must be labeled accordingly.

For aggregate reports, per-query `rr` averages to `mrr`. Empty relevant sets are excluded from recall and reviewed separately for abstention. Complete labeled-set coverage does not imply all labeled documents are jointly required.

## Release manifest

From week 25, keep one manifest per release. Include immutable image digest when available; otherwise Git/dependency versions; source/index snapshot; embedding/reranker/gate hashes; prompt and retrieval config; generator provider/model or inference-profile identity; database migration revision; evaluation and security-gate artifacts; previous approved release ID. Keep live access policy/revocations current across content rollback.

Commit small fictional fixtures, code, configurations and concise reports. Keep secrets, customer data, model weights and large generated files outside Git; store hashes and reproduction steps instead. Use versioned local storage initially and approved S3 storage during the production modules.
