from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class RefinementRegressionRepositoryTest(unittest.TestCase):
    def test_refinement_regression_guard(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts/check_refinement_regression.py")],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("PASS  refinement regression guard", completed.stdout)


if __name__ == "__main__":
    unittest.main()
