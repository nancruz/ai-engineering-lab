# Production implementation guide — AWS

Use with Modules 7 and 8. This is a concrete implementation route and provisioning checklist for the application you build. Terraform, service adapters and workflows are learner implementation tasks; this document does not pretend a tested turnkey infrastructure stack is included.

## Target architecture

| Component | Chosen implementation | Responsibility |
| --- | --- | --- |
| HTTPS entry | Application Load Balancer + ACM + your DNS subdomain | TLS and routing to healthy tasks |
| Identity | Cognito user pool; JWT verification inside the API | Authenticated subject/groups; document ACLs remain application policy |
| Serving | FastAPI container on ECS/Fargate | Bound request, retrieve evidence, build context, call generator |
| Source ingestion | Separate one-off Fargate task from the same build | Parse/chunk/embed/import candidate snapshots |
| Sources/artifacts | Private S3 buckets with versioning/encryption | Permitted source snapshots and immutable model/config artifacts |
| Retrieval persistence | Private RDS PostgreSQL with supported pgvector extension | Snapshot metadata, text, vectors and eligibility predicates |
| Generator | Bedrock Converse-compatible model selected in your region/account | Real generation through the replaceable adapter |
| Images/config/secrets | ECR, explicit task config, Secrets Manager | Immutable images; no embedded credentials |
| Operations | CloudWatch logs, metrics, dashboards and alarms | Sanitized request traces, availability and dependency signals |
| Provision/release | Terraform + GitHub Actions OIDC | Reviewable changes, immutable promotion and rollback |

Start with exact vector retrieval. Local BM25 can operate on the eligible active snapshot; if later moving lexical ranking to PostgreSQL, measure that as a new algorithm rather than claiming score equivalence. Kubernetes, autonomous agents, voice and multiple clouds are outside this RAG production path.

## Before you provision

Prepare these before week 44:

- A sandbox AWS account and a local SSO-authenticated CLI session with provisioning permissions. Runtime roles will have much narrower permissions.
- One region with your intended RDS extension version and Bedrock model/inference-profile access. Check quotas and model terms in that account.
- A controlled DNS subdomain and ACM certificate in the ALB region, validated before HTTPS rollout.
- A container build compatible with the chosen Fargate architecture and measured CPU/memory needs.
- A cost inventory covering task runtime, RDS, ALB, storage/backups/log retention, network/NAT or interface endpoints, image storage, data transfer and model calls. Billing alerts are delayed notifications, not hard spending caps. Bound task scaling, requests, output tokens and test duration separately.
- A teardown plan and checkpoint showing which resources will remain billable after the exercise.

No resource is created by these instructions alone. When you execute the exercises, inspect plans and costs in your own account. If you cannot fund cloud practice, complete the same container/database/security drills locally and label cloud deployment unfinished rather than reporting production deployment experience.

## Provisioning order

Implement resources in small Terraform slices under `projects/knowledge-assistant/infra/terraform/`:

1. **Bootstrap state:** use an encrypted remote state backend with locking supported by your selected Terraform/backend version. Restrict access; state may contain secrets. Keep staging and production-style environment states distinct. Do not commit `.tfstate` or secret tfvars.
2. **Networking:** VPC, public ALB subnets across appropriate Availability Zones, private application/database subnets, routes and security groups. Allow ALB→app port and app/job→PostgreSQL; no public database ingress. Decide explicitly between NAT egress and required VPC endpoints. Private subnets without working outbound/service endpoints cannot pull images, read secrets, ship logs or call Bedrock.
3. **Data/artifacts:** RDS PostgreSQL with the supported pgvector extension, encrypted storage, backups and restricted credentials; private/versioned S3 buckets for sources/artifacts. Configure retention according to the exercise budget and recovery objective. Create a migration role separately from the runtime query role where practical.
4. **Build/runtime identity:** ECR, log groups, Secrets Manager, task execution role and application task role. Execution role covers pulls/log shipping and injected secrets; task role covers actual application calls such as Bedrock/S3, restricted to intended resources. Include KMS rights only as required by configured keys.
5. **User identity:** Cognito user pool, app client/hosted sign-in and test groups. Never use the client-provided question role as the source of truth.
6. **Tasks:** task definitions referencing an immutable image digest and explicit environment/config/secrets. Include separate API, migration and ingestion commands. Set CPU/memory limits, health checks and shutdown grace periods from measured startup/request behavior.
7. **Initial data:** launch one-off migration and ingestion tasks in the private network. Validate candidate data and promote an approved index snapshot. Store operation logs and manifest IDs. The API does not perform schema migrations or full ingestion on every startup.
8. **Serving:** HTTPS ALB, `ip` target group for Fargate/awsvpc, readiness path, ECS service, DNS and ACM listener. Restrict task ingress to the ALB group. Enable HTTP→HTTPS redirect if exposing HTTP. Restrict pilot access and require valid app tokens before answer processing.
9. **Operate:** alarms/log retention, bounded autoscaling, CI federation, evaluation/smoke gates, rollback pointer and backup-restore tests. Promote the same image digest to the separate production-style environment after staging checks pass.

