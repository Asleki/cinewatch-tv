from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class CatalogExperienceRepositoryTest(unittest.TestCase):
    def test_catalog_experience_r3_static_policy(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/check_catalog_experience.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, msg=(completed.stdout + completed.stderr).strip())
        self.assertIn("PASS  R3 static catalog policy", completed.stdout)
        self.assertIn("does not claim browser qualification", completed.stdout)


if __name__ == "__main__":
    unittest.main()
