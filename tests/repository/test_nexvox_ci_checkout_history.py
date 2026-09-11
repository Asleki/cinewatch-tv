from __future__ import annotations

import re
import unittest
from pathlib import Path


class NexVoxCiCheckoutHistoryTests(unittest.TestCase):
    def test_quality_job_fetches_full_history_for_projection_validation(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        workflow = (repo_root / ".github/workflows/ci.yml").read_text(encoding="utf-8")

        match = re.search(
            r"(?ms)^  quality:\n(?P<quality>.*?)(?=^  security:\n)",
            workflow,
        )
        self.assertIsNotNone(match, "quality job block is missing")
        quality = match.group("quality")

        self.assertIn("persist-credentials: false", quality)
        self.assertRegex(quality, r"(?m)^\s+fetch-depth:\s+0\s*$")

    def test_security_job_remains_shallow_and_secret_free(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        workflow = (repo_root / ".github/workflows/ci.yml").read_text(encoding="utf-8")

        match = re.search(r"(?ms)^  security:\n(?P<security>.*)\Z", workflow)
        self.assertIsNotNone(match, "security job block is missing")
        security = match.group("security")

        self.assertIn("persist-credentials: false", security)
        self.assertNotRegex(security, r"(?m)^\s+fetch-depth:\s+0\s*$")
        self.assertNotIn("${{ secrets.", security)


if __name__ == "__main__":
    unittest.main()
