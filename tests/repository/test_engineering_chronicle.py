from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import unittest


class EngineeringChronicleRepositoryTest(unittest.TestCase):
    def test_engineering_chronicle_policy(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        completed = subprocess.run(
            [sys.executable, str(repo_root / "scripts/check_engineering_chronicle.py")],
            cwd=repo_root,
            check=False,
            text=True,
            capture_output=True,
        )
        if completed.returncode != 0:
            self.fail(f"chronicle policy failed\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}")


if __name__ == "__main__":
    unittest.main()
