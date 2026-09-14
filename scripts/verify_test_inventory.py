#!/usr/bin/env python3
"""Verify the reconciled 24+8+14+6 test classification against discovery."""
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
    hardening = set(inventory["external_challenge_hardening_tests"])
    publication = set(inventory["publication_reconciliation_tests"])
    failures = []
    groups = (formal, supplemental, hardening, publication)
    if any(groups[i] & groups[j] for i in range(len(groups)) for j in range(i + 1, len(groups))):
        failures.append("classification overlap")
    inventoried = formal | supplemental | hardening | publication
    if inventoried != discovered:
        failures.append(f"inventory/discovery mismatch; missing={sorted(discovered-inventoried)}; stale={sorted(inventoried-discovered)}")
    if len(formal) != 24 or len(supplemental) != 8 or len(hardening) != 14 or len(publication) != 6 or len(discovered) != 52:
        failures.append(f"count mismatch: formal={len(formal)}, supplemental={len(supplemental)}, hardening={len(hardening)}, publication={len(publication)}, discovered={len(discovered)}")
    if failures:
        print("FAIL: " + "; ".join(failures))
        return 1
    print("PASS: 24 formal + 8 supplemental + 14 external-challenge hardening + 6 publication-reconciliation = 52 discovered test methods")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
