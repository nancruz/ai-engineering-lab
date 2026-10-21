# First investigation — find the right evidence

You are building a fictional internal engineering knowledge assistant. Some source documents are outdated, some readers cannot access particular documents, and some questions use different wording from the source.

Your first practical task is to compare **the evidence a question needs** with **the documents search actually returns**. You do this before blaming or changing a language model.

## Continue here

After the [RAG introduction](lessons/00-rag-introduction.md), follow **[Module 1 — Week 1](lessons/Module_01.md#week-01--run-and-inspect-the-supplied-search)**. That is the single sequence of instructions. Do not treat this brief as extra homework.

You will use:

| Material | Purpose |
| --- | --- |
| [Practice viewer](tools/practice.py) | Display development questions without their reference labels |
| [dev.json](lab/data/dev.json) | Original questions and labels for checking your attempt |
| [corpus.json](lab/data/corpus.json) | Source text, document IDs, versions and roles |
| [evaluate.py](lab/evaluate.py) | Save what a supplied retriever returns |

The worked first case is **q02: “What is the current production catalog timeout?”** It uses `timeout-v2`, a current engineer-accessible source supporting 800 milliseconds. You then try q03 and other cases yourself. Exact commands and output tables are in Module 1.

## What happens after the first exercise

Week 1 inspects evidence; week 2 adds metric tests; week 3 tests filtering; week 4 runs a real RAG model call; weeks 5–6 build your own CLI/API. Existing work counts. There is no final incident memo, theory questionnaire or release decision due at the start.
