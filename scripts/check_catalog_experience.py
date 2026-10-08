#!/usr/bin/env python3
"""Static R3 catalog-policy gate. Real browser/provider proof is deliberately separate."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "/api/v1/catalog/title/{media_type}/{provider_id}": "v1_catalog_title",
    "/api/v1/catalog/title/{media_type}/{provider_id}/videos": "v1_catalog_title_videos",
    "/api/v1/catalog/title/{media_type}/{provider_id}/reviews": "v1_catalog_title_reviews",
    "/api/v1/catalog/title/tv/{provider_id}/season/{season_number}": "v1_catalog_tv_season",
    "/api/v1/catalog/person/{provider_id}": "v1_catalog_person",
    "/api/v1/catalog/provider/{provider_id}": "v1_catalog_provider",
    "/api/v1/catalog/browse/{kind}/{slug}": "v1_catalog_browse",
}


def fail(message: str) -> None:
    print(f"FAIL  {message}", file=sys.stderr)
    raise SystemExit(1)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    required = (
        "services/api/cinewatch_api/contracts/catalog.py",
        "services/api/cinewatch_api/catalog/service.py",
        "services/api/cinewatch_api/api/v1/catalog.py",
        "apps/web/src/components/catalog/TitleDetails.tsx",
        "apps/web/src/components/catalog/TitleVideos.tsx",
        "apps/web/src/components/catalog/PersonDetails.tsx",
        "apps/web/src/components/catalog/ReviewsPage.tsx",
        "apps/web/src/app/title/[mediaType]/[providerId]/details/page.tsx",
        "apps/web/src/app/title/[mediaType]/[providerId]/trailers/page.tsx",
        "apps/web/src/app/provider/[providerId]/page.tsx",
    )
    missing = [path for path in required if not (ROOT / path).is_file()]
    if missing:
        fail("missing R3 catalog paths: " + ", ".join(missing))
    print("PASS  R3 catalog source paths")

    api = read("services/api/cinewatch_api/api/v1/catalog.py")
    schema = json.loads((ROOT / "packages/contracts/openapi/cinewatch-v1.openapi.json").read_text(encoding="utf-8"))
    for path, operation in EXPECTED.items():
        if f'operation_id="{operation}"' not in api:
            fail(f"catalog API missing operation: {operation}")
        if schema.get("paths", {}).get(path, {}).get("get", {}).get("operationId") != operation:
            fail(f"canonical OpenAPI stale for {path}")
    print("PASS  title/video/review/season/person/provider/browse API authority")

    service = read("services/api/cinewatch_api/catalog/service.py")
    for token in (
        '"with_origin_country": "KE"',
        '"with_original_language": "sw"',
        '"with_companies"] = 3096',
        '"YouTube"',
        '"Trailer", "Teaser", "Clip", "Featurette", "Behind the Scenes"',
        '_person_crew_credits',
        'official_homepage_url',
    ):
        if token not in service:
            fail(f"catalog service missing R3 policy token: {token}")
    if "api_key" in service.casefold():
        fail("catalog service must not own provider credential values")
    print("PASS  discovery parity, video authority, behind-camera credits and provider handoff policy")

    title = read("apps/web/src/components/catalog/TitleDetails.tsx")
    for token in (
        '/trailers`',
        '/details`',
        'RatingSourceLogo source="tmdb"',
        '/provider/${provider.provider_id}',
        'Retry season',
        'state === "empty"',
        '/stream-now',
        '/under-development/music-tracks',
    ):
        if token not in title:
            fail(f"title experience missing R3 token: {token}")
    for forbidden in ("watch_information_url", "youtube-nocookie.com/embed"):
        if forbidden in title:
            fail(f"title page bypasses dedicated R3 authority: {forbidden}")
    print("PASS  title details use dedicated trailers/details, visual provenance, provider boundary and terminal season states")

    combined = title + read("apps/web/src/components/home/HomepageExperience.tsx") + read("apps/web/src/components/site/SiteFrame.tsx")
    for forbidden in ("setInterval(", "window.location.reload(", "location.reload("):
        if forbidden in combined:
            fail(f"periodic/full-page refresh is forbidden: {forbidden}")
    print("PASS  no periodic refresh mechanism")

    browser_source = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "apps/web/src").rglob("*.tsx"))
    for forbidden in ("api.themoviedb.org", "www.omdbapi.com", "TMDB_API_KEY", "OMDB_API_KEY"):
        if forbidden in browser_source:
            fail(f"provider authority leaked into browser source: {forbidden}")
    print("PASS  browser remains provider-secret neutral")

    print("PASS  R3 static catalog policy (does not claim browser qualification)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
