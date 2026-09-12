#!/usr/bin/env python3
"""Replay Rev-2 after removing copied output; a no-write checker must fail."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "baseline" / "a1_revision_bundle"
CHECKER_REL = Path("revision/checker_code_rev2.py")
OUTPUT_REL = Path("revision/checker_answers_rev2.jsonl")


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def records(value: bytes) -> list[dict[str, Any]]:
    return [json.loads(line) for line in value.decode("utf-8").splitlines() if line.strip()]


def redact(value: str, temp_root: str) -> str:
    value = value.replace(temp_root, "<TEMP>").replace(sys.executable, "<PYTHON_EXECUTABLE>")
    return re.sub(r"(?i)\b[A-Z]:\\Users\\[^\s]+", "<USER_PATH>", value)


def execute_replay(source_bundle: Path, checker_rel: Path = CHECKER_REL, output_rel: Path = OUTPUT_REL) -> dict[str, Any]:
    expected_path = source_bundle / output_rel
    expected = expected_path.read_bytes()
    with tempfile.TemporaryDirectory(prefix="a1-clean-replay-") as temp:
        copied = Path(temp) / "a1_revision_bundle"
        shutil.copytree(source_bundle, copied)
        generated = copied / output_rel
        if generated.exists():
            generated.unlink()
        generated_preexisted = generated.exists()
        run = subprocess.run(
            [sys.executable, str(copied / checker_rel)], cwd=temp,
            env={"PATH": os.environ.get("PATH", ""), "PYTHONIOENCODING": "utf-8"},
            text=True, capture_output=True, encoding="utf-8", timeout=120,
        )
        exists = generated.is_file()
        produced = generated.read_bytes() if exists else b""
        expected_normalized = expected.replace(b"\r\n", b"\n")
        produced_normalized = produced.replace(b"\r\n", b"\n")
        normalized = exists and produced_normalized == expected_normalized
        semantic = exists and records(produced) == records(expected)
        passed = not generated_preexisted and run.returncode == 0 and exists and normalized and semantic
        return {
            "passed": passed,
            "generated_preexisted": generated_preexisted,
            "checker_exit_code": run.returncode,
            "generated_file_exists": exists,
            "expected_sha256": digest_bytes(expected),
            "generated_sha256": digest_bytes(produced) if exists else "MISSING",
            "raw_hash_identical": exists and digest_bytes(produced) == digest_bytes(expected),
            "expected_normalized_sha256": digest_bytes(expected_normalized),
            "generated_normalized_sha256": digest_bytes(produced_normalized) if exists else "MISSING",
            "newline_normalized_identical": normalized,
            "semantic_records_identical": semantic,
            "stdout": redact(run.stdout, temp),
            "stderr": redact(run.stderr, temp),
        }


def format_report(result: dict[str, Any]) -> str:
    lines = [
        f"status={'PASS' if result['passed'] else 'FAIL'}",
        f"generated_preexisted={result['generated_preexisted']}",
        f"checker_exit_code={result['checker_exit_code']}",
        f"generated_file_exists={result['generated_file_exists']}",
        f"expected_sha256={result['expected_sha256']}",
        f"generated_sha256={result['generated_sha256']}",
        f"raw_hash_identical={result['raw_hash_identical']}",
        f"expected_normalized_sha256={result['expected_normalized_sha256']}",
        f"generated_normalized_sha256={result['generated_normalized_sha256']}",
        f"newline_normalized_identical={result['newline_normalized_identical']}",
        f"semantic_records_identical={result['semantic_records_identical']}",
        "--- checker stdout ---", result["stdout"].rstrip(),
        "--- checker stderr ---", result["stderr"].rstrip(), "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path)
    args = parser.parse_args()
    result = execute_replay(FROZEN)
    report = format_report(result)
    if args.log:
        args.log.parent.mkdir(parents=True, exist_ok=True)
        args.log.write_text(report, encoding="utf-8", newline="\n")
    print(report, end="")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
