#!/usr/bin/env python3
"""Static policy gate for CWTV.V1.3.3.2.2 homepage browser experience."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = (
    "services/api/cinewatch_api/contracts/home_experience.py",
    "services/api/cinewatch_api/home/experience.py",
    "services/api/cinewatch_api/api/v1/home_experience.py",
    "services/api/tests/test_home_experience.py",
    "services/api/tests/test_home_experience_endpoint.py",
    "apps/web/src/components/home/HomepageExperience.tsx",
    "apps/web/src/components/home/HomepageExperience.module.css",
    "apps/web/src/components/site/SiteFrame.tsx",
    "apps/web/src/components/site/SiteFrame.module.css",
    "apps/web/src/app/page.tsx",
    "apps/web/src/app/layout.tsx",
    "apps/web/next.config.ts",
    "docs/architecture/CineWatch_TV_V1_Homepage_Discovery_Trailer_Search_Browser_Runtime_Foundation_001.md",
    "docs/architecture/decisions/CWTV_ADR_0010_Homepage_Interaction_and_Lazy_Discovery_Authority.md",
    "docs/architecture/evidence/CineWatch_TV_V1_3_3_2_2_Homepage_Board_Reference_and_Runtime_Qualification_001.md",
    "tests/repository/test_homepage_experience.py",
)

EXPECTED_PATHS = {
    "/api/v1/home/rails/{slug}": "v1_home_rail",
    "/api/v1/home/trailers": "v1_home_trailers",
    "/api/v1/home/search": "v1_home_search",
    "/api/v1/home/genres": "v1_home_genres",
    "/api/v1/home/hero/{media_type}/{provider_id}": "v1_home_hero_experience",
}

EXPECTED_SCHEMAS = {
    "HomeExternalRating",
    "HomeTrailer",
    "HomeHeroExperience",
    "HomeRailResponse",
    "HomeTrailerCard",
    "HomeTrailerRailResponse",
    "HomeSearchSuggestion",
    "HomeSearchResponse",
    "HomeGenreEntry",
    "HomeGenresResponse",
}


def fail(message: str) -> None:
    print(f"FAIL  {message}", file=sys.stderr)
    raise SystemExit(1)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    if missing:
        fail("missing homepage experience paths: " + ", ".join(missing))
    print("PASS  homepage experience source, test and evidence paths")

    if (ROOT / "apps/web/src/app/api").exists():
        fail("Next.js application API routes remain forbidden; FastAPI owns product APIs")

    config = read("apps/web/next.config.ts")
    for token in ('source: "/api/cinewatch/:path*"', '/api/v1/:path*'):
        if token not in config:
            fail(f"same-origin FastAPI transport rewrite missing: {token}")
    print("PASS  FastAPI authority retained behind configuration-only browser rewrite")

    route = read("services/api/cinewatch_api/api/v1/home_experience.py")
    router = read("services/api/cinewatch_api/api/v1/router.py")
    if "home_experience_router" not in router or "include_router(home_experience_router)" not in router:
        fail("V1 router must compose homepage experience routes")
    for path, operation_id in EXPECTED_PATHS.items():
        suffix = path.removeprefix("/api/v1/home")
        if suffix and f'"{suffix}"' not in route:
            fail(f"homepage experience route source missing suffix: {suffix}")
        if f'operation_id="{operation_id}"' not in route:
            fail(f"homepage experience operation ID missing: {operation_id}")
    print("PASS  homepage lazy/search/trailer/genre/hero endpoint authority")

    service = read("services/api/cinewatch_api/home/experience.py")
    required_service_tokens = (
        '"upcoming": "Upcoming"',
        '"k-drama": "K-Drama"',
        '"kenyan-stories": "Kenyan Stories"',
        '"bollywood": "Bollywood"',
        '"nollywood": "Nollywood"',
        '"chinese": "Chinese"',
        '"hollywood": "Hollywood"',
        '"tyler-perry": "Tyler Perry"',
        '"/genre/movie/list"',
        '"/genre/tv/list"',
        '"/search/multi"',
        '"YouTube"',
        '"Trailer"',
        '"Teaser"',
        'f"/tv/{provider_id}/season/{latest_season}/videos"',
        "quote=None",
        "TRAILER_CANDIDATE_LIMIT = 6",
        "TRAILER_RAIL_LIMIT = 4",
    )
    for token in required_service_tokens:
        if token not in service:
            fail(f"homepage experience service missing policy token: {token}")
    if "api_key" in service.lower():
        fail("homepage experience service must not own raw provider credentials")
    print("PASS  bounded CineWatch discovery and season-aware trailer policy")

    base_contract = read("services/api/cinewatch_api/contracts/home.py")
    for token in ("genre_ids: list[int]", "future_path: str | None"):
        if token not in base_contract:
            fail(f"homepage card identity contract missing: {token}")
    print("PASS  lightweight future-destination identity retained on homepage cards")

    homepage = read("apps/web/src/components/home/HomepageExperience.tsx")
    for token in (
        'title="Stream Now"',
        "Coming to Stream Now",
        "Rights-cleared playback will appear here.",
        'title="Trending Now"',
        'title="Popular Movies"',
        'title="Popular TV Shows"',
        '<LazyRail slug="upcoming" />',
        '<LazyRail slug="k-drama" />',
        "LazyTrailerRail",
        "LazyGenres",
        "href={futurePath(item)}",
        "data-genre-ids",
        "youtube-nocookie.com/embed",
        "Watch Trailer",
    ):
        if token not in homepage:
            fail(f"homepage browser experience missing token: {token}")
    if "data-future-path" in homepage:
        fail("homepage must not retain inert future-route markers after R2 route activation")

    if "trending_people" in homepage:
        fail("people must not render as a homepage rail in CWTV.V1.3.3.2.2")
    if homepage.count("stream-placeholder-") != 1 or "length: 5" not in homepage:
        fail("Stream Now must render exactly five rights-safe placeholder slots")
    print("PASS  rights-safe Stream Now, live trailer and inert future-card behavior")

    frame = read("apps/web/src/components/site/SiteFrame.tsx")
    for token in (
        "/brand/cinewatch-lockup-on-dark.svg",
        "/brand/cinewatch-lockup-on-light.svg",
        "Voice search",
        "cinewatch-theme",
        "HomeGenreEntry",
        "HomeSearchSuggestion",
        'href="#stream-now"',
        'href="#discover"',
        'aria-disabled="true"',
    ):
        if token not in frame:
            fail(f"unified site frame missing token: {token}")
    print("PASS  exact repository lockups, unified search/theme/navigation/footer frame")

    source_tree = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "apps/web/src").rglob("*.tsx")
    )
    for forbidden in ("api.themoviedb.org", "TMDB_API_KEY", "OMDB_API_KEY"):
        if forbidden in source_tree:
            fail(f"provider credential/authority leaked into browser source: {forbidden}")
    print("PASS  browser source remains provider-credential neutral")

    schema = json.loads(
        (ROOT / "packages/contracts/openapi/cinewatch-v1.openapi.json").read_text(encoding="utf-8")
    )
    paths = schema.get("paths", {})
    for path, operation_id in EXPECTED_PATHS.items():
        operation = paths.get(path, {}).get("get", {})
        if operation.get("operationId") != operation_id:
            fail(f"canonical OpenAPI stale for {path}; regenerate contracts")
    schemas = schema.get("components", {}).get("schemas", {})
    for model in EXPECTED_SCHEMAS:
        if model not in schemas:
            fail(f"canonical OpenAPI missing homepage experience schema: {model}")

    generated = read("packages/contracts/src/generated/openapi.d.ts")
    index = read("packages/contracts/src/index.d.ts")
    for operation_id in EXPECTED_PATHS.values():
        if operation_id not in generated:
            fail(f"generated TypeScript missing operation: {operation_id}")
    for model in EXPECTED_SCHEMAS:
        if f"export type {model}" not in index:
            fail(f"contract index missing homepage experience alias: {model}")
    print("PASS  canonical OpenAPI and generated TypeScript homepage experience authority")

    evidence = read(
        "docs/architecture/evidence/CineWatch_TV_V1_3_3_2_2_Homepage_Board_Reference_and_Runtime_Qualification_001.md"
    )
    for token in (
        "1536 × 1229",
        "166a8da7fe6c2e2793d5f2083091d000d3f3057953cecde42bfad8f5101e1515",
        "browser evidence pending",
    ):
        if token.casefold() not in evidence.casefold():
            fail(f"homepage visual reference evidence missing: {token}")
    print("PASS  approved board reference preserved without claiming browser qualification")

    print("PASS  CWTV.V1.3.3.2.2 Homepage Discovery, Trailer, Search & Browser Runtime Foundation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
