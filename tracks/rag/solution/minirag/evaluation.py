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
    # LAB5-BEGIN
    # Task: Use _top(ranked, k). Return floats.
    if not relevant:
        return None
    return 1.0 if set(_top(ranked, k)) & set(relevant) else 0.0
    # LAB5-END


def recall_at_k(ranked, relevant, k):
    """Share of the relevant ids found in the top k."""
    # LAB5-BEGIN
    if not relevant:
        return None
    return len(set(_top(ranked, k)) & set(relevant)) / len(set(relevant))
    # LAB5-END


def reciprocal_rank(ranked, relevant, k):
    """1 / position of the first relevant id in the top k (positions start at 1), else 0.0."""
    # LAB5-BEGIN
    if not relevant:
        return None
    for position, item in enumerate(_top(ranked, k), 1):
        if item in relevant:
            return 1.0 / position
    return 0.0
    # LAB5-END


def ndcg_at_k(ranked, relevant, k):
    """Normalized discounted cumulative gain with binary relevance.

    DCG  = sum over positions i (from 1) of relevant items in the top k: 1 / log2(i + 1)
    IDCG = the DCG of a perfect ranking: sum for i = 1 .. min(len(relevant), k)
    nDCG = DCG / IDCG
    """
    # LAB5-BEGIN
    if not relevant:
        return None
    gold = set(relevant)
    dcg = sum(1 / math.log2(i + 1) for i, item in enumerate(_top(ranked, k), 1) if item in gold)
    idcg = sum(1 / math.log2(i + 1) for i in range(1, min(len(gold), k) + 1))
    return dcg / idcg
    # LAB5-END


def evidence_recall(texts, evidence):
    """Share of the labelled evidence strings that appear in the retrieved chunk texts.

    Document metrics only say the right document was found. This checks the
    passage that answers the question actually reached the prompt. Match
    case-insensitively; each evidence string must sit inside a single chunk.
    """
    # LAB5-BEGIN
    if not evidence:
        return None
    lowered = [t.lower() for t in texts]
    return sum(any(e.lower() in t for t in lowered) for e in evidence) / len(evidence)
    # LAB5-END


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
    # LAB5-BEGIN
    # Task: For each question q: hits = retriever.retrieve(q["question"], k=k, role=q["role"]);
    #       ranked = unique_docs(hits); compute each metric, evidence_recall and tokens;
    #       list leaked doc ids using ROLE_ACCESS. Return summarize(rows, [*METRICS, "evidence", "tokens"]).
    rows = []
    for q in questions:
        hits = retriever.retrieve(q["question"], k=k, role=q["role"])
        ranked = unique_docs(hits)
        row = {"id": q["id"], "type": q.get("type", ""), "role": q["role"], "relevant": q["relevant"], "retrieved": ranked}
        for name, metric in METRICS.items():
            row[name] = metric(ranked, q["relevant"], k)
        row["evidence"] = evidence_recall([h.chunk.text for h in hits], q.get("evidence", []))
        row["tokens"] = sum(count_tokens(h.chunk.text) for h in hits)
        visible = ROLE_ACCESS.get(q["role"], set())
        row["leaks"] = sorted({h.chunk.doc_id for h in hits if h.chunk.meta.get("access", "all") not in visible})
        rows.append(row)
    return summarize(rows, [*METRICS, "evidence", "tokens"])
    # LAB5-END


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
    # LAB5-BEGIN
    text = answer.text.lower()
    expect_abstain = question.get("expected") == "abstain"
    abstain_ok = answer.abstained == expect_abstain
    missing = [] if answer.abstained else [s for s in question.get("must_include", []) if s.lower() not in text]
    forbidden = [s for s in question.get("must_not_include", []) if s.lower() in text]
    return {"ok": abstain_ok and not missing and not forbidden, "abstain_ok": abstain_ok,
            "missing": missing, "forbidden": forbidden}
    # LAB5-END


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
    # LAB5-BEGIN
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("judge reply contains no JSON object")
    try:
        data = json.loads(text[start:end + 1])
    except json.JSONDecodeError as err:
        raise ValueError(f"judge reply is not valid JSON: {err}") from None
    claims = data.get("claims", [])
    supported = sum(1 for c in claims if c.get("supported") is True)
    return {"claims": claims, "faithfulness": supported / len(claims) if claims else None}
    # LAB5-END


def judge_faithfulness(result, llm):
    """LLM-as-judge: what share of the answer's claims do its sources support? (Supplied.)"""
    if result.answer.abstained or not result.messages:
        return {"claims": [], "faithfulness": None}
    sources = result.messages[-1]["content"].rsplit("\n\nQuestion:", 1)[0]
    reply = llm.complete([{"role": "user", "content": JUDGE_PROMPT.format(sources=sources, answer=result.answer.text)}],
                         max_tokens=800)
    return parse_judgement(re.sub(r"```(?:json)?", "", reply))
