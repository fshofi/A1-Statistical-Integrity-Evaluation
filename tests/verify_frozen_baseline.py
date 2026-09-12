#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B = ROOT / "baseline" / "a1_revision_bundle"
MANIFEST = B / "BUNDLE_CONTENT_SHA256.txt"
CASES = B / "a1_blind_check" / "cases.jsonl"
ANS = B / "revision" / "checker_answers_rev2.jsonl"

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def load_jsonl(path):
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

# Verify bundle content manifest. Lines are '<hash>  <relative path>'.
failures = []
for raw in MANIFEST.read_text(encoding="utf-8").splitlines():
    raw = raw.strip()
    if not raw or raw.startswith("#"):
        continue
    parts = raw.split(None, 1)
    if len(parts) != 2:
        continue
    expected, rel = parts
    rel = rel.strip().lstrip("*")
    path = B / rel
    if not path.exists():
        failures.append(f"missing: {rel}")
    elif sha256(path) != expected:
        failures.append(f"hash mismatch: {rel}")

cases = load_jsonl(CASES)
answers = load_jsonl(ANS)
assert len(cases) == 24, f"expected 24 cases, got {len(cases)}"
assert len(answers) == 24, f"expected 24 answers, got {len(answers)}"
assert {x['id'] for x in cases} == {x['case_id'] for x in answers}, "case-id mismatch"
assert not failures, "\n".join(failures)
print("PASS: frozen baseline manifest, 24 cases, 24 reference answers, matching IDs")
