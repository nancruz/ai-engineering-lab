"""Query transformation: rewrite the user's question before searching. (Lab 6.)"""
import re

MULTI_QUERY_PROMPT = """Rewrite the question below as {n} different search queries for an internal engineering wiki.
Use different wording and synonyms; keep product names and error codes exactly.
Return one query per line, with no numbering and nothing else.

Question: {question}"""


def parse_queries(text, original, n=3):
    """Clean an LLM's list of rewrites.

    Strip bullets and numbering ("1.", "2)", "-", "*"), surrounding quotes and
    whitespace; drop empty lines and duplicates (case-insensitive, including the
    original). Return [original] + up to n rewrites.
    """
    # LAB6-BEGIN
    # Task: Process text.splitlines() with a regex for leading list markers.
    queries, seen = [original], {original.strip().lower()}
    for line in text.splitlines():
        line = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", line).strip().strip('"\'').strip()
        if line and line.lower() not in seen and len(queries) <= n:
            queries.append(line)
            seen.add(line.lower())
    return queries
    # LAB6-END


def expand_query(question, llm, n=3):
    """Original question plus up to n LLM rewrites. (Supplied.)"""
    reply = llm.complete([{"role": "user", "content": MULTI_QUERY_PROMPT.format(n=n, question=question)}], temperature=0.7)
    return parse_queries(reply, question, n)


HYDE_PROMPT = """Write a short passage (3-4 sentences) from an internal engineering runbook that would answer this question.
It is fine to guess details; the passage is only used for searching.

Question: {question}"""


def hyde_query(question, llm):
    """HyDE: search with a hypothetical answer instead of the question. (Supplied, try it in Lab 6.)"""
    return llm.complete([{"role": "user", "content": HYDE_PROMPT.format(question=question)}], temperature=0.7)
