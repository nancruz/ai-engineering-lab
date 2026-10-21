# Module 07 — Prepare and deploy the RAG service on AWS

Weeks 40–45 · 3 hours per week · one evolving knowledge-assistant project.

## Start here

This starts the final 12-week production sequence. Bring a working local release; do not begin cloud deployment while the local pipeline is broken. Follow the [AWS guide](../guides/production-aws.md) alongside these sessions.

**Working result:** A containerized, authenticated staging service on ECS/Fargate with persistent pgvector retrieval, a separate ingestion job and real Bedrock inference.

Read only the current week's instructions. Use the reference section when a step points to a concept; there are no written theory answers or oral assessments. Demonstrate progress through working code, saved runs, tests and short observations attached to a change.

All shell commands start at the repository root. Paths beginning with `app/`, `tests/`, `artifacts/`, `data/` or `infra/` below mean files **inside** `projects/knowledge-assistant/`. You create these project files as the course progresses; the supplied baseline remains under `tracks/rag/lab/`. See the [project contract](../guides/project-contract.md) for the directory map, interfaces and commands.


## Week 40 — Make the API safe to expose

Start the production phase with application boundaries before provisioning infrastructure.

### Session A — Start and inspect (60 minutes)

Use your release candidate from week 38. Create `tests/security/` and `app/auth.py`. Define a principal containing subject ID, trusted groups and authorization scope version. Keep local fixture authentication enabled only in explicit development mode. In non-development mode, missing identity configuration must fail startup.

### Session B — Build or change (60 minutes)

