import copy
import json
import unittest
from pathlib import Path

from src.checker import load_cases, load_jsonl
from scripts.run_v1_2_hardening import outcome_for
from src.hardening import HardeningError, audit_reasoning_chain, audit_selection

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs" / "run1"


def fixture():
    expected = [row["id"] for row in load_cases()]
    responses = load_jsonl(RUN / "raw_model_responses.jsonl")
    provenance = json.loads((RUN / "definitive_task_provenance.json").read_text(encoding="utf-8"))
    provenance_ids = [row["case_id"] for row in provenance["tasks"]]
    attempts = [
        {
            "case_id": row["case_id"],
            "attempt_id": row["task_id"],
            "outcome": "COMPLETED",
            "preserved": True,
            "selected_for_scoring": True,
            "exclusion_basis": "NONE",
            "response_sha256": row["response_sha256"],
        }
        for row in responses
    ]
    design = json.loads((ROOT / "config" / "selection_design_v1_2.json").read_text(encoding="utf-8"))
    return expected, responses, provenance_ids, attempts, design


class SurvivorSelectionTests(unittest.TestCase):
    def test_reference_run_is_conditional_not_population_pass(self):
        result = audit_selection(*fixture())
        self.assertEqual(result["status"], "CONDITIONAL_PASS")
        self.assertFalse(result["population_claim_authorised"])
        self.assertTrue(result["selected_case_claim_authorised"])
        self.assertFalse(result["execution_attrition_observed"])

    def test_missing_failed_case_fails_closed(self):
        expected, responses, provenance, attempts, design = fixture()
        result = audit_selection(expected, responses[:-1], provenance, attempts[:-1], design)
        self.assertEqual(result["status"], "FAIL_CLOSED")
        self.assertFalse(result["selected_case_claim_authorised"])

    def test_cherry_picked_exclusion_fails_closed(self):
        expected, responses, provenance, attempts, design = fixture()
        attempts[2]["exclusion_basis"] = "OBSERVED_PERFORMANCE"
        attempts[2]["selected_for_scoring"] = False
        design["outcome_based_exclusions"] = 1
        result = audit_selection(expected, responses, provenance, attempts, design)
        self.assertEqual(result["status"], "FAIL_CLOSED")

    def test_unpreserved_retry_fails_closed(self):
        expected, responses, provenance, attempts, design = fixture()
        extra = copy.deepcopy(attempts[0])
        extra["attempt_id"] = "unpreserved-first-attempt"
        extra["preserved"] = False
        extra["selected_for_scoring"] = False
        attempts.insert(0, extra)
        responses[0]["retry_count"] = 1
        result = audit_selection(expected, responses, provenance, attempts, design)
        self.assertEqual(result["status"], "FAIL_CLOSED")

    def test_tampered_response_fails_closed(self):
        expected, responses, provenance, attempts, design = fixture()
        responses[0]["raw_model_response"] += " tampered"
        result = audit_selection(expected, responses, provenance, attempts, design)
        self.assertEqual(result["status"], "FAIL_CLOSED")

    def test_selected_attempt_must_bind_response_hash(self):
        expected, responses, provenance, attempts, design = fixture()
        attempts[0]["response_sha256"] = "0" * 64
        result = audit_selection(expected, responses, provenance, attempts, design)
        self.assertEqual(result["status"], "FAIL_CLOSED")

    def test_declared_complete_probability_sample_still_needs_separate_inference(self):
        expected, responses, provenance, attempts, design = fixture()
        design["selection_method"] = "PROBABILITY_SAMPLE"
        design["target_population"] = "defined synthetic frame"
        design["prior_development_activity_register_status"] = "COMPLETE_REGISTER"
        result = audit_selection(expected, responses, provenance, attempts, design)
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(result["population_claim_authorised"])


class ObservableReasoningTests(unittest.TestCase):
    def record(self):
        return json.loads((ROOT / "config" / "observable_reasoning_record_v1_2.json").read_text(encoding="utf-8"))

    def test_reference_record_is_conditional(self):
        result = audit_reasoning_chain(self.record(), ROOT)
        self.assertEqual(result["status"], "CONDITIONAL_PASS")
        self.assertFalse(result["execution_authorised"])

    def test_hidden_chain_claim_fails_closed(self):
        record = self.record()
        record["hidden_chain_of_thought_claimed"] = True
        self.assertEqual(audit_reasoning_chain(record)["status"], "FAIL_CLOSED")

    def test_missing_authority_boundary_fails_closed(self):
        record = self.record()
        record["authority_boundary"] = "AUTOMATIC_ACTION"
        self.assertEqual(audit_reasoning_chain(record)["status"], "FAIL_CLOSED")

    def test_missing_required_field_is_rejected(self):
        record = self.record()
        del record["scope"]
        with self.assertRaises(HardeningError):
            audit_reasoning_chain(record)

    def test_tampered_evidence_fails_closed(self):
        record = self.record()
        record["evidence_artifact_sha256"]["data/cases.jsonl"] = "0" * 64
        self.assertEqual(audit_reasoning_chain(record, ROOT)["status"], "FAIL_CLOSED")

    def test_refusal_and_truncation_are_not_classified_as_completed(self):
        base = {"failure_status": "NONE", "refusal_status": "NONE", "truncation_status": "NONE"}
        refusal = dict(base, refusal_status="REFUSED")
        truncated = dict(base, truncation_status="OUTPUT_LIMIT")
        self.assertEqual(outcome_for(refusal), "REFUSAL")
        self.assertEqual(outcome_for(truncated), "TRUNCATED")


if __name__ == "__main__":
    unittest.main()
