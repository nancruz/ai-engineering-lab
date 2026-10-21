# Module 08 — Release, monitor and operate RAG in production

Weeks 46–51 · 3 hours per week · one evolving knowledge-assistant project.

## Start here

Start with the authenticated AWS staging service from Module 7. Keep real inference tests bounded and reuse the same deployment route rather than starting a second platform.

**Working result:** An automated, observable and recoverable production-style RAG deployment, with a demonstrated restore and documented teardown.

Read only the current week's instructions. Use the reference section when a step points to a concept; there are no written theory answers or oral assessments. Demonstrate progress through working code, saved runs, tests and short observations attached to a change.

All shell commands start at the repository root. Paths beginning with `app/`, `tests/`, `artifacts/`, `data/` or `infra/` below mean files **inside** `projects/knowledge-assistant/`. You create these project files as the course progresses; the supplied baseline remains under `tracks/rag/lab/`. See the [project contract](../guides/project-contract.md) for the directory map, interfaces and commands.


## Week 46 — Automate releases without long-lived AWS keys

Deploy the same tested artifact rather than rebuilding an untracked version.

### Session A — Start and inspect (60 minutes)

Add GitHub Actions CI under `.github/workflows/` with project path filters: install locked dependencies, run deterministic tests, validate migrations and build the container. Pull requests do not receive production deployment permissions. Add a development evaluation job or explicit bounded manual run; live calls are separated from unit tests.

### Session B — Build or change (60 minutes)

Configure GitHub OIDC→AWS with trust restricted to this repository and the intended branch/environment. Separate CI deployment permissions from runtime task permissions. Add a staging workflow: build once→push immutable digest→run migrations→deploy the same digest→wait for stabilization→run authenticated smoke/security tests. Use expand/contract migrations that keep the previous app compatible.

### Session C — Run and verify (60 minutes)

Seed a failed gate and ensure deployment is skipped. Then deploy a harmless application change and verify image digest, Git SHA, pipeline config and index ID in the internal release record. Keep logs free of OIDC tokens and passwords. Add environment protection for promoting the already-tested digest to the production-style sandbox stage.

**Save:** CI workflow, scoped federation policy and a demonstrated successful/blocked deployment.

**Move on when:** a release can be repeated from GitHub without stored AWS access keys and a failed check cannot promote it. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 47 — Trace requests and alert on real failures

Make operational failures visible without leaking source content.

### Session A — Start and inspect (60 minutes)

Instrument request ID, retrieval/context/generation timings, active snapshot, model/prompt IDs, token usage where available, result status and error category. Use structured logs and optionally OpenTelemetry spans. Redact authorization headers, credentials, user questions and source bodies by default; use narrowly controlled development traces when needed.

### Session B — Build or change (60 minutes)

Create a CloudWatch dashboard for request rate, errors, latency distribution, provider failures/throttles, no-evidence/abstention counts, task memory/CPU and ingestion lag. Choose provisional SLOs from your workload, not from a copied target. Add alarm rules and an alert destination you control; use the CloudWatch console if you do not want external notifications.

### Session C — Run and verify (60 minutes)

Inject a provider timeout and a failed ingestion task. Confirm alarms change state, request IDs connect the affected stages, and readiness/liveness behave as intended. Inspect logs for planted fake secrets and verify they were redacted. Keep operational availability and reviewed answer quality as distinct signals.

**Save:** Dashboard, alarms, sanitized trace and controlled failure evidence.

**Move on when:** you can locate a failed answer request and see the failure stage without reading confidential raw content. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 48 — Test concurrency, latency and operating cost

Exercise workload limits instead of tuning from one happy-path request.

### Session A — Start and inspect (60 minutes)

Create `tests/load/` using a small load generator such as Locust. Define a mixed workload: repeated and new questions, longer inputs, restricted/no-evidence cases and a modest concurrency ramp. Set a maximum run duration/request count and estimate model-call cost before the cloud test. Start against a controlled generator double for infrastructure load, then a small bounded real-model batch.

### Session B — Build or change (60 minutes)

Measure end-to-end and stage p50/p95 with request count, concurrency and hardware recorded. Configure request deadlines, bounded queues/concurrency, database pool limits and retry budgets. Set an ECS scaling policy with explicit min/max capacity based on measured bottlenecks; more API tasks cannot fix a fixed Bedrock quota or database connection limit.

### Session C — Run and verify (60 minutes)

Change one bottleneck-driven setting, rerun the same workload and the quality/security regressions, then retain or revert it. Report all incurred attempts, input/output usage, task/database/load-balancer costs and ingestion work in cost per successful task. Separate simulated throughput from real-model throughput and cold from warm requests.

**Save:** Load script, bounded run reports, scaling configuration and cost worksheet.

