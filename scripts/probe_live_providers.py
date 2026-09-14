#!/usr/bin/env python
"""Probe configured CineWatch upstreams with real requests and identity checks.

This script never enables fixtures and never prints credentials. A provider is PASS
only after its real response satisfies the identity/shape check for that probe.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cinewatch_api.external.service import ExternalDataService
from cinewatch_api.providers.apify import ApifyScreenplayClient
from cinewatch_api.providers.kinocheck import KinoCheckClient
from cinewatch_api.providers.newsapi import NewsApiClient
from cinewatch_api.providers.omdb import OmdbClient
from cinewatch_api.providers.stands4 import Stands4LyricsClient
from cinewatch_api.providers.tmdb import TmdbClient
from cinewatch_api.providers.watchmode import WatchmodeClient
from cinewatch_api.settings import Settings

Probe = Callable[[], Awaitable[dict[str, object]]]


async def main() -> int:
    settings = Settings()
    report: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "fixture_mode": False,
        "providers": {},
        "not_probed": {
            "tunefind": "Evaluation candidate only; no usable trial credential is configured.",
            "movieglu": "No usable credential is configured.",
            "stands4_unassigned": "Additional STANDS4 credentials exist, but no service assignment is proven; no service is guessed.",
            "genius": "No usable OAuth/application credential is configured.",
            "7digital": "No usable OAuth/application credential is configured.",
            "nasa": "Account evidence exists, but no NASA API key is configured.",
            "roku": "Developer-program evidence exists, but no CineWatch API credential is configured.",
            "youtube_data_api": "No separate YouTube Data API credential is configured; current title trailers use TMDb video identities.",
            "tvmaze": "Candidate source only; no integration is implemented in Refined Test 02.",
            "musicbrainz": "Candidate source only; no integration is implemented in Refined Test 02.",
        },
    }

    async def probe(name: str, call: Probe) -> dict[str, object] | None:
        try:
            value = await call()
            status = str(value.pop("_qualification_status", "PASS"))
            report["providers"][name] = {"status": status, **value}
            return value
        except Exception as exc:  # qualification must preserve the real failure
            report["providers"][name] = {
                "status": "FAIL",
                "error_type": type(exc).__name__,
                "message": str(exc),
            }
            return None

    tmdb = TmdbClient(api_key=settings.tmdb_api_key)
    omdb = OmdbClient(api_key=settings.omdb_api_key)
    news = NewsApiClient(api_key=settings.news_api_key)
    watchmode = WatchmodeClient(api_key=settings.watchmode_api_key)
    kinocheck = KinoCheckClient(api_key=settings.kinocheck_api_key)
    lyrics = Stands4LyricsClient(
        user_id=settings.stands4_lyrics_user_id,
        token=settings.stands4_lyrics_token,
    )
    screenplay = ApifyScreenplayClient(token=settings.apify_api_token)

    await probe("tmdb_configuration", lambda: _tmdb_configuration(tmdb))
    await probe("tmdb_lupita_nyongo", lambda: _tmdb_lupita(tmdb))
    await probe("omdb_known_title", lambda: _omdb_title(omdb))
    await probe("newsapi_entertainment", lambda: _news(news))
    await probe("watchmode_tmdb_identity", lambda: _watchmode_identity(watchmode))
    await probe("kinocheck_tmdb_identity", lambda: _kinocheck_identity(kinocheck))
    await probe("stands4_lyrics_exact_identity", lambda: _lyrics_identity(lyrics))
    await probe("apify_screenplay_exact_identity", lambda: _screenplay_identity(screenplay))

    path = Path("qualification/live-provider-probe.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    failed = [name for name, payload in report["providers"].items() if payload["status"] == "FAIL"]
    for name, payload in report["providers"].items():
        print(f"{payload['status']}  {name}")
        if payload["status"] == "FAIL":
            print(f"      {payload['error_type']}: {payload['message']}")
        elif payload["status"] == "PARTIAL" and payload.get("detail"):
            print(f"      {payload['detail']}")
    for name, reason in report["not_probed"].items():
        print(f"NOT_PROBED  {name}: {reason}")
    print(f"REPORT {path}")
    return 1 if failed else 0


async def _tmdb_configuration(client: TmdbClient) -> dict[str, object]:
    payload = await client.configuration()
    images = payload.get("images")
    if not isinstance(images, dict):
        raise RuntimeError("TMDb configuration contained no images object.")
    return {"has_images_configuration": True}


async def _tmdb_lupita(client: TmdbClient) -> dict[str, object]:
    payload = await client.get_json(
        "/search/person",
        params={"query": "Lupita Nyong'o", "language": "en-US", "page": 1},
    )
    results = payload.get("results")
    if not isinstance(results, list) or not results:
        raise RuntimeError("TMDb returned no person result for Lupita Nyong'o.")
    exact = next(
        (
            item
            for item in results
            if isinstance(item, dict)
            and str(item.get("name", "")).casefold() == "lupita nyong'o".casefold()
        ),
        None,
    )
    if not isinstance(exact, dict):
        raise RuntimeError("TMDb returned results but no exact Lupita Nyong'o match.")
    return {
        "provider_id": exact.get("id"),
        "name": exact.get("name"),
        "known_for_department": exact.get("known_for_department"),
    }


async def _omdb_title(client: OmdbClient) -> dict[str, object]:
    payload = await client.lookup_imdb("tt1375666")
    if str(payload.get("imdbID", "")) != "tt1375666":
        raise RuntimeError("OMDb response did not preserve the requested IMDb identity.")
    return {"title": payload.get("Title"), "year": payload.get("Year"), "response": payload.get("Response")}


async def _news(client: NewsApiClient) -> dict[str, object]:
    payload = await client.get_json(
        "/everything",
        params={"q": "film OR television", "language": "en", "sortBy": "publishedAt", "pageSize": 3, "page": 1},
    )
    articles = payload.get("articles")
    if not isinstance(articles, list):
        raise RuntimeError("NewsAPI returned no article list.")
    return {
        "total_results": payload.get("totalResults"),
        "sample_titles": [item.get("title") for item in articles[:3] if isinstance(item, dict)],
    }


async def _watchmode_identity(client: WatchmodeClient) -> dict[str, object]:
    payload = await client.get_json(
        "/search/",
        params={"search_field": "tmdb_movie_id", "search_value": "278", "types": "movie"},
    )
    if not isinstance(payload, dict):
        raise RuntimeError("Watchmode search returned an invalid payload.")
    rows = payload.get("title_results")
    if not isinstance(rows, list):
        raise RuntimeError("Watchmode search returned no title_results list.")
    exact = [
        row for row in rows
        if isinstance(row, dict)
        and row.get("tmdb_id") == 278
        and str(row.get("tmdb_type", "")) == "movie"
    ]
    if len(exact) != 1:
        raise RuntimeError(f"Watchmode TMDb identity was not unique (matches={len(exact)}).")
    sources = await client.get_json("/title/movie-278/sources/", params={"regions": "US"})
    if not isinstance(sources, list):
        raise RuntimeError("Watchmode sources response was not a list.")
    return {
        "watchmode_id": exact[0].get("id"),
        "tmdb_id": 278,
        "tmdb_type": "movie",
        "source_count": len(sources),
    }


async def _kinocheck_identity(client: KinoCheckClient) -> dict[str, object]:
    payload = await client.get_json(
        "/movies",
        params={"tmdb_id": 299534, "language": "en", "categories": "Trailer"},
    )
    if not isinstance(payload, dict):
        raise RuntimeError("KinoCheck movie lookup returned an invalid payload.")
    if payload.get("tmdb_id") != 299534:
        raise RuntimeError("KinoCheck did not preserve the requested TMDb movie identity.")
    trailer = payload.get("trailer")
    videos = payload.get("videos")
    return {
        "kinocheck_id": payload.get("id"),
        "tmdb_id": payload.get("tmdb_id"),
        "title": payload.get("title"),
        "has_trailer": isinstance(trailer, dict),
        "video_count": len(videos) if isinstance(videos, list) else 0,
    }


async def _lyrics_identity(client: Stands4LyricsClient) -> dict[str, object]:
    service = ExternalDataService(lyrics=client)
    result = await service.lyrics_lookup("Forever Young", "Alphaville", album="Forever Young")
    if result.resolved and result.match is not None:
        return {"song": result.match.song, "artist": result.match.artist, "album": result.match.album, "candidate_count": result.candidate_count, "identity_mode": "unique_exact_match"}
    if not result.ambiguous or not result.candidates:
        raise RuntimeError("STANDS4 Lyrics returned no exact identity candidates.")
    selectable = [candidate for candidate in result.candidates if candidate.song_url]
    if not selectable:
        raise RuntimeError("STANDS4 Lyrics ambiguity could not be resolved by provider reference.")
    selected_url = selectable[0].song_url
    assert selected_url is not None
    selected = await service.lyrics_lookup("Forever Young", "Alphaville", album="Forever Young", reference_url=selected_url)
    if not selected.resolved or selected.match is None or selected.match.song_url != selected_url:
        raise RuntimeError("STANDS4 Lyrics explicit provider reference did not resolve deterministically.")
    return {"song": selected.match.song, "artist": selected.match.artist, "album": selected.match.album, "ambiguous_candidates_preserved": result.candidate_count, "explicit_reference_roundtrip": True, "identity_mode": "explicit_provider_reference"}


async def _screenplay_identity(client: ApifyScreenplayClient) -> dict[str, object]:
    result = await ExternalDataService(screenplay=client).script_lookup("The Matrix", year=1999)
    if not result.resolved or result.match is None:
        detail = "ambiguous" if result.ambiguous else "no exact match"
        raise RuntimeError(f"Apify screenplay identity was unresolved ({detail}).")
    payload = {
        "title": result.match.title,
        "requested_year": 1999,
        "provider_year": result.match.year,
        "year_verified": result.match.year == 1999,
        "source": result.match.source,
        "has_script_text": result.match.has_script_text,
        "word_count": result.match.word_count,
    }
    if result.match.year is None:
        payload["_qualification_status"] = "PARTIAL"
        payload["detail"] = "Exact title resolved uniquely; provider omitted optional year, so year remains unverified."
    return payload


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
