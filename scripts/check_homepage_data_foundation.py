#!/usr/bin/env python3
"""Static policy gate for CWTV.V1.3.3.2.1 homepage data authority."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "services/api/cinewatch_api/contracts/home.py",
    "services/api/cinewatch_api/home/__init__.py",
    "services/api/cinewatch_api/home/aggregation.py",
    "services/api/cinewatch_api/api/v1/home.py",
    "docs/architecture/CineWatch_TV_V1_TMDb_Real_Data_Homepage_Foundation_001.md",
    "docs/architecture/decisions/CWTV_ADR_0009_Homepage_Data_Contract_and_TMDb_Aggregation_Authority.md",
    "services/api/tests/test_home_aggregation.py",
    "services/api/tests/test_home_endpoint.py",
    "tests/repository/test_homepage_data_foundation.py",
]


def fail(message: str) -> None:
    print(f"FAIL  {message}", file=sys.stderr)
    raise SystemExit(1)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    if missing:
        fail("missing homepage foundation paths: " + ", ".join(missing))
    print("PASS  homepage data foundation paths")

    router = read("services/api/cinewatch_api/api/v1/router.py")
    if "home_router" not in router or "include_router(home_router)" not in router:
        fail("V1 router must compose the homepage route")
    home_route = read("services/api/cinewatch_api/api/v1/home.py")
    if 'operation_id="v1_home"' not in home_route:
        fail("homepage route must expose stable operation ID v1_home")
    print("PASS  stable /api/v1/home route composition")

    aggregation = read("services/api/cinewatch_api/home/aggregation.py")
    for endpoint in (
        '"/configuration"',
        '"/trending/all/day"',
        '"/movie/popular"',
        '"/tv/popular"',
        '"/trending/person/day"',
    ):
        if endpoint not in aggregation:
            fail(f"homepage aggregation missing TMDb authority endpoint: {endpoint}")
    if "MediaGap" not in aggregation:
        fail("homepage aggregation must reuse governed media-gap authority")
    if "OmdbClient" in aggregation or "omdb" in aggregation.lower():
        fail("OMDb must not become an unconditional homepage dependency")
    if "cinewatch_api.database" in aggregation or "sqlalchemy" in aggregation.lower():
        fail("homepage foundation must not introduce persistence authority")
    print("PASS  TMDb-primary bounded aggregation and fallback reuse")

    contract = read("services/api/cinewatch_api/contracts/home.py")
    for model in (
        "class HomeResponse",
        "class HomeSections",
        "class HomeItem",
        "class HomeRating",
        "class HomeMediaGap",
    ):
        if model not in contract:
            fail(f"homepage public contract missing model: {model}")
    print("PASS  provider-neutral homepage response model")

    schema_path = ROOT / "packages/contracts/openapi/cinewatch-v1.openapi.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    paths = schema.get("paths", {})
    if "/api/v1/home" not in paths:
        fail(
            "canonical OpenAPI is stale for homepage; "
            "run scripts/update_api_contracts.sh"
        )
    operation = paths["/api/v1/home"].get("get", {})
    if operation.get("operationId") != "v1_home":
        fail("canonical OpenAPI homepage operation ID drift")
    schemas = schema.get("components", {}).get("schemas", {})
    for model in ("HomeResponse", "HomeSections", "HomeItem", "HomeRating", "HomeMediaGap"):
        if model not in schemas:
            fail(f"canonical OpenAPI missing homepage schema: {model}")
    print("PASS  canonical OpenAPI homepage contract")

    generated = read("packages/contracts/src/generated/openapi.d.ts")
    if "v1_home" not in generated or '"/api/v1/home"' not in generated:
        fail("generated TypeScript contract is stale for homepage")
    index = read("packages/contracts/src/index.d.ts")
    for alias in ("HomeResponse", "HomeSections", "HomeItem", "HomeRating", "HomeMediaGap"):
        if f"export type {alias}" not in index:
            fail(f"governed contract alias missing: {alias}")
    print("PASS  generated TypeScript homepage authority")

    foundation = read("scripts/check_contract_foundation.py")
    if "if set(paths) != set(expected)" in foundation:
        fail(
            "contract foundation still exact-enumerates every API route; "
            "feature growth would cause an update cascade"
        )
    if "missing_foundation_paths = set(expected) - set(paths)" not in foundation:
        fail("contract foundation must enforce system routes as subset invariants")
    print("PASS  contract foundation neutralized against product-route update cascades")

    for public_path in paths:
        lowered = public_path.lower()
        if "/tmdb" in lowered or "/omdb" in lowered:
            fail(f"upstream provider identity leaked into public API path: {public_path}")
    print("PASS  public API hides upstream-provider route identity")

    docs = "\n".join(
        read(path)
        for path in (
            "docs/architecture/CineWatch_TV_V1_TMDb_Real_Data_Homepage_Foundation_001.md",
            "docs/architecture/decisions/CWTV_ADR_0009_Homepage_Data_Contract_and_TMDb_Aggregation_Authority.md",
        )
    )
    for forbidden in ("TMDB_API_KEY=", "OMDB_API_KEY=", "api_key="):
        if forbidden in docs:
            fail(f"secret assignment material entered homepage documentation: {forbidden}")
    print("PASS  homepage documentation secret-value exclusion")

    print("PASS  CWTV.V1.3.3.2.1 Homepage Data Contract & TMDb Aggregation Authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
