"""Auditable derived parsing; raw responses are never changed or overwritten."""
from __future__ import annotations

import ast
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config" / "scoring_policy_v1.json"
NUMBER = re.compile(r"^[\s]*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)(?:\s+(.+?))?[\s]*$")


class DuplicateKeyError(ValueError):
    pass


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _check_ast_duplicates(node: ast.AST) -> None:
    for child in ast.walk(node):
        if isinstance(child, ast.Dict):
            keys = []
            for key in child.keys:
                if key is None:
                    continue
                try:
                    value = ast.literal_eval(key)
                except Exception:
                    continue
                if value in keys:
                    raise DuplicateKeyError(f"duplicate JSON-like key: {value}")
                keys.append(value)


def load_policy(path: Path = POLICY_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs)


def _strip_fence(value: str) -> str:
    value = value.strip()
    if value.startswith("```") and value.endswith("```"):
        lines = value.splitlines()
        if len(lines) >= 3:
            return "\n".join(lines[1:-1]).strip()
    return value


@dataclass(frozen=True)
class ParseResult:
    status: str
    values: dict[str, dict[str, Any]]
    detail: str


def parse_response(response: Any, required_fields: list[str]) -> ParseResult:
    if response is None or (isinstance(response, str) and not response.strip()):
        return ParseResult("EMPTY", {}, "response is empty")
    parsed = response
    status = "STRUCTURED_OBJECT"
    if isinstance(response, str):
        candidate = _strip_fence(response)
        try:
            parsed = json.loads(candidate, object_pairs_hook=_unique_pairs)
            status = "VALID_JSON"
        except DuplicateKeyError as exc:
            return ParseResult("DUPLICATE_KEYS", {}, str(exc))
        except json.JSONDecodeError:
            try:
                tree = ast.parse(candidate, mode="eval")
                _check_ast_duplicates(tree)
                parsed = ast.literal_eval(tree)
                status = "VALID_JSON_LIKE"
            except DuplicateKeyError as exc:
                return ParseResult("DUPLICATE_KEYS", {}, str(exc))
            except (SyntaxError, ValueError, TypeError):
                match = NUMBER.fullmatch(candidate)
                if match and len(required_fields) == 1:
                    return ParseResult("PLAIN_TEXT_NUMBER", {required_fields[0]: {"value": float(match.group(1)), "unit": match.group(2)}}, "single requested field inferred")
                return ParseResult("UNPARSED", {}, "not valid JSON, supported JSON-like syntax, or an unambiguous single number")
    if isinstance(parsed, (int, float)) and not isinstance(parsed, bool) and len(required_fields) == 1:
        return ParseResult(status, {required_fields[0]: {"value": parsed, "unit": None}}, "single requested field inferred")
    if not isinstance(parsed, dict):
        return ParseResult("UNPARSED", {}, "parsed value is not a numeric object")
    source = parsed.get("numeric", parsed)
    if not isinstance(source, dict):
        return ParseResult("UNPARSED", {}, "numeric member is not an object")
    values: dict[str, dict[str, Any]] = {}
    for field, submitted in source.items():
        if isinstance(submitted, dict) and "value" in submitted:
            values[field] = {"value": submitted["value"], "unit": submitted.get("unit")}
        elif isinstance(submitted, (int, float)) and not isinstance(submitted, bool):
            values[field] = {"value": submitted, "unit": None}
    return ParseResult(status, values, "derived numeric fields parsed")


def _normalise_unit(value: str) -> str:
    return " ".join(value.strip().casefold().replace("_", " ").split())


def unit_status(submitted: Any, unit_name: str, policy: dict[str, Any]) -> str:
    if submitted is None or not isinstance(submitted, str) or not submitted.strip():
        return "MISSING"
    definition = policy["unit_definitions"][unit_name]
    canonical = _normalise_unit(definition["canonical"])
    candidate = _normalise_unit(submitted)
    if candidate == canonical:
        return "CANONICAL"
    if candidate in {_normalise_unit(x) for x in definition["aliases"]}:
        return "EQUIVALENT_ALIAS"
    return "INCOMPATIBLE"


def numeric_status(actual: Any, expected: Any, acceptance_name: str, policy: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(actual, (int, float)) or isinstance(actual, bool) or not math.isfinite(float(actual)):
        return {"status": "INVALID_NUMERIC_VALUE", "actual": actual, "expected": expected}
    rule = policy["numeric_acceptance"][acceptance_name]
    if rule["kind"] == "exact_integer":
        passed = float(actual).is_integer() and int(actual) == int(expected)
        tolerance = 0.0
    else:
        tolerance = float(rule["absolute_tolerance"])
        passed = abs(float(actual) - float(expected)) <= tolerance + 1e-15
    return {"status": "PASS" if passed else "FAIL", "actual": actual, "expected": expected, "acceptance": acceptance_name, "absolute_tolerance": tolerance}


def evaluate_response(case_id: str, response: Any, reference: dict[str, Any], policy: dict[str, Any] | None = None) -> dict[str, Any]:
    policy = policy or load_policy()
    case_policy = policy["cases"][case_id]
    required = case_policy["required_numeric_fields"]
    supplemental = case_policy["supplemental_numeric_fields"]
    present = not (response is None or (isinstance(response, str) and not response.strip()))
    parsed = parse_response(response, required)
    applicable = bool(required)
    found = set(parsed.values)
    fields_present = all(field in found for field in required)
    field_results = {}
    for field in required:
        if field not in parsed.values:
            field_results[field] = {"unit_status": "NOT_EVALUATED", "numeric_value_status": "MISSING", "mathematical_correctness": "NOT_EVALUATED"}
            continue
        submitted = parsed.values[field]
        numeric = numeric_status(submitted["value"], reference["numeric"][field]["value"], case_policy["fields"][field]["acceptance"], policy)
        field_results[field] = {
            "submitted_unit": submitted["unit"],
            "unit_status": unit_status(submitted["unit"], case_policy["fields"][field]["unit"], policy),
            "numeric_value_status": numeric["status"],
            "mathematical_correctness": numeric["status"] if numeric["status"] in {"PASS", "FAIL"} else "NOT_EVALUATED",
            "comparison": numeric,
        }
    evaluated = [x["mathematical_correctness"] for x in field_results.values()]
    if not applicable:
        math_status = "NOT_APPLICABLE"
    elif not present or parsed.status in {"UNPARSED", "DUPLICATE_KEYS", "EMPTY"} or not fields_present:
        math_status = "NOT_EVALUATED"
    else:
        math_status = "PASS" if all(x == "PASS" for x in evaluated) else "FAIL"
    return {
        "case_id": case_id,
        "response_present": "PASS" if present else "FAIL",
        "numeric_applicability": "APPLICABLE" if applicable else "NOT_APPLICABLE",
        "parse_status": parsed.status,
        "parse_detail": parsed.detail,
        "required_numeric_fields": required,
        "supplemental_reference_fields_excluded": supplemental,
        "required_fields_present": "NOT_APPLICABLE" if not applicable else ("PASS" if fields_present else "FAIL"),
        "unit_status": "NOT_APPLICABLE" if not applicable else {field: result["unit_status"] for field, result in field_results.items()},
        "numeric_value_status": "NOT_APPLICABLE" if not applicable else {field: result["numeric_value_status"] for field, result in field_results.items()},
        "mathematical_correctness": math_status,
        "field_results": field_results,
    }
