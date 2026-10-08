"""The root smoke must consume streamed HTML under pipefail."""
import shlex
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class FrontendStreamingSmokeTests(unittest.TestCase):
    def test_large_streamed_root_is_not_misreported_as_missing_brand(self):
        source = (ROOT / 'scripts/check_frontend_runtime.sh').read_text()
        line = next(s for s in source.splitlines() if 'frontend root smoke response missing' in s)
        producer = "import sys; sys.stdout.write('CineWatch TV\\n'); sys.stdout.flush(); sys.stdout.write('x'*2000000)"
        command = shlex.quote(sys.executable) + ' -c ' + shlex.quote(producer)
        curl = 'curl -fsS "http://$HOST:$PORT/"'
        self.assertIn(curl, line)
        line = line.replace(curl, command)
        result = subprocess.run(['bash', '-c', 'set -o pipefail; fail(){ return 1; }; ' + line], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode())


if __name__ == '__main__':
    unittest.main()
