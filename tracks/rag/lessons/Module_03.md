# Module 03 — Build ingestion, context and reliable answer generation

Weeks 14–19 · 3 hours per week · one evolving knowledge-assistant project.

## Start here

Use the API and selected retrieval config from Module 2. Reuse your real generator; this module expands the data and hardens the pipeline.

**Working result:** A rebuildable ingestion pipeline with traceable chunks, bounded context and reviewed real-model answers.

Read only the current week's instructions. Use the reference section when a step points to a concept; there are no written theory answers or oral assessments. Demonstrate progress through working code, saved runs, tests and short observations attached to a change.

All shell commands start at the repository root. Paths beginning with `app/`, `tests/`, `artifacts/`, `data/` or `infra/` below mean files **inside** `projects/knowledge-assistant/`. You create these project files as the course progresses; the supplied baseline remains under `tracks/rag/lab/`. See the [project contract](../guides/project-contract.md) for the directory map, interfaces and commands.


## Week 14 — Ingest longer source documents

Replace tiny pre-parsed fixtures with an ingestion pipeline you own.

### Session A — Start and inspect (60 minutes)

Choose a small permitted Markdown documentation set, retain its source URLs/license and copy an immutable snapshot into `data/sources/`. Aim for 10–20 substantive pages over the module, starting with three today. Add a manifest containing source ID, version, checksum, status and ACL.

### Session B — Build or change (60 minutes)

Create `app/ingest.py`. Parse headings and text; implement deterministic fixed-window chunks with source/version/start/end offsets. Use character offsets for reconstruction and label the window unit explicitly. Do not pretend characters equal model tokens. Write chunks to a versioned artifact directory.

### Session C — Run and verify (60 minutes)

Reconstruct each chunk from its original text offsets. Test stable IDs on unchanged content and changed IDs/version on edits. Add three source-backed questions from the longer documents, including a condition whose meaning spans a potential boundary.

**Save:** Permitted source snapshot, ingestion command, chunks and reconstruction tests.

**Move on when:** you can rebuild the same chunk artifacts without manually editing the index. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 15 — Keep conditions with their instructions

Compare chunk boundaries on the same actual documents.

### Session A — Start and inspect (60 minutes)

Inspect your boundary-sensitive cases. Add a short fixture containing a production rule and a different staging exception if your source set lacks one. Keep it clearly fictional and separate from imported documentation.

### Session B — Build or change (60 minutes)

Implement heading-aware segmentation carrying the heading path into every chunk. Preserve the fixed-window baseline. Re-embed only changed chunks. Keep the retrieval model/config fixed while changing segmentation.

### Session C — Run and verify (60 minutes)

Run the same questions against both chunk sets. Inspect whether the decisive condition reaches context, not only whether the parent document is retrieved. Aggregate chunk results to document IDs for comparisons using old document-level labels.

**Save:** Two chunk manifests and boundary-regression tests.

**Move on when:** a test reproduces condition loss in the weaker segmentation and verifies its chosen repair. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 16 — Pack bounded context

Make evidence selection explicit before the model request.

### Session A — Start and inspect (60 minutes)

Capture your pipeline's exact current context and model input count where available. Set an input budget that leaves room for system instructions, question and output. Use the selected model's tokenizer or provider token-count interface; otherwise label an estimate and use conservative limits.

### Session B — Build or change (60 minutes)

Implement `app/context.py`: deduplicate overlapping evidence, preserve source IDs, add bounded parent expansion and stop at the budget. Return selected and dropped chunk IDs plus the selection reason. Recheck eligibility after any parent expansion.

### Session C — Run and verify (60 minutes)

Run a multi-source question, a duplicate-heavy query and an overflow fixture. Check required facts retained in the actual sent context. Test deterministic selection and no dropped citation metadata. Do not silently truncate the final prompt string.

**Save:** Context builder, token/estimate records and three boundary tests.

**Move on when:** you can inspect why each passage reached or missed the generator. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 17 — Strengthen the generator adapter

Turn the first model call into a replaceable application component.

### Session A — Start and inspect (60 minutes)

Keep the real local provider working. Define `generate(messages, settings)` returning structured answer plus provider metadata. Add model ID, prompt version, timeout, output limit and usage where available. Inspect the [first-model guide](../guides/first-model.md) for the alternative Bedrock boundary.

### Session B — Build or change (60 minutes)

