"""Layered action gate for proposed agent actions. Standard library only.

Each defense is a separate, testable check that runs outside the model. The
browser guardrails workbench mirrors this file.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCENARIOS = json.loads((HERE / "data/guard_scenarios.json").read_text())

DEFENSES = ("authz_in_tools", "egress_allowlist", "require_approval", "bind_approval", "taint_hold", "idempotency_keys")
TOOL_RULES = {
    "search_knowledge": {"side_effect": False, "approver_roles": []},
    "draft_ticket": {"side_effect": False, "approver_roles": []},
    "create_ticket": {"side_effect": True, "approver_roles": ["engineer", "incident-commander"]},
    "rollback": {"side_effect": True, "approver_roles": ["incident-commander"]},
    "send_email": {"side_effect": True, "approver_roles": ["engineer", "incident-commander"]},
    "post_message": {"side_effect": True, "approver_roles": ["engineer", "incident-commander"]},
}
ALLOWED_EGRESS = ("example.internal",)


def _allowed_host(host):
    return any(host == d or host.endswith("." + d) for d in ALLOWED_EGRESS)


def gate(s, defenses):
    """Decide one proposed action. Returns outcome, the defense that decided it, and whether harm occurred."""
    on = set(defenses)
    unknown = on - set(DEFENSES)
    if unknown:
        raise ValueError(f"unknown defenses: {sorted(unknown)}")
    rule = TOOL_RULES[s["tool"]]

    def out(outcome, by, reason):
        harm = s["harmful"] and outcome == "executed"
        return {"scenario": s["id"], "outcome": outcome, "by": by, "reason": reason, "harm": harm}

    if s["tool"] == "search_knowledge":
        if "authz_in_tools" in on:
            return out("filtered", "authz_in_tools", "The tool removed sources the caller's role cannot read before the model saw them.")
        return out("executed", None, "Only the prompt asked the model not to reveal the value; the restricted source was returned.")
    if not rule["side_effect"]:
        return out("executed", None, "No external effect, so no approval is needed.")
    if "egress_allowlist" in on and s["egress"] and not _allowed_host(s["egress"]):
        return out("blocked", "egress_allowlist", f"{s['egress']} is not an allowed destination, whatever was approved.")
    a = s["approval"]
    if "require_approval" in on:
        if not a:
            return out("blocked", "require_approval", "No approval record exists for this action.")
        if a["role"] not in rule["approver_roles"]:
            return out("blocked", "require_approval", f"Approver role {a['role']} cannot approve {s['tool']}.")
    if "bind_approval" in on and a and a["fields_hash"] != s["fields_hash"]:
        return out("blocked", "bind_approval", "The approval was for different fields; changed fields need a new approval.")
    if "taint_hold" in on and s["tainted"] and (not a or a["by"] != "human"):
        return out("held", "taint_hold", "Untrusted content is in context, so an automatic approval is not enough; a person must confirm.")
    if "idempotency_keys" in on and s["already_executed"]:
        return out("deduplicated", "idempotency_keys", "Same idempotency key as a completed request; the saved result is returned.")
    return out("executed", None, "All enabled checks passed.")


def summarize(results):
    by_id = {s["id"]: s for s in SCENARIOS}
    return {
        "harmful_executed": sum(r["harm"] for r in results),
        "legitimate_stopped": sum(1 for r in results if not by_id[r["scenario"]]["harmful"] and r["outcome"] in ("blocked", "held")),
        "held_for_person": sum(r["outcome"] == "held" for r in results),
    }


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Evaluate the fictional guard scenarios against a set of defenses.")
    p.add_argument("--defenses", default=",".join(DEFENSES), help="Comma-separated list; empty for none.")
    args = p.parse_args()
    chosen = [d for d in args.defenses.split(",") if d]
    results = [gate(s, chosen) for s in SCENARIOS]
    for r in results:
        print(f"{r['scenario']:<26} {r['outcome']:<13} {r['by'] or '-':<18} {'HARM' if r['harm'] else ''}")
    print(json.dumps(summarize(results)))
