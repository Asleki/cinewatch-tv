from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


class NexVoxEngineeringCorpusQualificationTest(unittest.TestCase):
    def test_nexvox_engineering_corpus_contract(self) -> None:
        root = Path(__file__).resolve().parents[2]
        result = subprocess.run(
            ["python", "scripts/check_nexvox_engineering_corpus.py"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
