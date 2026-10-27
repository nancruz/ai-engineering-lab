"""Run an agent task and print or save its trajectory.

Examples (from the repository root):
  python3 tracks/agents/lab/run.py --task rollback-check
  python3 tracks/agents/lab/run.py --task orion --model scripted:eager --no-repeat-check
  python3 tracks/agents/lab/run.py --task rollback-check --model ollama:qwen3 --out projects/ops-agent/artifacts/runs/first.json
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from agent import FAULTS, TASKS, run_agent, compact  # noqa: E402


def show(record):
    print(f"task: {record['task']}   options: {compact(record['options'])}")
    for s in record["steps"]:
        if "final" in s:
            print(f"\n[{s['n']}] FINAL  (context ~{s['context_tokens']} tokens)\n    {s['final']}")
            continue
        print(f"\n[{s['n']}] {s['tool']}({compact(s['args'])})  (context ~{s['context_tokens']} tokens)")
        if s["note"]:
            print(f"    note: {s['note']}")
        text = compact(s["result"])
        print("    -> " + (text if len(text) < 300 else text[:300] + " ..."))
    print(f"\nstop reason: {record['stop_reason']}")
    print(f"side effects: {compact(record['side_effects'])}")
    for name, ok in record["checks"].items():
        print(f"  [{'x' if ok else ' '}] {name}")
    print("SUCCESS" if record["success"] else "NOT SUCCESSFUL")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--task", choices=[t["id"] for t in TASKS], required=True)
    p.add_argument("--model", default="scripted:careful", help="scripted:careful, scripted:eager or ollama:<tag>")
    p.add_argument("--max-steps", type=int, default=6)
    p.add_argument("--fault", choices=FAULTS, default="none")
    p.add_argument("--no-retry", action="store_true", help="do not retry transient tool errors in the harness")
    p.add_argument("--no-repeat-check", action="store_true", help="allow identical repeated calls")
    p.add_argument("--no-gate", action="store_true", help="let side-effecting tools run without approval (fictional world only)")
    p.add_argument("--out", help="save the full record (and raw model log) as JSON")
    a = p.parse_args()
    options = {"max_steps": a.max_steps, "fault": a.fault, "retry_transient": not a.no_retry,
               "detect_repeats": not a.no_repeat_check, "action_gate": not a.no_gate}
    model = None
    kind, _, name = a.model.partition(":")
    if kind == "scripted":
        options["model"] = name
    elif kind == "ollama":
        from real_model import OllamaModel
        model = OllamaModel(name)
        options["model"] = a.model
    else:
        p.error("unknown --model")
    record = run_agent(a.task, options, model)
    show(record)
    if a.out:
        if model is not None:
            record["model_log"] = model.log
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(record, indent=2))
        print(f"saved {a.out}")


if __name__ == "__main__":
    main()
