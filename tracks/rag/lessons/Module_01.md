# Module 01 — Diagnose a failing knowledge assistant

Weeks 1–6 · three hours per week · software-engineering experience assumed.

## Where to start

If you have read the [RAG introduction](00-rag-introduction.md), start at **Week 1, Session A** below. You do not need to read this entire module first. The [investigation brief](../FIRST_INVESTIGATION.md) explains the scenario; this page is the ordered set of instructions.

Follow one session at a time. Each has a purpose, numbered actions, an output and a completion check. Stop after 60 minutes and record your next unfinished step. Continue there next time; these are time budgets, not deadlines. Reading, setup and debugging all count.

For this module, you are investigating **retrieval**, not building a complete RAG application. Documents are already prepared as JSON. There is no live language model, ingestion service or vector database to configure.

## Prepare your workspace once

If you have not cloned the private repository, use your usual authenticated GitHub workflow:

```bash
git clone https://github.com/nancruz/ai-engineering-lab.git
cd ai-engineering-lab
```

If it is already cloned, open that checkout. From its root, create a place for your work:

```bash
mkdir -p projects/knowledge-assistant/experiments/module-01
python3 --version
```

Python 3.10 or later is sufficient for this module. No package installation or API key is required. Create a Markdown file named `notes.md` inside that experiments directory. Put each week's notes under a separate heading. Keep the supplied lab unchanged until an exercise specifically asks for an implementation.

**All commands below run from the repository root**, unless explicitly stated otherwise.

## Know the four files you will use first

| File | What it contains | How you use it |
| --- | --- | --- |
| [dev.json](../lab/data/dev.json) | Development questions and reference labels | Read a question and its user context; later compare your evidence labels with the supplied labels. |
| [corpus.json](../lab/data/corpus.json) | Fictional company documents | Find the actual text supporting an answer and check its metadata. |
| [evaluate.py](../lab/evaluate.py) | Runner for retrieval and evaluation | Execute it to save ranked search results; you do not need to modify it in week one. |
| [retrieval.py](../lab/retrieval.py) | Search methods, eligibility rules and metric functions | Read it when diagnosing behavior in weeks two and three. |

In `dev.json`, `query` is the user's question, `role` is their access role, and `current_only` tells the system whether archived documents must be excluded. `relevant` lists the supplied reference evidence IDs; `expected` says whether an answer is supported or the system should abstain. The remaining fields organize evaluation cases.

In `corpus.json`, `id` identifies a document, `text` contains its evidence, `status` distinguishes current from archived documents, and `roles` lists permitted readers.

**Learning limitation:** the reference labels are visible in the question file. Try selecting evidence from the document text before checking `relevant` and `expected`. If you already saw them, record that; this is guided practice, not a blind assessment. Do not inspect `heldout.json` during this module.

## Week 1 — Understand and inspect

### Session A — Understand the task (60 minutes)

**Purpose:** connect the RAG introduction to the actual files.

1. Read the introduction if you have not already. If you have, count that work as completed; do not repeat it.
2. Complete workspace setup above and open the two JSON data files.
3. In your notes, write 3–5 sentences describing what ingestion does before questions arrive and what query-time processing does for an individual request. Use a runbook update and a question about that runbook as examples. No code implementation is required.
4. Add one sentence explaining the starter lab's scope: it searches already prepared documents and evaluates retrieval; it does not generate an answer.

**Output:** a short explanation in `notes.md`.

**Done when:** you can distinguish preparing searchable knowledge from searching it for a user. If that is still unclear, revisit the introduction's “Two workflows” section before continuing.

### Session B — Decide what good evidence looks like (60 minutes)

**Purpose:** establish an expected result before inspecting the search output.

