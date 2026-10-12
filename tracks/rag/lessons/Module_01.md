# Module 01 — Diagnose a failing knowledge assistant

Weeks 1–6 · 18 hours total · software-engineering experience assumed.

First read [What a RAG system is](00-rag-introduction.md) during week one. Return to the metric explanation below in week two.

## Technical lesson

A RAG system has separable failure boundaries: source data, ingestion, representation, retrieval, context selection, generation and output validation. An answer can be fluent and cite a real document while still being wrong. A citation identifier proves where text came from; it does not prove that the cited passage entails the claim, is current, or is authorized for this user.

Begin by specifying the unit of truth. A question may need one passage, several jointly sufficient passages, a time-specific policy or an explicit refusal. Label supporting evidence independently from the system's retrieved results. Otherwise the benchmark rewards whichever evidence the current retriever happens to find. In this course, document-level labels start the exercise; later you add passage offsets and claim-level support.

### Start with a ranked list

Ask: “How do I roll back staging and production?” Document A explains staging; document B explains production. Both are needed for this question. Documents X and Y are irrelevant.

Suppose the first three unique retrieved IDs are **X, A, Y**. We found one of the two supporting documents, and the first useful result is in position two.

| Metric | What it asks | Result |
| --- | --- | --- |
| Recall@3 | What fraction of the labeled relevant documents did we find? | 1 / 2 = 0.5 |
| Hit@3 | Did we find at least one relevant document? | 1, meaning yes |
| Reciprocal Rank@3 (RR@3) | How early is the first relevant result? | 1 / 2 = 0.5 |
| Complete labeled-set coverage@3 | Did we retrieve every labeled relevant document? | 0, meaning no |

Hit is perfect here even though the production instructions are missing. RR rewards finding the first useful item early; it does not measure whether the remaining evidence was found.

**MRR means mean reciprocal rank across queries.** If three answerable questions have RR values 1, 0.5 and 0, their MRR is (1 + 0.5 + 0) / 3 = 0.5. The per-query JSON uses `rr`; the aggregate summary uses `mrr`.

### The notation, after the example

For question q, G(q) is the set of labeled relevant document IDs. R_k(q) is the first k unique retrieved document IDs, in retrieval order. The intersection G ∩ R_k contains IDs appearing in both; vertical bars mean “number of items.”

- Recall@k = |G ∩ R_k| / |G|, for nonempty G.
- Hit@k = 1 when the intersection is nonempty, otherwise 0.
- RR@k = 1 / rank of the first relevant result within the top k, otherwise 0.
- MRR@k = the mean of RR@k over the declared evaluation population. This harness uses answerable questions.

The supplied `complete` field means every labeled relevant ID was retrieved. It is a diagnostic, not a general answerability score. Relevant documents can be redundant: finding one of two equivalent sources can be sufficient even with recall 0.5. In our staging/production example the documents are complementary, so both are required. Later benchmarks should label required facts and alternative supporting passages to measure evidence sufficiency directly.

Questions with no authorized supporting evidence have an empty G. Recall is undefined there, so report them in an abstention slice, not as failed retrieval. The same words can be answerable for one principal and unanswerable for another. Authorization belongs in the evaluation context.

The offline harness contains a deliberately weak keyword retriever and deterministic answer fixtures. The fixtures reproduce failure shapes; they are not calls to an LLM and cannot establish model quality. This separation lets you debug evidence selection cheaply before integrating a generator. The corpus is fictional engineering material, with conflicts, paraphrases and restricted notes. Its small size supports controlled experiments, not claims about enterprise search performance.

## Worked example

A user asks for the current playback rollback procedure. An archived runbook shares the exact words in the query and scores above a current runbook that says “restore the previous release.” The old document is a good lexical match but wrong evidence for a current-policy question. Three possible interventions are metadata-based current-version selection, semantic retrieval and prompt instructions. Test metadata first: a prompt cannot reliably repair an incorrect authoritative-source selection rule.

## Six weekly labs

### Week 01 — Define the failure

- [ ] 60 minutes — Study and reason: Read the RAG introduction and investigation brief. Explain ingestion and query-time processing without changing code.
- [ ] 60 minutes — Implement or experiment: Annotate six development questions with supporting IDs and expected behaviour before inspecting predictions.
- [ ] 60 minutes — Test and explain: Run the faulty baseline after labeling; compare labels and traces and produce a stage-specific failure table.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 02 — Implement honest metrics

- [ ] 60 minutes — Study and reason: Calculate Recall, Hit and RR on the two-document example, then MRR across three queries. Read [retrieval.py](../lab/retrieval.py).
- [ ] 60 minutes — Implement or experiment: Add independently calculated metric tests. Contrast the existing complete labeled-set coverage field with sufficiency when two sources are redundant.
- [ ] 60 minutes — Test and explain: Demonstrate a case with perfect Hit and incomplete evidence; write why answer quality is not retrieval quality.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 03 — Repair the boundary

- [ ] 60 minutes — Study and reason: Inspect current/version and role metadata. Define what “current” means for present versus historical questions.
- [ ] 60 minutes — Implement or experiment: Compare faulty and current-authorized retrieval using unchanged query labels.
- [ ] 60 minutes — Test and explain: Explain improvements and remaining misses; do not change questions to improve scores.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 04 — Build a baseline

- [ ] 60 minutes — Study and reason: Read the BM25 formula in Module 2. Treat its implementation as provided infrastructure this week.
- [ ] 60 minutes — Implement or experiment: Compare keyword overlap and BM25 with identical eligible documents and k.
- [ ] 60 minutes — Test and explain: Inspect each regression and record corpus/config hashes with results.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 05 — Separate causes

- [ ] 60 minutes — Study and reason: Inspect the supplied [answer fixtures](../lab/data/answer_fixtures.json) and manually assess one unsupported claim with a valid citation. These are labeled examples, not outputs from a live model.
- [ ] 60 minutes — Implement or experiment: Add missing-context, wrong-version and unsupported-claim cases to the development suite.
- [ ] 60 minutes — Test and explain: Assign primary and contributing causes; explain which intervention addresses each.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 06 — Independent review

- [ ] 60 minutes — Study and reason: Close reference notes and choose one unresolved query family.
- [ ] 60 minutes — Implement or experiment: Implement one targeted fix or argue with evidence that no change is warranted.
- [ ] 60 minutes — Test and explain: Write a one-page release decision with examples, metric counts and limitations.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

## Investigation assessment

Incident: “The assistant is confidently giving an obsolete timeout. Search finds the service name, so the team thinks the model is hallucinating.” Reproduce it, identify the first broken boundary and compare two fixes. Do not accept a fix that changes the expected answer to match the old document.

## Review guidance — attempt first

A good diagnosis checks document authority before blaming generation. Filter candidates using trusted metadata for a current-policy question, then inspect retrieval. A paraphrase miss can remain after this repair and needs a different intervention. A referenced but unsupported numerical claim is a generation/validation problem even when retrieval is perfect. Keep those categories distinct in your report.

## Mastery gate

Pass when you reproduce the baseline, independently validate Recall, Hit, RR and aggregate MRR, trace three different failure types and defend a fix without hiding regressions. No unsupported quality percentage based on synthetic answer fixtures.

## Primary references

- https://www.anthropic.com/engineering/contextual-retrieval
- https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html
