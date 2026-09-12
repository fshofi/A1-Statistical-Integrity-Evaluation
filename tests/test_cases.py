import hashlib
import unittest
from pathlib import Path

from src.checker import CASES_PATH, load_cases, load_references

ROOT = Path(__file__).resolve().parents[1]


class CaseTests(unittest.TestCase):
    def test_counts_and_ids(self):
        cases = load_cases()
        references = load_references()
        self.assertEqual(len(cases), 24)
        self.assertEqual(len(references), 24)
        self.assertEqual({x["id"] for x in cases}, {x["case_id"] for x in references})

    def test_public_case_copy_is_exact(self):
        public = ROOT / "data" / "cases.jsonl"
        self.assertEqual(public.read_bytes(), CASES_PATH.read_bytes())
        self.assertEqual(hashlib.sha256(public.read_bytes()).hexdigest(), "79b4feb88561c0d3d46ba0f8f660f21bb997383652ea99a70651bfda6907a2ca")


if __name__ == "__main__":
    unittest.main()
