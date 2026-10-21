# Module 04 — Automate evaluation and release gates

Weeks 20–25 · 3 hours per week · one evolving knowledge-assistant project.

## Start here

Start with real answer records, your ingestion manifest and the local API. A useful benchmark grows incrementally while you fix actual failures.

**Working result:** A repeatable evaluation/review pipeline that can block an unsuitable release.

Read only the current week's instructions. Use the reference section when a step points to a concept; there are no written theory answers or oral assessments. Demonstrate progress through working code, saved runs, tests and short observations attached to a change.

All shell commands start at the repository root. Paths beginning with `app/`, `tests/`, `artifacts/`, `data/` or `infra/` below mean files **inside** `projects/knowledge-assistant/`. You create these project files as the course progresses; the supplied baseline remains under `tracks/rag/lab/`. See the [project contract](../guides/project-contract.md) for the directory map, interfaces and commands.


## Week 20 — Grow a useful regression dataset

Collect questions from actual source content and failure history.

### Session A — Start and inspect (60 minutes)

Create `data/benchmark/dev.jsonl` with the contract guide's schema. Reuse your independently labeled questions and add cases for exact terms, paraphrases, multi-source answers, conflicts, missing evidence and access differences. Group paraphrases under the same family ID.

### Session B — Build or change (60 minutes)

Add a dataset validator checking IDs, source references, ACL/temporal eligibility and duplicate question/family handling. Add a first batch of 10 useful questions, then grow toward roughly 40 over this module as time permits; do not invent confidence from that target count.

### Session C — Run and verify (60 minutes)

Run the API evaluation path and open every failure from the new batch. Repair ambiguous labels using source text and record label revisions. Keep label repairs separate from model/prompt changes so their effects remain visible.

**Save:** Versioned benchmark and validator results.

**Move on when:** new cases have source-backed expectations and the report exposes sample counts. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 21 — Create a real evaluation holdout

Prevent repeated tuning from becoming the final score.

### Session A — Start and inspect (60 minutes)

Split by intent/source family before tuning. Put a small distinct batch into `data/benchmark/final.jsonl` and save a split manifest. Work toward 20 final cases over time; disclose the actual count. The original four teaching holdouts can be used once as practice, not repeatedly called unseen.

### Session B — Build or change (60 minutes)

Add a split-overlap test for paraphrase families and source-fact duplicates. The final runner must require an explicit `--final` option. Keep routine CI on development/security fixtures rather than continuously exposing final labels to tuning.

### Session C — Run and verify (60 minutes)

Run the overlap checks with a deliberately duplicated family and verify failure. Remove that seeded duplicate. Freeze the final split hash and keep improving the application using development cases only.

**Save:** Split manifest and an executable leakage check.

**Move on when:** a duplicated family blocks evaluation preparation. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 22 — Automate paired comparisons

Generate an experiment report from compatible saved runs.

### Session A — Start and inspect (60 minutes)

Use one baseline and one candidate run with matching corpus, question set, k and family identities. Read [compare_runs.py](../lab/compare_runs.py) as an exploratory reference. Add equivalent identity checks to your project comparator, including prompt/model identifiers where they affect the comparison.

### Session B — Build or change (60 minutes)

Implement per-query and per-family deltas and a fixed-seed grouped bootstrap on retrieval recall. Also report raw wins/losses and answer-support counts if reviewed. Bootstrap retrieval and answer metrics separately rather than silently treating missing reviews as zeros.

### Session C — Run and verify (60 minutes)

Reject a comparison with changed corpus or query set in a test. Run a valid comparison and save the interval, family count and regressions. A tiny/broad interval is an inconclusive result, not a reason to tune on the final set.

**Save:** Comparison command, compatibility tests and actual run report.

**Move on when:** one command produces a reproducible comparison and refuses mismatched inputs. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 23 — Trial a model-assisted reviewer

Use an LLM judge as a tested helper for reviewing claims.

### Session A — Start and inspect (60 minutes)

Take reviewed development answers with both supported and unsupported claims. Create a judging prompt with a short rubric and examples, supplying exact evidence and hiding candidate system identity. Keep manual labels in a separate file.

### Session B — Build or change (60 minutes)

Run one real judge adapter on a bounded batch, record model/prompt IDs and compare its labels with your manual labels. Randomize candidate order where comparing pairs. Measure false approvals, false rejections and review coverage as counts.

