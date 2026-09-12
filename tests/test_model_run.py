import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.checker import CASES_PATH, load_cases, load_references
from src.schemas import UNAVAILABLE

ROOT = Path(__file__).resolve().parents[1]


class ModelRunTests(unittest.TestCase):
    def test_amended_pipeline_and_denominators(self):
        with tempfile.TemporaryDirectory(prefix="a1-amended-pipeline-") as temp:
            temp = Path(temp); responses = temp / "responses.jsonl"
            refs = {x["case_id"]: x for x in load_references()}; cases = load_cases()
            rows = [{"case_id": case["id"], "raw_model_response": {"numeric": refs[case["id"]]["numeric"]}} for case in cases]
            responses.write_text("".join(json.dumps(x) + "\n" for x in rows), encoding="utf-8")
            manifest = {
                "schema_version": "A1-RUN-MANIFEST-1.1", "run_id": "fixture", "provider": "test",
                "model_name": "fixture", "model_version_identifier": UNAVAILABLE, "interface_runtime": "unittest",
                "reasoning_setting": UNAVAILABLE, "utc_start_time": "2026-01-01T00:00:00Z", "utc_end_time": "2026-01-01T00:01:00Z",
                "exact_user_prompt_template": "fixture", "exact_case_payload": cases,
                "exact_system_prompt": UNAVAILABLE, "exact_developer_prompt": UNAVAILABLE,
                "temperature": UNAVAILABLE, "top_p": UNAVAILABLE, "maximum_output_tokens": UNAVAILABLE,
                "tool_access": "none", "browser_access": "none", "memory_access": "none", "retrieval_project_context_access": "none",
                "context_isolation_method": "fixture", "case_execution_order": [x["id"] for x in cases], "retry_policy": "none",
                "timeout_handling": "fail", "truncation_handling": "fail", "refusal_handling": "preserve", "model_provider_errors": [],
                "collector_software_version": "test", "source_repository_sha256": "a" * 64,
                "case_set_sha256": hashlib.sha256(CASES_PATH.read_bytes()).hexdigest(),
                "raw_response_sha256": hashlib.sha256(responses.read_bytes()).hexdigest(),
            }
            manifest_path = temp / "manifest.json"; manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            output = temp / "output"
            run = subprocess.run([sys.executable, str(ROOT / "scripts/run_benchmark.py"), str(responses), "--run-manifest", str(manifest_path), "--output-dir", str(output)], cwd=ROOT, text=True, capture_output=True, encoding="utf-8")
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            summary = json.loads((output / "summary.json").read_text())
            self.assertEqual(summary["case_count"], 24)
            self.assertEqual(summary["numeric_applicable_case_count"], 20)
            self.assertEqual(summary["numeric_non_applicable_case_count"], 4)
            self.assertEqual(summary["numeric_pass_count"], 20)
            self.assertEqual(summary["numeric_correctness_denominator"], 20)


if __name__ == "__main__": unittest.main()