1. Find **q02** in [dev.json](../lab/data/dev.json): “What is the current production catalog timeout?”
2. Find the two “Catalog request timeout” documents in [corpus.json](../lab/data/corpus.json).
3. Work through this example: `timeout-v2` supports an 800-millisecond deadline, is current and permits engineers. `timeout-v1` says 3,000 milliseconds but is archived. For this current-policy question, accept `timeout-v2`.
4. Copy the table below into your notes. Fill the remaining rows by reading the corpus yourself. Start with q03, then continue in the listed order. Use `[]` if no document provides an authorized answer.
5. Only after writing your reasoning, compare it with `relevant` and `expected`. If they differ, record the discrepancy rather than silently changing your reasoning.

| Question | Your accepted document IDs | Answer supported, or reason to abstain | Why these sources are valid |
| --- | --- | --- | --- |
| q02 — current catalog timeout | timeout-v2 | 800 milliseconds | Current; engineer access; directly answers the question |
| q03 — trace retention | Fill in | Fill in | Check text, status and roles |
| q13 — staging and production rollback | Fill in | Fill in | Check whether several sources are needed |
| q14 — capacity question as engineer | Fill in | Fill in | Check access permissions |
| q16 — ORION approval | Fill in | Fill in | Check whether evidence exists at all |
| q17 — “undo a bad stream-service rollout” | Fill in | Fill in | Look for meaning, not only matching words |

**Output:** evidence labels and reasons, starting with the worked example and q03.

**Done when:** each completed row explains why its evidence is acceptable. Aim for all six within the session; if time runs out, finish them next session before inspecting those questions' search outputs. Two carefully reasoned rows are a better starting point than six copied labels.

### Session C — Compare expectations with retrieval (60 minutes)

**Purpose:** see what the supplied search actually returns.

1. After labeling, run this from the repository root:

```bash
python3 tracks/rag/lab/evaluate.py --mode faulty --split dev --k 3 --out projects/knowledge-assistant/experiments/module-01/faulty.json
```

2. Open the generated `faulty.json`. Under `rows`, find `id: "q02"`.
3. Read `retrieved`: this list contains document IDs and scores in rank order. Look up those IDs in the corpus. A score indicates the retriever's match strength, not a probability of correctness.
4. Compare with your expected `timeout-v2`. Was it found? Was the archived version also returned? Which came first?
5. Repeat for the questions you labeled. Inspect `unauthorized` and `stale`, which list returned documents violating the request's access or freshness conditions. Ignore numerical metrics until week two.
6. Record results using this table:

| Question | Expected IDs | Retrieved IDs in order | Observation | Possible failure stage |
| --- | --- | --- | --- | --- |
| q02 | timeout-v2 | Copy from your run | Missing evidence, stale evidence, or no observed issue? | Retrieval/filtering, or no observed issue |

**Output:** saved run and a comparison table. End with: “The next thing I would investigate is ___ because ___.”

**Done when:** you can point to one observed behavior and explain its consequence for a future generator. Do not invent a failure if a question succeeds. This run does not demonstrate any actual LLM behavior.

**Next:** Week 2, Session A. You do not need an incident memo or release decision yet.

## Week 2 — Measure retrieval

### Session A — Calculate before coding (60 minutes)

1. Read “Week 2 reading — evidence and retrieval metrics” later on this page.
2. In your notes, use relevant IDs `[A, B]` and returned IDs `[X, A, Y]` at k=3. Calculate Recall, Hit, RR and complete labeled-set coverage.
3. Repeat for `[A, B, X]` and `[X, Y, Z]`.
4. Average the three RR values to calculate MRR. Explain why this is a collection-level metric.
5. For a case with no relevant documents, explain why this harness reports null metrics rather than treating recall as zero.

**Output/check:** a table of hand calculations. Compare the first row with the worked example below; resolve discrepancies before coding.

### Session B — Validate the implementation (60 minutes)

