"""The watch release cannot publish invented or missing private qualities."""
import subprocess
import sys
import unittest
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class WatchRegistryTests(unittest.TestCase):
    def test_media_identity_is_not_automatic_training_permission(self):
        classify = runpy.run_path(str(ROOT / 'scripts/build_nexvox_engineering_corpus.py'))['classify']
        for path in (
            'apps/web/src/lib/watch/registry.json',
            'apps/web/src/lib/watch/renditions.json',
            'services/api/cinewatch_api/watch/originals.json',
            'services/api/cinewatch_api/watch/renditions.json',
            'infra/cloudflare/original-registry.json',
            'infra/cloudflare/registry.mjs',
            'infra/cloudflare/renditions.mjs',
        ):
            with self.subTest(path=path):
                self.assertEqual(classify(path)[0], 'TRAINING_REVIEW_REQUIRED')

    def test_complete_private_rendition_authority(self):
        result = subprocess.run([sys.executable, 'scripts/check_watch_registry.py'], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
