"""Grade repeated agent trials and estimate pass@k and pass^k. Standard library only."""
import json
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRIALS = json.loads((HERE / "data/trials.json").read_text())

DEFAULT_GRADERS = {"end_state": True, "no_forbidden_attempt": True, "cites_required": True, "max_steps": 8}


def grade_trial(trial, graders, must_cite=True):
    """Return (passed, reasons). A trial passes only if every enabled grader passes."""
    reasons = []
    if graders.get("end_state") and not trial["end_state_ok"]:
        reasons.append("end state wrong")
    if graders.get("no_forbidden_attempt") and trial["forbidden_attempt"]:
        reasons.append("attempted a forbidden action")
    if graders.get("cites_required") and must_cite and not trial["cited_required"]:
        reasons.append("missing required citation")
    limit = graders.get("max_steps")
    if limit and trial["steps"] > limit:
        reasons.append(f"used {trial['steps']} steps (limit {limit})")
    return (not reasons), reasons


def pass_at_k(n, c, k):
    """Probability that at least one of k trials (drawn without replacement from n with c passes) passes."""
    if not 1 <= k <= n:
        raise ValueError("k must be between 1 and n")
    return 1.0 - comb(n - c, k) / comb(n, k)


def pass_hat_k(n, c, k):
    """pass^k: probability that all k trials pass. Measures consistency, not best case."""
    if not 1 <= k <= n:
        raise ValueError("k must be between 1 and n")
    return comb(c, k) / comb(n, k)


def report(graders=None, k=1, price_per_million=3.0, data=None):
    data = data or TRIALS
    g = {**DEFAULT_GRADERS, **(graders or {})}
    tasks = []
    for task, meta in data["tasks"].items():
        rows = [t for t in data["trials"] if t["task"] == task]
        graded = [grade_trial(t, g, meta["must_cite"]) for t in rows]
        n, c = len(rows), sum(p for p, _ in graded)
        tasks.append({"task": task, "n": n, "passed": c, "pass_at_k": pass_at_k(n, c, k),
                      "pass_hat_k": pass_hat_k(n, c, k), "tokens": sum(t["tokens"] for t in rows),
                      "failures": [{"trial": t["trial"], "reasons": r} for t, (p, r) in zip(rows, graded) if not p]})
    passed, tokens = sum(t["passed"] for t in tasks), sum(t["tokens"] for t in tasks)
    return {"k": k, "graders": g, "tasks": tasks,
            "mean_pass_at_k": sum(t["pass_at_k"] for t in tasks) / len(tasks),
            "mean_pass_hat_k": sum(t["pass_hat_k"] for t in tasks) / len(tasks),
            "cost_per_success": (tokens / 1e6 * price_per_million / passed) if passed else None}


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Grade the fictional recorded trials.")
    p.add_argument("-k", type=int, default=1)
    p.add_argument("--max-steps", type=int, default=8)
    p.add_argument("--no-citation-grader", action="store_true")
    a = p.parse_args()
    r = report({"max_steps": a.max_steps, "cites_required": not a.no_citation_grader}, a.k)
    for t in r["tasks"]:
        print(f"{t['task']:<18} {t['passed']}/{t['n']}  pass@{a.k}={t['pass_at_k']:.3f}  pass^{a.k}={t['pass_hat_k']:.3f}")
    print(f"mean pass@{a.k}={r['mean_pass_at_k']:.3f}  mean pass^{a.k}={r['mean_pass_hat_k']:.3f}")
