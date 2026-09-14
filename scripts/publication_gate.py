#!/usr/bin/env python3
"""Run publication checks and write concise, path-safe evidence logs."""
from __future__ import annotations

import datetime as dt
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def run(label: str, command: list[str]) -> tuple[int, str]:
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    completed = subprocess.run(
        command, cwd=ROOT, env=env, text=True, capture_output=True,
        encoding="utf-8", timeout=240,
    )
    output = (completed.stdout + completed.stderr).replace(str(ROOT), "<REPOSITORY>").replace(sys.executable, "<PYTHON_EXECUTABLE>")
    return completed.returncode, f"[{label}] exit={completed.returncode}\n{output.strip()}\n"


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
    checks = [
        ("dependency_install", [sys.executable, "-m", "pip", "install", "--no-index", "-r", "requirements.txt"]),
        ("frozen_baseline", [sys.executable, "tests/verify_frozen_baseline.py"]),
        ("test_inventory_reconciliation", [sys.executable, "scripts/verify_test_inventory.py"]),
        ("formal_and_supplemental_tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]),
        ("hardened_clean_replay", [sys.executable, "scripts/clean_replay.py", "--log", "results/HARDENED_CLEAN_REPLAY.log"]),
        ("external_challenge_hardening", [sys.executable, "scripts/run_v1_2_hardening.py"]),
        ("security_scan", [sys.executable, "scripts/security_scan.py"]),
    ]
    records = []
    test_record = ""
    failed = []
    for label, command in checks:
        code, record = run(label, command)
        records.append(record)
        if label == "formal_and_supplemental_tests":
            test_record = record
        if code:
            failed.append(label)
    status = "PASS" if not failed else "FAIL"
    header = f"A1 V1.2.1 PUBLICATION GATE\ntimestamp_utc={timestamp}\npython={sys.version.split()[0]}\nrun0_status=EXTERNAL / NOT SUPPLIED\nrun0_rescoring=BLOCKED\nstatus={status}\n"
    (RESULTS / "H01_H06_EXECUTION_LOG.txt").write_text(header + "\n".join(records), encoding="utf-8", newline="\n")
    discovered_count = test_record.count(" ... ok")
    (RESULTS / "H01_H06_TEST_REPORT.txt").write_text(
        f"A1 V1.2.1 REGRESSION TEST REPORT\ntimestamp_utc={timestamp}\noriginal_test_methods=32\nexternal_challenge_hardening_tests=14\npublication_reconciliation_tests=6\ntotal_discovered_test_methods={discovered_count}\nstatus={'PASS' if 'formal_and_supplemental_tests' not in failed else 'FAIL'}\n\n{test_record}",
        encoding="utf-8", newline="\n",
    )
    print(f"{status}: A1 V1.2.1 publication gate; logs written under results/")
    if failed:
        print("failed=" + ",".join(failed))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
