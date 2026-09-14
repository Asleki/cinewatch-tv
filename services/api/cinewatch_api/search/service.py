"""Typed entity search across titles, people, genres and watch providers."""

from __future__ import annotations

import asyncio
import re
from typing import Protocol

from cinewatch_api.contracts.search import SearchResponse, SearchSuggestion
from cinewatch_api.home.aggregation import HomepageAggregator
from cinewatch_api.providers.errors import ProviderError


class TmdbGateway(Protocol):
    async def get_json(
        self,
        path: str,
        *,
        params: dict[str, str | int | float | bool] | None = None,
    ) -> dict[str, object]: ...


class SearchService:
    """Resolve a user query into at most five route-aware CineWatch entities."""

    def __init__(self, tmdb: TmdbGateway) -> None:
        self._tmdb = tmdb
        self._normalizer = HomepageAggregator(tmdb)

    async def search(self, query: str) -> SearchResponse:
        normalized = " ".join(query.split())
        if len(normalized) < 2:
            raise ValueError("Search query must contain at least two characters.")

        configuration, multi, movie_genres, tv_genres = await asyncio.gather(
            self._tmdb.get_json("/configuration"),
            self._tmdb.get_json(
                "/search/multi",
                params={"query": normalized, "language": "en-US", "page": 1, "include_adult": False},
            ),
            self._tmdb.get_json("/genre/movie/list", params={"language": "en-US"}),
            self._tmdb.get_json("/genre/tv/list", params={"language": "en-US"}),
        )
        images = self._normalizer._image_configuration(configuration)

        suggestions: list[SearchSuggestion] = []
        seen_destinations: set[str] = set()

        for item in self._normalizer._normalize_results(
            multi,
            images=images,
            accepted_media_types={"movie", "tv", "person"},
        ):
            if item.media_type == "movie":
                entity_type = "MOVIE"
            elif item.media_type == "tv":
                entity_type = "TV_SHOW"
            else:
                entity_type = "PERSON"
            destination = item.future_path or (
                f"/person/{item.provider_id}"
                if item.media_type == "person"
                else f"/title/{item.media_type}/{item.provider_id}"
            )
            if destination in seen_destinations:
                continue
            image = item.profile_url if item.media_type == "person" else item.poster_url
            secondary = item.known_for_department if item.media_type == "person" else self._year(item.date)
            suggestions.append(
                SearchSuggestion(
                    entity_type=entity_type,  # type: ignore[arg-type]
                    canonical_id=f"tmdb:{item.media_type}:{item.provider_id}",
                    provider_id=item.provider_id,
                    label=item.title,
                    secondary_text=secondary,
                    image_url=image,
                    destination=destination,
                    source="tmdb",
                )
            )
            seen_destinations.add(destination)
            if len(suggestions) >= 5:
                return SearchResponse(query=normalized, suggestions=suggestions)

        for suggestion in self._genre_suggestions(normalized, movie_genres, tv_genres):
            if suggestion.destination in seen_destinations:
                continue
            suggestions.append(suggestion)
            seen_destinations.add(suggestion.destination)
            if len(suggestions) >= 5:
                return SearchResponse(query=normalized, suggestions=suggestions)

        # Provider discovery is useful but non-critical. A provider failure must not
        # erase otherwise valid title/person/genre suggestions.
        try:
            movie_providers, tv_providers = await asyncio.gather(
                self._tmdb.get_json("/watch/providers/movie", params={"language": "en-US"}),
                self._tmdb.get_json("/watch/providers/tv", params={"language": "en-US"}),
            )
        except ProviderError:
            movie_providers, tv_providers = {"results": []}, {"results": []}

        for suggestion in self._provider_suggestions(
            normalized,
            configuration,
            movie_providers,
            tv_providers,
        ):
            if suggestion.destination in seen_destinations:
                continue
            suggestions.append(suggestion)
            seen_destinations.add(suggestion.destination)
            if len(suggestions) >= 5:
                break

        return SearchResponse(query=normalized, suggestions=suggestions)

    def _genre_suggestions(
        self,
        query: str,
        movie_payload: dict[str, object],
        tv_payload: dict[str, object],
    ) -> list[SearchSuggestion]:
        needle = query.casefold()
        merged: dict[str, str] = {}
        for payload in (movie_payload, tv_payload):
            values = payload.get("genres")
            if not isinstance(values, list):
                continue
            for raw in values:
                if not isinstance(raw, dict):
                    continue
                name = self._text(raw.get("name"))
                if not name or needle not in name.casefold():
                    continue
                slug = self._slug(name)
                merged[slug] = name
        return [
            SearchSuggestion(
                entity_type="GENRE",
                canonical_id=f"cinewatch:genre:{slug}",
                label=name,
                secondary_text="Genre",
                destination=f"/genre/{slug}",
                source="cinewatch",
            )
            for slug, name in sorted(
                merged.items(),
                key=lambda pair: (0 if pair[1].casefold().startswith(needle) else 1, pair[1].casefold()),
            )
        ]

    def _provider_suggestions(
        self,
        query: str,
        configuration: dict[str, object],
        *payloads: dict[str, object],
    ) -> list[SearchSuggestion]:
        images = self._normalizer._image_configuration(configuration)
        needle = query.casefold()
        merged: dict[int, tuple[str, str | None]] = {}
        for payload in payloads:
            values = payload.get("results")
            if not isinstance(values, list):
                continue
            for raw in values:
                if not isinstance(raw, dict):
                    continue
                provider_id = self._positive_int(raw.get("provider_id"))
                name = self._text(raw.get("provider_name"))
                if provider_id is None or not name or needle not in name.casefold():
                    continue
                logo_path = self._text(raw.get("logo_path"))
                logo_url = (
                    self._normalizer._image_url(images.secure_base_url, images.profile_size, logo_path)
                    if logo_path
                    else None
                )
                merged[provider_id] = (name, logo_url)
        rows = sorted(
            merged.items(),
            key=lambda pair: (0 if pair[1][0].casefold().startswith(needle) else 1, pair[1][0].casefold()),
        )
        return [
            SearchSuggestion(
                entity_type="NETWORK_PROVIDER",
                canonical_id=f"tmdb:watch-provider:{provider_id}",
                provider_id=provider_id,
                label=name,
                secondary_text="Streaming provider",
                image_url=logo_url,
                destination=f"/provider/{provider_id}",
                source="tmdb",
            )
            for provider_id, (name, logo_url) in rows
        ]

    @staticmethod
    def _year(value: str | None) -> str | None:
        if not value:
            return None
        match = re.match(r"^(\d{4})", value)
        return match.group(1) if match else None

    @staticmethod
    def _slug(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")

    @staticmethod
    def _text(value: object) -> str | None:
        if not isinstance(value, str):
            return None
        stripped = value.strip()
        return stripped or None

    @staticmethod
    def _positive_int(value: object) -> int | None:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            return None
        return value
