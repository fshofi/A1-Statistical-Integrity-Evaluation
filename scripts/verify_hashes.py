#!/usr/bin/env python3
"""Verify frozen and publication SHA-256 manifests."""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.checker import verify_baseline


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            value.update(chunk)
    return value.hexdigest()


def verify_publication_manifest(path: Path) -> list[str]:
    failures = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.startswith("#"):
            continue
        expected, relative = raw.split(None, 1)
        target = ROOT / relative.strip().lstrip("*").removeprefix("./")
        if not target.is_file():
            failures.append(f"missing: {target.relative_to(ROOT)}")
        elif digest(target) != expected:
            failures.append(f"hash mismatch: {target.relative_to(ROOT)}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "PROJECT_SHA256.txt")
    args = parser.parse_args()
    failures = verify_baseline() + verify_publication_manifest(args.manifest)
    if failures:
        print("FAIL")
        print("\n".join(failures))
        return 1
    print("PASS: frozen bundle and publication manifests verify")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
