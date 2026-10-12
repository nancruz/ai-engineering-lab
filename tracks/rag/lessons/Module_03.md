# Module 03 — Chunking, context and grounded generation

Weeks 14–19 · 18 hours total · software-engineering experience assumed.

## Technical lesson

Chunking decides what evidence can be retrieved and what meaning survives segmentation. Fixed windows are a reproducible baseline, but splitting a prerequisite from an action can change the interpretation of a runbook. Heading-aware chunks preserve structure; parent-child retrieval uses small retrieval units and expands their surrounding context. Overlap increases storage and duplicate evidence, and can inflate naive metrics if sibling chunks are counted as independent successes.

Keep stable source IDs, version IDs and offsets on every chunk. Evaluate both passage relevance and coverage of distinct required facts. Aggregate to source-document IDs when comparing with document-level labels. A chunk-ID change should not accidentally redefine the test target. Context packing must respect token budgets and provenance, not merely concatenate the first k results.

Generation is conditional on a prompt, question and context. Low sampling temperature does not guarantee factuality or identical results across provider revisions. Require an output schema with answer, atomic claims, cited evidence IDs and an abstention reason. Schema validity checks syntax; claim verification checks whether evidence actually supports meaning. Separate these tests.

An answer may be supported by obsolete material and still be wrong for the question. Authority, time and entailment must all be satisfied. When sources conflict, identify the conflict and their scope rather than averaging incompatible instructions. When evidence is insufficient, abstention is a useful system action. A model saying “I am confident” is not an evidence sufficiency measure.

## Worked example

A runbook says “For EU production only, wait 15 minutes before rollback. In staging, rollback immediately.” A chunk beginning at “rollback immediately” loses its environment qualifier. Increasing k may retrieve more text while preserving the ambiguity. A useful intervention retains the heading and condition with the action, then tests both production and staging questions.

## Six weekly labs

### Week 14 — Define chunk identity

- [ ] 60 minutes — Study and reason: Mark the evidence spans for six questions and their required qualifiers.
- [ ] 60 minutes — Implement or experiment: Implement fixed-window chunking with source/version/offset metadata.
- [ ] 60 minutes — Test and explain: Check reconstruction and duplicate coverage; record the baseline.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 15 — Compare segmentation

- [ ] 60 minutes — Study and reason: Read context-loss examples and choose heading-aware segmentation.
- [ ] 60 minutes — Implement or experiment: Compare fixed and structural chunks with the retriever held constant.
- [ ] 60 minutes — Test and explain: Evaluate qualifier retention and document-level recall, not chunk counts alone.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 16 — Pack context

- [ ] 60 minutes — Study and reason: Define a token budget and source diversity policy.
- [ ] 60 minutes — Implement or experiment: Add deduplication and parent expansion while preserving offsets.
- [ ] 60 minutes — Test and explain: Test a multi-document question and an evidence-overflow case.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 17 — Integrate a generator

- [ ] 60 minutes — Study and reason: Choose one provider or local model; record model ID, prompt version and output contract.
- [ ] 60 minutes — Implement or experiment: Implement generation behind an adapter with timeout and schema validation.
- [ ] 60 minutes — Test and explain: Run a bounded development batch; distinguish fixtures from actual generated results.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 18 — Verify claims

- [ ] 60 minutes — Study and reason: Break ten generated answers into atomic factual claims.
- [ ] 60 minutes — Implement or experiment: Label support, citation validity, authority and abstention independently.
- [ ] 60 minutes — Test and explain: Inspect cases where a real citation fails to support the attached claim.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 19 — Resolve conflicts

- [ ] 60 minutes — Study and reason: Create current/historical and environment-specific questions.
- [ ] 60 minutes — Implement or experiment: Implement an explicit source-authority policy plus a conflict response.
- [ ] 60 minutes — Test and explain: Compare against prompt-only instructions and explain residual failure risk.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

## Investigation assessment

The correct runbook appears in top-3, yet the answer recommends a staging action in production. Determine whether segmentation, context selection or generation is responsible. Compare two fixes without changing the retriever and generator simultaneously.

## Review guidance — attempt first

First inspect the exact context sent to the model. If the qualifier was dropped, repair chunking/packing. If it is present and ignored, examine generation and validation. Showing a correct retrieved document is insufficient: the model may never have received the decisive sentence.

## Mastery gate

Pass when you can trace each answer claim to an authorized current evidence span, measure abstention separately, and reproduce one chunking-related failure. Require actual generation before reporting answer-quality scores.

## Primary references

- https://www.anthropic.com/engineering/contextual-retrieval
- https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
