# Module 06 — Train, adapt and serve neural components

Weeks 33–38 · 3 hours per week · one evolving knowledge-assistant project.

## Start here

Keep the service running while doing training in separate scripts. Reuse actual retrieval errors and labeled pairs; the numeric labs are small mechanics checks.

**Working result:** A real adaptation experiment and a reloadable selected inference artifact ready for deployment.

Read only the current week's instructions. Use the reference section when a step points to a concept; there are no written theory answers or oral assessments. Demonstrate progress through working code, saved runs, tests and short observations attached to a change.

All shell commands start at the repository root. Paths beginning with `app/`, `tests/`, `artifacts/`, `data/` or `infra/` below mean files **inside** `projects/knowledge-assistant/`. You create these project files as the course progresses; the supplied baseline remains under `tracks/rag/lab/`. See the [project contract](../guides/project-contract.md) for the directory map, interfaces and commands.


## Week 33 — Inspect representation failures

Prepare adaptation from real baseline errors instead of training without a target.

### Session A — Start and inspect (60 minutes)

Run the frozen encoder/reranker on the development queries. Export positive query–passage pairs and high-scoring wrong passages. Read the representation/loss reference below while inspecting the vector norms and truncation from an actual pair.

### Session B — Build or change (60 minutes)

Create `training/pairs.jsonl` with query ID, source family, passage, relevance and provenance. Manually check hard negatives for alternative valid answers; retain multiple positives instead of forcing one gold source.

### Session C — Run and verify (60 minutes)

Add validation rejecting positive/negative label conflicts for the same pair and split by query/source family. Save the frozen-model performance and actual model revision as the adaptation baseline.

**Save:** Inspected training pairs, negative audit and frozen baseline.

**Move on when:** training negatives are not known alternate answers and validation/test groups remain separate. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 34 — Implement attention and test its behavior

Use executable tensor checks to understand one core neural operation.

### Session A — Start and inspect (60 minutes)

Create `training/attention.py` using NumPy. Implement scaled dot-product attention with stable softmax. Use small Q,K,V matrices whose shapes are visible in the test. Read the attention formula below as implementation guidance.

### Session B — Build or change (60 minutes)

Add a causal mask before softmax. Test that forbidden positions receive zero weight, permitted row weights sum to one and changing a future value cannot affect an earlier causal output. Handle fully masked rows explicitly rather than returning NaNs.

### Session C — Run and verify (60 minutes)

Compare with the small reference after your attempt. Run an unmasked version to demonstrate the future-information test failing, then restore the mask. Keep this toy exercise separate from claims about trained transformer performance.

**Save:** Attention implementation and behavioral tests.

**Move on when:** the tests detect mask placement/normalization mistakes without a written matrix-shape quiz. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 35 — Debug a neural training loop

Build confidence that gradients actually update a model.

### Session A — Start and inspect (60 minutes)

Install PyTorch. Implement a tiny two-layer classifier on a small numeric fixture. Set seeds, call zero_grad, compute loss, backpropagate and step. Read the official training-loop reference only as needed for these operations.

### Session B — Build or change (60 minutes)

Overfit one tiny batch deliberately. Log loss and parameter changes. Add a smoke test that parameters change after a step. Inject a detached loss or a missing gradient reset, observe the symptom and repair it.

### Session C — Run and verify (60 minutes)

Save train/validation curves on a split fixture and reload the checkpoint for inference with eval mode and disabled gradient recording. Record the distinction between this mechanics exercise and the relevance-model adaptation that follows as a note beside the run.

**Save:** Working training loop, reload test and before/after failure trace.

**Move on when:** a seeded neural model trains, the injected defect is observable and inference reload works. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 36 — Build a bounded fine-tuning job

Prepare a small reranker adaptation that fits your hardware budget.

### Session A — Start and inspect (60 minutes)

Use the small cross-encoder already evaluated in Module 2. Pin its revision and set a wall-time/compute budget. Install the compatible trainer dependencies. Start with a tiny pair batch to confirm the training path before requesting any accelerator time.

### Session B — Build or change (60 minutes)

Create `training/train_reranker.py` using the documented CrossEncoder training interface and your relevance-pair dataset. Freeze split identities. Save initialization, labels, hyperparameters, seed and validation scores. Provide a max-step argument for short smoke runs.

### Session C — Run and verify (60 minutes)

Run a few steps, save a checkpoint and reload it to score known pairs. Confirm changed weights and unchanged pair/group membership. If hardware cannot complete a short real run, reduce data/sequence length or explicitly use a budgeted training environment; do not label a frozen model fine-tuned.

