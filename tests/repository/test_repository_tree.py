from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


class RepositoryTreeQualificationTest(unittest.TestCase):
    def test_repository_tree_contract(self) -> None:
        root = Path(__file__).resolve().parents[2]
        result = subprocess.run(
            ["python", "scripts/check_repository_tree.py"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
