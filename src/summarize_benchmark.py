#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "baseline" / "a1_revision_bundle" / "a1_blind_check" / "cases.jsonl"
ANS = ROOT / "baseline" / "a1_revision_bundle" / "revision" / "checker_answers_rev2.jsonl"

def load_jsonl(path):
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

cases = load_jsonl(CASES)
answers = load_jsonl(ANS)
print(f"cases={len(cases)}")
print(f"reference_answers={len(answers)}")
print(f"case_ids_match={set(x['id'] for x in cases) == set(x['case_id'] for x in answers)}")
print("case_ids=" + ",".join(x["id"] for x in cases))
