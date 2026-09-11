#!/usr/bin/env python3
"""Static policy gate for CWTV.V1.3.3.1 provider and media-fallback authority."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICE_ROOT = ROOT / "services/api"
sys.path.insert(0, str(SERVICE_ROOT))

from cinewatch_api.media.fallbacks import MediaGap  # noqa: E402

REQUIRED = (
    "docs/architecture/"
    "CineWatch_TV_V1_Local_Provider_Runtime_Secret_Boundary_and_Media_Fallback_Authority_001.md",
    "docs/architecture/decisions/CWTV_ADR_0008_Provider_Runtime_and_Media_Fallback_Authority.md",
    "services/api/cinewatch_api/providers/errors.py",
    "services/api/cinewatch_api/providers/tmdb.py",
    "services/api/cinewatch_api/providers/omdb.py",
    "services/api/cinewatch_api/media/fallbacks.py",
    "scripts/probe_provider_runtime.py",
    "scripts/reconcile_provider_fallbacks.py",
    "apps/web/public/provider-fallbacks/manifest.json",
    "services/api/tests/test_provider_settings.py",
    "services/api/tests/test_provider_clients.py",
    "services/api/tests/test_media_fallbacks.py",
    "tests/repository/test_provider_runtime.py",
)


def fail(message: str) -> None:
    print(f"FAIL  {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    if missing:
        fail("missing provider-runtime paths: " + ", ".join(missing))
    print("PASS  provider-runtime authority paths")

    env = (ROOT / ".env.example").read_text(encoding="utf-8")
    for key in ("TMDB_API_KEY=", "OMDB_API_KEY="):
        if key not in env:
            fail(f"local provider environment key missing: {key[:-1]}")
    if re.search(r"NEXT_PUBLIC_[A-Z0-9_]*(?:TMDB|OMDB|PROVIDER)", env):
        fail("provider credentials must never be browser-public environment variables")

    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    if ".env.*" not in gitignore or "!.env.example" not in gitignore:
        fail(".env.local exclusion policy is incomplete")
    print("PASS  local secret boundary and Git exclusion")

    settings = (ROOT / "services/api/cinewatch_api/settings.py").read_text(encoding="utf-8")
    for token in (
        'env_file=(".env", ".env.local")',
        "tmdb_api_key: SecretStr | None",
        "omdb_api_key: SecretStr | None",
    ):
        if token not in settings:
            fail(f"server-only provider settings authority missing: {token}")
    print("PASS  Pydantic SecretStr provider configuration")

    project = tomllib.loads((ROOT / "services/api/pyproject.toml").read_text(encoding="utf-8"))
    dependencies = project.get("project", {}).get("dependencies", [])
    if "httpx==0.28.1" not in dependencies:
        fail("provider HTTP runtime must pin httpx==0.28.1")
    print("PASS  governed provider HTTP dependency")

    if (ROOT / "apps/web/src/app/api").exists():
        fail("Next.js API routes remain forbidden; FastAPI owns provider policy")
    frontend_sources = list((ROOT / "apps/web/src").rglob("*.ts")) + list(
        (ROOT / "apps/web/src").rglob("*.tsx")
    )
    frontend = "\n".join(path.read_text(encoding="utf-8") for path in frontend_sources)
    for marker in ("api.themoviedb.org", "www.omdbapi.com", "TMDB_API_KEY", "OMDB_API_KEY"):
        if marker in frontend:
            fail(f"frontend bypasses CineWatch provider boundary: {marker}")
    print("PASS  FastAPI provider authority remains exclusive")

    manifest = json.loads(
        (ROOT / "apps/web/public/provider-fallbacks/manifest.json").read_text(encoding="utf-8")
    )
    if manifest.get("schema_version") != "1.0" or not isinstance(manifest.get("entries"), list):
        fail("provider fallback manifest schema is invalid")

    person = MediaGap(
        provider="tmdb",
        entity_type="person",
        provider_id=123456,
        entity_name="Jane Example",
        asset_kind="profile",
    )
    if person.remediation != "AWAITING_HUMAN_RESEARCH":
        fail("real-person fallback policy must require human research")
    if person.suggested_filename != "tmdb-person-123456-jane-example.webp":
        fail("person fallback naming authority drifted")

    network = MediaGap(
        provider="tmdb",
        entity_type="network",
        provider_id=213,
        entity_name="Example Network",
        asset_kind="logo",
    )
    if network.remediation != "GENERATION_ALLOWED":
        fail("network-logo remediation must remain generation-eligible")

    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts/reconcile_provider_fallbacks.py"), "--check"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode != 0:
        fail("fallback reconciliation failed: " + completed.stdout.strip())
    print("PASS  deterministic media-gap naming and fallback reconciliation")

    print("PASS  CWTV.V1.3.3.1 provider runtime, secret boundary, and media fallback policy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
