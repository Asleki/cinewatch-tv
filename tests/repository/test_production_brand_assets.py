from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ProductionBrandAssetRepositoryTest(unittest.TestCase):
    def test_production_brand_asset_browser_qualification_staging(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts/check_production_brand_assets.py")],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn(
            "PASS  CWTV.V1.3.2.3-R2 production brand browser approval lock",
            completed.stdout,
        )


if __name__ == "__main__":
    unittest.main()
