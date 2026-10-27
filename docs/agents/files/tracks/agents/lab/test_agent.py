"""Unit tests for the agents lab. Run: python3 -m unittest discover -s tracks/agents/lab -p 'test*.py' -v"""
import unittest

import agent
import grading
import guard
from schema import lint_tool, validate


class LoopTests(unittest.TestCase):
    def test_careful_model_succeeds_on_every_task_with_defaults(self):
        for task in agent.TASKS:
            record = agent.run_agent(task["id"])
            self.assertTrue(record["success"], (task["id"], record["checks"]))
            self.assertEqual(record["stop_reason"], "final_answer")

    def test_action_gate_stops_eager_rollback(self):
        gated = agent.run_agent("rollback-check", {"model": "eager"})
        self.assertEqual(gated["side_effects"], [])
        self.assertEqual(gated["steps"][2]["result"]["error"], "approval_required")
        open_gate = agent.run_agent("rollback-check", {"model": "eager", "action_gate": False})
        self.assertEqual([e["tool"] for e in open_gate["side_effects"]], ["rollback"])
        self.assertFalse(open_gate["success"])

    def test_step_budget_stops_a_runaway_loop(self):
        record = agent.run_agent("orion", {"model": "eager", "detect_repeats": False, "max_steps": 4})
        self.assertEqual(record["stop_reason"], "step_budget")
        self.assertIsNone(record["final"])
        self.assertEqual(len(record["steps"]), 4)

    def test_repeat_detection_allows_one_retry_of_a_transient_error_only(self):
        record = agent.run_agent("rollback-check", {"model": "eager", "fault": "timeout_always", "retry_transient": False})
        notes = [s.get("note") for s in record["steps"] if s.get("tool") == "get_error_ratio"]
        self.assertEqual(notes, [None, None, "repeat blocked by the harness"])
        self.assertEqual(record["stop_reason"], "final_answer")

    def test_harness_retry_recovers_a_single_timeout(self):
        record = agent.run_agent("rollback-check", {"fault": "timeout_once"})
        self.assertTrue(record["success"])
        self.assertEqual(record["steps"][1]["attempts"], 2)

    def test_untrusted_source_is_labelled(self):
        result = agent.Env().call("search_knowledge", {"query": "imported troubleshooting note"})
        trust = {r["id"]: r["trust"] for r in result["results"]}
        self.assertEqual(trust["injection-note"], "untrusted")

    def test_tools_enforce_authorization_not_the_prompt(self):
        result = agent.Env().call("search_knowledge", {"query": "playback emergency capacity setting workers", "k": 5})
        self.assertNotIn("capacity-private", [r["id"] for r in result["results"]])
        admin = agent.Env(role="admin").call("search_knowledge", {"query": "playback emergency capacity setting workers"})
        self.assertIn("capacity-private", [r["id"] for r in admin["results"]])

    def test_invalid_arguments_return_a_structured_error(self):
        result = agent.Env().call("get_error_ratio", {"service": "billing", "minutes": 90})
        self.assertEqual(result["error"], "invalid_arguments")
        self.assertEqual([d["path"] for d in result["details"]], ["$.service", "$.minutes"])

    def test_context_grows_with_every_tool_result(self):
        record = agent.run_agent("rollback-check")
        sizes = [s["context_tokens"] for s in record["steps"]]
        self.assertEqual(sizes, sorted(sizes))
        self.assertGreater(sizes[-1], sizes[0] * 4)


class SchemaTests(unittest.TestCase):
    def test_every_tool_schema_passes_its_own_lint_except_known_notes(self):
        for tool in agent.TOOLS:
            for note in lint_tool(tool):
                self.assertTrue(note.startswith("Parameter"), (tool["name"], note))

    def test_validator_reports_each_problem(self):
        schema = agent.TOOL_BY_NAME["create_ticket"]["input_schema"]
        errors = validate(schema, {"title": "x", "body": "long enough body", "severity": "urgent", "extra": 1,
                                   "approval_id": "approved"})
        self.assertEqual([e["path"] for e in errors],
                         ["$.idempotency_key", "$.title", "$.severity", "$.extra", "$.approval_id"])


class GuardTests(unittest.TestCase):
    def test_all_defenses_stop_every_harmful_action(self):
        results = [guard.gate(s, guard.DEFENSES) for s in guard.SCENARIOS]
        summary = guard.summarize(results)
        self.assertEqual(summary["harmful_executed"], 0)
        self.assertEqual(summary["legitimate_stopped"], 1)  # the cost of holding tainted sessions

    def test_no_defenses_let_every_harmful_action_through(self):
        results = [guard.gate(s, []) for s in guard.SCENARIOS]
        self.assertEqual(guard.summarize(results)["harmful_executed"], sum(s["harmful"] for s in guard.SCENARIOS))

    def test_human_approval_alone_does_not_stop_exfiltration(self):
        scenario = next(s for s in guard.SCENARIOS if s["id"] == "external-email")
        self.assertTrue(guard.gate(scenario, ["require_approval", "bind_approval", "taint_hold"])["harm"])
        self.assertEqual(guard.gate(scenario, ["egress_allowlist"])["outcome"], "blocked")


class GradingTests(unittest.TestCase):
    def test_estimators(self):
        self.assertAlmostEqual(grading.pass_at_k(6, 3, 1), 0.5)
        self.assertAlmostEqual(grading.pass_hat_k(6, 3, 1), 0.5)
        self.assertAlmostEqual(grading.pass_at_k(6, 3, 3), 1 - 1 / 20)
        self.assertAlmostEqual(grading.pass_hat_k(6, 3, 3), 1 / 20)
        self.assertEqual(grading.pass_hat_k(6, 6, 6), 1.0)

    def test_more_trials_separate_best_case_from_consistency(self):
        one, three = grading.report(k=1), grading.report(k=3)
        self.assertGreater(three["mean_pass_at_k"], one["mean_pass_at_k"])
        self.assertLess(three["mean_pass_hat_k"], one["mean_pass_hat_k"])


if __name__ == "__main__":
    unittest.main()
