#!/usr/bin/env python3
"""Export or verify the canonical CineWatch OpenAPI document."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def canonical_openapi_text(root: Path) -> str:
    service_root = root / "services/api"
    sys.path.insert(0, str(service_root))

    from cinewatch_api.application import create_app  # noqa: PLC0415
    from cinewatch_api.settings import Settings  # noqa: PLC0415

    app = create_app(Settings(_env_file=None))
    schema = app.openapi()
    return json.dumps(schema, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=repo_root())
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    root = args.repo.resolve()
    target = root / "packages/contracts/openapi/cinewatch-v1.openapi.json"
    expected = canonical_openapi_text(root)

    if args.check:
        if not target.is_file():
            print(f"FAIL  canonical OpenAPI document missing: {target.relative_to(root)}", file=sys.stderr)
            return 1
        actual = target.read_text(encoding="utf-8")
        if actual != expected:
            print("FAIL  canonical OpenAPI document is stale", file=sys.stderr)
            print("NEXT  run: python scripts/export_openapi_contract.py", file=sys.stderr)
            return 1
        print("PASS  canonical OpenAPI document matches FastAPI authority")
        return 0

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(expected, encoding="utf-8")
    print(f"PASS  wrote {target.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
