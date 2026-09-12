import unittest

from src.scoring import summarize_scores


class SummaryTests(unittest.TestCase):
    def test_not_applicable_is_excluded_not_passed(self):
        rows = [
            {"response_present": "FAIL", "numeric_applicability": "NOT_APPLICABLE", "mathematical_correctness": "NOT_APPLICABLE"},
            {"response_present": "PASS", "numeric_applicability": "APPLICABLE", "mathematical_correctness": "PASS"},
            {"response_present": "PASS", "numeric_applicability": "APPLICABLE", "mathematical_correctness": "NOT_EVALUATED"},
        ]
        result = summarize_scores(rows)
        self.assertEqual(result["numeric_pass_count"], 1)
        self.assertEqual(result["numeric_correctness_denominator"], 1)
        self.assertEqual(result["numeric_coverage_denominator"], 2)
        self.assertEqual(result["numeric_non_applicable_case_count"], 1)


if __name__ == "__main__": unittest.main()
