import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReproducibilityTests(unittest.TestCase):
    def test_hardened_clean_replay(self):
        environment = dict(os.environ)
        environment["PYTHONIOENCODING"] = "utf-8"
        run = subprocess.run(
            [sys.executable, str(ROOT / "scripts/clean_replay.py")],
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            encoding="utf-8",
            timeout=180,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("generated_preexisted=False", run.stdout)
        self.assertIn("generated_file_exists=True", run.stdout)
        self.assertIn("semantic_records_identical=True", run.stdout)


if __name__ == "__main__": unittest.main()
