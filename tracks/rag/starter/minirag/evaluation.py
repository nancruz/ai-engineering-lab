"""Measure retrieval and answers so changes are decisions, not guesses. (Lab 5.)

Retrieval metrics compare the ranked document IDs with the labelled relevant IDs.
They return None when a question has no relevant documents (it should be
abstained on), and those questions are reported separately.
"""
import json
import math
import re

from .generation import count_tokens
from .retrieval import ROLE_ACCESS, unique_docs


def _top(ranked, k):
    if k < 1:
        raise ValueError("k must be >= 1")
    return list(dict.fromkeys(ranked))[:k]


def hit_at_k(ranked, relevant, k):
    """1.0 if any relevant id is in the top k, else 0.0. None if nothing is relevant."""
    # TODO (Lab 5): Use _top(ranked, k). Return floats.
    raise NotImplementedError("Lab 5: write hit_at_k() in minirag/evaluation.py")


def recall_at_k(ranked, relevant, k):
    """Share of the relevant ids found in the top k."""
    # TODO (Lab 5): implement this, following the docstring.
    raise NotImplementedError("Lab 5: write recall_at_k() in minirag/evaluation.py")


def reciprocal_rank(ranked, relevant, k):
    """1 / position of the first relevant id in the top k (positions start at 1), else 0.0."""
    # TODO (Lab 5): implement this, following the docstring.
    raise NotImplementedError("Lab 5: write reciprocal_rank() in minirag/evaluation.py")


def ndcg_at_k(ranked, relevant, k):
    """Normalized discounted cumulative gain with binary relevance.

    DCG  = sum over positions i (from 1) of relevant items in the top k: 1 / log2(i + 1)
    IDCG = the DCG of a perfect ranking: sum for i = 1 .. min(len(relevant), k)
    nDCG = DCG / IDCG
    """
    # TODO (Lab 5): implement this, following the docstring.
    raise NotImplementedError("Lab 5: write ndcg_at_k() in minirag/evaluation.py")


def evidence_recall(texts, evidence):
    """Share of the labelled evidence strings that appear in the retrieved chunk texts.

    Document metrics only say the right document was found. This checks the
    passage that answers the question actually reached the prompt. Match
    case-insensitively; each evidence string must sit inside a single chunk.
    """
    # TODO (Lab 5): implement this, following the docstring.
    raise NotImplementedError("Lab 5: write evidence_recall() in minirag/evaluation.py")


METRICS = {"hit": hit_at_k, "recall": recall_at_k, "mrr": reciprocal_rank, "ndcg": ndcg_at_k}


def mean(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def evaluate_retrieval(retriever, questions, k=5):
    """Run every question through the retriever and score the document ranking.

    Returns {"rows": [...], "summary": {...}, "by_type": {type: {...}}}. Each row has
    id, type, role, relevant, retrieved (unique doc ids from the k retrieved chunks),
    one value per metric in METRICS, "evidence" (evidence_recall over the chunk texts),
    "tokens" (count_tokens of all retrieved chunk texts: what this costs in the prompt)
    and "leaks": retrieved docs the role may not read.
    """
    # TODO (Lab 5): For each question q: hits = retriever.retrieve(q["question"], k=k, role=q["role"]);
    #       ranked = unique_docs(hits); compute each metric, evidence_recall and tokens;
    #       list leaked doc ids using ROLE_ACCESS. Return summarize(rows, [*METRICS, "evidence", "tokens"]).
    raise NotImplementedError("Lab 5: write evaluate_retrieval() in minirag/evaluation.py")


def summarize(rows, keys):
    """Average `keys` over rows (ignoring None), overall and per question type. (Supplied.)"""
    def block(subset):
        out = {key: mean(r.get(key) for r in subset) for key in keys}
        out["n"] = len(subset)
        return out
    types = sorted({r["type"] for r in rows})
    return {"rows": rows, "summary": block(rows), "by_type": {t: block([r for r in rows if r["type"] == t]) for t in types}}


def check_answer(answer, question):
    """Deterministic answer checks against the labels in questions.json.

    - abstain_ok: the answer abstained if and only if question["expected"] == "abstain"
    - missing: strings from must_include that are absent (case-insensitive)
    - forbidden: strings from must_not_include that appear (case-insensitive)
    - ok: abstain_ok and nothing missing and nothing forbidden
      (when the model abstains, must_include is not checked)
    """
    # TODO (Lab 5): implement this, following the docstring.
    raise NotImplementedError("Lab 5: write check_answer() in minirag/evaluation.py")


def evaluate_answers(run, questions):
    """run(question_dict) -> RagResult. Scores every answer with check_answer. (Supplied.)"""
    rows = []
    for q in questions:
        result = run(q)
        check = check_answer(result.answer, q)
        cited = [c["doc_id"] for c in result.answer.citations]
        rows.append({"id": q["id"], "type": q.get("type", ""), "role": q["role"], "answer": result.answer.text,
                     "abstained": result.answer.abstained, "cited": cited,
                     "cites_relevant": (bool(set(cited) & set(q["relevant"])) if q["relevant"] else None),
                     "pass": 1.0 if check["ok"] else 0.0, "abstain_ok": 1.0 if check["abstain_ok"] else 0.0,
                     "missing": check["missing"], "forbidden": check["forbidden"], "timings": result.timings})
    for row in rows:
        row["cites_relevant"] = None if row["cites_relevant"] is None else float(row["cites_relevant"])
    return summarize(rows, ["pass", "abstain_ok", "cites_relevant"])


JUDGE_PROMPT = """You check whether an answer is supported by its sources.

Split the answer into its factual claims. For each claim decide whether the sources state it
(supported: true) or not (supported: false). Do not use outside knowledge.

Reply with JSON only, in this shape:
{{"claims": [{{"claim": "...", "supported": true}}]}}

Sources:
{sources}

Answer:
{answer}"""


def parse_judgement(text):
    """Read the judge's JSON reply.

    Accept extra text or ``` fences around the JSON: take everything from the first
    "{" to the last "}". Return {"claims": [...], "faithfulness": supported / total},
    with faithfulness None when there are no claims. Raise ValueError if no valid
    JSON object is found.
    """
    # TODO (Lab 5): implement this, following the docstring.
    raise NotImplementedError("Lab 5: write parse_judgement() in minirag/evaluation.py")


def judge_faithfulness(result, llm):
    """LLM-as-judge: what share of the answer's claims do its sources support? (Supplied.)"""
    if result.answer.abstained or not result.messages:
        return {"claims": [], "faithfulness": None}
    sources = result.messages[-1]["content"].rsplit("\n\nQuestion:", 1)[0]
    reply = llm.complete([{"role": "user", "content": JUDGE_PROMPT.format(sources=sources, answer=result.answer.text)}],
                         max_tokens=800)
    return parse_judgement(re.sub(r"```(?:json)?", "", reply))
