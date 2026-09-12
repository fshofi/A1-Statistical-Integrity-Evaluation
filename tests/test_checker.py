import unittest

from src.checker import verify_baseline


class CheckerTests(unittest.TestCase):
    def test_frozen_manifest_and_baseline(self):
        self.assertEqual(verify_baseline(), [])


if __name__ == "__main__":
    unittest.main()
