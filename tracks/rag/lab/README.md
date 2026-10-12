# Runnable investigation lab

From this folder, using Python 3.10+:

```bash
python3 -m unittest -v test_retrieval
python3 evaluate.py --mode faulty --out faulty.json
python3 evaluate.py --mode keyword --out keyword.json
python3 evaluate.py --mode bm25 --out bm25.json
python3 compare_runs.py keyword.json bm25.json
```

On Windows substitute `py -3` if needed. No third-party packages are needed for these commands. The faulty mode intentionally ignores authorization and current-version filtering, solely against the supplied fictional local data. Do not deploy it or connect confidential data to it.

For the numerical labs, install NumPy in an isolated environment using `python3 -m pip install numpy`, record the resolved version, then run `python3 ../reference-solutions/math_labs.py`. This lab trains a real small logistic model on generated numeric data and checks attention mechanics; it is not the final evidence-gate dataset or a trained transformer.

Reference retrieval is provided so your time goes into diagnosis and experiments. Implement your own metric, gradient or attention functions before checking the reference in modules that assess implementation.

## Extending the system

A retriever accepts a query context and returns ranked items with stable source IDs and scores. An embedding adapter must use a real model and its documented query/document preprocessing. A generator adapter returns structured claims, citations and optional abstention; preserve the exact context and model/prompt IDs. A model gate may only use serving-available features. Tool execution must enforce principal, approval and idempotency in code.

There is deliberately no fake LLM behind the reference. `answer_fixtures.json` contains human-authored failure examples with labels for learning. Add real generated outputs and human review in Module 3 before measuring generation quality. Dense models, PyTorch training, model adaptation, cloud deployment and the completed capstone are implementation assignments, not falsely pre-verified integrations.

## Data provenance and evaluation

All 27 documents and 18 questions are original fictional fixtures. Four question families are in `heldout.json`; the remaining 14 questions are development cases. Do not inspect the held-out questions during tuning. It is a procedural holdout, not a hidden secure exam. All later production-readiness work requires a broader independently labeled corpus and benchmark.

`relevant` means supporting document IDs under the question's role and temporal policy. Empty relevance means no authorized answer in this corpus. It does not mean search should return zero lexical matches. The evaluator deliberately excludes those questions from recall and does not manufacture an answer-quality score.

## Reading the metrics

Each row reports `recall`, `hit`, `rr` (reciprocal rank) and `complete` (all labeled relevant IDs found). The summary averages answerable rows and reports `mrr` for mean reciprocal rank. `complete` is not a universal evidence-sufficiency score; redundant sources need not all be retrieved. See [Module 1](../lessons/Module_01.md) for worked examples.
