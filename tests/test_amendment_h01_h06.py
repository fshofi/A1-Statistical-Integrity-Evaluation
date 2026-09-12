import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.clean_replay import execute_replay
from src.checker import load_references
from src.parsing import evaluate_response, load_policy, parse_response, unit_status
from src.schemas import SchemaError, UNAVAILABLE, validate_run_manifest, validate_semantic_review

ROOT = Path(__file__).resolve().parents[1]
REFERENCES = {row["case_id"]: row for row in load_references()}
POLICY = load_policy()


class H01RequestedVsSupplementalTests(unittest.TestCase):
    def test_policy_covers_all_cases_and_40_requested_values(self):
        self.assertEqual(set(POLICY["cases"]), set(REFERENCES))
        self.assertEqual(sum(len(x["required_numeric_fields"]) for x in POLICY["cases"].values()), 40)
        self.assertEqual({k: v["supplemental_numeric_fields"] for k, v in POLICY["cases"].items() if v["supplemental_numeric_fields"]}, {"Q731": ["coverage_narrow"]})
        for case_id, case_policy in POLICY["cases"].items():
            self.assertEqual(set(case_policy["required_numeric_fields"]) | set(case_policy["supplemental_numeric_fields"]), set(REFERENCES[case_id]["numeric"]))

    def test_q731_requested_fields_only_passes(self):
        response = {"numeric": {
            "nominal_lower": {"value": 10.040036, "unit": "measurement units"},
            "nominal_upper": {"value": 13.959964, "unit": "measurement units"},
        }}
        result = evaluate_response("Q731", response, REFERENCES["Q731"], POLICY)
        self.assertEqual(result["required_fields_present"], "PASS")
        self.assertEqual(result["mathematical_correctness"], "PASS")
        self.assertEqual(result["supplemental_reference_fields_excluded"], ["coverage_narrow"])


class H02ToleranceTests(unittest.TestCase):
    def evaluate(self, value):
        return evaluate_response("Q195", {"numeric": {"fault_given_negative": {"value": value, "unit": "proportion"}}}, REFERENCES["Q195"], POLICY)

    def test_exact_value_accepted(self):
        self.assertEqual(self.evaluate(0.005509641873278237)["mathematical_correctness"], "PASS")

    def test_valid_six_decimal_rounding_accepted(self):
        self.assertEqual(self.evaluate(0.005510)["mathematical_correctness"], "PASS")

    def test_materially_incorrect_nearby_value_rejected(self):
        self.assertEqual(self.evaluate(0.005512)["mathematical_correctness"], "FAIL")


class H03ParsingAndUnitTests(unittest.TestCase):
    def test_canonical_unit(self):
        self.assertEqual(unit_status("proportion (0 to 1)", "proportion", POLICY), "CANONICAL")

    def test_equivalent_unit(self):
        self.assertEqual(unit_status("proportion", "proportion", POLICY), "EQUIVALENT_ALIAS")

    def test_incompatible_unit(self):
        self.assertEqual(unit_status("percent", "proportion", POLICY), "INCOMPATIBLE")

    def test_original_submitted_unit_is_preserved(self):
        result = evaluate_response("Q195", {"fault_given_negative": {"value": 0.005510, "unit": "PROPORTION"}}, REFERENCES["Q195"], POLICY)
        self.assertEqual(result["field_results"]["fault_given_negative"]["submitted_unit"], "PROPORTION")

    def test_valid_json(self):
        parsed = parse_response('{"numeric":{"fault_given_negative":{"value":0.005510,"unit":"proportion"}}}', ["fault_given_negative"])
        self.assertEqual(parsed.status, "VALID_JSON")

    def test_valid_json_like(self):
        parsed = parse_response("{'numeric': {'fault_given_negative': {'value': 0.005510, 'unit': 'proportion'}}}", ["fault_given_negative"])
        self.assertEqual(parsed.status, "VALID_JSON_LIKE")

    def test_plain_text_number(self):
        parsed = parse_response("0.005510 proportion", ["fault_given_negative"])
        self.assertEqual(parsed.status, "PLAIN_TEXT_NUMBER")
        self.assertAlmostEqual(parsed.values["fault_given_negative"]["value"], 0.005510)

    def test_duplicate_json_key_rejected(self):
        parsed = parse_response('{"numeric":{"fault_given_negative":0.1,"fault_given_negative":0.2}}', ["fault_given_negative"])
        self.assertEqual(parsed.status, "DUPLICATE_KEYS")

    def test_duplicate_json_like_key_rejected(self):
        parsed = parse_response("{'fault_given_negative': 0.1, 'fault_given_negative': 0.2}", ["fault_given_negative"])
        self.assertEqual(parsed.status, "DUPLICATE_KEYS")

    def test_malformed_separate_from_math_failure(self):
        result = evaluate_response("Q195", "not a parseable numeric response", REFERENCES["Q195"], POLICY)
        self.assertEqual(result["parse_status"], "UNPARSED")
        self.assertEqual(result["mathematical_correctness"], "NOT_EVALUATED")


