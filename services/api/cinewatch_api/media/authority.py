"""Optional PostgreSQL-backed media resolver that never removes catalog entities."""

from __future__ import annotations

from sqlalchemy.orm import Session

from cinewatch_api.contracts.catalog import (
    CatalogBrowseResponse,
    CatalogPersonResponse,
    CatalogProviderResponse,
    CatalogSeasonResponse,
    CatalogTitleResponse,
)
from cinewatch_api.contracts.home import HomeItem, HomeResponse
from cinewatch_api.contracts.search import SearchResponse
from cinewatch_api.media.fallbacks import MediaGap
from cinewatch_api.media.repository import MediaAuthorityRepository


class MediaAuthority:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._repo = MediaAuthorityRepository(session)

    def _resolve(self, gap: MediaGap, provider_url: str | None) -> str | None:
        override = self._repo.find_override(gap)
        if override:
            return override
        if provider_url:
            return provider_url
        self._repo.record_gap(gap)
        return None

    def apply_home(self, payload: HomeResponse) -> HomeResponse:
        items: list[HomeItem] = []
        if payload.hero is not None:
            items.append(payload.hero)
        for group in (
            payload.sections.trending,
            payload.sections.popular_movies,
            payload.sections.popular_tv,
            payload.sections.trending_people,
        ):
            items.extend(group)
        seen: set[tuple[str, int]] = set()
        for item in items:
            key = (item.media_type, item.provider_id)
            if key in seen:
                continue
            seen.add(key)
            if item.media_type == "person":
                gap = MediaGap("tmdb", "person", item.provider_id, item.title, "profile")
                item.profile_url = self._resolve(gap, item.profile_url)
            else:
                poster = MediaGap("tmdb", item.media_type, item.provider_id, item.title, "poster")
                backdrop = MediaGap("tmdb", item.media_type, item.provider_id, item.title, "backdrop")
                item.poster_url = self._resolve(poster, item.poster_url)
                item.backdrop_url = self._resolve(backdrop, item.backdrop_url)
        self._session.commit()
        return payload

    def apply_title(self, payload: CatalogTitleResponse) -> CatalogTitleResponse:
        payload.poster_url = self._resolve(MediaGap("tmdb", payload.media_type, payload.provider_id, payload.title, "poster"), payload.poster_url)
        payload.backdrop_url = self._resolve(MediaGap("tmdb", payload.media_type, payload.provider_id, payload.title, "backdrop"), payload.backdrop_url)
        for member in [*payload.cast, *payload.crew]:
            member.profile_url = self._resolve(MediaGap("tmdb", "person", member.provider_id, member.name, "profile"), member.profile_url)
        for season in payload.seasons:
            if season.provider_id:
                season.poster_url = self._resolve(MediaGap("tmdb", "season", season.provider_id, season.name, "poster"), season.poster_url)
        for item in payload.recommendations:
            item.poster_url = self._resolve(MediaGap("tmdb", item.media_type, item.provider_id, item.title, "poster"), item.poster_url)
            item.backdrop_url = self._resolve(MediaGap("tmdb", item.media_type, item.provider_id, item.title, "backdrop"), item.backdrop_url)
        for network in payload.networks:
            if network.provider_id:
                network.logo_url = self._resolve(MediaGap("tmdb", "network", network.provider_id, network.name, "logo"), network.logo_url)
        for provider in payload.watch_providers:
            provider.logo_url = self._resolve(
                MediaGap("tmdb", "network", provider.provider_id, provider.name, "logo"),
                provider.logo_url,
            )
        self._session.commit()
        return payload

    def apply_person(self, payload: CatalogPersonResponse) -> CatalogPersonResponse:
        payload.profile_url = self._resolve(MediaGap("tmdb", "person", payload.provider_id, payload.name, "profile"), payload.profile_url)
        for item in [*payload.credits, *payload.crew_credits]:
            item.poster_url = self._resolve(MediaGap("tmdb", item.media_type, item.provider_id, item.title, "poster"), item.poster_url)
            item.backdrop_url = self._resolve(MediaGap("tmdb", item.media_type, item.provider_id, item.title, "backdrop"), item.backdrop_url)
        self._session.commit()
        return payload

    def apply_browse(self, payload: CatalogBrowseResponse) -> CatalogBrowseResponse:
        for item in payload.items:
            item.poster_url = self._resolve(MediaGap("tmdb", item.media_type, item.provider_id, item.title, "poster"), item.poster_url)
            item.backdrop_url = self._resolve(MediaGap("tmdb", item.media_type, item.provider_id, item.title, "backdrop"), item.backdrop_url)
        self._session.commit()
        return payload

    def apply_season(self, payload: CatalogSeasonResponse) -> CatalogSeasonResponse:
        # Season identity in this response is represented by series provider ID + season number;
        # episode IDs remain exact TMDb episode identities.
        for episode in payload.episodes:
            episode.still_url = self._resolve(MediaGap("tmdb", "episode", episode.provider_id, episode.name, "still"), episode.still_url)
        self._session.commit()
        return payload

    def apply_provider(self, payload: CatalogProviderResponse) -> CatalogProviderResponse:
        payload.logo_url = self._resolve(MediaGap("tmdb", "network", payload.provider_id, payload.name, "logo"), payload.logo_url)
        for item in payload.items:
            item.poster_url = self._resolve(MediaGap("tmdb", item.media_type, item.provider_id, item.title, "poster"), item.poster_url)
            item.backdrop_url = self._resolve(MediaGap("tmdb", item.media_type, item.provider_id, item.title, "backdrop"), item.backdrop_url)
        self._session.commit()
        return payload

    def apply_search(self, payload: SearchResponse) -> SearchResponse:
        for item in payload.suggestions:
            if not item.provider_id:
                continue
            if item.entity_type == "PERSON":
                gap = MediaGap("tmdb", "person", item.provider_id, item.label, "profile")
            elif item.entity_type == "MOVIE":
                gap = MediaGap("tmdb", "movie", item.provider_id, item.label, "poster")
            elif item.entity_type == "TV_SHOW":
                gap = MediaGap("tmdb", "tv", item.provider_id, item.label, "poster")
            elif item.entity_type == "NETWORK_PROVIDER":
                gap = MediaGap("tmdb", "network", item.provider_id, item.label, "logo")
            else:
                continue
            item.image_url = self._resolve(gap, item.image_url)
        self._session.commit()
        return payload
