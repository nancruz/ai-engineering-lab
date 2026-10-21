# What a RAG system is

Week 1 · first one-hour session · no prior AI background assumed.

By the end, you should be able to explain what retrieval contributes, distinguish ingestion from answering, and locate a failure before deciding which component to change. This lesson introduces concepts; the following modules develop their algorithms, mathematics and engineering trade-offs.

## Start with a problem you recognize

An engineer asks an internal assistant: **“How do I roll back the playback service in staging and production?”**

Your organization has service runbooks, deployment policies and incident reports. Some are current, some are obsolete, and some have restricted access. A general language model has not necessarily seen these documents. Even if it has seen an older public version, it has no reliable way to infer your current internal policy from its training alone.

You could paste the relevant runbooks into a prompt yourself. The model could then use those passages to draft an answer. A retrieval-augmented generation system automates the evidence-finding and context-building parts of that process.

**Retrieval-augmented generation (RAG)** means retrieving information from an external source and supplying it to a generative model as context for its response. In this course, that external source starts as a collection of documents. It can also be a search service or another authorized information source.

The language model produces the answer. The surrounding software determines which evidence it sees, under what access rules, and how the result is evaluated and served. Supplying evidence improves the opportunity to answer correctly; it does not guarantee that the model uses it correctly.

## Two workflows, with different responsibilities

There is usually preparation work before a question arrives and request processing when a user asks one.

### Ingestion: prepare sources for search

Imagine importing your runbooks into a searchable system:

1. **Load and parse documents.** Extract useful text from Markdown, HTML or PDF while preserving headings, lists and source locations.
2. **Attach metadata.** Keep a stable source ID, version, access permissions, service name and relevant dates. These describe authority and eligibility, not just search relevance.
3. **Split long documents into chunks.** A chunk is a smaller retrievable unit, often a section or a few paragraphs. Keep enough surrounding structure to interpret it.
4. **Build a search index.** A lexical index supports word-based search. A vector index supports search over embeddings. A system may use either or both.
5. **Maintain the index.** Updates and deletions must propagate. A current answer cannot depend on a superseded passage simply because the old version remains searchable.

Ingestion can be scheduled, event-driven or manual. It is not the same thing as training the language model: indexing a new runbook does not change the model's weights.

The starter lab treats each short document as one retrieval unit. That simplification lets you learn evidence selection first. Module 3 introduces chunking and the additional bookkeeping it requires.

### Query time: find evidence and answer

For the rollback question, the application:

1. **Establishes request context.** Who is asking? What can they access? Are they asking for today's process or a historical one?
2. **Retrieves candidates.** Search returns a ranked list of potentially useful documents or chunks, with stable IDs and scores.
3. **Optionally reranks candidates.** A more expensive relevance model can reorder a small candidate set. It cannot recover a document that never reached that set.
4. **Builds the model context.** Select passages, remove redundant material, retain citation IDs and stay within the input budget. Apply access controls before evidence reaches the model.
5. **Calls the generator.** Give it the question, selected evidence and instructions for answering, citing sources and handling insufficient evidence.
6. **Checks and serves the result.** Validate the output structure and examine support for its claims. Log enough information to reproduce a failure without exposing restricted content.

Eligibility rules must hold throughout the pipeline. For example, a shared cache must not return another user's restricted passages even if the original retrieval enforced permissions.

## Follow one question through the system

Suppose the corpus contains these fictional documents:

| ID | Content | Status |
| --- | --- | --- |
| A | Current staging rollback procedure | Current |
| B | Current production rollback procedure, including approval | Current |
| C | Earlier production rollback procedure | Archived |
| D | General playback architecture overview | Current |

The question asks about **both staging and production**, so A and B provide complementary evidence. A alone does not explain the production procedure.

A search result of **D, A, C** is plausible: all mention the service. But it omits B and includes obsolete instructions. The generator might combine current staging instructions with old production instructions into one fluent answer.

Now consider **A, B, D**. Retrieval found the evidence needed for both environments. The answer can still fail if the generator omits the production approval step, cites the wrong source or invents a command.

These are different failures. To diagnose them, preserve the retrieved IDs, the exact context sent to the model and the resulting claims. Looking only at the final answer cannot tell you where the problem began.

