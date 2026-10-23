# Practical completion and consolidation

Progress is demonstrated by working behavior and reproducible artifacts. There are no theory questionnaires, oral defenses or school-style grading scores. Use each session's “Move on when” check; if it is not met, keep working there within the weekly budget.

## Completion checkpoints

| After module | Practical check |
| --- | --- |
| 1 | Query your own local API, inspect real model evidence/citations, and see timeout/invalid-output tests pass. |
| 2 | Swap named retrieval configs, reproduce their actual rankings and keep the chosen version in the API. |
| 3 | Ingest a longer permitted source, retain its qualifiers in context and trace a reviewed answer claim to a source span. |
| 4 | Seed a quality/access regression and watch the release gate reject it. |
| 5 | Reload the learned gate, reproduce predictions and compare it with a simple serving baseline. |
| 6 | Reload the selected neural artifact after a real adaptation comparison; retain the frozen model if adaptation regresses. |
| 7 | Send an authenticated HTTPS request through deployed retrieval and Bedrock; reject an invalid or forbidden identity. |
| 8 | Promote a tested release, observe a controlled failure, restore the previous effective version and exercise a database restore. |

A failed model experiment can be complete; a broken implementation hidden behind a written explanation is unfinished. Finite security tests demonstrate their tested invariants, not universal attack resistance. Keep known limitations visible.

## Four consolidation weeks — three hours each

### Week 13

1. Session A: Finish the highest-priority incomplete retrieval step.
2. Session B: Rebuild model/vector caches from the recorded manifest in a clean process.
3. Session C: Run the chosen config through the API and save one comparison with its baseline. Repair any reproduction gap.

### Week 26

1. Session A: Finish benchmark/review/gate work blocking the local release.
2. Session B: Inject a split leak or unsupported citation and verify the relevant check fails.
3. Session C: Restore the fixtures, rerun the release gate and archive the effective manifest.

### Week 39

1. Session A: Finish actual training/checkpoint work, if incomplete.
2. Session B: Load the selected artifacts in a clean process; run feature/tokenizer/version mismatch checks.
3. Session C: Start the local service using the release manifest intended for production modules. Fix a failure before provisioning cloud infrastructure.

### Week 52

1. Session A: Finish the biggest deployment/operations gap, such as real identity verification or a backup restore.
2. Session B: Reproduce the operational demo using committed runbooks.
3. Session C: Verify teardown and retained costs, and leave the README clear enough for another engineer to repeat the work.

## Final deliverables

Keep a runnable project with dependency/config records, permitted source provenance, evaluation/review results, one applied training experiment, security tests, an immutable release manifest, Terraform/workflow definitions, deployment/rollback/restore/teardown runbooks and a short practical demo.

Clearly distinguish local fixtures, actual model calls, load tests with doubles, real cloud runs and any pilot. This evidence supports discussion of your engineering work; completing a course is not an employment guarantee or proof of specialist seniority.
