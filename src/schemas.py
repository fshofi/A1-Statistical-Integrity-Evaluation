"""Dependency-free validators for A1 records and amended provenance schemas."""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

DIMENSIONS = ("evidence", "assumptions", "method", "reasoning", "uncertainty", "validity", "conclusion")
FAILURE_CODES = {"N", "E", "A", "C", "U", "R", "M", "L", "X", "V", "VC"}
UNAVAILABLE = "UNAVAILABLE / NOT EXPOSED"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SCORES = {0, 1, 2}
ADJUDICATION_STATUSES = {"UNADJUDICATED", "AGREED", "DISAGREEMENT_UNRESOLVED", "ADJUDICATED", "SUPERSEDED"}


class SchemaError(ValueError):
    """Raised when an A1 record is structurally invalid."""


def _string(record: dict[str, Any], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SchemaError(f"{key!r} must be a non-empty string")
    return value


def _sha(record: dict[str, Any], key: str) -> str:
    value = _string(record, key)
    if not SHA256_RE.fullmatch(value):
        raise SchemaError(f"{key!r} must be a lowercase SHA-256 hex digest")
    return value


def _timestamp(record: dict[str, Any], key: str) -> str:
    value = _string(record, key)
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SchemaError(f"{key!r} must be an ISO-8601 timestamp") from exc
    return value


def validate_case(record: dict[str, Any]) -> dict[str, Any]:
    _string(record, "id")
    _string(record, "scenario")
    _string(record, "task")
    if "data" not in record:
        raise SchemaError("'data' is required")
    return record


def validate_reference(record: dict[str, Any]) -> dict[str, Any]:
    _string(record, "case_id")
    for key in ("derivation", "uncertainty", "conclusion", "minimum_repair", "execution_status"):
        _string(record, key)
    if not isinstance(record.get("numeric"), dict):
        raise SchemaError("'numeric' must be an object")
    if not isinstance(record.get("assumptions"), list) or not isinstance(record.get("ambiguities"), list):
        raise SchemaError("assumptions and ambiguities must be arrays")
    return record


@dataclass(frozen=True)
class ModelResponse:
    case_id: str
    response: Any


def validate_model_response(record: dict[str, Any]) -> ModelResponse:
    case_id = _string(record, "case_id")
    if "raw_model_response" in record:
        response = record["raw_model_response"]
    elif "response" in record:
        response = record["response"]
    else:
        raise SchemaError("'raw_model_response' is required (legacy 'response' is accepted)")
    return ModelResponse(case_id=case_id, response=response)


RUN_MANIFEST_FIELDS = {
    "schema_version", "run_id", "provider", "model_name", "model_version_identifier",
    "interface_runtime", "reasoning_setting", "utc_start_time", "utc_end_time",
    "exact_user_prompt_template", "exact_case_payload", "exact_system_prompt",
    "exact_developer_prompt", "temperature", "top_p", "maximum_output_tokens",
    "tool_access", "browser_access", "memory_access", "retrieval_project_context_access",
    "context_isolation_method", "case_execution_order", "retry_policy", "timeout_handling",
    "truncation_handling", "refusal_handling", "model_provider_errors",
    "collector_software_version", "source_repository_sha256", "case_set_sha256",
    "raw_response_sha256",
}


def validate_run_manifest(record: dict[str, Any]) -> dict[str, Any]:
    missing = RUN_MANIFEST_FIELDS - set(record)
    if missing:
        raise SchemaError(f"run manifest missing fields: {sorted(missing)}")
    for key in RUN_MANIFEST_FIELDS - {"exact_case_payload", "case_execution_order", "model_provider_errors", "temperature", "top_p", "maximum_output_tokens"}:
        _string(record, key)
    _timestamp(record, "utc_start_time")
    _timestamp(record, "utc_end_time")
    for key in ("source_repository_sha256", "case_set_sha256", "raw_response_sha256"):
        _sha(record, key)
    if not isinstance(record["exact_case_payload"], list) or not record["exact_case_payload"]:
        raise SchemaError("exact_case_payload must be a non-empty array")
    if not isinstance(record["case_execution_order"], list) or not all(isinstance(x, str) and x for x in record["case_execution_order"]):
        raise SchemaError("case_execution_order must be a non-empty string array")
    if not isinstance(record["model_provider_errors"], list):
        raise SchemaError("model_provider_errors must be an array")
    for key in ("temperature", "top_p", "maximum_output_tokens"):
        if record[key] is None:
            raise SchemaError(f"{key} must use {UNAVAILABLE!r} when not exposed, not null")
    for key in ("temperature", "top_p"):
        value = record[key]
        if value != UNAVAILABLE and (not isinstance(value, (int, float)) or isinstance(value, bool)):
            raise SchemaError(f"{key} must be numeric when exposed or {UNAVAILABLE!r}")
    if record["top_p"] != UNAVAILABLE and not 0 <= record["top_p"] <= 1:
        raise SchemaError("top_p must be from 0 to 1")
    maximum = record["maximum_output_tokens"]
    if maximum != UNAVAILABLE and (type(maximum) is not int or maximum <= 0):
        raise SchemaError(f"maximum_output_tokens must be a positive integer or {UNAVAILABLE!r}")
    return record


SEMANTIC_REVIEW_FIELDS = {
    "schema_version", "run_id", "case_id", "raw_response_sha256", "reviewer_identity",
    "reviewer_role", "reviewer_system_model", "review_timestamp", "rubric_version",
    "dimension", "score", "rationale", "confidence", "adjudication_status",
}


def validate_semantic_review(record: dict[str, Any]) -> dict[str, Any]:
    missing = SEMANTIC_REVIEW_FIELDS - set(record)
    if missing:
        raise SchemaError(f"semantic review missing fields: {sorted(missing)}")
    for key in SEMANTIC_REVIEW_FIELDS - {"score", "confidence"}:
        _string(record, key)
    _sha(record, "raw_response_sha256")
    _timestamp(record, "review_timestamp")
    if record["dimension"] not in DIMENSIONS:
        raise SchemaError(f"dimension must be one of {DIMENSIONS}")
    if type(record["score"]) is not int or record["score"] not in SCORES:
        raise SchemaError("score must be integer 0, 1, or 2")
    confidence = record["confidence"]
    if confidence is not None and (not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 1):
        raise SchemaError("confidence must be null or a number from 0 to 1")
    if record["adjudication_status"] not in ADJUDICATION_STATUSES:
        raise SchemaError(f"invalid adjudication_status: {record['adjudication_status']}")
    return record


def validate_review(record: dict[str, Any]) -> dict[str, Any]:
    """Reject legacy unbound aggregate reviews; accept amended per-dimension evidence."""
    return validate_semantic_review(record)