**Move on when:** overload has a predictable controlled response and any retained optimization preserves the measured quality/security baseline. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 49 — Practice rollback and disaster recovery

Recover both the serving version and its supporting data.

### Session A — Start and inspect (60 minutes)

Add `runbooks/rollback.md` referencing exact release manifests, image digests, prompt/config versions, index snapshots and model/gate artifact hashes. Record the role allowed to execute it and the service's intended RTO/RPO. Confirm backups and snapshot retention before the drill.

### Session B — Build or change (60 minutes)

Deploy a deliberately bad prompt or staging index behind a test release. Detect its regression using a fixed canary/evaluation case, roll back the full effective release, and rerun the same case. Keep current ACL revocations enforced even when content rolls back. Never blindly reverse a destructive schema migration.

### Session C — Run and verify (60 minutes)

Restore an RDS snapshot into an isolated database, run integrity/source-manifest checks and point a disposable task at it. Measure restore time and newest recovered data; compare with your RTO/RPO. Delete the drill resources after verification. Separately test provider outage behavior: return controlled unavailability/abstention, not fabricated answers or an unapproved automatic provider switch.

**Save:** Executed rollback record, backup-restore result and actual recovery timings.

**Move on when:** you have demonstrated answer-quality recovery and database restoration, beyond a green health endpoint. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 50 — Promote a controlled pilot

Apply production release discipline to a small training service.

### Session A — Start and inspect (60 minutes)

Create a separate production-style environment/state and secrets; if paying for a second environment is outside your budget, tear down or pause the first and recreate the isolated target sequentially. Preserve manifests and clearly label this limitation. Use the same Terraform modules and tested image digest; environment-specific settings remain explicit.

### Session B — Build or change (60 minutes)

Run the release gate before promotion, including real provider evaluation, identity/ACL tests, migration compatibility and rollback availability. Promote the tested digest and approved index/config. Route only a small permitted test audience to it. Use deterministic canary requests plus optional willing testers; no unsolicited invitations are required.

### Session C — Run and verify (60 minutes)

Observe failed tasks, corrections, latency/cost and access results. Apply a stop rule for leaks, excessive spend or failed quality gates. Capture the effective release record and one rollback-ready previous version. If gates fail, keep it in staging and fix the actual defect rather than removing the gate.

**Save:** Controlled promotion record, pilot observations and a previous-release pointer.

**Move on when:** promotion is reproducible, evidence-gated and reversible. This is a training deployment, not proof of enterprise readiness. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 51 — Complete an operations handoff and teardown

Leave a system another engineer can run and recover.

### Session A — Start and inspect (60 minutes)

Run the project from a clean checkout with the documented environment setup. Follow the deployment runbook without relying on shell history. Check migrations, ingestion publication, service deployment, authentication, monitoring and evaluation artifact paths.

### Session B — Build or change (60 minutes)

Record a short practical demo: ingest a harmless source update, observe the new answer/citation, reject a forbidden request, locate its sanitized trace, and restore the previous approved release. Keep credentials and restricted content out of the recording.

### Session C — Run and verify (60 minutes)

Execute or schedule within your own workflow the documented teardown: stop services/jobs, inspect planned Terraform destruction, remove disposable ALB/tasks/RDS/NAT/endpoints/buckets as appropriate, and review retained backups, logs, ECR layers and state for ongoing costs. Preserve only the artifacts you intentionally need. Add known limitations and exact reproduction commands to the README.

**Save:** Working deployment/operations runbooks, recorded demo and teardown/cost verification.

**Move on when:** the application can be deployed, observed, updated, recovered and removed using committed instructions. If the hour ends first, keep your current work and resume the unfinished step next session.

## Next step

Use [week 52 consolidation](../ASSESSMENT.md) to finish the biggest operational gap. Choose the next training track only after the end-to-end deployment path is reproducible.

## Reference while building

A deployable RAG release is the combination of code/image, dependency lock, source snapshot, chunking/embedding revision, retrieval config, prompt, generator model, optional learned artifacts and current access policy. Version them together; code-only rollback may not restore answer behavior.

The API serves a validated active snapshot. Ingestion writes a candidate snapshot independently, validates it, then promotes one pointer. Updates, deletion and permission revocation need different semantics: a previous content snapshot cannot restore access that has since been revoked.

Liveness measures whether the process is alive; readiness measures whether it can accept work with its required local state. Answer quality needs separate canary/evaluation cases. Provider outages need timeouts, bounded retries and controlled failures, not restart storms.

Build once and promote an immutable image digest. Separate CI federation, task execution and application task roles. Record migrations and model/provider changes as releases; rerun quality checks when the effective configuration changes.

See the [AWS implementation guide](../guides/production-aws.md) for resource order, identity, storage, provider integration, deployment checks and official references.
