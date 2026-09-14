"""Bounded title, person, review, season and browse aggregation for CineWatch pages."""

from __future__ import annotations

import asyncio
import re
from datetime import date, datetime, timedelta, timezone
from typing import Protocol

from cinewatch_api.contracts.catalog import (
    CatalogBrowseResponse,
    CatalogCastMember,
    CatalogCrewMember,
    CatalogEpisode,
    CatalogMediaSummary,
    CatalogNetwork,
    CatalogPersonCredit,
    CatalogPersonResponse,
    CatalogRating,
    CatalogReview,
    CatalogReviewsResponse,
    CatalogSeason,
    CatalogSeasonResponse,
    CatalogTitleResponse,
    CatalogTrailer,
    CatalogWatchProvider,
)
from cinewatch_api.home.aggregation import HomepageAggregator
from cinewatch_api.providers.errors import ProviderError, ProviderResponseError

BROWSE_LIMIT = 20
CAST_LIMIT = 18
CREW_LIMIT = 30
RECOMMENDATION_LIMIT = 12

COUNTRY_TITLES: dict[str, str] = {
    "KE": "Kenya",
    "NG": "Nigeria",
    "IN": "India",
    "KR": "South Korea",
    "CN": "China",
    "US": "United States",
    "GB": "United Kingdom",
    "ZA": "South Africa",
    "GH": "Ghana",
}

