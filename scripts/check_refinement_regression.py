#!/usr/bin/env python3
"""Static guard for browser-proven CineWatch features during test-repo refinement.

This gate deliberately does not claim browser qualification. It only prevents known
working feature code from being accidentally removed while presentation/provider
refinements are applied.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"FAIL  {message}", file=sys.stderr)
    raise SystemExit(1)


def read(path: str) -> str:
    target = ROOT / path
    if not target.is_file():
        fail(f"required refinement path missing: {path}")
    return target.read_text(encoding="utf-8")


def require(source: str, tokens: tuple[str, ...], label: str) -> None:
    for token in tokens:
        if token not in source:
            fail(f"{label} regression: missing {token}")


def forbid(source: str, tokens: tuple[str, ...], label: str) -> None:
    for token in tokens:
        if token in source:
            fail(f"{label} regression: obsolete customer-facing token remains: {token}")


def main() -> int:
    homepage = read("apps/web/src/components/home/HomepageExperience.tsx")
    title = read("apps/web/src/components/catalog/TitleDetails.tsx")
    frame = read("apps/web/src/components/site/SiteFrame.tsx")
    voice = read("apps/web/src/components/voice/VoiceLab.tsx")
    browse = read("apps/web/src/components/catalog/CatalogBrowse.tsx")
    media_identity = read("apps/web/src/components/catalog/MediaIdentity.tsx")
    news = read("apps/web/src/app/news/page.tsx")
    catalog_service = read("services/api/cinewatch_api/catalog/service.py")
    media_authority = read("services/api/cinewatch_api/media/authority.py")
    media_boundary = read("services/api/cinewatch_api/api/v1/media_authority.py")
    external_service = read("services/api/cinewatch_api/external/service.py")

    require(
        homepage,
        (
            "experience?.ratings?.map",
            "experience?.quote",
            "/trailers`",
            'title="Trending Now"',
            'title="Popular Movies"',
            'title="Popular TV Shows"',
            '<strong>Stream Now</strong>',
        ),
        "homepage",
    )
    print("PASS  homepage keeps ratings, quotes, trailers and proven discovery rails")

    require(
        title,
        (
            "lifecycleLabel(title.status",
            "RatingSourceLogo",
            "/trailers`",
            "/reviews`",
            "Retry season",
            'state === "empty"',
            'state === "error"',
            "/where-to-watch?media_type=",
            "/stream-now",
        ),
        "title experience",
    )
    print("PASS  title status, ratings, reviews, seasons and trailer journeys retained")

    require(
        frame,
        (
            '/api/cinewatch/search?q=',
            '.slice(0, 5)',
            'router.push("/voice-lab")',
            '["News", "/news"]',
            '["Trailers", "/trailers"]',
            '["Where to Watch", "/where-to-watch"]',
            '["Scripts", "/scripts"]',
            '["Lyrics & Songs", "/lyrics"]',
        ),
        "site frame",
    )
    print("PASS  search, Voice Lab and live footer destinations retained")

    require(
        voice,
        (
            "getUserMedia",
            "encodeWav",
            'type: "audio/wav"',
            "Accept recording",
            "Record again",
            "Submitted",
        ),
        "Voice Lab",
    )
    print("PASS  NexVox recording/playback/accept/retry lifecycle retained")

    require(
        news,
        (
            'new URL("/api/v1/news"',
            "article.image_url",
            "article.source.name",
            "article.title",
        ),
        "News",
    )
    print("PASS  real News data rendering path retained")

    require(
        media_identity,
        (
            "/brand/ratings/imdb.jpg",
            "/brand/ratings/rotten-tomatoes.jpg",
            "/brand/ratings/metacritic.jpg",
            "/brand/ratings/tmdb.jpg",
            "MediaTypeIcon",
        ),
        "rating/media identity",
    )
    print("PASS  rating logos and movie/TV icon identity retained")

    require(
        catalog_service,
        (
            "language_preference = bool(language)",
            "preferred_items + fallback_items",
            'params["primary_release_year"] = year',
            'params["first_air_date_year"] = year',
        ),
        "deterministic discovery",
    )
    require(browse, ("pageHref(basePath, payload, payload.page + 1)",), "browse pagination")
    print("PASS  type/year hard scope and deterministic language-priority discovery retained")

    require(
        media_authority,
        ("find_override", "record_gap", "return provider_url", "return None"),
        "missing media authority",
    )
    require(media_boundary, ("provider content remains eligible", "return payload"), "missing media fail-open boundary")
    print("PASS  missing-media logging/override remains fail-open for catalog eligibility")

    require(
        external_service,
        (
            'f"{media_type}-{tmdb_id}"',
            "self._identity(song) != self._identity(clean_term)",
            "self._identity(result_artist) != self._identity(clean_artist)",
            "if len(exact) != 1",
            "if year is not None",
        ),
        "external identity",
    )
    print("PASS  Watchmode/Lyrics/Screenplay identity guards retained")

    customer_sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "apps/web/src").rglob("*.tsx")
    )
    forbid(
        customer_sources,
        (
            "Loading CineWatch TV",
            "provider results",
            "Source: TMDb",
            "Live provider failure",
            "did not substitute fixture data",
            "live TMDb",
        ),
        "customer UI",
    )
    print("PASS  customer UI stays free of removed engineering/debug wording")

    print("PASS  refinement regression guard (static only; browser proof still required)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
