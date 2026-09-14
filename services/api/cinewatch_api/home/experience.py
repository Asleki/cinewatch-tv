"""Interactive homepage discovery, search, trailer, genre and hero enrichment services."""

from __future__ import annotations

import asyncio
import re
from datetime import date, datetime, timedelta, timezone
from typing import Protocol

from cinewatch_api.contracts.home import HomeItem
from cinewatch_api.contracts.home_experience import (
    HomeExternalRating,
    HomeGenreEntry,
    HomeGenresResponse,
    HomeHeroExperience,
    HomeRailResponse,
    HomeSearchResponse,
    HomeSearchSuggestion,
    HomeTrailer,
    HomeTrailerCard,
    HomeTrailerRailResponse,
)
from cinewatch_api.home.aggregation import HomepageAggregator, _ImageConfiguration
from cinewatch_api.providers.errors import ProviderError

RAIL_LIMIT = 12
TRAILER_RAIL_LIMIT = 4
TRAILER_CANDIDATE_LIMIT = 6

RAIL_TITLES: dict[str, str] = {
    "upcoming": "Upcoming",
    "k-drama": "K-Drama",
    "kenyan-stories": "Kenyan Stories",
    "bollywood": "Bollywood",
    "nollywood": "Nollywood",
    "chinese": "Chinese",
    "hollywood": "Hollywood",
    "documentaries": "Documentaries",
    "reality": "Reality",
    "tyler-perry": "Tyler Perry",
}


class TmdbGateway(Protocol):
    async def get_json(
        self,
        path: str,
        *,
        params: dict[str, str | int | float | bool] | None = None,
    ) -> dict[str, object]: ...


class OmdbGateway(Protocol):
    async def lookup_imdb(self, imdb_id: str) -> dict[str, object]: ...


