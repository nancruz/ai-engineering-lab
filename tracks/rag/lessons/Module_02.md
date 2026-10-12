# Module 02 — Retrieval algorithms and controlled comparisons

Weeks 7–12 · 18 hours total · software-engineering experience assumed.

## Technical lesson

Keyword overlap gives every matching term equal weight. BM25 gives rare terms more influence, saturates repeated occurrences and normalizes for length. One common positive-IDF variant is IDF(t)=log(1+(N-df(t)+0.5)/(df(t)+0.5)). Its term contribution is IDF(t)·f(t,d)(k1+1)/(f(t,d)+k1(1-b+b·|d|/avgdl)). Understand each quantity before tuning k1 or b. Exact identifiers often benefit from lexical search; semantic similarity may miss a one-character difference that changes the meaning.

A bi-encoder maps queries and documents independently into vectors. With normalized embeddings, dot product equals cosine similarity. A vector score is not a probability of relevance. Model instructions, query/document prefixes and truncation settings are part of the embedding configuration. Cache vectors using content hash and model revision; changing one requires invalidation.

Approximate nearest-neighbour search trades candidate recall for speed. On this small corpus, use exact search first so representation quality is not confused with index approximation. Compare ANN recall against exact vector top-k later, using a larger public corpus if necessary. It is a different metric from relevance recall against human labels.

Hybrid retrieval combines complementary rankings. Reciprocal rank fusion uses sum over systems of 1/(c+rank). It avoids assuming that BM25 and vector scores are on the same scale. It still needs candidate depth, a fusion constant and deduplication choices. A cross-encoder jointly processes query and passage to score relevance; it is more expensive per pair and usually operates on a shortlist. It cannot recover evidence absent from that shortlist.

## Worked example

Lexical ranking is [A,B,C], dense ranking [C,A,D]. With c=60, A receives 1/61+1/62; C receives 1/63+1/61. A wins despite not ranking first in dense search. This is a ranking rule, not a calibrated estimate that A is correct. If essential evidence E is absent from both lists, fusion and reranking cannot invent it.

## Six weekly labs

### Week 07 — Audit lexical scoring

- [ ] 60 minutes — Study and reason: Calculate one BM25 term contribution by hand using supplied document counts.
- [ ] 60 minutes — Implement or experiment: Explain the existing reference implementation and add a term-saturation test.
- [ ] 60 minutes — Test and explain: Compare tokenization for service IDs, punctuation and paraphrases.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 08 — Add real embeddings

- [ ] 60 minutes — Study and reason: Read the selected model card and retrieval instructions; record revision and license.
- [ ] 60 minutes — Implement or experiment: Implement a Sentence Transformers adapter and exact cosine retrieval; keep BM25 unchanged.
- [ ] 60 minutes — Test and explain: Record embedding latency separately from query latency and inspect top-k misses.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 09 — Run ablations

- [ ] 60 minutes — Study and reason: Define exact-match and paraphrase slices before running comparisons.
- [ ] 60 minutes — Implement or experiment: Evaluate lexical versus dense on the same development set and authorized candidates.
- [ ] 60 minutes — Test and explain: Report per-query deltas rather than a single average.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 10 — Fuse rankings

- [ ] 60 minutes — Study and reason: Derive reciprocal rank fusion and implement it over unique document IDs.
- [ ] 60 minutes — Implement or experiment: Compare lexical, dense and fused rankings using a fixed candidate budget.
- [ ] 60 minutes — Test and explain: Explain which failures fusion addresses and where it makes ranking worse.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 11 — Rerank candidates

- [ ] 60 minutes — Study and reason: Study joint query/passage scoring and its compute cost.
- [ ] 60 minutes — Implement or experiment: Add one small cross-encoder to rerank a fixed shortlist.
- [ ] 60 minutes — Test and explain: Measure quality and latency; inspect a miss outside the shortlist.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

### Week 12 — Choose an architecture

- [ ] 60 minutes — Study and reason: Freeze preprocessing and development questions for the comparison.
- [ ] 60 minutes — Implement or experiment: Select one retrieval configuration and document rejected alternatives.
- [ ] 60 minutes — Test and explain: Defend the choice under a smaller latency budget and on the exact-ID slice.

Save code/config, input snapshot, outputs and a short interpretation. Record one failure and the evidence used to diagnose it. If incomplete at 180 minutes, continue next week; do not add homework outside the budget.

## Investigation assessment

An embedding model improves paraphrases but breaks searches for error codes. A teammate proposes replacing keyword search entirely. Produce a paired comparison and a hybrid alternative, then recommend a release or a no-change decision.

## Review guidance — attempt first

Strong evidence includes exact-ID regressions, shortlist recall and timings. An aggregate gain does not justify breaking a critical slice. Compare against BM25, keep query preprocessing fixed and do not tune fusion on the held-out set. A larger embedding model is not automatically the right repair.

## Mastery gate

Pass when all rankings are reproducible, normalization is correct, fusion deduplicates items, and the architecture decision reports relevance quality plus cost/latency. The dense and reranker runs must use real models, not hand-written vectors.

## Primary references

- https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html
- https://www.sbert.net/docs/quickstart.html
