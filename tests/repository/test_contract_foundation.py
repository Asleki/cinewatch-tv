from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


class ContractFoundationRepositoryTest(unittest.TestCase):
    def test_contract_foundation_policy(self) -> None:
        root = Path(__file__).resolve().parents[2]
        completed = subprocess.run(
            [sys.executable, "scripts/check_contract_foundation.py"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            self.fail(
                "contract foundation policy failed\n"
                f"STDOUT:\n{completed.stdout}\n"
                f"STDERR:\n{completed.stderr}"
            )


if __name__ == "__main__":
    unittest.main()
