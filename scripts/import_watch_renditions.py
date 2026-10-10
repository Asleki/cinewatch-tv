#!/usr/bin/env python3
"""Verify an independently acquired private rendition receipt before source application."""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_SHA = '297c5c12e34900b5a4f807f73e664ad1c2a410c95830272ea36043f95f797f9d'
PROFILE = 'h264-240p-350k-aac64k-v1'


def normalize(receipt, originals):
    if receipt.get('status') != 'PASS' or receipt.get('inventory_sha256') != INVENTORY_SHA:
        raise ValueError('Unqualified receipt or source inventory mismatch')
    if receipt.get('bucket') != 'cinewatch-media-qualifications' or receipt.get('profile') != PROFILE:
        raise ValueError('Wrong private destination or profile')
    if receipt.get('originals_modified') is not False or receipt.get('public_access_authorized') is not False or receipt.get('rights_mode') != 'simulated-owner-only':
        raise ValueError('Owner-only rights/original-preservation boundary mismatch')
    required = {content_id for content_id, item in originals.items() if item['available'] and item['height'] > 240}
    variants = receipt.get('variants', {})
    if set(variants) != required or len(required) != 16:
        raise ValueError('Incomplete or unexpected derivative set')
    normalized = {}
    for content_id, item in variants.items():
        source = originals[content_id]
        if item.get('full_readback') != 'PASS' or item.get('full_decode') != 'PASS' or item.get('profile') != PROFILE:
            raise ValueError('Unqualified derived media')
        if item.get('parent_sha256') != source['sha256'] or item.get('height') != 240:
            raise ValueError('Broken source lineage or quality claim')
        sha = item.get('sha256', '')
        if not re.fullmatch('[0-9a-f]{64}', sha) or type(item.get('bytes')) is not int or item['bytes'] <= 0:
            raise ValueError('Malformed derived identity')
        expected_key = f'simulated-rights/bonanza/derived/{content_id}/240p/{sha}.mp4'
        if item.get('key') != expected_key:
            raise ValueError('Unapproved object key')
        probe = item.get('ffprobe', {})
        streams = probe.get('streams', [])
        videos = [stream for stream in streams if stream.get('codec_type') == 'video']
        if len(videos) != 1 or videos[0].get('height') != 240 or videos[0].get('codec_name') != 'h264':
            raise ValueError('FFprobe does not establish one genuine 240p H.264 stream')
        duration = float(probe.get('format', {}).get('duration', 'nan'))
        if not math.isfinite(duration) or duration <= 0 or abs(duration - float(source['duration_seconds'])) >= 1:
            raise ValueError('Derived duration mismatch')
        normalized[content_id] = {key: item[key] for key in ['key', 'sha256', 'bytes', 'height', 'parent_sha256', 'profile']}
    return normalized


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('receipt', type=Path)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    if args.receipt.is_symlink() or args.receipt.stat().st_size > 2_000_000:
        raise ValueError('Unsafe/oversized receipt')
    raw = args.receipt.read_bytes()
    if not re.fullmatch('[0-9a-f]{64}', args.sha256) or hashlib.sha256(raw).hexdigest() != args.sha256:
        raise ValueError('Receipt checksum mismatch')
    originals = json.loads((ROOT / 'infra/cloudflare/original-registry.json').read_text())
    normalized = normalize(json.loads(raw), originals)
    if not args.verify_only:
        body = json.dumps(normalized, indent=2) + '\n'
        for path in ['apps/web/src/lib/watch/renditions.json', 'services/api/cinewatch_api/watch/renditions.json']:
            (ROOT / path).write_text(body)
        (ROOT / 'infra/cloudflare/renditions.mjs').write_text('export default ' + body.rstrip() + ';\n')
    print(f'PASS receipt SHA-256, source lineage and {len(normalized)} private renditions; verify_only={args.verify_only}')


if __name__ == '__main__':
    main()