class H04ApplicabilityTests(unittest.TestCase):
    def test_empty_nonnumeric_cases_fail_completeness_not_math(self):
        for case_id in ("Q187", "Q639", "Q542", "Q976"):
            with self.subTest(case_id=case_id):
                result = evaluate_response(case_id, "", REFERENCES[case_id], POLICY)
                self.assertEqual(result["response_present"], "FAIL")
                self.assertEqual(result["numeric_applicability"], "NOT_APPLICABLE")
                self.assertEqual(result["required_fields_present"], "NOT_APPLICABLE")
                self.assertEqual(result["mathematical_correctness"], "NOT_APPLICABLE")


def valid_manifest():
    return {
        "schema_version": "A1-RUN-MANIFEST-1.1", "run_id": "run-1", "provider": "provider",
        "model_name": "model", "model_version_identifier": UNAVAILABLE, "interface_runtime": "api",
        "reasoning_setting": UNAVAILABLE, "utc_start_time": "2026-01-01T00:00:00Z", "utc_end_time": "2026-01-01T00:01:00Z",
        "exact_user_prompt_template": "{case}", "exact_case_payload": [{"id": "Q1"}],
        "exact_system_prompt": UNAVAILABLE, "exact_developer_prompt": UNAVAILABLE,
        "temperature": UNAVAILABLE, "top_p": UNAVAILABLE, "maximum_output_tokens": UNAVAILABLE,
        "tool_access": "none", "browser_access": "none", "memory_access": "none",
        "retrieval_project_context_access": "none", "context_isolation_method": "new context",
        "case_execution_order": ["Q1"], "retry_policy": "none", "timeout_handling": "record error",
        "truncation_handling": "record truncation", "refusal_handling": "preserve refusal",
        "model_provider_errors": [], "collector_software_version": "collector-1",
        "source_repository_sha256": "a" * 64, "case_set_sha256": "b" * 64, "raw_response_sha256": "c" * 64,
    }


class H05ManifestTests(unittest.TestCase):
    def test_required_provenance_or_unavailable_marker_validates(self):
        self.assertEqual(validate_run_manifest(valid_manifest())["temperature"], UNAVAILABLE)

    def test_missing_field_rejected(self):
        value = valid_manifest(); del value["tool_access"]
        with self.assertRaises(SchemaError): validate_run_manifest(value)

    def test_null_unexposed_setting_rejected(self):
        value = valid_manifest(); value["temperature"] = None
        with self.assertRaises(SchemaError): validate_run_manifest(value)

    def test_vague_unavailable_setting_rejected(self):
        value = valid_manifest(); value["temperature"] = "unknown"
        with self.assertRaises(SchemaError): validate_run_manifest(value)


def valid_review():
    return {
        "schema_version": "A1-SEMANTIC-REVIEW-1.1", "run_id": "run-1", "case_id": "Q195",
        "raw_response_sha256": hashlib.sha256(b"answer").hexdigest(), "reviewer_identity": "reviewer-1",
        "reviewer_role": "independent statistical reviewer", "reviewer_system_model": "human",
        "review_timestamp": "2026-01-01T01:00:00Z", "rubric_version": "A1-RUBRIC-1.1",
        "dimension": "evidence", "score": 2, "rationale": "The response uses the stated data.",
        "confidence": None, "adjudication_status": "UNADJUDICATED",
    }


class H06SemanticReviewTests(unittest.TestCase):
    def test_bound_review_validates(self):
        self.assertEqual(validate_semantic_review(valid_review())["score"], 2)

    def test_response_hash_required(self):
        value = valid_review(); del value["raw_response_sha256"]
        with self.assertRaises(SchemaError): validate_semantic_review(value)

    def test_reviewer_provenance_required(self):
        value = valid_review(); del value["reviewer_identity"]
        with self.assertRaises(SchemaError): validate_semantic_review(value)

    def test_rationale_and_rubric_required(self):
        value = valid_review(); value["rationale"] = ""
        with self.assertRaises(SchemaError): validate_semantic_review(value)


class ReplayHardeningTests(unittest.TestCase):
    def test_no_preexisting_output_and_real_checker_writes(self):
        result = execute_replay(ROOT / "baseline" / "a1_revision_bundle")
        self.assertFalse(result["generated_preexisted"])
        self.assertTrue(result["generated_file_exists"])
        self.assertEqual(result["expected_normalized_sha256"], result["generated_normalized_sha256"])
        self.assertTrue(result["passed"])

    def test_successful_no_write_checker_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle = Path(temp) / "bundle"
            (bundle / "revision").mkdir(parents=True)
            (bundle / "revision" / "checker_answers_rev2.jsonl").write_text('{"case_id":"Q1"}\n', encoding="utf-8")
            (bundle / "revision" / "checker_code_rev2.py").write_text("pass\n", encoding="utf-8")
            result = execute_replay(bundle)
            self.assertEqual(result["checker_exit_code"], 0)
            self.assertFalse(result["generated_file_exists"])
            self.assertFalse(result["passed"])


if __name__ == "__main__":
    unittest.main()
