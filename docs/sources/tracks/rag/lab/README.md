# Supplied runnable examples

Follow [Module 1](../lessons/Module_01.md) for the ordered exercises. This page is a command reference, not an extra sequence to complete first. All commands below start at the repository root unless indicated otherwise.

## First evidence investigation

```bash
python3 tracks/rag/tools/practice.py
python3 tracks/rag/tools/practice.py --check
python3 -m unittest discover -s tracks/rag/lab -p 'test*.py' -v
```

Display questions without reference labels first; use `--check` after your attempt. The viewer does not access the held-out question file.

## Retrieval runs

```bash
python3 tracks/rag/lab/evaluate.py --mode faulty --out projects/knowledge-assistant/experiments/module-01/faulty.json
python3 tracks/rag/lab/evaluate.py --mode keyword --out projects/knowledge-assistant/experiments/module-01/keyword.json
python3 tracks/rag/lab/evaluate.py --mode bm25 --out projects/knowledge-assistant/experiments/module-01/bm25.json
```

Create the output directory first. These commands use the standard library and make no model calls. Faulty mode deliberately bypasses access/freshness rules on fictional local data. Filtered keyword isolates the eligibility repair; BM25 then changes ranking. They are not a deployed application.

## First real model — week four

Follow [model setup](../guides/first-model.md), then:

```bash
python3 tracks/rag/lab/answer.py --question-id q02 --model llama3.2:3b --out projects/knowledge-assistant/experiments/module-01/answer-q02.json
```

This calls a real local Ollama model and saves exact context plus raw provider response. Output/citation validation does not check factual entailment. The script's fixture role is not authenticated. It is a first learning loop, not your completed service.

## Later references

`compare_runs.py` compares compatible retrieval runs with a grouped exploratory bootstrap. Use it during Module 4 after learning what its interval means. `../reference-solutions/math_labs.py` contains numerical mechanics examples for Modules 5–6; attempt your own implementations before consulting it.

The fictional corpus has 27 documents, 14 development questions and four held-out question families. Empty relevant sets represent no authorized supporting evidence; recall is undefined for these rows. Per-query `rr` becomes aggregate `mrr`. `complete` means all labeled relevant IDs were retrieved, not a universal sufficiency score.

`answer_fixtures.json` contains manually written labeled failure examples; never report them as generated model outputs. Real documentation, independent labels and application/cloud implementations are introduced explicitly in later modules.