class HomepageExperienceService:
    """Build interactive homepage surfaces without exposing provider credentials."""

    def __init__(self, tmdb: TmdbGateway, omdb: OmdbGateway | None = None) -> None:
        self._tmdb = tmdb
        self._omdb = omdb
        self._normalizer = HomepageAggregator(tmdb)

    async def rail(self, slug: str) -> HomeRailResponse:
        if slug not in RAIL_TITLES:
            raise ValueError("Unknown homepage rail.")

        configuration = await self._tmdb.get_json("/configuration")
        images = self._normalizer._image_configuration(configuration)

        if slug == "upcoming":
            items = await self._single_rail(
                "/movie/upcoming",
                images=images,
                media_type="movie",
                params={"language": "en-US", "page": 1},
            )
        elif slug == "k-drama":
            items = await self._single_rail(
                "/discover/tv",
                images=images,
                media_type="tv",
                params={
                    "with_original_language": "ko",
                    "sort_by": "popularity.desc",
                    "page": 1,
                },
            )
        elif slug == "bollywood":
            items = await self._single_rail(
                "/discover/movie",
                images=images,
                media_type="movie",
                params={
                    "with_original_language": "hi",
                    "sort_by": "popularity.desc",
                    "page": 1,
                },
            )
        elif slug == "documentaries":
            items = await self._single_rail(
                "/discover/movie",
                images=images,
                media_type="movie",
                params={"with_genres": 99, "sort_by": "popularity.desc", "page": 1},
            )
        elif slug == "reality":
            items = await self._single_rail(
                "/discover/tv",
                images=images,
                media_type="tv",
                params={"with_genres": 10764, "sort_by": "popularity.desc", "page": 1},
            )
        elif slug == "tyler-perry":
            items = await self._single_rail(
                "/discover/movie",
                images=images,
                media_type="movie",
                params={"with_companies": 3096, "sort_by": "popularity.desc", "page": 1},
            )
        elif slug == "kenyan-stories":
            items = await self._combined_rail(
                images=images,
                requests=(
                    (
                        "/discover/movie",
                        "movie",
                        {"with_origin_country": "KE", "sort_by": "popularity.desc", "page": 1},
                    ),
                    (
                        "/discover/tv",
                        "tv",
                        {"with_origin_country": "KE", "sort_by": "popularity.desc", "page": 1},
                    ),
                    (
                        "/discover/tv",
                        "tv",
                        {"with_original_language": "sw", "sort_by": "popularity.desc", "page": 1},
                    ),
                ),
            )
        elif slug == "nollywood":
            items = await self._combined_rail(
                images=images,
                requests=(
                    (
                        "/discover/movie",
                        "movie",
                        {"with_origin_country": "NG", "sort_by": "popularity.desc", "page": 1},
                    ),
                    (
                        "/discover/tv",
                        "tv",
                        {"with_origin_country": "NG", "sort_by": "popularity.desc", "page": 1},
                    ),
                ),
            )
        elif slug == "chinese":
            items = await self._combined_rail(
                images=images,
                requests=(
                    (
                        "/discover/movie",
                        "movie",
                        {"with_original_language": "zh", "sort_by": "popularity.desc", "page": 1},
                    ),
                    (
                        "/discover/tv",
                        "tv",
                        {"with_original_language": "zh", "sort_by": "popularity.desc", "page": 1},
                    ),
                ),
            )
        elif slug == "hollywood":
            items = await self._combined_rail(
                images=images,
                requests=(
                    (
                        "/discover/movie",
                        "movie",
                        {"with_origin_country": "US", "sort_by": "popularity.desc", "page": 1},
                    ),
                    (
                        "/discover/tv",
                        "tv",
                        {"with_origin_country": "US", "sort_by": "popularity.desc", "page": 1},
                    ),
                ),
            )
        else:  # pragma: no cover - protected by RAIL_TITLES and branches above
            items = []

        return HomeRailResponse(slug=slug, title=RAIL_TITLES[slug], items=items)

    async def search(self, query: str) -> HomeSearchResponse:
        normalized_query = " ".join(query.split())
        if len(normalized_query) < 2:
            raise ValueError("Homepage search query must contain at least two characters.")

        configuration, payload = await asyncio.gather(
            self._tmdb.get_json("/configuration"),
            self._tmdb.get_json(
                "/search/multi",
                params={"query": normalized_query, "language": "en-US", "page": 1},
            ),
        )
        images = self._normalizer._image_configuration(configuration)
        items = self._normalizer._normalize_results(
            payload,
            images=images,
            accepted_media_types={"movie", "tv", "person"},
        )

        suggestions: list[HomeSearchSuggestion] = []
        for item in items:
            image_url = item.profile_url if item.media_type == "person" else item.poster_url
            secondary = item.known_for_department if item.media_type == "person" else item.date
            suggestions.append(
                HomeSearchSuggestion(
                    provider_id=item.provider_id,
                    media_type=item.media_type,
                    label=item.title,
                    secondary_text=secondary,
                    image_url=image_url,
                    future_path=item.future_path or self._future_path(item),
                )
            )
            if len(suggestions) >= 8:
                break
        return HomeSearchResponse(query=normalized_query, suggestions=suggestions)

    async def genres(self) -> HomeGenresResponse:
        movie_payload, tv_payload = await asyncio.gather(
            self._tmdb.get_json("/genre/movie/list", params={"language": "en-US"}),
            self._tmdb.get_json("/genre/tv/list", params={"language": "en-US"}),
        )

        merged: dict[str, dict[str, object]] = {}
        self._merge_genres(merged, movie_payload, "movie")
        self._merge_genres(merged, tv_payload, "tv")

        genres = [
            HomeGenreEntry(
                name=str(record["name"]),
                slug=slug,
                movie_provider_id=self._positive_int(record.get("movie_provider_id")),
                tv_provider_id=self._positive_int(record.get("tv_provider_id")),
                future_path=f"/genre/{slug}",
            )
            for slug, record in sorted(merged.items(), key=lambda pair: str(pair[1]["name"]).casefold())
        ]
        return HomeGenresResponse(genres=genres)

    async def hero(self, media_type: str, provider_id: int) -> HomeHeroExperience:
        if media_type not in {"movie", "tv"}:
            raise ValueError("Hero media type must be movie or tv.")
        if provider_id <= 0:
            raise ValueError("Hero provider identity must be positive.")

        details = await self._tmdb.get_json(
            f"/{media_type}/{provider_id}",
            params={"language": "en-US", "append_to_response": "external_ids,credits,videos"},
        )

        writers = self._writers(details, media_type)
        trailer = await self._hero_trailer(details, media_type, provider_id)
        ratings = await self._external_ratings(details)

        return HomeHeroExperience(
            provider_id=provider_id,
            media_type=media_type,
            writers=writers,
            ratings=ratings,
            trailer=trailer,
            quote=None,
        )

    async def trailer_rail(self) -> HomeTrailerRailResponse:
        configuration, payload = await asyncio.gather(
            self._tmdb.get_json("/configuration"),
            self._tmdb.get_json(
                "/movie/upcoming",
                params={"language": "en-US", "page": 1},
            ),
        )
        images = self._normalizer._image_configuration(configuration)
        candidates = self._normalizer._normalize_results(
            payload,
            images=images,
            forced_media_type="movie",
            accepted_media_types={"movie"},
        )[:TRAILER_CANDIDATE_LIMIT]

        resolved = await asyncio.gather(
            *(self._movie_trailer_card(item) for item in candidates),
        )
        cards = [item for item in resolved if item is not None][:TRAILER_RAIL_LIMIT]
        return HomeTrailerRailResponse(items=cards)

    async def _single_rail(
        self,
        path: str,
        *,
        images: _ImageConfiguration,
        media_type: str,
        params: dict[str, str | int | float | bool],
    ) -> list[HomeItem]:
        payload = await self._tmdb.get_json(path, params=params)
        return self._normalizer._normalize_results(
            payload,
            images=images,
            forced_media_type=media_type,
            accepted_media_types={media_type},
        )[:RAIL_LIMIT]

    async def _combined_rail(
        self,
        *,
        images: _ImageConfiguration,
        requests: tuple[
            tuple[str, str, dict[str, str | int | float | bool]], ...
        ],
    ) -> list[HomeItem]:
        payloads = await asyncio.gather(
            *(self._tmdb.get_json(path, params=params) for path, _media_type, params in requests)
        )
        items: list[HomeItem] = []
        for payload, (_path, media_type, _params) in zip(payloads, requests, strict=True):
            items.extend(
                self._normalizer._normalize_results(
                    payload,
                    images=images,
                    forced_media_type=media_type,
                    accepted_media_types={media_type},
                )
            )

        deduped: dict[tuple[str, int], HomeItem] = {}
        for item in items:
            key = (item.media_type, item.provider_id)
            current = deduped.get(key)
            if current is None or (item.popularity or 0.0) > (current.popularity or 0.0):
                deduped[key] = item
        return sorted(
            deduped.values(),
            key=lambda item: (item.popularity or 0.0, item.provider_id),
            reverse=True,
        )[:RAIL_LIMIT]

    async def _movie_trailer_card(self, item: HomeItem) -> HomeTrailerCard | None:
        payload = await self._tmdb.get_json(f"/movie/{item.provider_id}/videos", params={"language": "en-US"})
        trailer = self._select_video(self._video_results(payload))
        if trailer is None:
            return None
        return HomeTrailerCard(item=item, trailer=trailer)

    async def _hero_trailer(
        self,
        details: dict[str, object],
        media_type: str,
        provider_id: int,
    ) -> HomeTrailer | None:
        appended_videos = details.get("videos")
        series_results = self._video_results(appended_videos if isinstance(appended_videos, dict) else {})

        if media_type == "movie":
            return self._select_video(series_results)

        latest_season, latest_air_date = self._latest_regular_season(details)
        if latest_season is not None:
            season_payload = await self._tmdb.get_json(
                f"/tv/{provider_id}/season/{latest_season}/videos",
                params={"language": "en-US"},
            )
            selected = self._select_video(
                self._video_results(season_payload),
                season_number=latest_season,
            )
            if selected is not None:
                return selected

        return self._select_video(
            series_results,
            expected_season=latest_season,
            latest_air_date=latest_air_date,
        )

    async def _external_ratings(self, details: dict[str, object]) -> list[HomeExternalRating]:
        if self._omdb is None:
            return []
        external_ids = details.get("external_ids")
        if not isinstance(external_ids, dict):
            return []
        imdb_id = self._text(external_ids.get("imdb_id"))
        if not imdb_id:
            return []
        try:
            payload = await self._omdb.lookup_imdb(imdb_id)
        except ProviderError:
            return []
        return self._parse_omdb_ratings(payload)

    @staticmethod
    def _parse_omdb_ratings(payload: dict[str, object]) -> list[HomeExternalRating]:
        ratings: list[HomeExternalRating] = []
        raw = payload.get("Ratings")
        if isinstance(raw, list):
            for entry in raw:
                if not isinstance(entry, dict):
                    continue
                source = HomepageExperienceService._text(entry.get("Source"))
                value = HomepageExperienceService._text(entry.get("Value"))
                if not source or not value:
                    continue
                source_map = {
                    "Internet Movie Database": "imdb",
                    "Rotten Tomatoes": "rotten_tomatoes",
                    "Metacritic": "metacritic",
                }
                normalized = source_map.get(source)
                if normalized:
                    ratings.append(
                        HomeExternalRating(source=normalized, display_value=value)  # type: ignore[arg-type]
                    )
        return ratings[:3]

    @staticmethod
    def _writers(details: dict[str, object], media_type: str) -> list[str]:
        names: list[str] = []
        if media_type == "tv":
            created_by = details.get("created_by")
            if isinstance(created_by, list):
                for record in created_by:
                    if isinstance(record, dict):
                        name = HomepageExperienceService._text(record.get("name"))
                        if name:
                            names.append(name)

        credits = details.get("credits")
        if isinstance(credits, dict):
            crew = credits.get("crew")
            if isinstance(crew, list):
                for record in crew:
                    if not isinstance(record, dict):
                        continue
                    department = HomepageExperienceService._text(record.get("department"))
                    job = HomepageExperienceService._text(record.get("job"))
                    if department != "Writing" and job not in {"Writer", "Screenplay", "Story", "Teleplay"}:
                        continue
                    name = HomepageExperienceService._text(record.get("name"))
                    if name:
                        names.append(name)

        return HomepageExperienceService._dedupe_text(names)[:5]

    @staticmethod
    def _latest_regular_season(details: dict[str, object]) -> tuple[int | None, date | None]:
        seasons = details.get("seasons")
        if not isinstance(seasons, list):
            return None, None
        candidates: list[tuple[int, date | None]] = []
        today = date.today()
        for season in seasons:
            if not isinstance(season, dict):
                continue
            number = HomepageExperienceService._positive_int(season.get("season_number"))
            if number is None:
                continue
            air_date = HomepageExperienceService._date(season.get("air_date"))
            if air_date is not None and air_date > today:
                continue
            candidates.append((number, air_date))
        if not candidates:
            return None, None
        return max(candidates, key=lambda item: item[0])

    @staticmethod
    def _select_video(
        videos: list[dict[str, object]],
        *,
        season_number: int | None = None,
        expected_season: int | None = None,
        latest_air_date: date | None = None,
    ) -> HomeTrailer | None:
        ranked: list[tuple[tuple[int, int, int, float], HomeTrailer]] = []
        season_pattern = re.compile(r"\bseason\s+(\d+)\b", re.IGNORECASE)

        for raw in videos:
            if HomepageExperienceService._text(raw.get("site")) != "YouTube":
                continue
            video_type = HomepageExperienceService._text(raw.get("type"))
            if video_type not in {"Trailer", "Teaser"}:
                continue
            key = HomepageExperienceService._text(raw.get("key"))
            name = HomepageExperienceService._text(raw.get("name"))
            if not key or not name:
                continue

            if expected_season is not None:
                season_match = season_pattern.search(name)
                if season_match and int(season_match.group(1)) != expected_season:
                    continue
                if latest_air_date is not None:
                    published = HomepageExperienceService._datetime(raw.get("published_at"))
                    threshold = datetime.combine(
                        latest_air_date - timedelta(days=45),
                        datetime.min.time(),
                        tzinfo=timezone.utc,
                    )
                    if published is not None and published < threshold:
                        continue

            published = HomepageExperienceService._datetime(raw.get("published_at"))
            official = raw.get("official") is True
            score = (
                2 if video_type == "Trailer" else 1,
                1 if official else 0,
                1 if "official" in name.casefold() else 0,
                published.timestamp() if published else 0.0,
            )
            ranked.append(
                (
                    score,
                    HomeTrailer(
                        youtube_key=key,
                        name=name,
                        video_type=video_type,  # type: ignore[arg-type]
                        official=official,
                        published_at=published.isoformat().replace("+00:00", "Z") if published else None,
                        season_number=season_number,
                    ),
                )
            )

        if not ranked:
            return None
        ranked.sort(key=lambda pair: pair[0], reverse=True)
        return ranked[0][1]

    @staticmethod
    def _video_results(payload: dict[str, object]) -> list[dict[str, object]]:
        results = payload.get("results")
        if not isinstance(results, list):
            return []
        return [item for item in results if isinstance(item, dict)]

    @staticmethod
    def _merge_genres(
        target: dict[str, dict[str, object]],
        payload: dict[str, object],
        media_type: str,
    ) -> None:
        genres = payload.get("genres")
        if not isinstance(genres, list):
            return
        for raw in genres:
            if not isinstance(raw, dict):
                continue
            provider_id = HomepageExperienceService._positive_int(raw.get("id"))
            name = HomepageExperienceService._text(raw.get("name"))
            if provider_id is None or not name:
                continue
            slug = HomepageExperienceService._slug(name)
            record = target.setdefault(slug, {"name": name})
            record[f"{media_type}_provider_id"] = provider_id

    @staticmethod
    def _future_path(item: HomeItem) -> str:
        if item.media_type == "person":
            return f"/person/{item.provider_id}"
        return f"/title/{item.media_type}/{item.provider_id}"

    @staticmethod
    def _dedupe_text(values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            key = value.casefold()
            if key in seen:
                continue
            seen.add(key)
            result.append(value)
        return result

    @staticmethod
    def _slug(value: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
        return normalized or "genre"

    @staticmethod
    def _positive_int(value: object) -> int | None:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            return None
        return value

    @staticmethod
    def _text(value: object) -> str | None:
        if not isinstance(value, str):
            return None
        stripped = value.strip()
        return stripped or None

    @staticmethod
    def _date(value: object) -> date | None:
        text = HomepageExperienceService._text(value)
        if not text:
            return None
        try:
            return date.fromisoformat(text[:10])
        except ValueError:
            return None

    @staticmethod
    def _datetime(value: object) -> datetime | None:
        text = HomepageExperienceService._text(value)
        if not text:
            return None
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
