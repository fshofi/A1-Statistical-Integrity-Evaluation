"""A1 V1.1 controls for selection survivorship and observable reasoning lineage.

These controls do not claim access to hidden chain-of-thought.  They audit the
observable evidence record: submitted cases, attempts, preserved outputs,
declared exclusions, review artifacts, conclusions, and authority boundaries.
"""
from __future__ import annotations

import hashlib
from collections import defaultdict
from pathlib import Path
from typing import Any

ALLOWED_OUTCOMES = {"COMPLETED", "REFUSAL", "TIMEOUT", "TRUNCATED", "PROVIDER_ERROR"}
ALLOWED_SELECTION_METHODS = {"PURPOSIVE_DESIGNED_CONTRASTS", "PROBABILITY_SAMPLE"}
ALLOWED_PRIOR_ACTIVITY_STATUS = {"COMPLETE_REGISTER", "PARTIAL_REGISTER", "UNAVAILABLE_IN_FULL"}
OBSERVABLE_SCOPE = "OBSERVABLE_EVIDENCE_RECORD_ONLY"


class HardeningError(ValueError):
    """Raised when a hardening input is structurally invalid."""


def _nonempty(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise HardeningError(f"{name} must be a non-empty string")
    return value


def _response_sha256(value: Any) -> str:
    if isinstance(value, str):
        payload = value.encode("utf-8")
    else:
        import json
        payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def audit_selection(
    expected_case_ids: list[str],
    responses: list[dict[str, Any]],
    provenance_case_ids: list[str],
    attempts: list[dict[str, Any]],
    design: dict[str, Any],
) -> dict[str, Any]:
    """Audit selection and attrition without converting a selected set into a population.

    A critical inconsistency fails closed.  Residual uncertainty about earlier
    development activity or population representativeness produces a
    conditional pass and blocks population-level claims.
    """
    if not expected_case_ids or len(expected_case_ids) != len(set(expected_case_ids)):
        raise HardeningError("expected_case_ids must be a non-empty unique list")
    if design.get("schema_version") != "A1-SELECTION-DESIGN-1.2":
        raise HardeningError("selection design schema_version must be A1-SELECTION-DESIGN-1.2")

    selection_method = _nonempty(design.get("selection_method"), "selection_method")
    if selection_method not in ALLOWED_SELECTION_METHODS:
        raise HardeningError(f"unsupported selection_method: {selection_method}")
    prior_status = _nonempty(
        design.get("prior_development_activity_register_status"),
        "prior_development_activity_register_status",
    )
    if prior_status not in ALLOWED_PRIOR_ACTIVITY_STATUS:
        raise HardeningError(f"invalid prior development status: {prior_status}")

    response_ids = [row.get("case_id") for row in responses]
    provenance_ids = list(provenance_case_ids)
    checks: list[dict[str, str]] = []

    def check(name: str, passed: bool, evidence: str, severity: str = "CRITICAL") -> None:
        checks.append({
            "check": name,
            "status": "PASS" if passed else "FAIL",
            "severity": severity,
            "evidence": evidence,
        })

    check(
        "response_universe_complete",
        response_ids == expected_case_ids and len(response_ids) == len(set(response_ids)),
        f"expected={len(expected_case_ids)}; preserved={len(response_ids)}; order_and_uniqueness_checked",
    )
    check(
        "provenance_universe_complete",
        provenance_ids == expected_case_ids and len(provenance_ids) == len(set(provenance_ids)),
        f"expected={len(expected_case_ids)}; provenance_records={len(provenance_ids)}",
    )

    invalid_response_metadata: list[str] = []
    response_hash_failures: list[str] = []
    for row in responses:
        case_id = str(row.get("case_id"))
        if type(row.get("retry_count")) is not int or row["retry_count"] < 0:
            invalid_response_metadata.append(f"{case_id}:retry_count")
        for field in ("failure_status", "refusal_status", "truncation_status"):
            if not isinstance(row.get(field), str) or not row[field]:
                invalid_response_metadata.append(f"{case_id}:{field}")
        expected_hash = row.get("response_sha256")
        if not isinstance(expected_hash, str) or expected_hash != _response_sha256(row.get("raw_model_response")):
            response_hash_failures.append(case_id)
    check("response_metadata_complete", not invalid_response_metadata, f"invalid={invalid_response_metadata}")
    check("response_hash_integrity", not response_hash_failures, f"mismatches={response_hash_failures}")

    attempts_by_case: dict[str, list[dict[str, Any]]] = defaultdict(list)
    attempt_ids: list[str] = []
    invalid_attempts: list[str] = []
    unpreserved_attempts: list[str] = []
    outcome_based_exclusions: list[str] = []
    for row in attempts:
        case_id = _nonempty(row.get("case_id"), "attempt.case_id")
        attempt_id = _nonempty(row.get("attempt_id"), "attempt.attempt_id")
        outcome = _nonempty(row.get("outcome"), "attempt.outcome")
        if outcome not in ALLOWED_OUTCOMES:
            invalid_attempts.append(attempt_id)
        if row.get("preserved") is not True:
            unpreserved_attempts.append(attempt_id)
        if row.get("exclusion_basis") == "OBSERVED_PERFORMANCE":
            outcome_based_exclusions.append(attempt_id)
        attempt_ids.append(attempt_id)
        attempts_by_case[case_id].append(row)

    check("attempt_ids_unique", len(attempt_ids) == len(set(attempt_ids)), f"attempts={len(attempt_ids)}")
    check("attempt_outcomes_valid", not invalid_attempts, f"invalid={invalid_attempts}")
    check("all_attempts_preserved", not unpreserved_attempts, f"unpreserved={unpreserved_attempts}")
    check(
        "no_outcome_based_exclusion",
        not outcome_based_exclusions and design.get("outcome_based_exclusions") == 0,
        f"attempt_exclusions={outcome_based_exclusions}; declared={design.get('outcome_based_exclusions')}",
    )

    missing_attempt_cases = [case_id for case_id in expected_case_ids if not attempts_by_case.get(case_id)]
    unexpected_attempt_cases = sorted(set(attempts_by_case) - set(expected_case_ids))
    check(
        "definitive_attempt_universe_complete",
        not missing_attempt_cases and not unexpected_attempt_cases,
        f"missing={missing_attempt_cases}; unexpected={unexpected_attempt_cases}",
    )

    retry_mismatches: list[str] = []
    selected_mismatches: list[str] = []
    selected_hash_mismatches: list[str] = []
    response_by_case = {row.get("case_id"): row for row in responses}
    for case_id in expected_case_ids:
        case_attempts = attempts_by_case.get(case_id, [])
        selected = [row for row in case_attempts if row.get("selected_for_scoring") is True]
        if len(selected) != 1:
            selected_mismatches.append(case_id)
        elif selected[0].get("response_sha256") != response_by_case.get(case_id, {}).get("response_sha256"):
            selected_hash_mismatches.append(case_id)
        declared_retry_count = response_by_case.get(case_id, {}).get("retry_count")
        if declared_retry_count is not None and declared_retry_count != max(0, len(case_attempts) - 1):
            retry_mismatches.append(case_id)
    check("one_selected_attempt_per_case", not selected_mismatches, f"mismatches={selected_mismatches}")
    check("selected_attempt_hash_bound", not selected_hash_mismatches, f"mismatches={selected_hash_mismatches}")
    check("retry_count_consistent", not retry_mismatches, f"mismatches={retry_mismatches}")

    critical_failures = [row for row in checks if row["status"] == "FAIL" and row["severity"] == "CRITICAL"]
    execution_attrition_observed = any(
        row.get("outcome") != "COMPLETED" for row in attempts if row.get("case_id") in set(expected_case_ids)
    )
    representative = selection_method == "PROBABILITY_SAMPLE" and bool(design.get("target_population"))
    historical_registry_complete = prior_status == "COMPLETE_REGISTER"

    residual_flags: list[dict[str, str]] = []
    if not representative:
        residual_flags.append({
            "flag": "POPULATION_REPRESENTATIVENESS_NOT_ESTABLISHED",
            "consequence": "Results remain descriptive for the 24 selected cases; no population accuracy claim is admissible.",
        })
    if not historical_registry_complete:
        residual_flags.append({
            "flag": "PRIOR_DEVELOPMENT_ATTEMPT_UNIVERSE_INCOMPLETE",
            "consequence": "The definitive run is internally complete, but absence of all earlier pilot/corrective artifacts cannot be cryptographically proven.",
        })

    if critical_failures:
        status = "FAIL_CLOSED"
    elif residual_flags:
        status = "CONDITIONAL_PASS"
    else:
        status = "PASS"

    return {
        "schema_version": "A1-SELECTION-AUDIT-1.2",
        "status": status,
        "analysis_complete": not critical_failures,
        "population_claim_authorised": False,
        "selected_case_claim_authorised": not critical_failures,
        "expected_case_count": len(expected_case_ids),
        "preserved_response_count": len(response_ids),
        "attempt_count": len(attempts),
        "execution_attrition_observed": execution_attrition_observed,
        "selection_method": selection_method,
        "prior_development_activity_register_status": prior_status,
        "checks": checks,
        "residual_flags": residual_flags,
        "scope_note": "This is an internal-consistency and disclosure control, not proof that unrecorded attempts never existed.",
    }


def audit_reasoning_chain(record: dict[str, Any], artifact_root: Path | None = None) -> dict[str, Any]:
    """Audit an observable reasoning record without claiming hidden-thought access."""
    required = {
        "schema_version",
        "scope",
        "hidden_chain_of_thought_claimed",
        "evidence_artifacts",
        "evidence_artifact_sha256",
        "assumptions_review_status",
        "method_review_status",
        "uncertainty_review_status",
        "discarded_alternatives_capture",
        "conclusion_review_status",
        "authority_boundary",
        "structured_semantic_review_status",
        "reviewer_independence_status",
    }
    missing = sorted(required - set(record))
    if missing:
        raise HardeningError(f"reasoning record missing fields: {missing}")
    if record["schema_version"] != "A1-OBSERVABLE-REASONING-RECORD-1.2":
        raise HardeningError("reasoning record schema_version must be A1-OBSERVABLE-REASONING-RECORD-1.2")
    if record["scope"] != OBSERVABLE_SCOPE:
        raise HardeningError(f"scope must be {OBSERVABLE_SCOPE}")
    if not isinstance(record["evidence_artifacts"], list) or not record["evidence_artifacts"]:
        raise HardeningError("evidence_artifacts must be a non-empty list")
    if not isinstance(record["evidence_artifact_sha256"], dict):
        raise HardeningError("evidence_artifact_sha256 must be an object")

    artifact_failures: list[str] = []
    for relative in record["evidence_artifacts"]:
        expected_hash = record["evidence_artifact_sha256"].get(relative)
        if not isinstance(expected_hash, str) or len(expected_hash) != 64:
            artifact_failures.append(f"{relative}:missing_or_invalid_hash")
            continue
        if artifact_root is not None:
            target = artifact_root / relative
            if not target.is_file():
                artifact_failures.append(f"{relative}:missing")
            elif hashlib.sha256(target.read_bytes()).hexdigest() != expected_hash:
                artifact_failures.append(f"{relative}:hash_mismatch")

    checks = [
        {
            "check": "no_hidden_chain_of_thought_claim",
            "status": "PASS" if record["hidden_chain_of_thought_claimed"] is False else "FAIL",
            "severity": "CRITICAL",
            "evidence": "A1 audits observable artifacts only.",
        },
        {
            "check": "evidence_lineage_present",
            "status": "PASS" if len(record["evidence_artifacts"]) >= 4 and not artifact_failures else "FAIL",
            "severity": "CRITICAL",
            "evidence": f"artifact_count={len(record['evidence_artifacts'])}; failures={artifact_failures}",
        },
        {
            "check": "authority_boundary_explicit",
            "status": "PASS" if record["authority_boundary"] == "EVALUATION_ONLY_NO_EXECUTION_AUTHORITY" else "FAIL",
            "severity": "CRITICAL",
            "evidence": str(record["authority_boundary"]),
        },
    ]
    critical_failures = [row for row in checks if row["status"] == "FAIL"]

    residual_flags: list[dict[str, str]] = []
    if record["discarded_alternatives_capture"] != "SYSTEMATICALLY_CAPTURED":
        residual_flags.append({
            "flag": "DISCARDED_ALTERNATIVES_NOT_SYSTEMATICALLY_CAPTURED",
            "consequence": "Run 1 cannot support a claim that every plausible alternative was considered.",
        })
    if record["structured_semantic_review_status"] != "COMPLETE":
        residual_flags.append({
            "flag": "STRUCTURED_SEMANTIC_REVIEW_INCOMPLETE",
            "consequence": "Attributed narrative adjudication exists, but the 168-record structured review queue remains unscored.",
        })
    if record["reviewer_independence_status"] != "INDEPENDENT_HUMAN_REVIEW":
        residual_flags.append({
            "flag": "INDEPENDENT_HUMAN_VALIDATION_ABSENT",
            "consequence": "AI-assisted and architect-led review must not be described as independent human validation.",
        })

    if critical_failures:
        status = "FAIL_CLOSED"
    elif residual_flags:
        status = "CONDITIONAL_PASS"
    else:
        status = "PASS"
    return {
        "schema_version": "A1-OBSERVABLE-REASONING-AUDIT-1.2",
        "status": status,
        "analysis_complete": not critical_failures,
        "execution_authorised": False,
        "checks": checks,
        "residual_flags": residual_flags,
        "scope_note": "Observable evidence lineage is auditable; hidden model cognition is neither observed nor reconstructed.",
    }
