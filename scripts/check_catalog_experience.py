#!/usr/bin/env python3
"""Static architecture gate for CWTV.V1.3.3.2.2-R2 navigable catalog hardening."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = (
    "services/api/cinewatch_api/contracts/catalog.py",
    "services/api/cinewatch_api/catalog/__init__.py",
    "services/api/cinewatch_api/catalog/service.py",
    "services/api/cinewatch_api/api/v1/catalog.py",
    "apps/web/src/lib/api/catalog-client.ts",
    "apps/web/src/components/catalog/CatalogBrowse.tsx",
    "apps/web/src/components/catalog/TitleDetails.tsx",
    "apps/web/src/components/catalog/PersonDetails.tsx",
    "apps/web/src/app/title/[mediaType]/[providerId]/page.tsx",
    "apps/web/src/app/person/[providerId]/page.tsx",
    "apps/web/src/app/genre/[slug]/page.tsx",
    "apps/web/src/app/discover/[slug]/page.tsx",
    "apps/web/src/app/country/[code]/page.tsx",
    "apps/web/src/app/genres/page.tsx",
    "apps/web/src/app/cinema-guide/page.tsx",
    "services/api/tests/test_catalog_service.py",
    "services/api/tests/test_catalog_endpoint.py",
    "tests/repository/test_catalog_experience.py",
)

EXPECTED = {
    "/api/v1/catalog/title/{media_type}/{provider_id}": "v1_catalog_title",
    "/api/v1/catalog/title/{media_type}/{provider_id}/reviews": "v1_catalog_title_reviews",
    "/api/v1/catalog/title/tv/{provider_id}/season/{season_number}": "v1_catalog_tv_season",
    "/api/v1/catalog/person/{provider_id}": "v1_catalog_person",
    "/api/v1/catalog/browse/{kind}/{slug}": "v1_catalog_browse",
}


def fail(message: str) -> None:
    print(f"FAIL  {message}", file=sys.stderr)
    raise SystemExit(1)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    if missing:
        fail("missing catalog experience paths: " + ", ".join(missing))
    print("PASS  catalog page, API, test and policy paths")

    router = read("services/api/cinewatch_api/api/v1/router.py")
    if "catalog_router" not in router or "include_router(catalog_router)" not in router:
        fail("catalog router is not composed into V1")
    source = read("services/api/cinewatch_api/api/v1/catalog.py")
    for operation in EXPECTED.values():
        if f'operation_id="{operation}"' not in source:
            fail(f"missing catalog operation identity: {operation}")
    print("PASS  bounded title/person/review/season/browse API authority")

    service = read("services/api/cinewatch_api/catalog/service.py")
    for token in (
        "watch/providers",
        '"Rotten Tomatoes"',
        '"Internet Movie Database"',
        '"with_origin_country": "KE"',
        '"with_original_language": "sw"',
        '"with_companies"] = 3096',
        'f"/tv/{provider_id}/season/{latest_season}/videos"',
    ):
        if token not in service:
            fail(f"catalog service missing governed enrichment token: {token}")
    if "api_key" in service.casefold():
        fail("catalog service must not own provider credential values")
    print("PASS  provider-neutral page enrichment and discovery heuristics")

    frame = read("apps/web/src/components/site/SiteFrame.tsx")
    for token in ('href="/genres"', 'href="/cinema-guide"', "router.push(item.futurePath)", "cinewatch-theme"):
        if token not in frame:
            fail(f"site frame navigation hardening missing: {token}")
    homepage = read("apps/web/src/components/home/HomepageExperience.tsx")
    for token in ("href={futurePath(item)}", "href={destination}", "className={styles.seeAll}", "CompactLoading"):
        if token not in homepage:
            fail(f"homepage navigation/loading hardening missing: {token}")
    if "data-future-path" in homepage:
        fail("homepage must not retain inert future-route markers after R2 route activation")
    print("PASS  homepage identities are active destinations with compact loading")

    combined_ui = frame + "\n" + homepage + "\n" + read("apps/web/src/components/catalog/TitleDetails.tsx")
    for forbidden in ("setInterval(", "window.location.reload(", "location.reload("):
        if forbidden in combined_ui:
            fail(f"periodic/full-page refresh behavior is forbidden: {forbidden}")
    if "seasonStatus" not in combined_ui or '"error"' not in combined_ui:
        fail("TV season expansion must distinguish loading from failure")
    print("PASS  no periodic refresh mechanism and season loading has terminal failure state")

    browser_source = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "apps/web/src").rglob("*.tsx"))
    for forbidden in ("api.themoviedb.org", "TMDB_API_KEY", "OMDB_API_KEY"):
        if forbidden in browser_source:
            fail(f"provider credential authority leaked into browser source: {forbidden}")
    print("PASS  browser remains credential-neutral")

    schema_path = ROOT / "packages/contracts/openapi/cinewatch-v1.openapi.json"
    if schema_path.is_file():
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        paths = schema.get("paths", {})
        for path, operation_id in EXPECTED.items():
            operation = paths.get(path, {}).get("get", {})
            if operation.get("operationId") != operation_id:
                fail(f"canonical OpenAPI stale for {path}; regenerate contracts")
    generated = read("packages/contracts/src/generated/openapi.d.ts")
    for operation in EXPECTED.values():
        if operation not in generated:
            fail(f"generated TypeScript stale for operation {operation}")
    print("PASS  FastAPI -> OpenAPI -> TypeScript catalog propagation")

    print("PASS  CWTV.V1.3.3.2.2-R2 Homepage Navigation, Catalog & Loading Hardening")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
