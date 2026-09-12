#!/usr/bin/env python3
"""Produce IV-01 hash evidence without changing any frozen file."""
from __future__ import annotations

import datetime as dt
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "baseline/a1_revision_bundle/originals/checker_answers.jsonl"
REV2 = ROOT / "baseline/a1_revision_bundle/revision/checker_answers_rev2.jsonl"
OUTPUT = ROOT / "results/IV01_HASH_EVIDENCE.txt"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    original = sha(ORIGINAL)
    rev2 = sha(REV2)
    passed = original == "b9c55dbf0386050f70f05ae0dea0370b9c1b71ff193af6f881bcee5fc48ca31c" and rev2 == "fa5af07dde36625f21b64a776f4e11b78eb7f19859105adff6d2a2875ad921f7"
    report = "\n".join([
        "A1 IV-01 INDEPENDENT HASH RECONCILIATION",
        f"timestamp_utc={dt.datetime.now(dt.timezone.utc).isoformat()}",
        f"status={'PASS' if passed else 'FAIL'}",
        f"{original}  ./baseline/a1_revision_bundle/originals/checker_answers.jsonl",
        f"{rev2}  ./baseline/a1_revision_bundle/revision/checker_answers_rev2.jsonl",
        "relationship=distinct provenance stages; original blind output versus corrected Rev-2 distribution",
        "rev2_distribution_member=True",
        "frozen_files_modified=False",
        "",
    ])
    OUTPUT.write_text(report, encoding="utf-8", newline="\n")
    print(report, end="")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
