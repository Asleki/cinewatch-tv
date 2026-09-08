from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class FrontendSkeletonRepositoryTest(unittest.TestCase):
    def test_frontend_skeleton_policy(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts/check_frontend_skeleton.py")],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("PASS  CWTV.V1.2.4 frontend skeleton policy", completed.stdout)


if __name__ == "__main__":
    unittest.main()
