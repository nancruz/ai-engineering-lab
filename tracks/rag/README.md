# Build and deploy a RAG knowledge assistant

A practical AI engineering course for an experienced software engineer. **Three hours per week, one evolving project.** You learn concepts while implementing, measuring and debugging their effect on a working system. Basic Python/software engineering is assumed.

## Start at one place

1. Read [What a RAG system is](lessons/00-rag-introduction.md) once.
2. Open [Module 1 — Week 1](lessons/Module_01.md#week-01--run-and-inspect-the-supplied-search).
3. Follow Session A, then B, then C. Each session states its actions, files, saved result and completion check. Continue at the next unfinished step.

The [investigation brief](FIRST_INVESTIGATION.md) is background for the first task, not a second assignment path. The [project contract](guides/project-contract.md) is a lookup for filenames/interfaces/commands, not required reading cover to cover.

Already completed the introduction, evidence labeling or baseline runs? Keep them. Resume at the corresponding next session in Module 1. Do not redo work just because this course was revised.

## What you build, in order

| Weeks | Module | Working result |
| --- | --- | --- |
| 1–6 | [1. Local RAG service](lessons/Module_01.md) | Inspect search, add checks, run a real model in week 4, own CLI in week 5 and local HTTP API in week 6 |
| 7–12 | [2. Better retrieval](lessons/Module_02.md) | Compare BM25, dense, hybrid and reranking in the same service |
| 13 | [Consolidation](ASSESSMENT.md) | Reproduce the chosen retrieval configuration |
| 14–19 | [3. Ingestion and grounded answers](lessons/Module_03.md) | Import longer documents, preserve evidence boundaries and review actual generated claims |
| 20–25 | [4. Automated evaluation](lessons/Module_04.md) | Version benchmarks, compare runs and block a bad release |
| 26 | [Consolidation](ASSESSMENT.md) | Repair the biggest evaluation gap |
| 27–32 | [5. Applied supervised learning](lessons/Module_05.md) | Train, test and integrate an evidence-quality gate |
| 33–38 | [6. Neural training and adaptation](lessons/Module_06.md) | Debug real training and compare a fine-tuned reranker with a frozen model |
| 39 | [Consolidation](ASSESSMENT.md) | Reload and reproduce the selected model artifacts |
| 40–45 | [7. Prepare and deploy on AWS](lessons/Module_07.md) | Identity, persistent pgvector retrieval, separate ingestion, containers and authenticated staging deployment |
| 46–51 | [8. Operate production RAG](lessons/Module_08.md) | CI/CD, telemetry, load/cost control, release promotion, rollback, database restore and handoff |
| 52 | [Consolidation](ASSESSMENT.md) | Complete the largest operational gap and verify teardown |

## Weekly working pattern

Each week has three one-hour sessions. Read the short relevant concept, change or build one component, then run it and inspect the result. Theory is available inside each module as a reference. There are no school-style theory questions, workflow essays or oral assessments.

Evidence of progress is the working result: code, tests, request traces, evaluated runs, model artifacts and deployed behavior. Short observations belong beside the experiment or change they explain; a negative result or retained baseline is acceptable when supported by the run.

The schedule contains 48 learning weeks plus four consolidation weeks: 156 planned hours. It is a planning estimate, not a promise that all implementation fits precisely. Setup/debugging count. Stop at the limit and continue next time; do not accumulate extra required homework. Tests validate the property being changed rather than merely mirroring the implementation.

## One stack and one project

Build in `projects/knowledge-assistant/`. The baseline lives in `tracks/rag/lab/` and remains reproducible. The first model uses Ollama locally; production uses the same provider interface with Bedrock. Retrieval begins in files, then moves to PostgreSQL/pgvector. Serving uses FastAPI, containers and ECS/Fargate. Infrastructure is Terraform and release automation is GitHub Actions.

The final **12 learning weeks are dedicated to production**. Follow the [AWS implementation guide](guides/production-aws.md) with Modules 7 and 8. AWS account/model access, domain/TLS, costs and cleanup are explicit prerequisites. Actual cloud practice incurs your own account charges; the course setup does not provision resources or make paid calls.

Agents, ticket-writing tools, MCP and voice are potential future tracks. They are not prerequisites for deploying this RAG service.

## Supplied versus implemented

**Supplied runnable examples:** fictional corpus/questions, lexical/BM25 retrieval, evaluation/comparison, label-hiding practice viewer, a minimal real Ollama RAG loop, deterministic boundary tests and numerical ML/attention references.

**You implement progressively:** your API, dense/hybrid/rerank adapters, ingestion/context, benchmark/review pipeline, applied training, persistent store, identity checks, Terraform, CI and operational runbooks. Interface contracts and implementation steps specify what to create; no completed cloud infrastructure is falsely claimed as tested.

The tiny fictional corpus teaches failure diagnosis. Later work adds permitted real documentation and independently labeled cases. Separate fixtures, real-model outputs, simulated load and actual deployment evidence in reports. A training deployment demonstrates practices on a bounded workload, not enterprise-scale reliability.

## Supporting material

- [Progress checklist](PROGRESS.md)
- [Practical completion and consolidation](ASSESSMENT.md)
- [Project layout and contracts](guides/project-contract.md)
- [First real model setup](guides/first-model.md)
- [AWS deployment and operation guide](guides/production-aws.md)
- [Environment/dependencies](ENVIRONMENT.md)
- [Short experiment template](EXPERIMENT_TEMPLATE.md)
- [What changed in this revision](CHANGELOG.md)

GitHub is the current source for this course. Notion remains a navigation/planning dashboard; earlier Notion lesson copies and downloads are snapshots.