Version the prompt as a file, validate output shape and citation membership, and keep semantic support review separate. Add bounded retries for transient failures with a total request deadline; do not retry malformed output indefinitely. Store provider errors as errors.

### Session C — Run and verify (60 minutes)

Run 5–10 development questions with exact evidence and output recorded. Inject timeout, invalid JSON and unknown citation IDs using test doubles. Confirm a non-retryable error does not start another paid/model request.

**Save:** Provider interface, versioned prompt and real/model-double results clearly distinguished.

**Move on when:** providers can be replaced without changing retrieval or API response contracts. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 18 — Build a claim review workflow

Evaluate answer quality from actual outputs rather than from fluency.

### Session A — Start and inspect (60 minutes)

Export factual claims from the stored answers into `artifacts/reviews.csv`: query ID, claim, cited chunk IDs, support label, authority label and reviewer note. Start with five answers; split compound claims when different evidence supports each part.

### Session B — Build or change (60 minutes)

Add a review-import command and report counts of supported, contradicted and unsupported claims, plus correct/incorrect abstentions. Preserve the denominator and distinguish unanswered questions from answered claims. Keep the review tied to prompt/model/index IDs.

### Session C — Run and verify (60 minutes)

Use the manual [answer fixtures](../lab/data/answer_fixtures.json) as labeled examples to test report logic; mark them as fixtures. Run the report separately on real outputs and inspect one citation that points to a real source but fails to support its attached claim.

**Save:** Review CSV, report command and tested aggregation.

**Move on when:** answer-quality counts trace to actual claims and review labels, not retrieval scores alone. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 19 — Exercise updates and conflicts

Test real source changes through ingestion to the answer.

### Session A — Start and inspect (60 minutes)

Copy the source snapshot into a new version. Edit one harmless policy value in a fictional document, archive its prior version, and create a historical question. Record the intended current/historical authority rules in configuration.

### Session B — Build or change (60 minutes)

Rebuild the new index, answer current and historical questions, and preserve the exact context for each. For unresolved same-authority conflicts, return a conflict/insufficient-evidence response rather than merge incompatible instructions. Apply eligibility before generation.

### Session C — Run and verify (60 minutes)

Repeat after restoring the previous snapshot. Compare fixed-window versus repaired segmentation for one failure while keeping generator/config fixed. Save current, historical and conflict cases as regression tests for deployment later.

**Save:** Versioned source refresh and end-to-end authority/conflict cases.

**Move on when:** the API reflects deliberate source-version changes and can reproduce the old behavior from an old snapshot. If the hour ends first, keep your current work and resume the unfinished step next session.

## Next step

Open [Module 4](Module_04.md), Week 20.

## Reference — concepts used in the experiments

Chunking decides what evidence can be retrieved and what meaning survives segmentation. Fixed windows are a reproducible baseline, but splitting a prerequisite from an action can change the interpretation of a runbook. Heading-aware chunks preserve structure; parent-child retrieval uses small retrieval units and expands their surrounding context. Overlap increases storage and duplicate evidence, and can inflate naive metrics if sibling chunks are counted as independent successes.

Keep stable source IDs, version IDs and offsets on every chunk. Evaluate both passage relevance and coverage of distinct required facts. Aggregate to source-document IDs when comparing with document-level labels. A chunk-ID change should not accidentally redefine the test target. Context packing must respect token budgets and provenance, not merely concatenate the first k results.

Generation is conditional on a prompt, question and context. Low sampling temperature does not guarantee factuality or identical results across provider revisions. Require an output schema with answer, atomic claims, cited evidence IDs and an abstention reason. Schema validity checks syntax; claim verification checks whether evidence actually supports meaning. Separate these tests.

An answer may be supported by obsolete material and still be wrong for the question. Authority, time and entailment must all be satisfied. When sources conflict, identify the conflict and their scope rather than averaging incompatible instructions. When evidence is insufficient, abstention is a useful system action. A model saying “I am confident” is not an evidence sufficiency measure.

## Worked example

A runbook says “For EU production only, wait 15 minutes before rollback. In staging, rollback immediately.” A chunk beginning at “rollback immediately” loses its environment qualifier. Increasing k may retrieve more text while preserving the ambiguity. A useful intervention retains the heading and condition with the action, then tests both production and staging questions.


## Primary references

- https://www.anthropic.com/engineering/contextual-retrieval
- https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
