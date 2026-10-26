"""Verify output boundaries; these tests do not measure model quality."""
import unittest
import io
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from answer import validate_output, generate, main

class OutputBoundaryTests(unittest.TestCase):
    def test_unknown_source_rejected(self):
        with self.assertRaises(ValueError):
            validate_output({"answer": "x", "citations": ["invented"], "abstained": False}, {"real"})

    def test_answer_needs_source(self):
        with self.assertRaises(ValueError):
            validate_output({"answer": "x", "citations": [], "abstained": False}, {"real"})

    def test_abstention_does_not_claim_support(self):
        with self.assertRaises(ValueError):
            validate_output({"answer": "unknown", "citations": ["real"], "abstained": True}, {"real"})

    def test_schema_does_not_establish_truth(self):
        value = {"answer": "A wrong value can still pass a schema.", "citations": ["real"], "abstained": False}
        self.assertEqual(validate_output(value, {"real"}), value)

    def test_provider_receives_actual_evidence_and_bounded_output(self):
        raw = {"message": {"content": "{}"}}
        response = io.BytesIO(json.dumps(raw).encode())
        with patch("answer.urlopen", return_value=response) as request:
            self.assertEqual(generate("question", [{"id": "real", "text": "evidence"}],
                                      "test-double-model", "http://localhost:11434", 3), raw)
        payload = json.loads(request.call_args.args[0].data)
        self.assertFalse(payload["stream"])
        self.assertEqual(payload["options"]["num_predict"], 512)
        self.assertEqual(json.loads(payload["messages"][1]["content"])["evidence"][0]["text"], "evidence")

    def test_invalid_model_output_is_saved_and_fails(self):
        raw = {"message": {"content": "not json"}}
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "run.json"
            with patch("answer.generate", return_value=raw), patch("sys.argv", [
                "answer.py", "--model", "test-double-model", "--out", str(target)
            ]), patch("sys.stderr", new_callable=io.StringIO):
                with self.assertRaises(SystemExit) as exit_status:
                    main()
            self.assertEqual(exit_status.exception.code, 1)
            result = json.loads(target.read_text())
            self.assertIsNone(result["answer"])
            self.assertTrue(result["validation_error"])
            self.assertEqual(result["provider_response"], raw)
            self.assertTrue(result["evidence"])

if __name__ == "__main__":
    unittest.main()
