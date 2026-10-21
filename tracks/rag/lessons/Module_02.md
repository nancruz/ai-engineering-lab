# Module 02 — Improve retrieval with measured experiments

Weeks 7–12 · 3 hours per week · one evolving knowledge-assistant project.

## Start here

Bring the CLI/API from Module 1 and its development cases. The document IDs and evaluation labels remain stable throughout these comparisons.

**Working result:** A configurable lexical/dense/hybrid/reranked retrieval stack selected by measured quality and latency.

Read only the current week's instructions. Use the reference section when a step points to a concept; there are no written theory answers or oral assessments. Demonstrate progress through working code, saved runs, tests and short observations attached to a change.

All shell commands start at the repository root. Paths beginning with `app/`, `tests/`, `artifacts/`, `data/` or `infra/` below mean files **inside** `projects/knowledge-assistant/`. You create these project files as the course progresses; the supplied baseline remains under `tracks/rag/lab/`. See the [project contract](../guides/project-contract.md) for the directory map, interfaces and commands.


## Week 07 — Make lexical ranking inspectable

Use ranking traces to improve exact-term search before adding another model.

### Session A — Start and inspect (60 minutes)

Open your copied BM25 implementation and the reference explanation below. Add a debug option returning tokenized query, per-document score and top matched terms. Use q02 and an exact service identifier from your project documents as the first inputs.

### Session B — Build or change (60 minutes)

Add tokenizer fixtures covering `catalog-v2`, `ERR_401`, punctuation and the paraphrase q17. Compare shared-word ranking and BM25 using the same eligibility policy and k=3. Preserve the original tokenization as a named baseline.

### Session C — Run and verify (60 minutes)

Add a term-frequency saturation test and an exact-identifier ranking test. Run the development evaluation against each tokenizer. Keep a change only if its affected cases improve without unacceptable regressions; save the per-query ranking differences.

**Save:** Lexical diagnostics, tokenizer tests and a before/after run pair.

**Move on when:** a ranking change can be traced to specific tokens and tested documents. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 08 — Add real embeddings

Add semantic search behind the same retrieval interface.

### Session A — Start and inspect (60 minutes)

Install Sentence Transformers in the project environment. Use `sentence-transformers/all-MiniLM-L6-v2` as the initial small English encoder; read its model card, record revision/license and actual embedding dimension. Apply its documented preprocessing and truncation. Start with exact vector search, not ANN.

### Session B — Build or change (60 minutes)

Implement `app/embeddings.py` and `app/dense.py`. Encode documents once, cache with content hash plus model revision, normalize vectors and rank by cosine similarity. Encode a query using the model's query interface. Apply eligibility before ranking the eligible candidates. Return the same IDs/scores contract as BM25.

### Session C — Run and verify (60 minutes)

Run q17 and q18 and compare with BM25. Test that a changed document/model revision invalidates its cache, normalized nonzero vectors have unit norm, and unauthorized text never enters context. Time cold embedding creation separately from warm query retrieval.

**Save:** Dense adapter, vector cache manifest and actual model run records.

**Move on when:** dense search uses real model vectors and can be swapped into your API without changing its response schema. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 09 — Compare search on useful slices

Prevent a paraphrase improvement from hiding exact-name regressions.

### Session A — Start and inspect (60 minutes)

Create `data/retrieval-cases.jsonl` from development examples, grouped by intent. Add a few exact identifiers and paraphrases using documents you are authorized to use. Label evidence from source text before inspecting candidate results. Keep the small fictional cases as regression fixtures.

### Session B — Build or change (60 minutes)

Implement `app/evaluate.py` to accept named retrieval configs and emit the run schema in the contract guide. Evaluate BM25 and dense on identical question IDs, source snapshot, permissions and k. Add `slice` and `family` to every row.

### Session C — Run and verify (60 minutes)

Produce a per-query CSV with recall, RR, retrieved IDs and elapsed time for both systems. Sort regressions first. Inspect at least one unchanged or worse result; if no regressions occur, retain that observation without manufacturing one.

**Save:** A reusable evaluation command and slice comparison CSV.

**Move on when:** the same harness evaluates both actual retrieval implementations and does not mix corpus versions. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 10 — Combine lexical and dense candidates

Implement hybrid retrieval without treating unrelated score scales as comparable.

### Session A — Start and inspect (60 minutes)

Use fixed candidate depths of 10 per retriever, or all eligible documents if fewer. Inspect overlapping and unique source IDs from the two candidate lists. Read the RRF example below just before implementation.

### Session B — Build or change (60 minutes)