## Vocabulary you will use

| Term | Meaning and practical consequence |
| --- | --- |
| Corpus | The collection of source documents being searched. Its quality limits what the system can know from retrieval. |
| Chunk | A retrievable portion of a document. Poor boundaries can separate a rule from its exception. |
| Metadata | Information such as source, version and permissions. It helps determine which evidence is valid for this request. |
| Embedding | A model-produced numerical vector representing text. Similarity can help find related wording, but is not proof of factual support. |
| Lexical retrieval | Search based on words and their statistics. It can be effective for exact names, identifiers and specialist terms. BM25 is one such ranking method. |
| Dense retrieval | Search using learned vector representations. It can help match paraphrases but can also rank irrelevant passages highly. |
| Hybrid retrieval | Combining lexical and dense retrieval results. Its value must be measured against simpler baselines. |
| Top-k | The first k ranked retrieval units. Here, k=3 means three unique document IDs; later exercises may operate on chunks. |
| Reranker | A model that rescores candidate query–passage pairs, usually after initial retrieval. |
| Context | Information supplied to the generator for the current request, including selected evidence. |
| Token | A unit of text processed by a model, often a word fragment. Token counts affect context limits, latency and cost. |
| Grounded answer | An answer whose factual claims are supported by the supplied evidence. Grounding is distinct from whether the source itself is current and correct. |
| Citation | A link or identifier connecting a claim to a source. A citation can exist without actually supporting the claim. |
| Abstention | Declining to make an unsupported claim, or explaining what evidence is missing. It can be the correct outcome. |
| Evaluation set | Questions with independently established expectations, used to measure system behavior. It needs more than easy questions that the current system already answers. |

## What RAG changes—and what it leaves unresolved

RAG lets an application use external evidence at request time without retraining the generator each time a document changes. It also makes source inspection and citation possible. This is useful for policies, runbooks and other knowledge that changes or is specific to an organization.

Fine-tuning is a different operation: it updates model parameters using training examples. It may improve a task or behavior, and can coexist with retrieval. It does not automatically solve document freshness or request-specific permissions.

A RAG system does not require an autonomous agent. A fixed pipeline can retrieve evidence and generate a response. Later, an agent may choose tools or take multiple steps; those choices introduce additional evaluation and control requirements.

RAG is also not always necessary. A SQL query, a conventional search interface or a deterministic workflow may meet the user need more directly. In this course, we use RAG because synthesizing an answer across multiple authorized documents is the learning problem.

## Why evaluation has several layers

Before a single overall quality score, ask separate questions:

- **Retrieval:** Did the system find the supporting evidence? How highly did it rank it?
- **Context construction:** Did the final model input retain all the necessary information?
- **Generation:** Are the answer's claims supported? Did it answer the whole question?
- **System behavior:** Were access and freshness rules respected? Was latency and cost acceptable? Did it abstain when necessary?

For our example, finding A but missing B counts as finding *some* evidence. It does not provide everything needed to answer both parts. Module 1 turns this distinction into Hit, Recall and Reciprocal Rank using concrete lists before introducing notation.

There is an important qualification: two relevant documents are not always both required. If A and B were duplicate copies of the same complete procedure, finding one could be sufficient. An evaluation must distinguish relevance from jointly required evidence. Our example intentionally uses complementary staging and production procedures.

## Your first exercise

Within this session, explain the following aloud or in a short note:

1. Which work happens when a runbook changes, and which happens when a user asks a question?
2. If the current production document never reaches the generator, where would you investigate first?
3. If the correct document reaches the generator but the answer omits approval, what would you inspect?
4. Why are a high similarity score and a valid citation insufficient evidence of correctness?

A good explanation separates source maintenance, search, context selection and generation. You do not need to memorize framework names or formulas yet.

Next, read the short [investigation scenario](../FIRST_INVESTIGATION.md), then follow [Module 1 — Week 1, Session A](Module_01.md#session-a--understand-the-task-60-minutes). Your answers above count toward that session's explanation; do not repeat completed work. Module 1 provides the exact files, commands and completion checks for each session. The supplied lab implements retrieval and evaluation only; there is no hidden LLM call. Real generation is added in Module 3, after you can diagnose what evidence the system provides.