1. Open [retrieval.py](../lab/retrieval.py), find `metrics`, and trace the first example through the function.
2. Open [test_retrieval.py](../lab/test_retrieval.py) to see how the supplied tests call it.
3. Add your own test file beside it, named `test_my_metrics.py`. Test the two additional ranked lists from Session A using your hand-calculated expected values. Include an empty-evidence case. You are adding verification, not replacing the reference algorithm.
4. Run:

```bash
python3 -m unittest discover -s tracks/rag/lab -p 'test*.py' -v
```

**Output/check:** passing tests whose expected values you can explain independently. Investigate a failure; do not change expectations just to match the implementation.

### Session C — Interpret scores (60 minutes)

1. In your saved run, find q13 and compare its retrieved IDs with the two reference evidence IDs.
2. Recalculate that row's metrics and compare them with the JSON.
3. Explain how Hit can equal 1 while required evidence is missing.
4. Now imagine two documents repeat the same complete answer. Explain why finding only one can be sufficient despite incomplete labeled-set coverage.

**Output/check:** a short explanation of what each score measures and what it cannot establish about answer quality.

**Next:** Week 3. Keep labels and corpus unchanged for the next comparison.

## Week 3 — Test metadata filtering

### Session A — Locate the policy (60 minutes)

1. Read `eligible` and `retrieve` in [retrieval.py](../lab/retrieval.py).
2. Trace q02 through the role and status checks. Then compare q14 and q15: the question text is the same, but the reader's role differs.
3. Write the eligibility rule in plain English. Explain why an archived document may be eligible for a historical request but not a current-only request.

**Output/check:** identify the code that the deliberately faulty mode bypasses. Distinguish permission filtering from ranking.

### Session B — Change one factor (60 minutes)

Run the filtered keyword mode against the same questions and corpus:

```bash
python3 tracks/rag/lab/evaluate.py --mode keyword --split dev --k 3 --out projects/knowledge-assistant/experiments/module-01/keyword.json
```

Compare with `faulty.json`. Both use word overlap; the important change is document eligibility. Inspect the six selected rows and the summary's `queries_with_unauthorized`, `queries_with_stale` and `mean_metrics`.

**Output/check:** a before/after table showing both access/freshness violations and retrieval scores. Record unchanged scores too.

### Session C — Explain the limits (60 minutes)

1. Explain which changes are attributable to filtering.
2. Inspect q17 and q18 for paraphrase behavior. Did filtering improve their evidence retrieval?
3. Describe one remaining problem and one suitable next experiment. Do not assume every metric must improve.

**Output/check:** a paragraph distinguishing metadata-policy failures from relevance-ranking failures.

**Next:** Week 4; keep the filtered keyword run as the comparison baseline.

## Week 4 — Compare ranking methods

### Session A — Understand the comparison (60 minutes)

1. Read the technical lesson at the start of [Module 2](Module_02.md), stopping before its weekly labs.
2. Explain how BM25 uses term frequency, document frequency and document length, whereas this keyword baseline counts shared unique words.
3. Record the comparison controls: same corpus, questions, eligibility policy and k=3.

**Output/check:** state what changes and what stays fixed. Full BM25 implementation work belongs to Module 2.

### Session B — Run BM25 (60 minutes)

```bash
python3 tracks/rag/lab/evaluate.py --mode bm25 --split dev --k 3 --out projects/knowledge-assistant/experiments/module-01/bm25.json
```

Compare `bm25.json` with `keyword.json`. For each question whose ranking changed, record whether Recall or RR improved, worsened or stayed the same. Use per-query values rather than only the aggregate.

**Output/check:** a small comparison table backed by actual document IDs.

### Session C — Make a decision (60 minutes)

1. Record the commands and `corpus_sha256` from both runs; verify that their corpus hashes match.
2. Explain one regression, improvement or unchanged result by inspecting the documents.
3. State whether this dataset justifies switching ranking methods. “No demonstrated improvement” is a valid conclusion.

**Output/check:** a short decision with evidence and the limitation that this is a small fictional dataset. No bootstrap statistics are required yet; those are introduced later.