For each slice: `terraform fmt -check`, `terraform validate`, `terraform plan`, review resource changes, then apply the saved approved plan. Follow these with the specific network/service checks in the weekly lesson. CLI switches and provider resources follow the pinned versions you record in the project; do not paste a plan from an unrelated environment.

## Identity boundary

Use a maintained JWT library with a configured trusted issuer and JWKS endpoint. Verify signature against the appropriate trusted signing key and algorithm, issuer, expiry, `token_use=access`, correct Cognito `client_id` and required scopes. Do not assume an access token uses the same audience convention as an ID token; apply the documented checks for the actual token type. Reject tokens from another pool/client, expired tokens and attempts to change the verification algorithm.

Map validated subject/groups to your document access policy on the server. Missing/unknown groups grant no privileged access. Cache keys include effective authorization scope and scope version; do not log raw tokens. JWT groups remain a snapshot of token issuance, so immediate revocation requirements need a current server-side revocation/scope check and cache invalidation, not waiting indefinitely for expiry.

Development test issuers/keys must be disallowed outside explicit development mode. Add tests observing the actual context passed to the generator, including cache hits and parent-chunk expansion. Reject unauthorized content before it reaches prompts, public citations, logs or cached outputs.

## Storage and index layout

Create migrations rather than handwritten changes in the console. A minimal model has:

- `snapshots`: snapshot ID, state (building/validated/active/retained), corpus/config hashes and source manifest location.
- `sources`: snapshot ID, stable source ID/version, status, checksum and ACL metadata.
- `chunks`: snapshot ID, source ID/version, stable chunk ID, text, offsets, heading metadata, allowed roles, status, model revision and vector.
- `active_release`: one pointer to an approved manifest and index snapshot, updated transactionally.
- `revocations/tombstones`: current source/access prohibitions and event-version ordering independent of historical content retention.

Declare `vector(n)` using the actual encoder dimension. Create a separate embedding/index version if model or dimension changes; do not mix incompatible embeddings. The runtime database role should not own migration permissions.

Example shape for exact authorized vector retrieval (adapt to your actual schema, use bound parameters and the pgvector driver adapter):

```sql
SELECT chunk_id, source_id, text, embedding <=> %(query_vector)s AS distance
FROM chunks
WHERE snapshot_id = %(snapshot)s
  AND allowed_roles && %(trusted_roles)s::text[]
  AND (NOT %(current_only)s OR status = 'current')
  AND NOT EXISTS (
    SELECT 1 FROM revocations r
    WHERE r.source_id = chunks.source_id AND r.blocks_access
  )
ORDER BY embedding <=> %(query_vector)s, chunk_id
LIMIT %(k)s;
```

This is a teaching query shape, not the complete tenant/ABAC schema. Never interpolate roles/vector strings into SQL. Test relevant scope and deletion behavior before deploying. If a later ANN index changes filtered candidate recall, compare against this exact eligible baseline; increasing k or applying an access filter after top-k is not an automatic fix.

Build candidate snapshots separately, validate, then promote the pointer. Bind a request to one snapshot so its retrieval/context/citations stay consistent. Ingestion duplicates and out-of-order events use version comparisons and idempotent operations. Rollback may restore content, but never reverse a current access revocation or deletion requirement.

