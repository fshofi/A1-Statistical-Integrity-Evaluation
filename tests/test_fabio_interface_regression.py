from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")


class FabioInterfaceRegressionTests(unittest.TestCase):
    def test_explicit_non_causal_guard_is_present(self):
        self.assertIn("causalNegation", HTML)
        self.assertIn("A1 does not convert the negation into a causal claim.", HTML)

    def test_temporal_leakage_respects_explicit_exclusion(self):
        self.assertIn("explicitLeakExclusion", HTML)
        self.assertIn("Future or post-outcome information is explicitly excluded", HTML)

    def test_evidence_presence_is_not_presented_as_sufficiency(self):
        self.assertIn("Evidence sufficiency: SCREENED", HTML)
        self.assertIn("Presence is not completeness", HTML)
        self.assertNotIn("Evidence record: PRESENT", HTML)


if __name__ == "__main__":
    unittest.main()
