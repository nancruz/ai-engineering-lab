# Module 06 — Neural representations, attention and adaptation

Weeks 33–38 · 18 hours total · software-engineering experience assumed.

## Technical lesson

Dense retrieval learns a representation in which relevant query/document pairs should be close. A contrastive objective compares a positive pair with negatives: -log(exp(sim(q,d+)/τ)/Σj exp(sim(q,dj)/τ)). Temperature changes the concentration of the distribution. In-batch negatives are convenient, but a supposedly negative passage may also answer the question. False negatives corrupt the training signal.

A transformer builds contextual representations. Scaled dot-product attention is softmax(QKᵀ/√dk)V. Q, K and V are learned projections of token representations. The matrix has one score per query/key position; masks exclude forbidden positions before softmax. A decoder uses a causal mask; a bidirectional encoder can attend across the input. Attention weights are not automatically a faithful explanation of the model's decision.

Training requires a loss, gradient computation, optimizer step and correct gradient reset. Begin by overfitting a tiny batch to find broken labels, disconnected gradients or shape errors. Compare training and validation curves; falling training loss with worsening validation is evidence of overfitting. Model.eval() changes behaviour such as dropout; disabling gradient tracking is a separate inference concern.

Adaptation is warranted only after diagnosing a representation mismatch. First compare a frozen encoder or reranker. Then fine-tune a small model on labeled query/passage pairs with hard negatives from the baseline. Split by document or query family so the same source facts do not appear on both sides. Keep compute bounded and record initialization, random seeds and model revision.

Fine-tuning retrieval representation does not refresh changing policies in model weights reliably. RAG supplies current evidence; adaptation changes how the model represents or performs a task. Parameter-efficient tuning reduces trainable parameters, not the need for sound labels and evaluation. Generative fine-tuning is an optional extension; a small reranker adaptation is the core exercise.

## Worked example

A batch has query “How do I restore the previous release?” with one rollback runbook as positive and a second equally valid rollback guide as a negative. A contrastive loss pushes an actually relevant passage away. Inspect hard negatives manually and use multi-positive labels or remove ambiguous negatives before trusting a lower loss.

## Six weekly labs

### Week 33 — Representations and loss

- [ ] 60 minutes — Study and reason: Derive cosine similarity and the contrastive objective on a two-pair example.
- [ ] 60 minutes — Implement or experiment: Run a frozen encoder and inspect norms, similarities and truncation.
- [ ] 60 minutes — Test and explain: Find one false-negative candidate and explain its effect on learning.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 34 — Implement attention

- [ ] 60 minutes — Study and reason: Calculate matrix shapes for Q,K,V and a small mask.
- [ ] 60 minutes — Implement or experiment: Run the supplied NumPy attention lab and write a masked version independently.
- [ ] 60 minutes — Test and explain: Test row sums, causal masking and a numerical-stability edge case.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 35 — Train a neural model

- [ ] 60 minutes — Study and reason: Read the training loop and autograd concepts in PyTorch documentation.
- [ ] 60 minutes — Implement or experiment: Implement a small two-layer classifier and deliberately overfit a tiny batch.
- [ ] 60 minutes — Test and explain: Diagnose one injected no-gradient or missing-zero-grad failure.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 36 — Prepare adaptation data

- [ ] 60 minutes — Study and reason: Collect positive pairs and inspect baseline hard negatives.
- [ ] 60 minutes — Implement or experiment: Split by query/source family, preserving multi-positive evidence.
- [ ] 60 minutes — Test and explain: Audit labels and compare the frozen-model baseline.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 37 — Adapt a small reranker

- [ ] 60 minutes — Study and reason: Choose a small compatible model and set a compute/time limit.
- [ ] 60 minutes — Implement or experiment: Fine-tune on a bounded subset and save a checkpoint with data/config metadata.
- [ ] 60 minutes — Test and explain: Compare validation relevance and latency against the frozen model.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 38 — Decide whether to retain it

- [ ] 60 minutes — Study and reason: Freeze adaptation choices and run a held-out comparison.
- [ ] 60 minutes — Implement or experiment: Reload the checkpoint in a fresh process and inspect regressions.
- [ ] 60 minutes — Test and explain: Keep or reject the adaptation using measured benefit, not completion pride.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

## Investigation assessment

Training loss improves every epoch, but held-out retrieval gets worse. Investigate label quality, false negatives, split leakage, learning rate and checkpoint selection before increasing model size.

## Review guidance — attempt first

A tiny-batch overfit test checks whether the training path works; it does not establish generalization. Separate representation limitations from label problems. If adaptation regresses, retaining the frozen model is a legitimate result when supported by a sound experiment.

## Mastery gate

Pass when you explain tensor shapes and gradients, demonstrate a working neural training loop, identify false negatives, and complete a real frozen-versus-adapted comparison. No credit for merely calling a hosted inference endpoint.

## Primary references

- https://docs.pytorch.org/tutorials/beginner/basics/
- https://huggingface.co/learn/llm-course/en/chapter1/1
- https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html
