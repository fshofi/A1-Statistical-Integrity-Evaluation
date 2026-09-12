#!/usr/bin/env python3
"""Verify the reconciled 24+8 test classification against discovery."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "config" / "test_inventory_v1.json"


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item.id().removeprefix("tests.")


def main() -> int:
    sys.path.insert(0, str(ROOT))
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    discovered = set(flatten(unittest.defaultTestLoader.discover(str(ROOT / "tests"), top_level_dir=str(ROOT / "tests"))))
    formal = set(inventory["formal_h01_h06_unit_tests"])
    supplemental = set(inventory["supplemental_integration_artifact_replay_checks"])
    failures = []
    if formal & supplemental:
        failures.append("classification overlap")
    if formal | supplemental != discovered:
        failures.append(f"inventory/discovery mismatch; missing={sorted(discovered-(formal|supplemental))}; stale={sorted((formal|supplemental)-discovered)}")
    if len(formal) != 24 or len(supplemental) != 8 or len(discovered) != 32:
        failures.append(f"count mismatch: formal={len(formal)}, supplemental={len(supplemental)}, discovered={len(discovered)}")
    if failures:
        print("FAIL: " + "; ".join(failures))
        return 1
    print("PASS: 24 formal H01-H06 unit tests + 8 supplemental integration/artifact/replay checks = 32 discovered test methods")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