**Next:** Week 5, which distinguishes search failures from answer failures.

## Week 5 — Diagnose failure stages

### Session A — Read an answer critically (60 minutes)

1. Open [answer_fixtures.json](../lab/data/answer_fixtures.json). These are manually written examples with labels, not generated outputs.
2. Choose one example and look up its cited evidence in the corpus.
3. Identify the claim being made. Does the source support it? Is the source eligible and current for the intended request?
4. Write what you know and what the fixture does not record. Do not assume an unrecorded model input or retrieval trace.

**Output/check:** one claim–evidence comparison, separating a valid citation identifier from actual support.

### Session B — Create diagnostic cases (60 minutes)

In your experiment directory, create `diagnostic-cases.md` with three constructed examples:

1. **Missing context:** the required source exists but is absent from the supplied context.
2. **Wrong version:** context contains an archived policy for a current-policy question.
3. **Unsupported claim:** context contains the correct policy but the written answer invents a value.

For each, record question, reader role, supplied document IDs, sample answer, expected behavior and the faulty stage. Label these as constructed examples. Keep them separate from `dev.json`, whose runner evaluates retrieval rather than answer claims.

**Output/check:** three cases with enough evidence for another person to follow your diagnosis.

### Session C — Match repair to cause (60 minutes)

For each case, propose one intervention and a check that would reveal whether it worked. Explain why changing a prompt cannot reliably substitute for missing evidence or access enforcement.

**Output/check:** a cause → intervention → verification table. These are diagnostic proposals, not measured model improvements.

**Next:** Week 6, where you assemble the final investigation.

## Week 6 — Review and decide

### Session A — Choose a bounded investigation (60 minutes)

1. Revisit the comparisons from weeks three and four.
2. Choose one unresolved issue you can investigate within the remaining two sessions.
3. Write a hypothesis, a proposed change and a success check before making the change. Use the [experiment template](../EXPERIMENT_TEMPLATE.md).
4. If the evidence does not justify another change, choose an explicit no-change decision and identify the evidence needed next.

**Output/check:** one scoped experiment or a justified no-change proposal. Do not start a new end-to-end application.

### Session B — Attempt and verify (60 minutes)

1. If implementing a change, copy the lab into your project directory so the supplied baseline remains reproducible. Keep its relative `data/` structure intact.
2. Make the targeted change and run its tests and development evaluation from that copy.
3. Save the exact command, code revision and result. Compare against the appropriate unchanged baseline.
4. If incomplete, record an inconclusive result and resume next session rather than claiming success. For a no-change decision, use this session to verify the evidence supporting it.

**Output/check:** a reproducible result, including regressions, or an evidence-backed decision to retain the baseline.

### Session C — Write the final memo (60 minutes)

Write a one-page memo covering:

- The symptom and affected question IDs.
- Expected evidence versus retrieved evidence.
- The first observed failure stage and any contributing stages.
- What filtering changed in week three, and what ranking changed in week four.
- Your final experiment or no-change decision.
- Measured outcomes, limitations and a release/no-go recommendation.

Support a recommendation with retrieval evidence only. The lab has not established generation quality, enterprise-scale effectiveness or production readiness.

**Done when:** another engineer can reproduce your observations and understand your decision without asking which files or commands you used. Use the review below to check your reasoning, then proceed to [Module 2](Module_02.md).


## Week 2 reading — evidence and retrieval metrics

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


## Final review — after week six

Check that your memo explains why a citation can be real yet support a wrong answer, why a retrieval hit is not complete evidence, how access changes answerability, and why filtering does not necessarily solve paraphrases. Include one successful case as well as failures.

Completion requires reproducible results, independently checked metrics, three distinct failure examples and a defensible decision. A no-go result can demonstrate good engineering judgment.

## Further reading

These are references for deeper study within your time budget, not extra prerequisites:

- https://www.anthropic.com/engineering/contextual-retrieval
- https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html