COLLECTION_TITLES: dict[str, str] = {
    "trending": "Trending Now",
    "popular-movies": "Popular Movies",
    "popular-tv": "Popular TV Shows",
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


class CatalogService:
    """Server-only provider composition for page-level CineWatch discovery."""

    def __init__(self, tmdb: TmdbGateway, omdb: OmdbGateway | None = None) -> None:
        self._tmdb = tmdb
        self._omdb = omdb
        self._normalizer = HomepageAggregator(tmdb)

    async def title(
        self,
        media_type: str,
        provider_id: int,
        *,
        watch_region: str | None = None,
    ) -> CatalogTitleResponse:
        self._validate_media(media_type)
        if provider_id <= 0:
            raise ValueError("Catalog provider identity must be positive.")

        config, details = await asyncio.gather(
            self._tmdb.get_json("/configuration"),
            self._tmdb.get_json(
                f"/{media_type}/{provider_id}",
                params={
                    "language": "en-US",
                    "append_to_response": "external_ids,credits,videos,reviews,recommendations",
                },
            ),
        )
        try:
            providers = await self._tmdb.get_json(
                f"/{media_type}/{provider_id}/watch/providers"
            )
        except ProviderError:
            providers = {"results": {}}
        images = self._normalizer._image_configuration(config)

        title = self._text(details.get("title")) or self._text(details.get("name"))
        if not title:
            raise ProviderResponseError(
                provider="tmdb",
                code="TMDB_CATALOG_TITLE_INVALID",
                message="TMDb returned an invalid title payload.",
            )

        release_date = self._text(details.get("release_date")) or self._text(details.get("first_air_date"))
        external_ids = details.get("external_ids")
        imdb_id = self._text(external_ids.get("imdb_id")) if isinstance(external_ids, dict) else None
        omdb_payload = await self._omdb_payload(imdb_id)

        credits = details.get("credits") if isinstance(details.get("credits"), dict) else {}
        videos = details.get("videos") if isinstance(details.get("videos"), dict) else {}
        trailer = await self._select_title_trailer(media_type, provider_id, details, videos)
        ratings = self._ratings(details, omdb_payload)
        selected_region, watch_items, watch_link = self._watch_providers(providers, images, watch_region)

        return CatalogTitleResponse(
            provider_id=provider_id,
            media_type=media_type,  # type: ignore[arg-type]
            title=title,
            original_title=self._text(details.get("original_title")) or self._text(details.get("original_name")),
            tagline=self._text(details.get("tagline")),
            overview=self._text(details.get("overview")),
            release_date=release_date,
            year=self._year(release_date),
            runtime_minutes=self._runtime(details, media_type),
            status=self._text(details.get("status")),
            original_language=self._text(details.get("original_language")),
            genres=self._genre_names(details.get("genres")),
            poster_url=self._image(images.secure_base_url, images.poster_size, details.get("poster_path")),
            backdrop_url=self._image(images.secure_base_url, images.backdrop_size, details.get("backdrop_path")),
            ratings=ratings,
            networks=self._networks(details, images),
            watch_region=selected_region,
            watch_providers=watch_items,
            watch_information_url=watch_link,
            trailer=trailer,
            creators=self._creators(details),
            writers=self._writers(credits),
            cast=self._cast(credits, images),
            crew=self._crew(credits, images),
            seasons=self._seasons(details, images) if media_type == "tv" else [],
            reviews=self._reviews_from_appended(details)[:3],
            review_count=self._review_count(details),
            recommendations=self._recommendations(details, images, media_type),
            awards=self._text(omdb_payload.get("Awards")) if omdb_payload else None,
            box_office=self._text(omdb_payload.get("BoxOffice")) if omdb_payload else None,
            production_budget=self._nonnegative_int(details.get("budget")),
            revenue=self._nonnegative_int(details.get("revenue")),
        )

    async def reviews(self, media_type: str, provider_id: int, *, page: int = 1) -> CatalogReviewsResponse:
        self._validate_media(media_type)
        payload = await self._tmdb.get_json(
            f"/{media_type}/{provider_id}/reviews",
            params={"language": "en-US", "page": page},
        )
        return CatalogReviewsResponse(
            provider_id=provider_id,
            media_type=media_type,  # type: ignore[arg-type]
            page=max(1, self._positive_int(payload.get("page")) or page),
            total_pages=max(0, self._int(payload.get("total_pages")) or 0),
            total_results=max(0, self._int(payload.get("total_results")) or 0),
            reviews=self._reviews(payload.get("results"))[:20],
        )

    async def season(self, provider_id: int, season_number: int) -> CatalogSeasonResponse:
        if provider_id <= 0 or season_number < 0:
            raise ValueError("Invalid television season identity.")
        config, payload = await asyncio.gather(
            self._tmdb.get_json("/configuration"),
            self._tmdb.get_json(
                f"/tv/{provider_id}/season/{season_number}",
                params={"language": "en-US"},
            ),
        )
        images = self._normalizer._image_configuration(config)
        name = self._text(payload.get("name")) or f"Season {season_number}"
        episodes: list[CatalogEpisode] = []
        raw_episodes = payload.get("episodes")
        if isinstance(raw_episodes, list):
            for raw in raw_episodes:
                if not isinstance(raw, dict):
                    continue
                episode_id = self._positive_int(raw.get("id"))
                episode_number = self._int(raw.get("episode_number"))
                episode_name = self._text(raw.get("name"))
                if episode_id is None or episode_number is None or not episode_name:
                    continue
                episodes.append(
                    CatalogEpisode(
                        provider_id=episode_id,
                        episode_number=max(0, episode_number),
                        season_number=season_number,
                        name=episode_name,
                        overview=self._text(raw.get("overview")),
                        air_date=self._text(raw.get("air_date")),
                        runtime_minutes=self._nonnegative_int(raw.get("runtime")),
                        still_url=self._image(images.secure_base_url, images.backdrop_size, raw.get("still_path")),
                    )
                )
        return CatalogSeasonResponse(
            provider_id=provider_id,
            season_number=season_number,
            name=name,
            overview=self._text(payload.get("overview")),
            poster_url=self._image(images.secure_base_url, images.poster_size, payload.get("poster_path")),
            episodes=episodes,
        )

    async def person(self, provider_id: int) -> CatalogPersonResponse:
        if provider_id <= 0:
            raise ValueError("Catalog person identity must be positive.")
        config, details = await asyncio.gather(
            self._tmdb.get_json("/configuration"),
            self._tmdb.get_json(f"/person/{provider_id}", params={"language": "en-US"}),
        )
        try:
            credits_payload = await self._tmdb.get_json(
                f"/person/{provider_id}/combined_credits",
                params={"language": "en-US"},
            )
        except ProviderError:
            credits_payload = {"cast": []}
        images = self._normalizer._image_configuration(config)
        name = self._text(details.get("name"))
        if not name:
            raise ProviderResponseError(
                provider="tmdb",
                code="TMDB_CATALOG_PERSON_INVALID",
                message="TMDb returned an invalid person payload.",
            )
        credits = self._person_credits(credits_payload, images)
        hero_backdrop = next((item.backdrop_url for item in credits if item.backdrop_url), None)
        return CatalogPersonResponse(
            provider_id=provider_id,
            name=name,
            biography=self._text(details.get("biography")),
            known_for_department=self._text(details.get("known_for_department")),
            birthday=self._text(details.get("birthday")),
            deathday=self._text(details.get("deathday")),
            place_of_birth=self._text(details.get("place_of_birth")),
            profile_url=self._image(images.secure_base_url, images.profile_size, details.get("profile_path")),
            hero_backdrop_url=hero_backdrop,
            credits=credits,
        )

    async def browse(
        self,
        kind: str,
        slug: str,
        *,
        page: int = 1,
        media_type: str = "all",
        year: int | None = None,
        language: str | None = None,
        sort: str = "popularity.desc",
    ) -> CatalogBrowseResponse:
        if kind not in {"genre", "collection", "country"}:
            raise ValueError("Unknown catalog browse kind.")
        if media_type not in {"all", "movie", "tv"}:
            raise ValueError("Unknown catalog browse media type.")
        if page < 1:
            raise ValueError("Catalog browse page must be positive.")

        config = await self._tmdb.get_json("/configuration")
        images = self._normalizer._image_configuration(config)
        requests, title = await self._browse_requests(
            kind,
            slug,
            page=page,
            media_type=media_type,
            year=year,
            language=language,
            sort=sort,
        )
        requests = [
            (path, self._normalize_year_params(path, params), forced_media)
            for path, params, forced_media in requests
        ]
        payloads = await asyncio.gather(
            *(self._tmdb.get_json(path, params=params) for path, params, _ in requests),
            return_exceptions=True,
        )
        groups: list[list[CatalogMediaSummary]] = []
        total_pages = 0
        total_results = 0
        first_provider_error: ProviderError | None = None
        for payload, (_, _, forced_media) in zip(payloads, requests, strict=True):
            if isinstance(payload, ProviderError):
                first_provider_error = first_provider_error or payload
                continue
            if isinstance(payload, BaseException):
                raise payload
            total_pages = max(total_pages, max(0, self._int(payload.get("total_pages")) or 0))
            total_results += max(0, self._int(payload.get("total_results")) or 0)
            groups.append(self._summaries(payload, images, forced_media))
        if not groups and first_provider_error is not None:
            raise first_provider_error
        merged = self._dedupe_summaries(self._round_robin(groups))
        return CatalogBrowseResponse(
            kind=kind,  # type: ignore[arg-type]
            slug=slug,
            title=title,
            page=page,
            total_pages=total_pages,
            total_results=total_results,
            media_type=media_type,  # type: ignore[arg-type]
            year=year,
            language=language,
            sort=sort,
            items=merged[:BROWSE_LIMIT],
        )

    async def _browse_requests(
        self,
        kind: str,
        slug: str,
        *,
        page: int,
        media_type: str,
        year: int | None,
        language: str | None,
        sort: str,
    ) -> tuple[list[tuple[str, dict[str, str | int | float | bool], str]], str]:
        if kind == "genre":
            movie_genres, tv_genres = await asyncio.gather(
                self._tmdb.get_json("/genre/movie/list", params={"language": "en-US"}),
                self._tmdb.get_json("/genre/tv/list", params={"language": "en-US"}),
            )
            movie_id, name = self._resolve_genre(movie_genres, slug)
            tv_id, tv_name = self._resolve_genre(tv_genres, slug)
            if movie_id is None and tv_id is None:
                raise ValueError("Unknown CineWatch genre.")
            title = name or tv_name or slug.replace("-", " ").title()
            requests: list[tuple[str, dict[str, str | int | float | bool], str]] = []
            if media_type in {"all", "movie"} and movie_id:
                requests.append(("/discover/movie", self._discover_params(page, sort, year, language, genre_id=movie_id), "movie"))
            if media_type in {"all", "tv"} and tv_id:
                requests.append(("/discover/tv", self._discover_params(page, sort, year, language, genre_id=tv_id), "tv"))
            return requests, title

        if kind == "country":
            code = slug.upper()
            if code not in COUNTRY_TITLES:
                raise ValueError("Unknown CineWatch country collection.")
            requests = []
            if media_type in {"all", "movie"}:
                requests.append(("/discover/movie", self._discover_params(page, sort, year, language, country=code), "movie"))
            if media_type in {"all", "tv"}:
                requests.append(("/discover/tv", self._discover_params(page, sort, year, language, country=code), "tv"))
            return requests, f"Stories from {COUNTRY_TITLES.get(code, code)}"

        return self._collection_requests(slug, page, media_type, year, language, sort), COLLECTION_TITLES.get(slug, slug.replace("-", " ").title())

    def _collection_requests(
        self,
        slug: str,
        page: int,
        media_type: str,
        year: int | None,
        language: str | None,
        sort: str,
    ) -> list[tuple[str, dict[str, str | int | float | bool], str]]:
        if slug not in COLLECTION_TITLES:
            raise ValueError("Unknown CineWatch discovery collection.")
        if slug == "trending":
            requests = []
            if media_type in {"all", "movie"}:
                requests.append(("/trending/movie/week", {"language": "en-US", "page": page}, "movie"))
            if media_type in {"all", "tv"}:
                requests.append(("/trending/tv/week", {"language": "en-US", "page": page}, "tv"))
            return requests
        if slug == "popular-movies":
            return [] if media_type == "tv" else [("/movie/popular", {"language": "en-US", "page": page}, "movie")]
        if slug == "popular-tv":
            return [] if media_type == "movie" else [("/tv/popular", {"language": "en-US", "page": page}, "tv")]
        if slug == "upcoming":
            return [] if media_type == "tv" else [("/movie/upcoming", {"language": "en-US", "page": page}, "movie")]
        requests: list[tuple[str, dict[str, str | int | float | bool], str]] = []
        if slug == "k-drama":
            return [] if media_type == "movie" else [("/discover/tv", self._discover_params(page, sort, year, language or "ko"), "tv")]
        if slug == "kenyan-stories":
            for path, mt, extra in (
                ("/discover/movie", "movie", {"with_origin_country": "KE"}),
                ("/discover/tv", "tv", {"with_origin_country": "KE"}),
                ("/discover/movie", "movie", {"with_original_language": "sw"}),
                ("/discover/tv", "tv", {"with_original_language": "sw"}),
            ):
                if media_type != "all" and media_type != mt:
                    continue
                params = self._discover_params(page, sort, year, language)
                params.update(extra)
                requests.append((path, params, mt))
            return requests
        if slug == "bollywood":
            langs = [language] if language else ["hi", "te", "pa", "ta"]
            for lang in langs:
                if media_type in {"all", "movie"}:
                    requests.append(("/discover/movie", self._discover_params(page, sort, year, lang), "movie"))
            return requests
        if slug == "nollywood":
            for path, mt in (("/discover/movie", "movie"), ("/discover/tv", "tv")):
                if media_type != "all" and media_type != mt:
                    continue
                requests.append((path, self._discover_params(page, sort, year, language, country="NG"), mt))
            return requests
        if slug == "chinese":
            for path, mt in (("/discover/movie", "movie"), ("/discover/tv", "tv")):
                if media_type != "all" and media_type != mt:
                    continue
                requests.append((path, self._discover_params(page, sort, year, language or "zh"), mt))
            return requests
        if slug == "hollywood":
            for path, mt in (("/discover/movie", "movie"), ("/discover/tv", "tv")):
                if media_type != "all" and media_type != mt:
                    continue
                requests.append((path, self._discover_params(page, sort, year, language, country="US"), mt))
            return requests
        if slug == "documentaries":
            for path, mt in (("/discover/movie", "movie"), ("/discover/tv", "tv")):
                if media_type != "all" and media_type != mt:
                    continue
                requests.append((path, self._discover_params(page, sort, year, language, genre_id=99), mt))
            return requests
        if slug == "reality":
            return [] if media_type == "movie" else [("/discover/tv", self._discover_params(page, sort, year, language, genre_id=10764), "tv")]
        if slug == "tyler-perry":
            for path, mt in (("/discover/movie", "movie"), ("/discover/tv", "tv")):
                if media_type != "all" and media_type != mt:
                    continue
                params = self._discover_params(page, sort, year, language)
                params["with_companies"] = 3096
                requests.append((path, params, mt))
            return requests
        return requests

    @staticmethod
    def _discover_params(page: int, sort: str, year: int | None, language: str | None, *, country: str | None = None, genre_id: int | None = None) -> dict[str, str | int | float | bool]:
        params: dict[str, str | int | float | bool] = {"page": page, "sort_by": sort, "include_adult": False}
        if language:
            params["with_original_language"] = language
        if country:
            params["with_origin_country"] = country
        if genre_id:
            params["with_genres"] = genre_id
        if year:
            params["primary_release_year"] = year
            params["first_air_date_year"] = year
        return params


    @staticmethod
    def _normalize_year_params(
        path: str,
        params: dict[str, str | int | float | bool],
    ) -> dict[str, str | int | float | bool]:
        normalized = dict(params)
        if path.endswith("/movie"):
            normalized.pop("first_air_date_year", None)
            if normalized.get("sort_by") == "first_air_date.desc":
                normalized["sort_by"] = "primary_release_date.desc"
        elif path.endswith("/tv"):
            normalized.pop("primary_release_year", None)
            if normalized.get("sort_by") == "primary_release_date.desc":
                normalized["sort_by"] = "first_air_date.desc"
        return normalized

    async def _omdb_payload(self, imdb_id: str | None) -> dict[str, object]:
        if self._omdb is None or not imdb_id:
            return {}
        try:
            return await self._omdb.lookup_imdb(imdb_id)
        except ProviderError:
            return {}

    async def _select_title_trailer(self, media_type: str, provider_id: int, details: dict[str, object], videos_payload: dict[str, object]) -> CatalogTrailer | None:
        series_videos = self._video_results(videos_payload)
        if media_type == "movie":
            return self._select_video(series_videos)
        latest_season, latest_air_date = self._latest_regular_season(details)
        if latest_season is not None:
            try:
                season_payload = await self._tmdb.get_json(
                    f"/tv/{provider_id}/season/{latest_season}/videos",
                    params={"language": "en-US"},
                )
            except ProviderError:
                season_payload = {"results": []}
            selected = self._select_video(
                self._video_results(season_payload),
                season_number=latest_season,
            )
            if selected is not None:
                return selected
        return self._select_video(series_videos, expected_season=latest_season, latest_air_date=latest_air_date)

    @staticmethod
    def _select_video(videos: list[dict[str, object]], *, season_number: int | None = None, expected_season: int | None = None, latest_air_date: date | None = None) -> CatalogTrailer | None:
        ranked: list[tuple[tuple[int, int, int, float], CatalogTrailer]] = []
        season_pattern = re.compile(r"\bseason\s+(\d+)\b", re.IGNORECASE)
        for raw in videos:
            if CatalogService._text(raw.get("site")) != "YouTube":
                continue
            video_type = CatalogService._text(raw.get("type"))
            if video_type not in {"Trailer", "Teaser"}:
                continue
            key = CatalogService._text(raw.get("key"))
            name = CatalogService._text(raw.get("name"))
            if not key or not name:
                continue
            if expected_season is not None:
                match = season_pattern.search(name)
                if match and int(match.group(1)) != expected_season:
                    continue
                if latest_air_date is not None:
                    published = CatalogService._datetime(raw.get("published_at"))
                    threshold = datetime.combine(latest_air_date - timedelta(days=45), datetime.min.time(), tzinfo=timezone.utc)
                    if published is not None and published < threshold:
                        continue
            published = CatalogService._datetime(raw.get("published_at"))
            official = raw.get("official") is True
            ranked.append(((2 if video_type == "Trailer" else 1, 1 if official else 0, 1 if "official" in name.casefold() else 0, published.timestamp() if published else 0.0), CatalogTrailer(
                youtube_key=key,
                name=name,
                video_type=video_type,  # type: ignore[arg-type]
                official=official,
                published_at=published.isoformat().replace("+00:00", "Z") if published else None,
                season_number=season_number,
            )))
        if not ranked:
            return None
        ranked.sort(key=lambda pair: pair[0], reverse=True)
        return ranked[0][1]

    @staticmethod
    def _latest_regular_season(details: dict[str, object]) -> tuple[int | None, date | None]:
        seasons = details.get("seasons")
        if not isinstance(seasons, list):
            return None, None
        candidates: list[tuple[int, date | None]] = []
        today = date.today()
        for raw in seasons:
            if not isinstance(raw, dict):
                continue
            number = CatalogService._int(raw.get("season_number"))
            if number is None or number <= 0:
                continue
            air = CatalogService._date(raw.get("air_date"))
            if air is not None and air > today:
                continue
            candidates.append((number, air))
        return max(candidates, key=lambda item: item[0]) if candidates else (None, None)

    @staticmethod
    def _video_results(payload: dict[str, object]) -> list[dict[str, object]]:
        raw = payload.get("results")
        return [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []

    def _ratings(self, details: dict[str, object], omdb: dict[str, object]) -> list[CatalogRating]:
        ratings: list[CatalogRating] = []
        vote = self._number(details.get("vote_average"))
        vote_count = self._nonnegative_int(details.get("vote_count"))
        if vote is not None and vote > 0 and (vote_count is None or vote_count > 0):
            ratings.append(CatalogRating(source="tmdb", display_value=f"{vote:.1f}/10"))
        raw = omdb.get("Ratings")
        source_map = {"Internet Movie Database": "imdb", "Rotten Tomatoes": "rotten_tomatoes", "Metacritic": "metacritic"}
        if isinstance(raw, list):
            for record in raw:
                if not isinstance(record, dict):
                    continue
                source = self._text(record.get("Source")); value = self._text(record.get("Value"))
                normalized = source_map.get(source or "")
                if normalized and value and value.casefold() != "n/a":
                    ratings.append(CatalogRating(source=normalized, display_value=value))  # type: ignore[arg-type]
        return ratings[:4]

    def _networks(self, details: dict[str, object], images) -> list[CatalogNetwork]:
        raw = details.get("networks")
        if not isinstance(raw, list):
            raw = details.get("production_companies") if isinstance(details.get("production_companies"), list) else []
        result: list[CatalogNetwork] = []
        for record in raw:
            if not isinstance(record, dict):
                continue
            name = self._text(record.get("name"))
            if not name:
                continue
            result.append(CatalogNetwork(provider_id=self._positive_int(record.get("id")), name=name, logo_url=self._image(images.secure_base_url, images.poster_size, record.get("logo_path"))))
        return result[:12]

    def _watch_providers(self, payload: dict[str, object], images, preferred_region: str | None) -> tuple[str | None, list[CatalogWatchProvider], str | None]:
        results = payload.get("results")
        if not isinstance(results, dict) or not results:
            return None, [], None
        candidates = []
        if preferred_region:
            candidates.append(preferred_region.upper())
        candidates.extend(["KE", "US", "GB"])
        candidates.extend(sorted(str(key) for key in results))
        region = next((code for code in candidates if isinstance(results.get(code), dict)), None)
        if not region:
            return None, [], None
        record = results[region]
        assert isinstance(record, dict)
        items: list[CatalogWatchProvider] = []
        seen: set[int] = set()
        for monetization in ("flatrate", "free", "ads", "rent", "buy"):
            if len(items) >= 18:
                break
            providers = record.get(monetization)
            if not isinstance(providers, list):
                continue
            for raw in providers:
                if not isinstance(raw, dict):
                    continue
                provider_id = self._positive_int(raw.get("provider_id")); name = self._text(raw.get("provider_name"))
                if provider_id is None or not name or provider_id in seen:
                    continue
                seen.add(provider_id)
                items.append(CatalogWatchProvider(provider_id=provider_id, name=name, logo_url=self._image(images.secure_base_url, images.poster_size, raw.get("logo_path")), monetization_type=monetization))  # type: ignore[arg-type]
                if len(items) >= 18:
                    break
        return region, items, self._text(record.get("link"))

    def _cast(self, credits: dict[str, object], images) -> list[CatalogCastMember]:
        raw = credits.get("cast")
        if not isinstance(raw, list):
            return []
        result = []
        for record in raw:
            if not isinstance(record, dict): continue
            provider_id = self._positive_int(record.get("id")); name = self._text(record.get("name"))
            if provider_id is None or not name: continue
            result.append(CatalogCastMember(provider_id=provider_id, name=name, character=self._text(record.get("character")), profile_url=self._image(images.secure_base_url, images.profile_size, record.get("profile_path")), future_path=f"/person/{provider_id}"))
            if len(result) >= CAST_LIMIT: break
        return result

    def _crew(self, credits: dict[str, object], images) -> list[CatalogCrewMember]:
        raw = credits.get("crew")
        if not isinstance(raw, list): return []
        result=[]
        for record in raw:
            if not isinstance(record, dict): continue
            provider_id=self._positive_int(record.get("id")); name=self._text(record.get("name"))
            if provider_id is None or not name: continue
            result.append(CatalogCrewMember(provider_id=provider_id,name=name,department=self._text(record.get("department")),job=self._text(record.get("job")),profile_url=self._image(images.secure_base_url,images.profile_size,record.get("profile_path")),future_path=f"/person/{provider_id}"))
            if len(result)>=CREW_LIMIT: break
        return result

    def _seasons(self, details: dict[str, object], images) -> list[CatalogSeason]:
        raw=details.get("seasons")
        if not isinstance(raw,list): return []
        result=[]
        for record in raw:
            if not isinstance(record,dict): continue
            number=self._int(record.get("season_number")); name=self._text(record.get("name"))
            if number is None or number<0 or not name: continue
            result.append(CatalogSeason(provider_id=self._positive_int(record.get("id")),season_number=number,name=name,episode_count=max(0,self._int(record.get("episode_count")) or 0),air_date=self._text(record.get("air_date")),overview=self._text(record.get("overview")),poster_url=self._image(images.secure_base_url,images.poster_size,record.get("poster_path"))))
        return result

    def _reviews_from_appended(self, details: dict[str, object]) -> list[CatalogReview]:
        raw=details.get("reviews")
        return self._reviews(raw.get("results")) if isinstance(raw,dict) else []

    def _review_count(self, details: dict[str, object]) -> int:
        raw=details.get("reviews")
        return max(0,self._int(raw.get("total_results")) or 0) if isinstance(raw,dict) else 0

    def _reviews(self, value: object) -> list[CatalogReview]:
        if not isinstance(value,list): return []
        result=[]
        for record in value:
            if not isinstance(record,dict): continue
            rid=self._text(record.get("id")); author=self._text(record.get("author")); content=self._text(record.get("content"))
            if not rid or not author or not content: continue
            details=record.get("author_details") if isinstance(record.get("author_details"),dict) else {}
            avatar=self._text(details.get("avatar_path")); avatar_url=None
            if avatar:
                avatar_url=avatar[1:] if avatar.startswith("/") and avatar[1:].startswith("http") else (f"https://image.tmdb.org/t/p/w185{avatar}" if avatar.startswith("/") else avatar)
            result.append(CatalogReview(provider_review_id=rid,author=author,author_avatar_url=avatar_url,rating=self._clamp_rating(details.get("rating")),content=content,created_at=self._text(record.get("created_at"))))
        return result

    def _recommendations(
        self,
        details: dict[str, object],
        images,
        media_type: str,
    ) -> list[CatalogMediaSummary]:
        raw = details.get("recommendations")
        if not isinstance(raw, dict):
            return []
        payload = {"results": raw.get("results", [])}
        return self._dedupe_summaries(
            self._summaries(payload, images, media_type)
        )[:RECOMMENDATION_LIMIT]

    def _person_credits(self, payload: dict[str, object], images) -> list[CatalogPersonCredit]:
        raw=payload.get("cast")
        if not isinstance(raw,list): return []
        credits=[]
        for record in raw:
            if not isinstance(record,dict): continue
            mt=self._text(record.get("media_type"))
            if mt not in {"movie","tv"}: continue
            provider_id=self._positive_int(record.get("id")); title=self._text(record.get("title")) or self._text(record.get("name"))
            if provider_id is None or not title: continue
            release=self._text(record.get("release_date")) or self._text(record.get("first_air_date"))
            credits.append(CatalogPersonCredit(provider_id=provider_id,media_type=mt,title=title,role=self._text(record.get("character")),year=self._year(release),popularity=self._number(record.get("popularity")),poster_url=self._image(images.secure_base_url,images.poster_size,record.get("poster_path")),backdrop_url=self._image(images.secure_base_url,images.backdrop_size,record.get("backdrop_path")),future_path=f"/title/{mt}/{provider_id}"))  # type: ignore[arg-type]
        credits.sort(key=lambda item:(item.popularity or 0.0,item.year or 0),reverse=True)
        seen=set(); result=[]
        for item in credits:
            key=(item.media_type,item.provider_id)
            if key in seen: continue
            seen.add(key); result.append(item)
            if len(result)>=40: break
        return result

    def _summaries(self, payload: dict[str, object], images, forced_media: str, *, accept_only: str | None = None) -> list[CatalogMediaSummary]:
        raw=payload.get("results")
        if not isinstance(raw,list): return []
        result=[]
        for record in raw:
            if not isinstance(record,dict): continue
            mt=self._text(record.get("media_type")) or forced_media
            if mt not in {"movie","tv"} or (accept_only and mt!=accept_only): continue
            provider_id=self._positive_int(record.get("id")); title=self._text(record.get("title")) or self._text(record.get("name"))
            if provider_id is None or not title: continue
            release=self._text(record.get("release_date")) or self._text(record.get("first_air_date"))
            result.append(CatalogMediaSummary(provider_id=provider_id,media_type=mt,title=title,year=self._year(release),poster_url=self._image(images.secure_base_url,images.poster_size,record.get("poster_path")),backdrop_url=self._image(images.secure_base_url,images.backdrop_size,record.get("backdrop_path")),rating=self._number(record.get("vote_average")),future_path=f"/title/{mt}/{provider_id}"))  # type: ignore[arg-type]
        return result

    @staticmethod
    def _round_robin(groups: list[list[CatalogMediaSummary]]) -> list[CatalogMediaSummary]:
        result: list[CatalogMediaSummary] = []
        index = 0
        while True:
            added = False
            for group in groups:
                if index < len(group):
                    result.append(group[index])
                    added = True
            if not added:
                break
            index += 1
        return result

    @staticmethod
    def _dedupe_summaries(items: list[CatalogMediaSummary]) -> list[CatalogMediaSummary]:
        seen=set(); result=[]
        for item in items:
            key=(item.media_type,item.provider_id)
            if key in seen: continue
            seen.add(key); result.append(item)
        return result

    @staticmethod
    def _resolve_genre(payload: dict[str, object], slug: str) -> tuple[int | None, str | None]:
        raw=payload.get("genres")
        if not isinstance(raw,list): return None,None
        for record in raw:
            if not isinstance(record,dict): continue
            name=CatalogService._text(record.get("name")); provider_id=CatalogService._positive_int(record.get("id"))
            if name and provider_id and CatalogService._slug(name)==slug:
                return provider_id,name
        return None,None

    @staticmethod
    def _genres(value: object) -> list[dict[str, object]]:
        return [x for x in value if isinstance(x,dict)] if isinstance(value,list) else []

    @staticmethod
    def _genre_names(value: object) -> list[str]:
        return [name for record in CatalogService._genres(value) if (name:=CatalogService._text(record.get("name")))]

    @staticmethod
    def _creators(details: dict[str, object]) -> list[str]:
        raw=details.get("created_by")
        if not isinstance(raw,list): return []
        return CatalogService._dedupe_text([name for record in raw if isinstance(record,dict) and (name:=CatalogService._text(record.get("name")))])[:12]

    @staticmethod
    def _writers(credits: dict[str, object]) -> list[str]:
        raw=credits.get("crew")
        if not isinstance(raw,list): return []
        names=[]
        for record in raw:
            if not isinstance(record,dict): continue
            dep=CatalogService._text(record.get("department")); job=CatalogService._text(record.get("job"))
            if dep!="Writing" and job not in {"Writer","Screenplay","Story","Teleplay","Creator"}: continue
            if name:=CatalogService._text(record.get("name")): names.append(name)
        return CatalogService._dedupe_text(names)[:12]

    @staticmethod
    def _runtime(details: dict[str, object], media_type: str) -> int | None:
        if media_type=="movie": return CatalogService._nonnegative_int(details.get("runtime"))
        raw=details.get("episode_run_time")
        if isinstance(raw,list):
            for item in raw:
                value=CatalogService._nonnegative_int(item)
                if value is not None: return value
        return None

    @staticmethod
    def _image(base: str, size: str, value: object) -> str | None:
        path=CatalogService._text(value)
        if not path: return None
        return f"{base.rstrip('/')}/{size}/{path.lstrip('/')}"

    @staticmethod
    def _validate_media(value: str) -> None:
        if value not in {"movie","tv"}: raise ValueError("Catalog media type must be movie or tv.")

    @staticmethod
    def _slug(value: str) -> str:
        return re.sub(r"[^a-z0-9]+","-",value.casefold()).strip("-") or "item"

    @staticmethod
    def _year(value: str | None) -> int | None:
        if not value or len(value)<4 or not value[:4].isdigit(): return None
        year=int(value[:4]); return year if 1800<=year<=2200 else None

    @staticmethod
    def _date(value: object) -> date | None:
        text=CatalogService._text(value)
        if not text: return None
        try: return date.fromisoformat(text)
        except ValueError: return None

    @staticmethod
    def _datetime(value: object) -> datetime | None:
        text=CatalogService._text(value)
        if not text: return None
        try:
            parsed=datetime.fromisoformat(text.replace("Z","+00:00"))
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except ValueError: return None

    @staticmethod
    def _text(value: object) -> str | None:
        if not isinstance(value,str): return None
        stripped=value.strip(); return stripped or None

    @staticmethod
    def _clamp_rating(value: object) -> float | None:
        number = CatalogService._number(value)
        if number is None:
            return None
        return max(0.0, min(10.0, number))

    @staticmethod
    def _number(value: object) -> float | None:
        if isinstance(value,bool): return None
        return float(value) if isinstance(value,(int,float)) else None

    @staticmethod
    def _int(value: object) -> int | None:
        return value if isinstance(value,int) and not isinstance(value,bool) else None

    @staticmethod
    def _positive_int(value: object) -> int | None:
        result=CatalogService._int(value); return result if result is not None and result>0 else None

    @staticmethod
    def _nonnegative_int(value: object) -> int | None:
        result=CatalogService._int(value); return result if result is not None and result>=0 else None

    @staticmethod
    def _dedupe_text(values: list[str]) -> list[str]:
        seen=set(); result=[]
        for value in values:
            key=value.casefold()
            if key in seen: continue
            seen.add(key); result.append(value)
        return result
