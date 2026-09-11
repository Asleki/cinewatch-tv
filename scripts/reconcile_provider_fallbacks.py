#!/usr/bin/env python3
"""Validate and deterministically reconcile CineWatch provider fallback WebP assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FALLBACK_ROOT = ROOT / "apps/web/public/provider-fallbacks"
MANIFEST = FALLBACK_ROOT / "manifest.json"

DIRECTORIES: dict[str, tuple[str, set[str]]] = {
    "people": ("profile", {"person"}),
    "networks": ("logo", {"network"}),
    "posters": ("poster", {"movie", "tv"}),
    "backdrops": ("backdrop", {"movie", "tv"}),
}
NAME_RE = re.compile(
    r"^(?P<provider>[a-z0-9]+)-(?P<entity>person|network|movie|tv)-"
    r"(?P<provider_id>[1-9][0-9]*)-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\.webp$"
)


def fail(message: str) -> None:
    print(f"FAIL  {message}", file=sys.stderr)
    raise SystemExit(1)


def is_webp(path: Path) -> bool:
    data = path.read_bytes()[:12]
    return len(data) == 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"


def build_manifest() -> dict[str, object]:
    entries: list[dict[str, object]] = []
    for directory, (asset_kind, allowed_entities) in DIRECTORIES.items():
        asset_dir = FALLBACK_ROOT / directory
        asset_dir.mkdir(parents=True, exist_ok=True)
        for path in sorted(asset_dir.iterdir(), key=lambda item: item.name):
            if not path.is_file() or path.name.startswith("."):
                continue
            match = NAME_RE.fullmatch(path.name)
            if match is None:
                fail(f"invalid fallback filename: {path.relative_to(ROOT)}")
            entity_type = match.group("entity")
            if entity_type not in allowed_entities:
                fail(
                    f"fallback entity {entity_type} is invalid for {directory}: "
                    f"{path.relative_to(ROOT)}"
                )
            if not is_webp(path):
                fail(f"fallback asset is not a valid WebP container: {path.relative_to(ROOT)}")
            content = path.read_bytes()
            entries.append(
                {
                    "provider": match.group("provider"),
                    "entity_type": entity_type,
                    "provider_id": int(match.group("provider_id")),
                    "slug": match.group("slug"),
                    "asset_kind": asset_kind,
                    "filename": path.name,
                    "public_path": f"/provider-fallbacks/{directory}/{path.name}",
                    "sha256": hashlib.sha256(content).hexdigest(),
                    "size_bytes": len(content),
                }
            )
    entries.sort(
        key=lambda entry: (
            str(entry["provider"]),
            str(entry["entity_type"]),
            int(entry["provider_id"]),
            str(entry["asset_kind"]),
        )
    )
    return {
        "schema_version": "1.0",
        "generator": "scripts/reconcile_provider_fallbacks.py",
        "entries": entries,
    }


def canonical_text(manifest: dict[str, object]) -> str:
    return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    expected = canonical_text(build_manifest())
    if args.check:
        if not MANIFEST.is_file():
            fail("fallback manifest is missing")
        if MANIFEST.read_text(encoding="utf-8") != expected:
            fail("fallback manifest is stale; run scripts/reconcile_provider_fallbacks.py")
        print("PASS  provider fallback manifest is reconciled")
        return 0

    MANIFEST.write_text(expected, encoding="utf-8")
    manifest = json.loads(expected)
    print(f"PASS  reconciled {len(manifest['entries'])} provider fallback asset(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
