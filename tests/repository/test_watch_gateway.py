"""Run the private gateway security regressions in the ordinary Linux CI gate."""
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class WatchGatewayTests(unittest.TestCase):
    def test_private_gateway_security(self):
        result = subprocess.run(
            ['node', '--test', 'tests/watch/gateway.test.mjs'],
            cwd=ROOT, text=True, capture_output=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
