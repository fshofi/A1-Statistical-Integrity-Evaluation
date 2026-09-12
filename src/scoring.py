"""Amended scoring layer with explicit applicability and denominator reporting."""
from __future__ import annotations

from typing import Any

from src.parsing import evaluate_response, load_policy

def score_case(response: Any, reference: dict[str, Any], review: Any = None, **_: Any) -> dict[str, Any]:
    if review is not None:
        raise ValueError("semantic reviews must be validated and stored as response-bound per-dimension records; they are not silently merged into deterministic scoring")
    result = evaluate_response(reference["case_id"], response, reference, load_policy())
    result.update({
        "qualitative_status": "RUBRIC_HUMAN_REVIEW_REQUIRED",
        "dimension_scores": None,
        "failure_codes": [],
        "overall_score": None,
    })
    return result


def summarize_scores(rows: list[dict[str, Any]]) -> dict[str, Any]:
    applicable = [row for row in rows if row["numeric_applicability"] == "APPLICABLE"]
    evaluated = [row for row in applicable if row["mathematical_correctness"] in {"PASS", "FAIL"}]
    passed = [row for row in evaluated if row["mathematical_correctness"] == "PASS"]
    non_applicable = [row for row in rows if row["numeric_applicability"] == "NOT_APPLICABLE"]
    return {
        "case_count": len(rows),
        "response_present_count": sum(row["response_present"] == "PASS" for row in rows),
        "response_completeness_denominator": len(rows),
        "numeric_applicable_case_count": len(applicable),
        "numeric_non_applicable_case_count": len(non_applicable),
        "numeric_evaluated_case_count": len(evaluated),
        "numeric_pass_count": len(passed),
        "numeric_correctness_denominator": len(evaluated),
        "numeric_coverage_denominator": len(applicable),
        "numeric_unevaluated_applicable_count": len(applicable) - len(evaluated),
        "semantic_reviewed_decision_count": 0,
        "semantic_review_status": "RUBRIC_HUMAN_REVIEW_REQUIRED",
        "leaderboard_eligible": False,
        "leaderboard_note": "No leaderboard: non-applicable items are excluded and missing/unparsed items are not counted as passes.",
    }
