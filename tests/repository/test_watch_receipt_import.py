"""Synthetic metadata checks only; no receipt here asserts a real R2 upload."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('watch_import', ROOT / 'scripts/import_watch_renditions.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture():
    originals = json.loads((ROOT / 'infra/cloudflare/original-registry.json').read_text())
    variants = {}
    for content_id, source in originals.items():
        if not source['available'] or source['height'] <= 240:
            continue
        sha = 'a' * 64
        variants[content_id] = {'sha256': sha, 'bytes': 100, 'height': 240,
            'key': f'simulated-rights/bonanza/derived/{content_id}/240p/{sha}.mp4',
            'parent_sha256': source['sha256'], 'profile': module.PROFILE,
            'full_readback': 'PASS', 'full_decode': 'PASS',
            'ffprobe': {'streams': [{'codec_type': 'video', 'codec_name': 'h264', 'height': 240}],
                        'format': {'duration': source['duration_seconds']}}}
    return originals, {'status': 'PASS', 'inventory_sha256': module.INVENTORY_SHA,
        'bucket': 'cinewatch-media-qualifications', 'profile': module.PROFILE,
        'originals_modified': False, 'public_access_authorized': False,
        'rights_mode': 'simulated-owner-only', 'variants': variants}


class WatchReceiptTests(unittest.TestCase):
    def test_complete_metadata_normalizes_without_inventing_sources(self):
        originals, receipt = fixture()
        result = module.normalize(receipt, originals)
        self.assertEqual(len(result), 16)
        self.assertNotIn('S02E15', result)
        self.assertNotIn('S02_CLIP01', result)

    def test_rejects_incomplete_or_unapproved_receipts(self):
        originals, receipt = fixture()
        for patch in [{'status': 'FAILED'}, {'inventory_sha256': 'wrong'}, {'originals_modified': True}, {'public_access_authorized': True}, {'bucket': 'other'}, {'rights_mode': 'public'}, {'variants': {}}]:
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                module.normalize(dict(receipt, **patch), originals)

    def test_rejects_false_lineage_quality_and_qualification(self):
        originals, receipt = fixture()
        content_id = next(iter(receipt['variants']))
        for patch in [{'parent_sha256': 'wrong'}, {'height': 480}, {'full_readback': 'FAILED'}, {'full_decode': 'FAILED'}, {'bytes': 0}, {'key': '../other.mp4'}]:
            modified = copy.deepcopy(receipt)
            modified['variants'][content_id].update(patch)
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                module.normalize(modified, originals)

    def test_nonfinite_or_wrong_duration_is_rejected(self):
        originals, receipt = fixture()
        content_id = next(iter(receipt['variants']))
        for duration in ['NaN', 'inf', '-1', '1']:
            modified = copy.deepcopy(receipt)
            modified['variants'][content_id]['ffprobe']['format']['duration'] = duration
            with self.subTest(duration=duration), self.assertRaises(ValueError):
                module.normalize(modified, originals)
