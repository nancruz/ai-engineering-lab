# Module 05 — Train and integrate an evidence-quality model

Weeks 27–32 · 3 hours per week · one evolving knowledge-assistant project.

## Start here

Reuse the actual pipeline traces and evaluation tooling. This is a focused supervised-learning project inside the RAG service, not a generic Python introduction.

**Working result:** A trained, evaluated, versioned evidence gate—or a measured decision to keep the simpler baseline.

Read only the current week's instructions. Use the reference section when a step points to a concept; there are no written theory answers or oral assessments. Demonstrate progress through working code, saved runs, tests and short observations attached to a change.

All shell commands start at the repository root. Paths beginning with `app/`, `tests/`, `artifacts/`, `data/` or `infra/` below mean files **inside** `projects/knowledge-assistant/`. You create these project files as the course progresses; the supplied baseline remains under `tracks/rag/lab/`. See the [project contract](../guides/project-contract.md) for the directory map, interfaces and commands.


## Week 27 — Collect training examples from your pipeline

Create an applied ML dataset: whether selected evidence is sufficient to attempt an answer.

### Session A — Start and inspect (60 minutes)

Export candidate contexts and serving-time features from development runs: retrieval scores, score margins, number of returned sources and question length. Label evidence sufficiency by reading question and context, independently of the generator's confidence. Keep gold evidence counts and support labels out of serving features.

### Session B — Build or change (60 minutes)

Write `app/features.py` and a versioned JSONL dataset with family IDs. Define train/validation/test families before scaling or tuning. Reuse the growing benchmark, but reserve a fresh model-test partition if earlier final cases have been inspected.

### Session C — Run and verify (60 minutes)

Audit a small batch for leaked features and ambiguous sufficiency labels. Evaluate always-answer, always-abstain and a simple score threshold; save answer coverage and unsupported-answer counts. Start small and record actual sample counts instead of claiming production calibration.

**Save:** Feature contract, labeled rows, split manifest and three simple baselines.

**Move on when:** every inference feature can be computed without reference labels or future information. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 28 — Implement a gradient and make it testable

Learn the math through a working numerical check rather than a written derivation.

### Session A — Start and inspect (60 minutes)

Install NumPy. Create `training/logistic_numpy.py` with sigmoid, binary cross-entropy and an analytic gradient for a tiny numeric batch. Read the logistic formulas in the reference immediately before implementing. Use stable loss arithmetic.

### Session B — Build or change (60 minutes)

Implement central finite differences and compare them with your gradient using a fixed batch and epsilon. Add a test for maximum absolute error and a short gradient-descent loop whose loss decreases. Start with float64 and a suitably small tolerance, such as 1e-5 for this controlled fixture.

### Session C — Run and verify (60 minutes)

Run your code, then compare with [math_labs.py](../reference-solutions/math_labs.py). Deliberately flip the gradient sign and ensure the test detects it. Restore it and save the diagnostic output. Generated numeric data tests mechanics, not evidence-gate quality.

**Save:** Independent numerical implementation and a gradient-check test.

**Move on when:** the check detects a real gradient defect and the repaired optimizer lowers loss. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 29 — Train a small evidence gate

Fit and reload a real model on your application features.

### Session A — Start and inspect (60 minutes)

Install scikit-learn. Create a Pipeline containing StandardScaler and regularized LogisticRegression. Split by family, fit preprocessing only on training data and keep model-test rows untouched.

### Session B — Build or change (60 minutes)

Train candidate regularization settings using group-aware validation on the training/development workflow. Save preprocessing with the fitted estimator and feature order. Compare against the score-threshold baseline on the same validation rows.

### Session C — Run and verify (60 minutes)

Add a training/inference feature-order test and a group-overlap test. Save prediction rows including true sufficiency, score and split. If a small dataset yields one-class folds, reduce/fix the split protocol rather than claiming an uncomputed score.

**Save:** Fitted pipeline, valid split checks and baseline comparison.

**Move on when:** the loaded model reproduces saved predictions and no family leaks across the declared partitions. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 30 — Inspect probability errors

Use plotted/aggregated outcomes to avoid trusting an overconfident gate.

### Session A — Start and inspect (60 minutes)

Build reliability bins from validation predictions and report the count in every bin, Brier score and absolute errors. Keep sparse bins visible; a few examples cannot establish calibration.

### Session B — Build or change (60 minutes)

