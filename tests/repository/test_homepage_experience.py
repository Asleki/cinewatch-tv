from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class HomepageExperienceRepositoryTest(unittest.TestCase):
    def test_homepage_experience_policy(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/check_homepage_experience.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=(completed.stdout + completed.stderr).strip(),
        )
        self.assertIn("PASS  CWTV.V1.3.3.2.2", completed.stdout)


if __name__ == "__main__":
    unittest.main()
