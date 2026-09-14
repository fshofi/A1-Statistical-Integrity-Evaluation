"""Publication-claim controls added for the V1.2.1 reconciliation release."""
from __future__ import annotations

import csv
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class PublicationReconciliationTests(unittest.TestCase):
    def test_raw_reviewer_receipt_hashes_match(self):
        expected = {
            "reviews/gemini_lane_a/Gemini_2.5_Pro_Lane_A_RAW.pdf": "4d45d1adf04b4350582ee3221612577f5590be730ff9acfb9ea2961b2eb93d61",
            "reviews/abacus_lane_b/INDEPENDENCE_DECLARATION_COMPLETED.md": "56ca9927ee5df42983b2d8977f960d2c273a1438297047a5cc066ff89723fd38",
            "reviews/abacus_lane_b/LANE_B_REPORT_COMPLETED.md": "9b5ea9f3405580e2c2a1575532293b997aeb77f9594348f40e05ed3e8ea28236",
            "reviews/claude_final_gate/CLAUDE_FINAL_GO_REPORT_RAW.md": "33999453668bae2ccb71029fb567bbd22c6c7e973c6109b1336d8cd3ddf74001",
        }
        for relative, digest in expected.items():
            self.assertEqual(sha256(ROOT / relative), digest, relative)

    def test_core_benchmark_evidence_is_unchanged(self):
        record = json.loads((ROOT / "config/observable_reasoning_record_v1_2.json").read_text(encoding="utf-8"))
        for relative, digest in record["evidence_artifact_sha256"].items():
            self.assertEqual(sha256(ROOT / relative), digest, relative)

    def test_public_claim_surfaces_avoid_elevated_review_wording(self):
        surfaces = [
            "README.md",
            "RESULTS.md",
            "AI_ASSISTANCE_DISCLOSURE.md",
            "evidence/PORTFOLIO_AND_RECRUITER_COPY.md",
        ]
        prohibited = [
            "attributed independent AI-assisted",
            "underwent independent analytical review",
            "Abacus (Kimi K3) produced",
            "The Abacus Lane B review was verified as Kimi K3",
            "A1 is independently human validated",
        ]
        combined = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in surfaces)
        for phrase in prohibited:
            self.assertNotIn(phrase, combined)

    def test_release_freeze_blocks_elevated_claims(self):
        freeze = json.loads((ROOT / "PUBLICATION_FREEZE_V1_2_1.json").read_text(encoding="utf-8"))
        self.assertEqual(freeze["release"], "1.2.1-final")
        self.assertFalse(freeze["independent_human_validation"])
        self.assertFalse(freeze["institutional_certification_claim_authorised"])
        self.assertFalse(freeze["population_claim_authorised"])
        self.assertFalse(freeze["client_deployment_claim_authorised"])

    def test_claim_ledger_contains_review_prohibitions(self):
        with (ROOT / "evidence/CLAIM_LEDGER_V1_2_1.csv").open(encoding="utf-8", newline="") as handle:
            rows = {row["claim_id"]: row for row in csv.DictReader(handle)}
        self.assertEqual(rows["A1C-10"]["status"], "SUPPORTED_WITH_QUALIFICATION")
        for claim_id in ("A1C-11", "A1C-12", "A1C-13"):
            self.assertEqual(rows[claim_id]["status"], "PROHIBITED", claim_id)

    def test_reconciliation_disposition_is_bounded(self):
        text = (ROOT / "evidence/CROSS_MODEL_REVIEW_RECONCILIATION_V1_2_1.md").read_text(encoding="utf-8")
        self.assertIn("**CONDITIONAL GO**", text)
        self.assertIn("**NO-GO** for operational deployment claims", text)
        self.assertIn("independent human validation is absent", text)


if __name__ == "__main__":
    unittest.main()