## Bedrock generator adapter

Install a pinned boto3/botocore pair in the project environment and use the default credential chain locally (SSO) and the task role in ECS. Select a Converse-compatible model or inference-profile ID actually available to your region/account; no universal model identifier is hardcoded here. Validate IAM rights against the model/profile resources used, including any required regional inference destinations.

A minimal boundary to adapt in your application:

```python
import boto3
from botocore.config import Config

client = boto3.client(
    'bedrock-runtime',
    region_name=settings.aws_region,
    config=Config(connect_timeout=5, read_timeout=60,
                  retries={'mode': 'standard', 'total_max_attempts': 2}),
)
response = client.converse(
    modelId=settings.model_id,
    system=[{'text': system_prompt}],
    messages=[{'role': 'user', 'content': [{'text': user_payload}]}],
    inferenceConfig={'maxTokens': 512, 'temperature': 0},
)
text = ''.join(block.get('text', '')
               for block in response['output']['message']['content'])
```

Here `settings`, `system_prompt` and `user_payload` are provided by your pipeline; this is an adapter fragment, not a standalone script. Reuse your output validator and record raw stop reason, model identity and usage metadata. Check selected-model support for inference settings. Requesting JSON in a prompt does not guarantee valid JSON, and Converse compatibility does not guarantee identical generation across models.

These timeout/retry values are an initial bounded example, not your whole-service deadline. Enforce one overall request budget, avoid nested retry multiplication and test throttling, timeout and nonretryable access errors. A synchronous call's cancellation behavior must be measured; do not assume cancelling an HTTP request cancels billed provider work.

## Release order and rollback

Use one immutable manifest linking image digest, dependency/model hashes, schema revision, index/source snapshot, prompt/config, gate artifact and evaluated provider model/profile. Keep current access policy independent and up to date.

A release job runs deterministic checks→bounded development evaluation/reviews→policy gate→build/publish digest→compatible migrations→deploy staging→authenticated smoke/security checks→promote the same digest. In production practice, provider/index changes also require their own quality checks. Do not build a different image for “production” after evaluating staging.

Rollback selects the previous approved effective release, verifies schema compatibility, updates the service/task and approved content/config pointer, then runs answer and security canaries. A destructive schema change may need forward repair or restored data rather than blindly running a down migration. Test RDS restore separately; a retained old container is not a database backup.

## Definition of deployment completion

You have finished this path when all of these have been exercised, not merely described:

- Authenticated HTTPS requests return real-model answers with authorized traceable evidence.
- Missing/forged/wrong-scope identities fail and negative tests inspect context/cache paths.
- A separate job refreshes a validated index and failure leaves the prior active snapshot intact.
- Clean build/deploy records exact image/config/data/model versions.
- CI blocks a seeded quality/security regression and deploys a valid version through scoped OIDC.
- Logs/dashboard expose a failed request without raw secrets/source bodies.
- Bounded load tests show measured behavior and controlled overload/cost limits.
- A bad prompt/index release is detected and rolled back with quality verification.
- A backup is restored and tested in an isolated environment.
- Teardown includes retained resources that could keep billing.

A successful small training deployment demonstrates these practices on its tested workload. It does not establish universal prompt-injection safety, enterprise-scale quality or multi-year production experience.

## Official implementation references

Checked while revising this course; verify account/region/version specifics when executing:

- [ECS with Application Load Balancer](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/alb.html)
- [ECS IAM role boundaries](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-iam-role-overview.html)
- [Secrets Manager injection into ECS](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/specifying-sensitive-data-tutorial.html)
- [RDS PostgreSQL supported extensions](https://docs.aws.amazon.com/AmazonRDS/latest/PostgreSQLReleaseNotes/postgresql-extensions.html)
- [pgvector query/index behavior](https://github.com/pgvector/pgvector)
- [Cognito JWT verification](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html)
- [Cognito access-token claims](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-the-access-token.html)
- [Bedrock Converse inference](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html)
- [GitHub Actions OIDC with AWS](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws)