Implement a JWT verifier using a maintained library and the [AWS production guide](../guides/production-aws.md#identity-boundary). Configure issuer, app client, trusted signing algorithm and JWKS source. Validate signature, expiry, token_use and client/scope claims. Map trusted groups to document roles; ignore roles in prompts or request bodies. Unit-test the boundary with a controlled signing key/test issuer; real Cognito tokens are checked after provisioning.

### Session C — Run and verify (60 minutes)

Send the same capacity query under admin, engineer, missing, expired and wrong-client tokens. Spy on generator input and assert restricted evidence never reaches it for engineers. Ensure a nonexistent/forbidden document ID returns no privileged content in errors or traces. Mark fixture and real-token tests separately.

**Save:** JWT boundary, non-development startup checks and security tests.

**Move on when:** forged/missing identities fail closed, and document filtering uses the trusted principal throughout the answer path. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 41 — Persist authorized retrieval in PostgreSQL

Replace process-local index state with a production-capable store while keeping a comparison baseline.

### Session A — Start and inspect (60 minutes)

Start local PostgreSQL with pgvector using Docker Compose and a pinned image digest. Follow [storage migration](../guides/production-aws.md#storage-and-index-layout). Create a migration for source/chunk rows, a vector dimension matching your selected encoder and an index-snapshot table. Keep role/snapshot predicates in SQL, not after the first top-k results.

### Session B — Build or change (60 minutes)

Implement `app/store.py` and a migration/import command. Store text, metadata, vectors and checksums in one candidate snapshot. Compare eligible exact vector top-k with the file-based retriever on the same data. Keep BM25 over the eligible active snapshot if your chosen configuration uses it; do not silently replace BM25 with PostgreSQL full-text rank and call it equivalent.

### Session C — Run and verify (60 minutes)

Test SQL-level role/status filtering, model/dimension mismatch and a database timeout. Restart the API and database without deleting the volume and rerun q02. Inspect `EXPLAIN` on an authorized query. Use exact vector search first; ANN/HNSW tuning is an optional measured extension, not an extra required database migration.

**Save:** Compose database, schema migration, import command and retrieval-parity report.

**Move on when:** authorized indexed data survives process restart and the same fixtures exercise the new persistent path. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 42 — Publish source changes without corrupting live answers

Keep ingestion separate from serving, with a recoverable publication point.

### Session A — Start and inspect (60 minutes)

Create `app/ingestion_job.py` as a one-shot command that loads a source manifest, parses/chunks/embeds it and writes a candidate snapshot. The API reads the active snapshot ID once per request. It must never rebuild the full index at startup or during an answer request.

### Session B — Build or change (60 minutes)

Add validation before promotion and a transactional active-snapshot pointer update. Make duplicate upserts idempotent. Implement versioned tombstones so old upserts cannot resurrect deleted sources. Permission revocation must also affect old snapshots: maintain a current deny/revocation check independent of historical content, so rollback cannot restore access that was removed.

### Session C — Run and verify (60 minutes)

While querying snapshot A, build B, change a fictional policy, delete a source and replay an older event. Promote B only after validation. Confirm in-flight requests stay internally consistent and new requests use B. Roll back to A and verify the current revocation overlay still blocks deleted/forbidden content. If caching is enabled, key it by authorization scope/version, snapshot and effective pipeline version and invalidate on revocations; otherwise keep caching disabled.

**Save:** Separate ingestion job, snapshot publisher, tombstone/revocation tests and rollback record.

**Move on when:** a failed import cannot replace the active index and restoring content cannot undo current permissions. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 43 — Build a container that starts predictably

Package inference and ingestion as reproducible, independently runnable commands.

### Session A — Start and inspect (60 minutes)

Add a multi-stage Dockerfile, dependency lock, `.dockerignore` and nonroot runtime user. Download/pin inference model artifacts during a controlled build or fetch them from a versioned store; production startup must not silently download a mutable “latest” model. Record model license and checksums. Exclude source secrets, training outputs and local environments.

### Session B — Build or change (60 minutes)

Build and run the API container with the local database, then run the ingestion entrypoint as a separate container. Configure CPU/memory from measured cold-start use. Add process liveness and local-dependency readiness: a provider outage should not trigger endless container restarts. Handle SIGTERM by stopping new work and allowing bounded in-flight requests to drain.

### Session C — Run and verify (60 minutes)

From a clean checkout/environment, rebuild and run migration→ingestion→API→smoke tests. Kill the API mid-request and check restart behavior. Block model-download network access after the artifact is available and ensure startup remains reproducible. Capture image digest, architecture, model hashes and startup time.

**Save:** Dockerfile, reproducible image, readiness behavior and container smoke results.

**Move on when:** API and ingestion run from the same immutable build with separate entrypoints and no embedded credentials. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 44 — Provision a small AWS staging environment

Create one explicit cloud route rather than choosing among multiple platforms.

### Session A — Start and inspect (60 minutes)

Read [AWS prerequisites and costs](../guides/production-aws.md#before-you-provision). Use a sandbox account, one region with your chosen Bedrock model available, an existing domain/subdomain and an ACM certificate. Inventory expected charges for ALB, RDS, tasks, egress/NAT or endpoints and model calls. Configure billing alerts; alerts are not hard spending caps. Set task/output/request limits and a teardown deadline before `terraform apply`. No cloud resources are created by reading this course.

### Session B — Build or change (60 minutes)

Create the Terraform resources in the guide's [provisioning order](../guides/production-aws.md#provisioning-order): state/locking, VPC/subnets/security groups, private RDS, S3 source/artifact buckets, ECR, CloudWatch, Secrets Manager, Cognito and IAM roles. Enable encryption and required access controls. Use local CLI SSO credentials for bootstrap, never commit keys. Validate and inspect the plan, then apply this first infrastructure slice.

### Session C — Run and verify (60 minutes)

Run migrations/import through a one-off Fargate task in the private network after the task definition is ready; prepare its command/config now and finish execution next week. Verify the database has no public endpoint exposure, bucket objects are not publicly readable, and only the intended task security group can reach the database. Save resource IDs and a dry-run teardown plan. If provisioning consumes the budget, resume here; do not add paid services to catch up.

**Save:** `infra/terraform/` first slice, reviewed plan, cost inventory and resource-access checks.

**Move on when:** foundational resources exist in the sandbox with a documented network/identity model. API service deployment follows next week. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 45 — Deploy a real authenticated staging request

Complete the first AWS deployment with real inference and persistent retrieval.

### Session A — Start and inspect (60 minutes)

Build and push the tested image to ECR, recording its digest. Implement the Bedrock Converse adapter in `app/generation.py` using the guide's example and your selected model/inference-profile ID. First run a bounded request from a local authorized CLI session and verify timeout/usage/error mapping. This provider change requires evaluation; it is not equivalent to the local model.

### Session B — Build or change (60 minutes)

Complete Terraform for ECS/Fargate task definition/service, HTTPS ALB with `ip` target group, ACM listener and DNS. Put tasks and RDS in private subnets, allow task ingress only from the ALB, and provide documented outbound connectivity for ECR/logs/S3/Bedrock. Grant the execution role image/log/secret access and the task role only application AWS actions. Run migration and ingestion as one-off tasks, then start the API against the approved snapshot.

### Session C — Run and verify (60 minutes)

Use Cognito sign-in to obtain a real access token. Call `POST /answer` through HTTPS; verify q02 returns a real generated answer with authorized citations and a release/request ID. Try absent, expired and wrong-group tokens; inspect sanitized CloudWatch traces. Run evaluation against staging using that same identity boundary, label Bedrock results separately, and keep the endpoint restricted to the small test scope until gates pass.

**Save:** Deployed HTTPS staging endpoint, real-token tests, image/release IDs and cloud evaluation.

**Move on when:** an authenticated request crosses ALB→API→authorized database retrieval→Bedrock and an unauthorized request is rejected. If the hour ends first, keep your current work and resume the unfinished step next session.

## Next step

Continue directly to [Module 8](Module_08.md). It adds controlled releases, monitoring, load checks, recovery and the final production-style rollout.

## Reference while building

A deployable RAG release is the combination of code/image, dependency lock, source snapshot, chunking/embedding revision, retrieval config, prompt, generator model, optional learned artifacts and current access policy. Version them together; code-only rollback may not restore answer behavior.

The API serves a validated active snapshot. Ingestion writes a candidate snapshot independently, validates it, then promotes one pointer. Updates, deletion and permission revocation need different semantics: a previous content snapshot cannot restore access that has since been revoked.

Liveness measures whether the process is alive; readiness measures whether it can accept work with its required local state. Answer quality needs separate canary/evaluation cases. Provider outages need timeouts, bounded retries and controlled failures, not restart storms.

Build once and promote an immutable image digest. Separate CI federation, task execution and application task roles. Record migrations and model/provider changes as releases; rerun quality checks when the effective configuration changes.

See the [AWS implementation guide](../guides/production-aws.md) for resource order, identity, storage, provider integration, deployment checks and official references.