Where validation size permits, trial a simple calibration method on a separate calibration partition. Otherwise keep the raw model and explicitly defer calibration; still generate the reliability report. Do not fit a calibrator on final test labels.

### Session C — Run and verify (60 minutes)

Add a fixture of intentionally overconfident wrong predictions and ensure your report exposes the error. Save actual-model and artificial-fixture reports separately. Use measured limitations when selecting the operating policy next week.

**Save:** Reliability report, diagnostic fixture and retained calibration configuration.

**Move on when:** probability quality is measured on data outside base fitting, or the insufficiency of that evidence is explicit. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 31 — Connect the gate to answer behavior

Make the model change the actual application path.

### Session A — Start and inspect (60 minutes)

On validation data, sweep thresholds and produce answer coverage versus unsupported answers among answered cases. Choose a threshold using your intended risk trade-off before opening model-test predictions.

### Session B — Build or change (60 minutes)

Add the gate between context selection and generation. Below threshold, return an evidence-insufficient abstention. Keep authorization checks earlier and independent. Version the gate artifact and threshold in configuration; support disabling it to restore the baseline.

### Session C — Run and verify (60 minutes)

Test insufficient-context abstention, sufficient-context passage and missing-feature failure. Compare real answering with/without the gate on a fixed development batch. Do not let a high gate score override a permission failure.

**Save:** API gate integration and coverage/risk report.

**Move on when:** the gate can prevent generation, its errors are visible, and it is not mistaken for an access-control boundary. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 32 — Release or reject the learned component

Treat a trained model as a versioned deployment artifact.

### Session A — Start and inspect (60 minutes)

Freeze feature schema, preprocessing, estimator and threshold. Save training/data/config hashes, package versions and validation results in a model manifest. Only load artifacts from your own trusted training pipeline.

### Session B — Build or change (60 minutes)

Reload in a fresh process and evaluate the untouched model-test partition once. Compare with the threshold baseline using counts and family slices. Test feature-schema mismatch and missing-model failure.

### Session C — Run and verify (60 minutes)

Select the learned gate only if its measured benefit warrants it; otherwise retain the simple threshold and archive the experiment. Include the selected artifact ID in your application release manifest. No essay or model-defense interview is required.

**Save:** Reloadable artifact, test result and selected serving configuration.

**Move on when:** a fresh process reproduces the decision and the application can revert to its prior policy. If the hour ends first, keep your current work and resume the unfinished step next session.

## Next step

Open [Module 6](Module_06.md), Week 33.

## Reference — concepts used in the experiments

Use the retrieval system to create a supervised problem: estimate whether the available evidence is sufficient to attempt an answer. Labels must describe evidence sufficiency independently of a model's declared confidence. Candidate features include lexical score, dense score, top-1/top-2 margin, number of distinct supporting sources and query length. Do not use gold relevance counts as serving features. They are known only during labeling and would leak the answer.

A logistic model computes z=wᵀx+b and p=1/(1+exp(-z)). Binary cross-entropy is -[y log p+(1-y)log(1-p)]. Its gradient with respect to weights is Xᵀ(p-y)/n, plus a regularization term if used. Standardize using training statistics only. A finite-difference gradient check compares each analytic component with (L(w+ε)-L(w-ε))/(2ε).

Split by query family or source cluster before feature selection, scaling and tuning. Group cross-validation belongs inside the training/development workflow. Keep a final test partition for one frozen comparison. Begin with always-answer, always-abstain and a simple score threshold; a learned model must justify its complexity.

Discrimination and calibration differ. A score can rank sufficient evidence well while overstating its probabilities. Inspect reliability bins with sample counts and Brier score, while remembering Brier also reflects discrimination. Calibrate only on data not used to fit the base model. With a small benchmark, avoid fitting a flexible calibrator on a handful of examples.

Choose an operating threshold using error costs: unsupported answers may be more costly than unnecessary abstentions. Report coverage (fraction answered) and risk among answered questions. A system abstaining on everything has no useful coverage. A gate is a fallible quality mechanism, not an authorization boundary.

## Worked example

Two systems both answer 70% of questions. One makes 3 unsupported answers out of 70, the other 12. Coverage alone hides the difference. Compare risk at comparable coverage, with absolute counts. Do not choose a threshold on the final test set and report the result as an unbiased deployment estimate.


## Primary references

- https://scikit-learn.org/stable/common_pitfalls.html
- https://scikit-learn.org/stable/modules/calibration.html
