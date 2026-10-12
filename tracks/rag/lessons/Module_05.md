# Module 05 — Train a model for an evidence decision

Weeks 27–32 · 18 hours total · software-engineering experience assumed.

## Technical lesson

Use the retrieval system to create a supervised problem: estimate whether the available evidence is sufficient to attempt an answer. Labels must describe evidence sufficiency independently of a model's declared confidence. Candidate features include lexical score, dense score, top-1/top-2 margin, number of distinct supporting sources and query length. Do not use gold relevance counts as serving features. They are known only during labeling and would leak the answer.

A logistic model computes z=wᵀx+b and p=1/(1+exp(-z)). Binary cross-entropy is -[y log p+(1-y)log(1-p)]. Its gradient with respect to weights is Xᵀ(p-y)/n, plus a regularization term if used. Standardize using training statistics only. A finite-difference gradient check compares each analytic component with (L(w+ε)-L(w-ε))/(2ε).

Split by query family or source cluster before feature selection, scaling and tuning. Group cross-validation belongs inside the training/development workflow. Keep a final test partition for one frozen comparison. Begin with always-answer, always-abstain and a simple score threshold; a learned model must justify its complexity.

Discrimination and calibration differ. A score can rank sufficient evidence well while overstating its probabilities. Inspect reliability bins with sample counts and Brier score, while remembering Brier also reflects discrimination. Calibrate only on data not used to fit the base model. With a small benchmark, avoid fitting a flexible calibrator on a handful of examples.

Choose an operating threshold using error costs: unsupported answers may be more costly than unnecessary abstentions. Report coverage (fraction answered) and risk among answered questions. A system abstaining on everything has no useful coverage. A gate is a fallible quality mechanism, not an authorization boundary.

## Worked example

Two systems both answer 70% of questions. One makes 3 unsupported answers out of 70, the other 12. Coverage alone hides the difference. Compare risk at comparable coverage, with absolute counts. Do not choose a threshold on the final test set and report the result as an unbiased deployment estimate.

## Six weekly labs

### Week 27 — Define the dataset

- [ ] 60 minutes — Study and reason: Label sufficient versus insufficient evidence for development queries, with written rules.
- [ ] 60 minutes — Implement or experiment: Generate serving-available feature rows and group IDs; exclude gold evidence coverage.
- [ ] 60 minutes — Test and explain: Audit ten rows and compare constant/threshold baselines.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 28 — Derive and implement

- [ ] 60 minutes — Study and reason: Work through the logistic gradient on two examples.
- [ ] 60 minutes — Implement or experiment: Run the supplied NumPy training lab, then implement the same gradient independently.
- [ ] 60 minutes — Test and explain: Use finite differences and compare the independently implemented gradient.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 29 — Evaluate by groups

- [ ] 60 minutes — Study and reason: Read leakage and grouped validation principles.
- [ ] 60 minutes — Implement or experiment: Train a standardized logistic pipeline with group-aware splits and regularization.
- [ ] 60 minutes — Test and explain: Compare a random split with grouped validation and explain any optimistic gap.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 30 — Investigate calibration

- [ ] 60 minutes — Study and reason: Inspect reliability bins and probability error on held-out validation predictions.
- [ ] 60 minutes — Implement or experiment: Compare raw scores with a simple calibrated alternative only if sample size permits.
- [ ] 60 minutes — Test and explain: Report bin counts; reject claims unsupported by sparse data.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 31 — Select a policy

- [ ] 60 minutes — Study and reason: Define costs for unsupported answer versus unnecessary abstention.
- [ ] 60 minutes — Implement or experiment: Choose a threshold on validation data and implement a coverage-risk report.
- [ ] 60 minutes — Test and explain: Stress the policy with missing-source and stale-source cases.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 32 — Ship a model artifact

- [ ] 60 minutes — Study and reason: Freeze features, threshold and model; save preprocessing together.
- [ ] 60 minutes — Implement or experiment: Reload in a fresh process and run the untouched test partition.
- [ ] 60 minutes — Test and explain: Produce a model card with failure slices and rollback conditions.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

## Investigation assessment

A sufficiency classifier achieves excellent validation performance. One feature is “number of gold passages retrieved,” and paraphrases were split randomly. Remove unavailable features, split by family and quantify how the conclusion changes.

## Review guidance — attempt first

The original result is invalid as a serving estimate: the gold feature is unavailable online and intent leakage makes evaluation optimistic. A lower corrected score is progress toward truth. Do not hide it behind a new aggregate metric. If the model fails to beat the score threshold reliably, retain the simpler baseline.

## Mastery gate

Pass when your gradient check succeeds, preprocessing is train-only, evaluation uses groups, the serving feature contract is valid and threshold selection never uses the final test labels.

## Primary references

- https://scikit-learn.org/stable/common_pitfalls.html
- https://scikit-learn.org/stable/modules/calibration.html
