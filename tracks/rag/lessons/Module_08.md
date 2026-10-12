# Module 08 — Operate, assess and present the system

Weeks 46–51 · 18 hours total · software-engineering experience assumed.

## Technical lesson

Production engineering adds workload, concurrency, observability and change management to model quality. Measure end-to-end latency and each stage separately: retrieval, reranking, generation and external tools. Report p50/p95 with sample count and workload description; nine toy requests do not characterize tail latency. Cancellation and bounded retries prevent abandoned requests from consuming unbounded resources.

Cost per successful task includes failed attempts, retries, embedding refreshes, reranker compute and infrastructure. A cheaper model can increase total cost if it requires retries or causes more human correction. Test optimizations with a fixed quality benchmark. Cache hits should be measured separately from cold requests, and security scope must remain correct.

A deployable artifact includes code, dependencies, corpus/model/prompt versions, configuration and evaluation results. A rollback may need to restore an index snapshot and prompt alongside code. A model provider change can alter behaviour without a code diff; schedule a benchmark when the effective model changes. A runbook describes detection, mitigation, rollback and recovery verification.

The capstone is an internal engineering knowledge assistant with explicit current/historical semantics, evidence-backed answers, permissions and a bounded optional ticket-drafting tool. Recruit a small pilot only after the core boundaries work. Observe corrections and failed tasks. A few users reveal failures; they do not establish statistically reliable product uplift.

Your portfolio should explain the original problem, alternatives, experiments, rejected changes, failure investigations and measured limitations. An employer can assess independent implementation and reasoning from this evidence. A training deployment remains a training deployment; do not describe it as years of production experience.

## Worked example

A smaller model cuts cost per call by 40%, but requires two attempts on average and still has lower success. Compare cost per successful task under the same retry policy before claiming savings. Then inspect whether retrying repeats the same failure rather than providing new evidence.

## Six weekly labs

### Week 46 — Package a release

- [ ] 60 minutes — Study and reason: Write the runtime and dependency contract and choose one protected deployment route.
- [ ] 60 minutes — Implement or experiment: Containerize the service and add reproducible unit/evaluation commands.
- [ ] 60 minutes — Test and explain: Rebuild from a clean checkout and document secrets and teardown.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 47 — Instrument and deploy

- [ ] 60 minutes — Study and reason: Define trace fields and a redaction policy before collecting content.
- [ ] 60 minutes — Implement or experiment: Deploy a small service, set a personal spending cap and exercise realistic requests.
- [ ] 60 minutes — Test and explain: Trace one failed task end to end and verify authentication and cancellation.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 48 — Optimize with evidence

- [ ] 60 minutes — Study and reason: Choose one bottleneck from measured stage timings.
- [ ] 60 minutes — Implement or experiment: Try one change such as batching, caching or a smaller model.
- [ ] 60 minutes — Test and explain: Compare latency, cost per success and the unchanged quality benchmark.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 49 — Run an incident drill

- [ ] 60 minutes — Study and reason: Define provider outage, stale index and bad prompt scenarios.
- [ ] 60 minutes — Implement or experiment: Inject one failure and perform rollback with a versioned runbook.
- [ ] 60 minutes — Test and explain: Verify recovery using benchmark cases, not only a green health endpoint.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 50 — Pilot and audit

- [ ] 60 minutes — Study and reason: Freeze the pilot scope and label any simulated testing honestly.
- [ ] 60 minutes — Implement or experiment: Observe two willing testers or run an independent scenario-based assessment.
- [ ] 60 minutes — Test and explain: Record corrections, failures and the highest-value repair.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 51 — Final IC assessment

- [ ] 60 minutes — Study and reason: Freeze the final configuration and open the held-out assessment.
- [ ] 60 minutes — Implement or experiment: Implement an unfamiliar change and diagnose a seeded failure without a walkthrough.
- [ ] 60 minutes — Test and explain: Present the evidence dossier and choose next specialization or suitable applications.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

## Investigation assessment

The service is healthy, latency is normal, and answers regress after a document refresh. Reproduce the affected corpus version, locate the broken stage and perform a rollback that restores answer behaviour.

## Review guidance — attempt first

A container health check says little about answer quality. Compare source snapshots, chunk IDs, embedding revisions and prompt/model configuration. Restore the complete effective configuration and verify with relevant benchmark cases. If the incident cannot be reproduced, improve version capture before claiming a root cause.

## Mastery gate

Pass when another engineer can run the service, reproduce evaluation, observe a failure, execute rollback and inspect a candid case study. Present real model measurements separately from offline fixtures.

## Primary references

- https://docs.aws.amazon.com/bedrock/
- https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
