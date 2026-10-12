# Applied AI Engineering through RAG — start here

A practical AI engineering track for an experienced software engineer. Start by understanding how RAG works, then diagnose a flawed knowledge-retrieval system with supplied data, metrics and traces.

## Time and progression

Three hours weekly, preferably three one-hour sessions. The plan contains 48 learning weeks and four consolidation weeks: 52 weeks, 156 scheduled hours. This is a workload estimate, not a job guarantee. Difficult labs may take additional weeks; depth is assessed by evidence, not by a deadline. Setup and debugging count toward study time. No extra “optional required” homework.

The eight chapters contain technical explanations, worked examples, six weekly labs each, investigation assessments and review guidance. Read only the current module. Primary references extend a topic within the study budget; they do not replace missing lesson content.

## Your first week: three hours

1. **Understand (60 minutes):** Read [What a RAG system is](lessons/00-rag-introduction.md). Explain ingestion and query-time processing in your own words, then read the [investigation brief](FIRST_INVESTIGATION.md).
2. **Label (60 minutes):** Pick six development questions. Read the corpus and record supporting document IDs, role and time constraints before viewing retrieval outputs.
3. **Inspect (60 minutes):** Run the faulty baseline using the [lab instructions](lab/README.md). Compare its traces with your labels and write a failure table. Stop at three hours and record the next action.

This introductory work is part of week one, not an extra prerequisite week. Formal metrics begin in week two; filtered-baseline comparisons follow in weeks three and four.

The retrieval lab uses Python 3.10+ standard library only. The numerical ML and attention labs use NumPy. Dense retrieval, reranking, neural adaptation and live generation are learner implementations requiring additional libraries/models; these are explicitly identified in their modules. No paid calls or cloud resources have been created for you.

## What you will build

One evolving engineering knowledge assistant: evidence benchmark → lexical/dense/hybrid search → grounded generation → calibrated evidence gate → model adaptation → authorized tool use → operated service. A focused supervised-learning project and neural-model adaptation remain required, so the course is not only API integration.

## Data and claims

The supplied corpus is fictional teaching material. Early numbers are controlled experiments. Before the later release assessments, expand with public documentation or material you are authorized to use and independently labeled questions. Never claim the small synthetic corpus establishes production effectiveness.

The held-out fixture file is accessible in this repository; it is a procedural holdout, not a secret exam. Do not inspect or tune on it before the designated assessment. Create new held-out intent families for later milestones.

## Completion

For each module, submit code/config, evaluation results, error examples, an architecture/experiment decision and an independent explanation. Use `ASSESSMENT.md`. A rejected model or no-go release can be a successful learning result when the reasoning is correct.

Keep reference implementations closed until your own attempt where a lab asks you to implement an algorithm. The provided retrieval engine is intentionally ready to run: this course does not spend weeks recreating basic software scaffolding.

## Lessons and checkpoints

| Weeks | Lesson |
| --- | --- |
| 1 | [Introduction: what RAG is](lessons/00-rag-introduction.md) |
| 1–6 | [1. Diagnose a failing knowledge assistant](lessons/Module_01.md) |
| 7–12 | [2. Retrieval algorithms and controlled comparisons](lessons/Module_02.md) |
| 13 | Consolidation and assessment |
| 14–19 | [3. Chunking, context and grounded generation](lessons/Module_03.md) |
| 20–25 | [4. Evaluation, uncertainty and release decisions](lessons/Module_04.md) |
| 26 | Consolidation and assessment |
| 27–32 | [5. Train an evidence decision model](lessons/Module_05.md) |
| 33–38 | [6. Neural representations, attention and adaptation](lessons/Module_06.md) |
| 39 | Consolidation and assessment |
| 40–45 | [7. Authorization, freshness and bounded tools](lessons/Module_07.md) |
| 46–51 | [8. Operate, assess and present](lessons/Module_08.md) |
| 52 | Consolidation and assessment |

Use the [progress checklist](PROGRESS.md), [assessment criteria](ASSESSMENT.md), [experiment template](EXPERIMENT_TEMPLATE.md) and [environment notes](ENVIRONMENT.md). Consolidation weeks are for finishing and reviewing existing work, without new required topics.
