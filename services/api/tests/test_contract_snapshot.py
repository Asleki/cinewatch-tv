from __future__ import annotations

import json
from pathlib import Path

from cinewatch_api.application import create_app
from cinewatch_api.settings import Settings


def test_canonical_openapi_snapshot_matches_fastapi_authority() -> None:
    root = Path(__file__).resolve().parents[3]
    snapshot = json.loads(
        (root / "packages/contracts/openapi/cinewatch-v1.openapi.json").read_text(encoding="utf-8")
    )
    live = create_app(Settings(_env_file=None)).openapi()
    assert snapshot == live
