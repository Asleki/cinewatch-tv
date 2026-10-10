#!/usr/bin/env python3
"""Fail closed on private media authority drift or incomplete production qualities."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATHS = [ROOT / 'infra/cloudflare/original-registry.json', ROOT / 'apps/web/src/lib/watch/registry.json', ROOT / 'services/api/cinewatch_api/watch/originals.json']


def verify():
    originals = json.loads(PATHS[0].read_text())
    expected = {f'S02E{n:02d}' for n in range(1, 18)} | {f'S02_CLIP{n:02d}' for n in range(1, 5)}
    if set(originals) != expected:
        raise ValueError('Original registry must retain exactly 21 verified identities')
    worker_originals = json.loads((ROOT / 'infra/cloudflare/registry.mjs').read_text().strip().removeprefix('export default ').removesuffix(';'))
    if worker_originals != originals:
        raise ValueError('Worker original registry drift')
    for path in PATHS[1:]:
        if json.loads(path.read_text()) != originals:
            raise ValueError(f'Original registry drift: {path.relative_to(ROOT)}')
    for content_id, item in originals.items():
        permitted = content_id.startswith('S02_CLIP') or int(content_id[4:]) <= 14
        if item['available'] is not permitted:
            raise ValueError('Owner-approved episode restriction changed')
        if not re.fullmatch('[0-9a-f]{64}', item['sha256']) or type(item['bytes']) is not int or item['bytes'] <= 0:
            raise ValueError('Invalid source identity')
        if item['key'] != f"simulated-rights/bonanza/{content_id}/{item['sha256']}.mp4":
            raise ValueError('Original key drift')
    paths = [ROOT / 'apps/web/src/lib/watch/renditions.json', ROOT / 'services/api/cinewatch_api/watch/renditions.json']
    variants = json.loads(paths[0].read_text())
    if variants != json.loads(paths[1].read_text()):
        raise ValueError('Frontend/backend rendition authority drift')
    worker_variants = json.loads((ROOT / 'infra/cloudflare/renditions.mjs').read_text().strip().removeprefix('export default ').removesuffix(';'))
    if worker_variants != variants:
        raise ValueError('Worker rendition authority drift')
    required = {content_id for content_id, item in originals.items() if item['available'] and item['height'] > 240}
    if set(variants) != required:
        raise ValueError(f'Release blocked: expected {len(required)} verified 240p variants; got {len(variants)}')
    for content_id, item in variants.items():
        if item['parent_sha256'] != originals[content_id]['sha256'] or item['height'] != 240 or type(item['bytes']) is not int or item['bytes'] <= 0:
            raise ValueError('Invalid rendition lineage or resolution')
        if not re.fullmatch('[0-9a-f]{64}', item['sha256']) or item['key'] != f"simulated-rights/bonanza/derived/{content_id}/240p/{item['sha256']}.mp4":
            raise ValueError('Invalid immutable rendition identity')
    return len(originals), len(variants)


if __name__ == '__main__':
    try:
        count, variants = verify()
        print(f'PASS private watch registry: {count} originals, {variants} verified 240p variants')
    except (KeyError, ValueError, TypeError) as error:
        print(f'FAIL {error}')
        raise SystemExit(1)