Implement reciprocal rank fusion in `app/hybrid.py` using unique IDs, c=60 and deterministic tie breaking. Test against the supplied `rrf` reference after your implementation. Expose BM25, dense and hybrid as named configuration values.

### Session C — Run and verify (60 minutes)

Evaluate all three at final k=3. Save fusion contributions for q17 and one exact-name query. Check deduplication and ACL invariants. Keep candidate depth fixed during this comparison so its effect is not confused with the fusion rule.

**Save:** Hybrid adapter, fusion tests and comparison results.

**Move on when:** hybrid retrieval is reproducible and every final ID came from an eligible candidate list. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 11 — Rerank a shortlist

Measure whether a second model earns its inference cost.

### Session A — Start and inspect (60 minutes)

Install/load `cross-encoder/ms-marco-MiniLM-L6-v2` with its recorded revision and model-card preprocessing. Capture a fixed hybrid shortlist of up to 10 unique candidates per question. Do not change the shortlist while evaluating reranking.

### Session B — Build or change (60 minutes)

Implement `app/rerank.py` using query/passage pairs and the CrossEncoder interface. Keep source IDs associated with scores. Return the top three after reranking. Measure shortlist recall separately: missing evidence outside the list cannot be repaired here.

### Session C — Run and verify (60 minutes)

Compare quality and stage timings with and without the real reranker. Test duplicate IDs, empty candidates and timeout behavior. If using a fallback, explicitly record that it returned the original hybrid ordering rather than a reranked result.

**Save:** Rerank adapter, fixed-shortlist results and timings.

**Move on when:** you have a measured choice between a simpler pipeline and the extra model. If the hour ends first, keep your current work and resume the unfinished step next session.

## Week 12 — Wire the chosen retriever into the API

Finish with a working change rather than a written algorithm defense.

### Session A — Start and inspect (60 minutes)

Select the retrieval config from the stored comparisons. Save it in `configs/retrieval.json` with encoder/reranker revision, candidate limits and preprocessing. Keep the rejected configs so runs remain reproducible.

### Session B — Build or change (60 minutes)

Load that config in your API. Expose effective config ID in traces, not internal prompts in the public response. Add a smoke command that calls q02 and a paraphrase through the same application path used by HTTP.

### Session C — Run and verify (60 minutes)

Restart from a clean environment and run tests, evaluation and two real answers. Add 3–5 lines beside the config change stating the observed benefit/cost, or retain BM25 if alternatives did not justify switching.

**Save:** Versioned config, integrated endpoint and clean-start smoke result.

**Move on when:** a user request uses the selected retriever and the baseline can still be restored. If the hour ends first, keep your current work and resume the unfinished step next session.

## Next step

Use [week 13 consolidation](../ASSESSMENT.md), then [Module 3](Module_03.md).

## Reference — concepts used in the experiments

Keyword overlap gives every matching term equal weight. BM25 gives rare terms more influence, saturates repeated occurrences and normalizes for length. One common positive-IDF variant is IDF(t)=log(1+(N-df(t)+0.5)/(df(t)+0.5)). Its term contribution is IDF(t)·f(t,d)(k1+1)/(f(t,d)+k1(1-b+b·|d|/avgdl)). Understand each quantity before tuning k1 or b. Exact identifiers often benefit from lexical search; semantic similarity may miss a one-character difference that changes the meaning.

A bi-encoder maps queries and documents independently into vectors. With normalized embeddings, dot product equals cosine similarity. A vector score is not a probability of relevance. Model instructions, query/document prefixes and truncation settings are part of the embedding configuration. Cache vectors using content hash and model revision; changing one requires invalidation.

Approximate nearest-neighbour search trades candidate recall for speed. On this small corpus, use exact search first so representation quality is not confused with index approximation. Compare ANN recall against exact vector top-k later, using a larger public corpus if necessary. It is a different metric from relevance recall against human labels.

Hybrid retrieval combines complementary rankings. Reciprocal rank fusion uses sum over systems of 1/(c+rank). It avoids assuming that BM25 and vector scores are on the same scale. It still needs candidate depth, a fusion constant and deduplication choices. A cross-encoder jointly processes query and passage to score relevance; it is more expensive per pair and usually operates on a shortlist. It cannot recover evidence absent from that shortlist.

## Worked example

Lexical ranking is [A,B,C], dense ranking [C,A,D]. With c=60, A receives 1/61+1/62; C receives 1/63+1/61. A wins despite not ranking first in dense search. This is a ranking rule, not a calibrated estimate that A is correct. If essential evidence E is absent from both lists, fusion and reranking cannot invent it.


## Primary references

- https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html
- https://www.sbert.net/docs/quickstart.html

- [Encoder model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [Reranker model card](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2)
