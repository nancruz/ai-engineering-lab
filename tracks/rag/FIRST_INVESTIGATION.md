# First investigation — scenario and starting point

## What you are investigating

You have inherited a fictional internal knowledge assistant. Some retrieved documents are obsolete, some questions use different wording from their sources, and some evidence is restricted to particular readers.

Your first goal is to compare **which documents should support an answer** with **which documents the supplied search returns**. Over six weeks, you will learn to measure those differences and evaluate targeted repairs.

The starter lab performs retrieval and evaluation only. There is no live LLM, and you are not expected to build ingestion, embeddings or a complete assistant before beginning.

## Go here next

If you have finished the [RAG introduction](lessons/00-rag-introduction.md), open **[Module 1 — Week 1, Session A](lessons/Module_01.md#session-a--understand-the-task-60-minutes)**.

That page contains the complete ordered instructions. Follow one session at a time; do not read all six weeks before starting.

If you have already explained ingestion and query-time processing and set up the repository, continue directly to **[Session B — Decide what good evidence looks like](lessons/Module_01.md#session-b--decide-what-good-evidence-looks-like-60-minutes)**.

## What the first exercise uses

| Material | Purpose |
| --- | --- |
| [dev.json](lab/data/dev.json) | Questions and their user context; also contains reference labels for checking your reasoning |
| [corpus.json](lab/data/corpus.json) | Fictional source documents, including their versions and access permissions |
| [evaluate.py](lab/evaluate.py) | Runs a supplied retriever and saves its ranked results |
| [Module 1](lessons/Module_01.md) | Exact steps, commands, examples and completion checks |

Start with **q02: “What is the current production catalog timeout?”** Session B walks through finding and justifying its evidence. Then you attempt q03 yourself before expanding to other cases.

## What is due now versus later

| Stage | What you produce |
| --- | --- |
| Week 1 | Short workflow explanation, evidence-label table and comparison with a saved faulty retrieval run |
| Week 2 | Hand-calculated metrics and tests |
| Week 3 | Comparison before and after metadata filtering |
| Week 4 | Comparison of keyword and BM25 ranking |
| Week 5 | Three documented failure cases with proposed checks |
| Week 6 | Final incident memo and justified decision |

The final incident memo and release recommendation are **week-six deliverables**. You do not need them to finish week one.

Three hours per week is the time budget. Reading and setup count. If a session runs out of time, record the unfinished step and resume there next time. Already completed reading does not need to be repeated.