### Session C — Run and verify (60 minutes)

Add a regression where verbosity disguises an unsupported value. Inspect disagreements and flag uncertain cases for human review. Keep hard access-control tests independent of judge opinion; a judge cannot authorize content.

**Save:** Judge adapter, review comparison and disagreement cases.

**Move on when:** the judge is either retained with known limitations or disabled based on observed errors. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 24 — Block a bad release automatically

Convert quality observations into a repeatable gate.

### Session A — Start and inspect (60 minutes)

Create `configs/release-policy.json` before final evaluation: required security tests, citation-shape checks, provisional quality/latency budgets and minimum review coverage. Use your measured baseline rather than an unexplained universal percentage.

### Session B — Build or change (60 minutes)

Implement `make -C projects/knowledge-assistant check` for deterministic tests and `make -C projects/knowledge-assistant eval` for bounded real-model development evaluation. Add `make -C projects/knowledge-assistant gate` consuming compatible run/review artifacts and exiting nonzero on policy failure. Keep external model calls out of ordinary unit tests.

### Session C — Run and verify (60 minutes)

Seed an unknown citation and an access violation in separate fixtures. Verify each blocks the gate, then restore the code. Keep archived gate outputs for the later deployment workflow.

**Save:** Release policy, commands and a demonstrated blocked release.

**Move on when:** the release command fails because of a relevant defect, not only lint or HTTP availability. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 25 — Cut an evaluated application release

Exercise the complete release flow locally before cloud deployment.

### Session A — Start and inspect (60 minutes)

Freeze code/config/data and run the final evaluation once for this milestone. Record which final cases are now consumed; future tuning requires a newly reserved final set. Keep the source snapshot, run manifest and review files together.

### Session B — Build or change (60 minutes)

Create `artifacts/releases/<release-id>/manifest.json` using the contract guide. Include approved index/prompt/model/config and review/gate artifact checksums. Save missing evidence and failures rather than editing outputs.

### Session C — Run and verify (60 minutes)

Run the release gate and tag an approved local release or mark it blocked. A blocked result is a practical outcome: fix it using development cases before deployment. Preserve a last-known-good manifest for rollback exercises.

**Save:** Complete release manifest, frozen evaluation and gate result.

**Move on when:** another run can identify exactly what configuration was evaluated and whether it is eligible for a pilot. If the hour ends first, keep your current work and resume the unfinished step next session.

## Next step

Use [week 26 consolidation](../ASSESSMENT.md), then [Module 5](Module_05.md).

## Reference — concepts used in the experiments

A benchmark is a measurement instrument. Its query distribution, labels, grading rubric and sample size determine what you may conclude. Separate development questions from a held-out family-level test set. Paraphrases of the same intent belong to one group; random splitting can leak the exact evidence pattern across partitions. Keep a corpus snapshot and benchmark version with each run.

Relevance labels can be graded: 0 irrelevant, 1 partially helpful, 2 directly sufficient. DCG@k sums (2^grade-1)/log2(rank+1), and nDCG divides by the ideal ordering for that query. State the gain convention. nDCG is useful for ranked graded relevance; it does not prove a generated answer is supported.

For paired system comparisons, compute per-query or per-family differences. Resample families, not individual correlated paraphrases, to form an exploratory bootstrap interval for the mean delta. This does not repair a biased benchmark or give reliable precision on a tiny fixture. Report sample count, distribution and failures alongside any interval. An interval crossing zero suggests the experiment has not clearly distinguished configurations on that sample.

LLM judges are fallible classifiers. Blind candidate identity, shuffle order and compare with human labels. Measure disagreement by failure category; a judge can prefer verbose unsupported answers. Record judge prompt and model revision. Repeated runs characterize stochastic variation. Unit tests, retrieval metrics and judged answer quality cover different properties.

Select release criteria before evaluating the held-out set. Distinguish a hard security invariant from a soft quality target. Zero observed unauthorized results in a finite test suite is necessary for that suite, not proof of universal safety. A release decision must state the sample, scenarios and unresolved risks.

## Worked example

System B wins on 18 paraphrases of one question and loses on three independent task families. Treating 21 rows as independent makes the result look stronger than it is. Group by intent, inspect family-level deltas and ask whether one task family dominates the benchmark.


## Primary references

- https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- https://scikit-learn.org/stable/modules/cross_validation.html
