#!/usr/bin/env python3
"""Run the A1 V1.2 external-challenge hardening audits."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.checker import load_cases, load_jsonl
from src.hardening import audit_reasoning_chain, audit_selection
from src.utils import read_json, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=ROOT / "runs" / "run1")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "runs" / "run1" / "hardening_v1_2")
    parser.add_argument("--design", type=Path, default=ROOT / "config" / "selection_design_v1_2.json")
    parser.add_argument("--reasoning-record", type=Path, default=ROOT / "config" / "observable_reasoning_record_v1_2.json")
    return parser.parse_args()


def outcome_for(row: dict) -> str:
    """Classify the preserved attempt without allowing refusal/truncation to disappear."""
    if row.get("failure_status") != "NONE":
        return row["failure_status"]
    if row.get("refusal_status") != "NONE":
        return "REFUSAL"
    if row.get("truncation_status") != "NONE":
        return "TRUNCATED"
    return "COMPLETED"


def main() -> int:
    options = parse_args()
    cases = load_cases()
    expected_ids = [row["id"] for row in cases]
    responses = load_jsonl(options.run_dir / "raw_model_responses.jsonl")
    provenance = read_json(options.run_dir / "definitive_task_provenance.json")
    provenance_ids = [row["case_id"] for row in provenance["tasks"]]

    attempts = []
    for row in responses:
        attempts.append({
            "case_id": row["case_id"],
            "attempt_id": row["task_id"],
            "outcome": outcome_for(row),
            "preserved": True,
            "selected_for_scoring": True,
            "exclusion_basis": "NONE",
            "response_sha256": row["response_sha256"],
        })

    selection = audit_selection(expected_ids, responses, provenance_ids, attempts, read_json(options.design))
    reasoning = audit_reasoning_chain(read_json(options.reasoning_record), ROOT)
    combined = {
        "schema_version": "A1-EXTERNAL-CHALLENGE-HARDENING-1.2",
        "selection_audit": selection,
        "observable_reasoning_audit": reasoning,
        "overall_status": "FAIL_CLOSED" if "FAIL_CLOSED" in {selection["status"], reasoning["status"]} else "CONDITIONAL_PASS",
        "client_pitch_status": "QUALIFIED_PORTFOLIO_USE_ONLY",
        "population_performance_claim_authorised": False,
        "independent_validation_claim_authorised": False,
    }
    options.output_dir.mkdir(parents=True, exist_ok=True)
    write_json(options.output_dir / "selection_audit.json", selection)
    write_json(options.output_dir / "observable_reasoning_audit.json", reasoning)
    write_json(options.output_dir / "hardening_summary.json", combined)
    print(json.dumps({
        "selection": selection["status"],
        "reasoning": reasoning["status"],
        "overall": combined["overall_status"],
        "critical_failures": sum(x["status"] == "FAIL" for x in selection["checks"] + reasoning["checks"]),
        "residual_flags": len(selection["residual_flags"]) + len(reasoning["residual_flags"]),
    }, sort_keys=True))
    return 1 if combined["overall_status"] == "FAIL_CLOSED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
