# Assessment and evidence dossier

Score each dimension 0–3: 0 missing, 1 explained only, 2 implemented with guidance, 3 implemented and independently debugged. Require 3 for the main algorithm/evaluation boundary of a module before advancing. Security invariants must pass all defined negative cases; a finite test suite is not a universal guarantee.

Dimensions: problem definition; data/label validity; implementation; experimental control; error diagnosis; reproducibility; operational reasoning. Do not average away invalid evaluation or permission leakage with a polished demo.

## Four consolidation weeks

- Week 13: reproduce retrieval comparisons; debug a held-back query family; defend lexical versus dense trade-offs.
- Week 26: audit benchmark leakage and judge disagreement; repeat an inconclusive experiment; write a release/no-go decision.
- Week 39: reproduce training/checkpoint inference; diagnose a bad gradient or false negative; defend frozen versus adapted models.
- Week 52: close the largest capstone gap; perform an unfamiliar change and incident recovery; review IC readiness.

Each consolidation week is 3 × 60 minutes. Use it for unfinished core work first.

## Final practical

1. Diagnose an answer error without being told the failing stage.
2. Implement a new retrieval or authorization requirement with meaningful tests.
3. Identify a leaked feature or invalid validation split in a model experiment.
4. Explain and check a gradient or attention computation.
5. Reproduce a model/retrieval comparison and its uncertainty limitations.
6. Recover a failed effect without duplicate writes.
7. Deploy/rollback the effective code, corpus and model configuration.

The final dossier contains a runnable repository, dependency/config record, corpus provenance, benchmark protocol, paired experiment reports, one model-training report, threat tests, runbook, incident report and a 10-minute demo. Clearly label simulations, real model calls, pilots and remaining limitations. Existing software seniority transfers; specialist AI seniority must be demonstrated rather than inferred.
