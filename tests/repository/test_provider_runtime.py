from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


class ProviderRuntimeFoundationTests(unittest.TestCase):
    def test_provider_runtime_policy(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        completed = subprocess.run(
            [
                sys.executable,
                str(repo_root / "scripts/check_provider_runtime.py"),
            ],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout)


if __name__ == "__main__":
    unittest.main()
