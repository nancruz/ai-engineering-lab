# Module 04 — Evaluation, uncertainty and release decisions

Weeks 20–25 · 18 hours total · software-engineering experience assumed.

## Technical lesson

A benchmark is a measurement instrument. Its query distribution, labels, grading rubric and sample size determine what you may conclude. Separate development questions from a held-out family-level test set. Paraphrases of the same intent belong to one group; random splitting can leak the exact evidence pattern across partitions. Keep a corpus snapshot and benchmark version with each run.

Relevance labels can be graded: 0 irrelevant, 1 partially helpful, 2 directly sufficient. DCG@k sums (2^grade-1)/log2(rank+1), and nDCG divides by the ideal ordering for that query. State the gain convention. nDCG is useful for ranked graded relevance; it does not prove a generated answer is supported.

For paired system comparisons, compute per-query or per-family differences. Resample families, not individual correlated paraphrases, to form an exploratory bootstrap interval for the mean delta. This does not repair a biased benchmark or give reliable precision on a tiny fixture. Report sample count, distribution and failures alongside any interval. An interval crossing zero suggests the experiment has not clearly distinguished configurations on that sample.

LLM judges are fallible classifiers. Blind candidate identity, shuffle order and compare with human labels. Measure disagreement by failure category; a judge can prefer verbose unsupported answers. Record judge prompt and model revision. Repeated runs characterize stochastic variation. Unit tests, retrieval metrics and judged answer quality cover different properties.

Select release criteria before evaluating the held-out set. Distinguish a hard security invariant from a soft quality target. Zero observed unauthorized results in a finite test suite is necessary for that suite, not proof of universal safety. A release decision must state the sample, scenarios and unresolved risks.

## Worked example

System B wins on 18 paraphrases of one question and loses on three independent task families. Treating 21 rows as independent makes the result look stronger than it is. Group by intent, inspect family-level deltas and ask whether one task family dominates the benchmark.

## Six weekly labs

### Week 20 — Expand the benchmark

- [ ] 60 minutes — Study and reason: Write a sampling plan across exact IDs, paraphrases, conflicts, multi-hop and no-evidence questions.
- [ ] 60 minutes — Implement or experiment: Expand to at least 40 development questions grouped by intent; label evidence before runs.
- [ ] 60 minutes — Test and explain: Audit duplicates and label ambiguity; do not call this population-representative.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 21 — Define a held-out set

- [ ] 60 minutes — Study and reason: Choose separate intent families and record a split manifest.
- [ ] 60 minutes — Implement or experiment: Create at least 20 held-out questions and seal them from tuning.
- [ ] 60 minutes — Test and explain: Verify no paraphrase family crosses splits and document limitations.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 22 — Quantify differences

- [ ] 60 minutes — Study and reason: Calculate paired deltas and family-level averages.
- [ ] 60 minutes — Implement or experiment: Implement grouped bootstrap with a fixed seed using stored run files.
- [ ] 60 minutes — Test and explain: Interpret an interval without claiming significance from tiny samples.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 23 — Audit a judge

- [ ] 60 minutes — Study and reason: Define a claim-support rubric with two positive and two negative examples.
- [ ] 60 minutes — Implement or experiment: Compare an LLM judge against manually labeled answers with candidate IDs hidden.
- [ ] 60 minutes — Test and explain: Report disagreements and decide which labels still need human review.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 24 — Build regression checks

- [ ] 60 minutes — Study and reason: Choose hard invariants and provisional quality budgets before test evaluation.
- [ ] 60 minutes — Implement or experiment: Add benchmark execution and a comparison report to CI or a local release command.
- [ ] 60 minutes — Test and explain: Introduce an unsupported citation regression and demonstrate a blocked release.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 25 — Make a release decision

- [ ] 60 minutes — Study and reason: Freeze all choices and run the held-out set once for this milestone.
- [ ] 60 minutes — Implement or experiment: Write a quality/latency/cost report with counts and failure examples.
- [ ] 60 minutes — Test and explain: Choose release, restricted pilot or no-go and defend it.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

## Investigation assessment

A dashboard reports a five-point quality improvement after a prompt change. The judge also changed, five hard questions disappeared, and answer length doubled. Reconstruct a comparable experiment and decide whether the improvement is supported.

## Review guidance — attempt first

Hold the benchmark, judge and grading rubric fixed to attribute a prompt effect. Regrade archived outputs if possible. Missing hard cases are a benchmark change, not product improvement. Add human review of the longer answers; more claims create more opportunities for unsupported content.

## Mastery gate

Pass when a second engineer can reproduce the comparison, family grouping is defensible, uncertainty is reported honestly and your release gate catches a deliberate regression.

## Primary references

- https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- https://scikit-learn.org/stable/modules/cross_validation.html
