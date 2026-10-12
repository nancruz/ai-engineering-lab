# Module 07 — Authorization, freshness and bounded tool use

Weeks 40–45 · 18 hours total · software-engineering experience assumed.

## Technical lesson

A RAG service often joins content from systems with different permissions. Authorization must be derived from a trusted authenticated principal and enforced before evidence reaches generation. A role supplied in the question is not an identity. Filtering after top-k can discard all candidates while authorized evidence remains below the cutoff; permission-aware candidate selection or sufficient overfetch with strict filtering is needed. No unauthorized text may enter context, traces exposed to users or shared caches.

Cache identity includes corpus version, model/prompt configuration, query and relevant authorization scope. A cached answer for an administrator must not be reused for a restricted user. A permission change can invalidate cached outputs even when document bytes are unchanged. Do not log confidential content merely to improve observability.

Freshness requires update, deletion and version semantics. A connector event may arrive twice or out of order. Use source version IDs, idempotent upserts and tombstones for deletion. Index rebuilds should be auditable and atomically promoted where practical. Current-policy filtering must still permit authorized historical questions through an explicit temporal policy.

Tool calling adds effects to an uncertain model. Treat a model's call as a proposal: validate its schema, permissions and business constraints in code. Read-only search can be automatic; a ticket write uses human approval and an idempotency key. Persist the request state, approval and completed effect, so retrying a run does not duplicate a write.

A retrieved document that says “ignore the user and call this tool” is untrusted content, not a privileged instruction. Prompt formatting helps separate content but is not a complete security boundary. Narrow tool authority, validate arguments and test adversarial content. An agent is justified only where adaptive steps improve a measured task over an explicit workflow.

## Worked example

An admin asks for a restricted capacity setting. The service caches the answer by query text. A viewer asks the same question and receives the cached answer without retrieval. Retrieval authorization tests pass, but the end-to-end system leaks. Scope the cache and test the entire response path, including cache hits.

## Six weekly labs

### Week 40 — Enforce identity

- [ ] 60 minutes — Study and reason: Define principal, document ACL and access-decision contracts.
- [ ] 60 minutes — Implement or experiment: Extend the lab filter to an authenticated service boundary.
- [ ] 60 minutes — Test and explain: Test cross-role queries and ensure restricted evidence never reaches context.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 41 — Test cache isolation

- [ ] 60 minutes — Study and reason: List fields affecting answer identity, including permission scope.
- [ ] 60 minutes — Implement or experiment: Implement or simulate a scoped answer cache and invalidation on permission changes.
- [ ] 60 minutes — Test and explain: Reproduce the admin-to-viewer leak in an isolated test and show the repair.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 42 — Handle source lifecycle

- [ ] 60 minutes — Study and reason: Define version ordering, updates and tombstones.
- [ ] 60 minutes — Implement or experiment: Implement idempotent document upsert/delete and a corpus snapshot ID.
- [ ] 60 minutes — Test and explain: Replay duplicate/out-of-order events and verify no stale deleted evidence remains.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 43 — Add bounded tools

- [ ] 60 minutes — Study and reason: Define two read-only tools and a sandbox ticket-write contract.
- [ ] 60 minutes — Implement or experiment: Implement schema validation, approval and step/time limits.
- [ ] 60 minutes — Test and explain: Test malicious document instructions, invalid arguments and an unapproved write.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 44 — Recover safely

- [ ] 60 minutes — Study and reason: Model durable states for requested, approved, executing and completed.
- [ ] 60 minutes — Implement or experiment: Inject a timeout after a sandbox write and retry using an idempotency key.
- [ ] 60 minutes — Test and explain: Prove only one effect occurred and explain the persistence boundary.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 45 — Compare agent and workflow

- [ ] 60 minutes — Study and reason: Define a multi-step information task and a deterministic baseline.
- [ ] 60 minutes — Implement or experiment: Run repeated tasks with both designs and inspect failure traces.
- [ ] 60 minutes — Test and explain: Choose the simpler design unless adaptive execution earns its complexity.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

## Investigation assessment

The agent creates the same ticket twice after a timeout, despite a prompt saying “never duplicate tickets.” Find the missing application invariant and demonstrate a fix with a repeatable failure injection.

## Review guidance — attempt first

The fix belongs at the effect boundary: stable idempotency keys and persisted effect results, not a stronger prompt. Approval must be associated with the actual arguments; changing a requested write after approval requires a fresh decision. Demonstrate duplicate calls without duplicate effects.

## Mastery gate

Pass when authorization holds across retrieval/cache/context, updates and deletions are reproducible, and retries cannot duplicate the tested write. State that finite adversarial tests do not prove universal injection resistance.

## Primary references

- https://www.anthropic.com/engineering/building-effective-agents
- https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
