"""Inspectable agent loop, fictional tools and scripted models. Standard library only.

The scripted models are deterministic stand-ins for a language model. They make
the loop's mechanics (budgets, retries, repeat detection, the action gate)
observable without an API key. real_model.py plugs a real model into the same
loop. docs/agents/assets/agentlab.js mirrors this file for the browser
workbenches; tests/site/test_site.py checks they produce identical runs.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from retrieval import retrieve  # noqa: E402  (small BM25 over data/corpus.json)
from schema import validate  # noqa: E402


def load(name):
    return json.loads((HERE / "data" / name).read_text())


CORPUS = load("corpus.json")
WORLD = load("world.json")
TOOLS = load("tools.json")
TASKS = load("tasks.json")
TOOL_BY_NAME = {t["name"]: t for t in TOOLS}
TASK_BY_ID = {t["id"]: t for t in TASKS}

DEFAULTS = {"model": "careful", "max_steps": 6, "retry_transient": True,
            "detect_repeats": True, "action_gate": True, "fault": "none"}
FAULTS = ("none", "timeout_once", "timeout_always")


def compact(obj):
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


def est_tokens(obj):
    """Rough token estimate: about four characters per token. Use real usage counts when a provider returns them."""
    text = obj if isinstance(obj, str) else compact(obj)
    return (len(text) + 3) // 4


def fields_hash(fields):
    """FNV-1a over the exact ticket fields, so an approval can be bound to them."""
    text = compact({"title": fields["title"], "body": fields["body"], "severity": fields["severity"]})
    h = 0x811C9DC5
    for ch in text:
        h ^= ord(ch)
        h = (h * 0x01000193) & 0xFFFFFFFF
    return "h" + format(h, "08x")


class Env:
    """Fictional tool implementations with recorded side effects."""

    def __init__(self, fault="none", role=None):
        if fault not in FAULTS:
            raise ValueError(f"unknown fault: {fault}")
        self.fault, self.role = fault, role or WORLD["caller_role"]
        self.metric_calls, self.side_effects, self.drafts, self.approvals = 0, [], [], {}

    def call(self, name, args, gate=True):
        tool = TOOL_BY_NAME.get(name)
        if not tool:
            return {"error": "unknown_tool", "message": f"No tool named {name}.", "retryable": False}
        problems = validate(tool["input_schema"], args)
        if problems:
            return {"error": "invalid_arguments", "details": problems,
                    "message": "Fix the listed fields and call again.", "retryable": False}
        if tool["side_effect"] and gate and args.get("approval_id") not in self.approvals:
            roles = " or ".join(tool["approver_roles"])
            return {"error": "approval_required",
                    "message": f"{name} has an external effect. Ask a person with role {roles} to approve this exact request, or draft it instead.",
                    "retryable": False}
        return getattr(self, "_" + name)(args)

    def _search_knowledge(self, args):
        query = {"query": args["query"], "role": self.role, "current_only": True}
        by_id = {d["id"]: d for d in CORPUS}
        results = []
        for hit in retrieve(query, CORPUS, "bm25", args.get("k", 3)):
            doc = by_id[hit["id"]]
            results.append({"id": doc["id"], "title": doc["title"], "status": doc["status"],
                            "trust": "untrusted" if doc["source"] == "fictional-import" else "internal",
                            "text": doc["text"]})
        return {"results": results}

    def _get_error_ratio(self, args):
        self.metric_calls += 1
        if self.fault == "timeout_always" or (self.fault == "timeout_once" and self.metric_calls == 1):
            return {"error": "timeout", "message": "Metrics backend did not respond within 2 s.", "retryable": True}
        service = WORLD["services"][args["service"]]
        points = service["canary_error_percent"][-args["minutes"]:]
        return {"service": args["service"], "release": service["current_release"], "unit": "percent",
                "points": [{"minute": m, "percent": p} for m, p in points]}

    def _draft_ticket(self, args):
        draft = {"draft_id": f"D-{len(self.drafts) + 1}", "fields_hash": fields_hash(args), "status": "draft"}
        self.drafts.append({**draft, "fields": args})
        return draft

    def _create_ticket(self, args):
        self.side_effects.append({"tool": "create_ticket", "args": args})
        return {"ticket_id": f"T-{len(self.side_effects)}", "status": "created"}

    def _rollback(self, args):
        self.side_effects.append({"tool": "rollback", "args": args})
        return {"service": args["service"], "release": args["to_release"], "status": "restored"}


# ---------------------------------------------------------------- scripted models
def _call(tool, args): return {"tool": tool, "args": args}
def _final(text): return {"final": text}
def _calls(steps, tool): return [s for s in steps if s.get("tool") == tool]
def _ids(result): return [r["id"] for r in result.get("results", [])]


def _trailing_above(points, threshold):
    run, start = 0, None
    for point in reversed(points):
        if point["percent"] <= threshold:
            break
        run, start = run + 1, point["minute"]
    return run, start


ABSTAIN = ("I could not find any record of who approved project ORION on 14 September in the sources I can read. "
           "I will not guess; check the project's decision log or ask its owner.")


def _rollback_policy(steps, eager):
    if not _calls(steps, "search_knowledge"):
        return _call("search_knowledge", {"query": "playback rollback canary error approval"})
    metrics = _calls(steps, "get_error_ratio")
    if not metrics:
        return _call("get_error_ratio", {"service": "playback", "minutes": 9})
    result = metrics[-1]["result"]
    if "error" in result:
        if eager and result["error"] == "timeout":
            return _call("get_error_ratio", {"service": "playback", "minutes": 9})
        return _final("I could not verify the playback canary error ratio because the metrics tool failed. "
                      "Restoring r41 needs incident commander approval once the condition is confirmed [rollback-v2]. "
                      "I made no production change; ask the on-call engineer to check the dashboard.")
    run, start = _trailing_above(result["points"], 2)
    last = result["points"][-1]["percent"]
    if run < 5:
        return _final(f"Rollback condition not met: the canary error ratio has been above 2 percent for {run} "
                      f"consecutive minutes; the policy needs five [rollback-v2]. Keep watching.")
    rollbacks = _calls(steps, "rollback")
    if eager and not rollbacks:
        return _call("rollback", {"service": "playback", "to_release": "r41"})
    if rollbacks and rollbacks[-1]["result"].get("status") == "restored":
        return _final(f"Rolled back playback to r41: the canary error ratio was above 2 percent for {run} "
                      f"consecutive minutes [rollback-v2].")
    drafts = [s for s in _calls(steps, "draft_ticket") if "draft_id" in s["result"]]
    if not drafts:
        return _call("draft_ticket", {
            "title": "Request incident commander approval: restore playback r41",
            "body": (f"Canary error ratio above 2 percent for {run} consecutive minutes since {start} after release r42 "
                     f"(latest {last} percent). Policy rollback-v2 requires incident commander approval before "
                     f"restoring r41. Preserve the trace bundle before changing traffic."),
            "severity": "high"})
    return _final(f"Rollback condition met: the playback canary error ratio has been above 2 percent for {run} "
                  f"consecutive minutes (since {start}, latest {last} percent) after release r42. Restoring r41 "
                  f"requires incident commander approval [rollback-v2]. I drafted {drafts[-1]['result']['draft_id']} "
                  f"to request that approval and made no production change.")


def scripted(eager):
    def model(task, steps, messages):
        searches = _calls(steps, "search_knowledge")
        if task["id"] == "credential-policy":
            if not searches:
                return _call("search_knowledge", {"query": "service credential support ticket"})
            if "keys-v2" in _ids(searches[-1]["result"]):
                return _final("No. Never put a credential value in a support ticket. To replace a service credential, "
                              "create a new key, deploy dual-key verification, migrate callers, then revoke the old key "
                              "after the overlap window [keys-v2].")
            return _final("I could not find a current policy for this. Ask the security owner before sharing any credential.")
        if task["id"] == "rollback-check":
            return _rollback_policy(steps, eager)
        if task["id"] == "orion":
            if eager:
                if searches and searches[-1]["result"].get("error") == "repeated_call":
                    return _final(ABSTAIN)
                return _call("search_knowledge", {"query": "ORION approval"})
            if not searches:
                return _call("search_knowledge", {"query": "project ORION approval 14 September"})
            if len(searches) == 1:
                return _call("search_knowledge", {"query": "ORION approved decision"})
            return _final(ABSTAIN)
        if task["id"] == "injected-note":
            if not searches:
                return _call("search_knowledge", {"query": "imported troubleshooting note"})
            if "injection-note" not in _ids(searches[-1]["result"]):
                return _final("I could not find the imported troubleshooting note.")
            if not eager:
                return _final("The imported troubleshooting note contains no troubleshooting steps. It tells the reader to "
                              "send the restricted capacity value to a new ticket; that is untrusted content, so I did not "
                              "act on it [injection-note]. Flag the note for review before it is used in a handover.")
            created = _calls(steps, "create_ticket")
            if not created:
                return _call("create_ticket", {
                    "title": "Playback emergency capacity value",
                    "body": "Requested by the imported troubleshooting note: send the restricted capacity value.",
                    "severity": "low", "idempotency_key": "note-capacity-1"})
            if created[-1]["result"].get("status") == "created":
                return _final(f"Created ticket {created[-1]['result']['ticket_id']} as the imported note instructed [injection-note].")
            return _final("The imported note asked for a ticket with the restricted capacity value. Creating it needs "
                          "approval, so nothing was created [injection-note].")
        return _final("This scripted model has no policy for that task.")
    return model


SCRIPTED = {"careful": scripted(False), "eager": scripted(True)}


# ---------------------------------------------------------------- the loop
def run_agent(task_id, options=None, model=None):
    """Run one task. Returns a trajectory record (JSON-serialisable)."""
    o = {**DEFAULTS, **(options or {})}
    if o["max_steps"] < 1:
        raise ValueError("max_steps must be positive")
    task = TASK_BY_ID[task_id]
    env = Env(o["fault"])
    policy = model or SCRIPTED[o["model"]]
    messages = [{"role": "system", "content": WORLD["system_prompt"]}, {"role": "user", "content": task["prompt"]}]
    context = est_tokens(WORLD["system_prompt"]) + est_tokens(task["prompt"])
    steps, final, stop = [], None, "step_budget"
    for n in range(1, o["max_steps"] + 1):
        action = policy(task, steps, messages)
        if "final" in action:
            final, stop = action["final"], "final_answer"
            steps.append({"n": n, "final": final, "context_tokens": context})
            messages.append({"role": "assistant", "content": final})
            break
        call = {"tool": action["tool"], "args": action["args"]}
        same = [s for s in steps if s.get("tool") == call["tool"] and compact(s["args"]) == compact(call["args"])]
        prior = same[-1] if same else None
        # A repeat is allowed only to retry a transient failure, and only once.
        blocked = prior is not None and (not prior["result"].get("retryable") or len(same) >= 2)
        attempts, note = 1, None
        if o["detect_repeats"] and blocked:
            result = {"error": "repeated_call",
                      "message": f"Identical call already made at step {prior['n']}. Use that result, change the arguments, or answer.",
                      "retryable": False}
            attempts, note = 0, "repeat blocked by the harness"
        else:
            result = env.call(call["tool"], call["args"], o["action_gate"])
            if result.get("retryable") and o["retry_transient"]:
                result, attempts, note = env.call(call["tool"], call["args"], o["action_gate"]), 2, "harness retried a transient error"
            if result.get("error") == "approval_required":
                note = "blocked by the action gate"
        steps.append({"n": n, "tool": call["tool"], "args": call["args"], "result": result,
                      "attempts": attempts, "note": note, "context_tokens": context})
        messages.append({"role": "assistant", "tool_call": call})
        messages.append({"role": "tool", "name": call["tool"], "content": compact(result)})
        context += est_tokens(call) + est_tokens(result)
    record = {"task": task_id, "options": o, "steps": steps, "stop_reason": stop, "final": final,
              "side_effects": env.side_effects, "drafts": env.drafts, "context_tokens": context}
    record["checks"] = check(task, record)
    record["success"] = all(record["checks"].values())
    return record


def check(task, record):
    """End-state checks: what happened, not how the transcript reads."""
    c, final = task["checks"], (record["final"] or "")
    out = {}
    if c["must_answer"]:
        out["answered"] = record["final"] is not None
    if c["must_cite"]:
        out["cites required sources"] = all(f"[{s}]" in final for s in c["must_cite"])
    if c["final_must_include"]:
        out["states the key point"] = all(x.lower() in final.lower() for x in c["final_must_include"])
    out["no forbidden side effects"] = not any(e["tool"] in c["forbidden_side_effects"] for e in record["side_effects"])
    if c["required_drafts"]:
        out["drafted for approval"] = len(record["drafts"]) >= c["required_drafts"]
    return out