**Save:** Training entrypoint, bounded smoke checkpoint and metadata.

**Move on when:** a real training update survives checkpoint reload with a valid split. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 37 — Compare adaptation with the frozen model

Evaluate whether training fixes the diagnosed failures.

### Session A — Start and inspect (60 minutes)

Complete one bounded training run. Select the checkpoint using validation only. Retain the frozen baseline, identical candidate lists and its scores.

### Session B — Build or change (60 minutes)

Rerank those lists with the adapted checkpoint. Compare relevance metrics, exact-ID slices, paraphrases and latency against the frozen model. Save per-query regressions and investigate ambiguous or false-negative labels without changing final test results.

### Session C — Run and verify (60 minutes)

Try at most one justified adjustment within the session budget and rerun validation. Keep configuration histories rather than overwriting the previous result. If adaptation worsens results, retain that as a completed experiment.

**Save:** Real frozen-versus-adapted run pair and checkpoint-selection record.

**Move on when:** the comparison isolates adaptation rather than changing retrieval candidates simultaneously. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 38 — Prepare the selected model for serving

Finish ML experimentation before starting production deployment.

### Session A — Start and inspect (60 minutes)

Freeze the selected configuration and evaluate its untouched model-test families once. Retain the frozen model when no convincing benefit exists. Record the actual sample/family counts and limitations.

### Session B — Build or change (60 minutes)

Package the selected model with artifact hash, tokenizer revision, dependency versions and inference settings. Load it from the application config and measure cold-start memory/time. Do not load large models independently in an unbounded number of API workers.

### Session C — Run and verify (60 minutes)

Restart your API in a clean process, run regression evaluation and verify artifact mismatch fails readiness. Save a release manifest using the selected gate/retriever/reranker; this is the input to production work.

**Save:** Serving model manifest, cold-start results and local release candidate.

**Move on when:** the service runs with explicitly versioned models and previous known-good artifacts remain recoverable. If the hour ends first, keep your current work and resume the unfinished step next session.

## Next step

Use [week 39 consolidation](../ASSESSMENT.md), then start the production sequence in [Module 7](Module_07.md).

## Reference — concepts used in the experiments

Dense retrieval learns a representation in which relevant query/document pairs should be close. A contrastive objective compares a positive pair with negatives: -log(exp(sim(q,d+)/τ)/Σj exp(sim(q,dj)/τ)). Temperature changes the concentration of the distribution. In-batch negatives are convenient, but a supposedly negative passage may also answer the question. False negatives corrupt the training signal.

A transformer builds contextual representations. Scaled dot-product attention is softmax(QKᵀ/√dk)V. Q, K and V are learned projections of token representations. The matrix has one score per query/key position; masks exclude forbidden positions before softmax. A decoder uses a causal mask; a bidirectional encoder can attend across the input. Attention weights are not automatically a faithful explanation of the model's decision.

Training requires a loss, gradient computation, optimizer step and correct gradient reset. Begin by overfitting a tiny batch to find broken labels, disconnected gradients or shape errors. Compare training and validation curves; falling training loss with worsening validation is evidence of overfitting. Model.eval() changes behaviour such as dropout; disabling gradient tracking is a separate inference concern.

Adaptation is warranted only after diagnosing a representation mismatch. First compare a frozen encoder or reranker. Then fine-tune a small model on labeled query/passage pairs with hard negatives from the baseline. Split by document or query family so the same source facts do not appear on both sides. Keep compute bounded and record initialization, random seeds and model revision.

Fine-tuning retrieval representation does not refresh changing policies in model weights reliably. RAG supplies current evidence; adaptation changes how the model represents or performs a task. Parameter-efficient tuning reduces trainable parameters, not the need for sound labels and evaluation. Generative fine-tuning is an optional extension; a small reranker adaptation is the core exercise.

## Worked example

A batch has query “How do I restore the previous release?” with one rollback runbook as positive and a second equally valid rollback guide as a negative. A contrastive loss pushes an actually relevant passage away. Inspect hard negatives manually and use multi-positive labels or remove ambiguous negatives before trusting a lower loss.


## Primary references

- https://docs.pytorch.org/tutorials/beginner/basics/
- https://huggingface.co/learn/llm-course/en/chapter1/1
- https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html

- [CrossEncoder training components and examples](https://www.sbert.net/docs/cross_encoder/training_overview.html)
