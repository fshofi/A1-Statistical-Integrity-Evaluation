#!/usr/bin/env python3
"""Conservative source-tree scan for publication-sensitive material."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__"}
TEXT_SUFFIXES = {".py", ".md", ".txt", ".json", ".jsonl", ".toml", ".yml", ".yaml", ".log", ""}
RULES = {
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "assigned secret": re.compile(r"(?i)\b(api[_-]?key|access[_-]?token|client[_-]?secret|password)\b\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
    "Windows user path": re.compile(r"(?i)\b[A-Z]:\\Users\\[^\\\s]+"),
    "POSIX home path": re.compile(r"/(?:home|Users)/[^/\s]+"),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    findings = []
    for path in sorted(args.root.rglob("*")):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in RULES.items():
            for match in pattern.finditer(content):
                line = content.count("\n", 0, match.start()) + 1
                findings.append(f"{path.relative_to(args.root)}:{line}: {label}")
    if findings:
        print("FAIL: potential publication-sensitive content")
        print("\n".join(findings))
        return 1
    print("PASS: no common secrets, private keys, or user-home paths detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
