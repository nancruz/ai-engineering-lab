# First investigation — correct-looking answers from the wrong evidence

## Assignment

You have inherited an internal engineering assistant. Users report obsolete policy answers, missed paraphrases and a restricted operational value appearing for the wrong reader. The team suggests using a larger model. Your task is to determine what evidence supports that proposal and implement a more targeted first repair.

This is your first six-week module, not a one-evening task. Each week's work fits a three-hour planning budget. You already know how to write software: the new learning is measurement, evidence authority and model-system failure analysis.

## What is supplied

- A fictional corpus of 27 current, archived, restricted and adversarial documents.
- Fourteen development questions, including a multi-document question and no-evidence cases.
- Four held-out intent families for a later frozen assessment.
- A faulty keyword retriever, an authorized/current keyword baseline and a BM25 reference.
- Per-query traces with Recall@k, Hit@k, RR@k and complete labeled-set coverage; aggregate MRR@k across answerable questions.
- Five manually labeled answer-failure fixtures. They are not model-generated results.

## Your first three hours

**Hour 1:** Read [What a RAG system is](lessons/00-rag-introduction.md), then this brief. Explain the two workflows and where evidence can be lost.

**Hour 2:** Pick six development questions and label the evidence you would accept, including role and current/historical intent. Write these labels before running retrieval or inspecting its traces.

**Hour 3:** Run the faulty baseline and compare its traces with your labels. Write a short failure table and your next action. Stop at three hours. Metrics are introduced in week two; filtered keyword and BM25 comparisons follow in weeks three and four.

Commands are in [lab/README.md](lab/README.md). You can use the reference code directly this week; rebuilding CLI scaffolding is not a learning objective.

## Required artifact

A short incident memo: symptom; affected question IDs; expected evidence; retrieved evidence; primary/contributing failure stages; proposed experiment; before/after counts; limitation; release or no-go decision. Include saved run files and a reproducible command.

## Questions you must answer

1. Why can a valid citation still support a wrong answer?
2. When can Hit@3 equal one while the context is insufficient?
3. Why should no-evidence questions not get an arbitrary recall of zero?
4. Does removing stale evidence solve paraphrase misses?
5. What has this offline lab established about an actual LLM? What has it not established?

## Review key — attempt first

A citation may be stale, unauthorized, partially relevant or attached to an unsupported claim. Multi-evidence questions need complete required evidence, not one hit. Empty-gold recall is undefined and belongs in a separate abstention evaluation. Metadata and representation failures need different repairs. This reference establishes retrieval and metric behaviour on a fictional corpus, not real generation quality or enterprise performance.

A strong submission may reject a larger model as premature, but only after examining where evidence was lost. A prompt change is not a substitute for authorization enforcement.
