"""Access and integrity checks for the frozen A1 reference layer."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from src.schemas import validate_case, validate_reference


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "baseline" / "a1_revision_bundle"
CASES_PATH = FROZEN / "a1_blind_check" / "cases.jsonl"
REFERENCES_PATH = FROZEN / "revision" / "checker_answers_rev2.jsonl"
MANIFEST_PATH = FROZEN / "BUNDLE_CONTENT_SHA256.txt"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line, object_pairs_hook=_reject_duplicate_keys) for line in stream if line.strip()]


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def load_cases() -> list[dict[str, Any]]:
    return [validate_case(row) for row in load_jsonl(CASES_PATH)]


def load_references() -> list[dict[str, Any]]:
    return [validate_reference(row) for row in load_jsonl(REFERENCES_PATH)]


def verify_frozen_manifest() -> list[str]:
    failures: list[str] = []
    for raw in MANIFEST_PATH.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue
        expected, relative = raw.split(None, 1)
        relative = relative.strip().lstrip("*")
        target = FROZEN / relative
        if not target.is_file():
            failures.append(f"missing: {relative}")
        elif sha256(target) != expected:
            failures.append(f"hash mismatch: {relative}")
    return failures


def verify_baseline() -> list[str]:
    failures = verify_frozen_manifest()
    cases = load_cases()
    references = load_references()
    if len(cases) != 24:
        failures.append(f"expected 24 cases, got {len(cases)}")
    if len(references) != 24:
        failures.append(f"expected 24 reference answers, got {len(references)}")
    case_ids = [row["id"] for row in cases]
    reference_ids = [row["case_id"] for row in references]
    if len(case_ids) != len(set(case_ids)):
        failures.append("duplicate case IDs")
    if len(reference_ids) != len(set(reference_ids)):
        failures.append("duplicate reference IDs")
    if set(case_ids) != set(reference_ids):
        failures.append("case/reference ID mismatch")
    return failures
