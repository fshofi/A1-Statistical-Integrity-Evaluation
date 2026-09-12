#!/usr/bin/env python3
"""Create the deterministic publication SHA-256 manifest."""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "PROJECT_SHA256.txt"
SKIP_PARTS = {".git", ".venv", "venv", "__pycache__"}


def main() -> int:
    rows = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path == OUTPUT or any(part in SKIP_PARTS for part in path.parts):
            continue
        relative = path.relative_to(ROOT).as_posix()
        rows.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  ./{relative}")
    OUTPUT.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUTPUT.name} with {len(rows)} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
