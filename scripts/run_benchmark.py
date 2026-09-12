#!/usr/bin/env python3
"""Parse and deterministically score a run under the amended A1 protocol."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.checker import CASES_PATH, load_cases, load_jsonl, load_references, verify_baseline, write_jsonl
from src.scoring import score_case, summarize_scores
from src.schemas import DIMENSIONS, SchemaError, validate_model_response, validate_run_manifest, validate_semantic_review
from src.utils import read_json, write_json


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def response_sha256(response: object) -> str:
    if isinstance(response, str):
        payload = response.encode("utf-8")
    else:
        payload = json.dumps(response, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("responses", type=Path, help="immutable raw response JSONL")
    parser.add_argument("--run-manifest", type=Path, required=True, help="mandatory A1-RUN-MANIFEST-1.1 JSON")
    parser.add_argument("--reviews", type=Path, help="optional response-bound per-dimension semantic-review JSONL")
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    options = args()
    failures = verify_baseline()
    if failures:
        raise SystemExit("Frozen baseline verification failed:\n" + "\n".join(failures))
    manifest = validate_run_manifest(read_json(options.run_manifest))
    if manifest["raw_response_sha256"] != sha256(options.responses):
        raise SchemaError("run manifest raw_response_sha256 does not match response file")
    if manifest["case_set_sha256"] != sha256(CASES_PATH):
        raise SchemaError("run manifest case_set_sha256 does not match frozen cases")
    cases = load_cases()
    if manifest["exact_case_payload"] != cases:
        raise SchemaError("run manifest exact_case_payload does not match public cases")
    expected_order = [case["id"] for case in cases]
    if manifest["case_execution_order"] != expected_order:
        raise SchemaError("case_execution_order does not match the submitted response order policy")
    references = {row["case_id"]: row for row in load_references()}
    response_rows = [validate_model_response(row) for row in load_jsonl(options.responses)]
    ids = [row.case_id for row in response_rows]
    if ids != expected_order or len(ids) != len(set(ids)):
        raise SchemaError("responses must contain the 24 case IDs once, in manifest order")

    review_rows = []
    if options.reviews:
        seen = set()
        response_hashes = {row.case_id: response_sha256(row.response) for row in response_rows}
        for raw in load_jsonl(options.reviews):
            review = validate_semantic_review(raw)
            key = (review["run_id"], review["case_id"], review["reviewer_identity"], review["dimension"])
            if key in seen:
                raise SchemaError(f"duplicate semantic review decision: {key}")
            seen.add(key)
            if review["run_id"] != manifest["run_id"]:
                raise SchemaError("semantic review run_id mismatch")
            if review["case_id"] not in response_hashes:
                raise SchemaError("semantic review references unknown case")
            if review["raw_response_sha256"] != response_hashes[review["case_id"]]:
                raise SchemaError("semantic review raw-response hash mismatch")
            review_rows.append(review)

    scored = []
    for item in response_rows:
        row = score_case(item.response, references[item.case_id])
        row["raw_response_sha256"] = response_sha256(item.response)
        row["semantic_review_decisions_present"] = sum(x["case_id"] == item.case_id for x in review_rows)
        row["semantic_review_dimensions_missing"] = sorted(set(DIMENSIONS) - {x["dimension"] for x in review_rows if x["case_id"] == item.case_id})
        scored.append(row)
    options.output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(options.output_dir / "derived_parsing_and_scores.jsonl", scored)
    summary = summarize_scores(scored)
    summary["semantic_review_decision_count"] = len(review_rows)
    summary["semantic_reviews_aggregated"] = False
    summary["disagreement_policy"] = "Represent separately; no silent averaging or forced consensus."
    write_json(options.output_dir / "summary.json", summary)
    print(f"Processed {len(scored)} cases; deterministic denominator={summary['numeric_correctness_denominator']}/{summary['numeric_applicable_case_count']} applicable cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
