"""Normalize TMDb homepage data behind the CineWatch V1 contract."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from cinewatch_api.contracts.home import (
    HomeItem,
    HomeMediaGap,
    HomeRating,
    HomeResponse,
    HomeSections,
)
from cinewatch_api.media.fallbacks import MediaGap
from cinewatch_api.providers.errors import ProviderResponseError

SECTION_LIMIT = 12


class TmdbGateway(Protocol):
    """Narrow provider surface required by homepage aggregation."""

    async def get_json(
        self,
        path: str,
        *,
        params: dict[str, str | int | float | bool] | None = None,
    ) -> dict[str, object]:
        """Return one authenticated TMDb JSON object."""


@dataclass(frozen=True, slots=True)
class _ImageConfiguration:
    secure_base_url: str
    poster_size: str
    backdrop_size: str
    profile_size: str


class HomepageAggregator:
    """Build one bounded, provider-neutral CineWatch homepage payload."""

    def __init__(self, tmdb: TmdbGateway) -> None:
        self._tmdb = tmdb

    async def build(self) -> HomeResponse:
        configuration = await self._tmdb.get_json("/configuration")
        images = self._image_configuration(configuration)

        trending_payload = await self._tmdb.get_json(
            "/trending/all/day",
            params={"language": "en-US"},
        )
        movies_payload = await self._tmdb.get_json(
            "/movie/popular",
            params={"language": "en-US", "page": 1},
        )
        tv_payload = await self._tmdb.get_json(
            "/tv/popular",
            params={"language": "en-US", "page": 1},
        )
        people_payload = await self._tmdb.get_json(
            "/trending/person/day",
            params={"language": "en-US"},
        )

        trending = self._normalize_results(
            trending_payload,
            images=images,
            accepted_media_types={"movie", "tv"},
        )
        popular_movies = self._normalize_results(
            movies_payload,
            images=images,
            forced_media_type="movie",
            accepted_media_types={"movie"},
        )
        popular_tv = self._normalize_results(
            tv_payload,
            images=images,
            forced_media_type="tv",
            accepted_media_types={"tv"},
        )
        trending_people = self._normalize_results(
            people_payload,
            images=images,
            forced_media_type="person",
            accepted_media_types={"person"},
        )

        hero = next(
            (item for item in trending if item.backdrop_url),
            trending[0] if trending else None,
        )

        return HomeResponse(
            hero=hero,
            sections=HomeSections(
                trending=trending,
                popular_movies=popular_movies,
                popular_tv=popular_tv,
                trending_people=trending_people,
            ),
        )

    def _normalize_results(
        self,
        payload: dict[str, object],
        *,
        images: _ImageConfiguration,
        accepted_media_types: set[str],
        forced_media_type: str | None = None,
    ) -> list[HomeItem]:
        raw_results = payload.get("results")
        if not isinstance(raw_results, list):
            raise ProviderResponseError(
                provider="tmdb",
                code="TMDB_HOME_RESULTS_INVALID",
                message="TMDb returned an invalid homepage result collection.",
            )

        normalized: list[HomeItem] = []
        for raw in raw_results:
            if not isinstance(raw, dict):
                continue
            item = self._normalize_item(
                raw,
                images=images,
                forced_media_type=forced_media_type,
            )
            if item is None or item.media_type not in accepted_media_types:
                continue
            normalized.append(item)
            if len(normalized) >= SECTION_LIMIT:
                break
        return normalized

    def _normalize_item(
        self,
        raw: dict[str, object],
        *,
        images: _ImageConfiguration,
        forced_media_type: str | None,
    ) -> HomeItem | None:
        media_type = forced_media_type or self._text(raw.get("media_type"))
        if media_type not in {"movie", "tv", "person"}:
            return None

        provider_id = raw.get("id")
        if isinstance(provider_id, bool) or not isinstance(provider_id, int):
            return None
        if provider_id <= 0:
            return None

        if media_type == "movie":
            title = self._text(raw.get("title"))
            date = self._text(raw.get("release_date"))
        else:
            title = self._text(raw.get("name"))
            date = self._text(raw.get("first_air_date")) if media_type == "tv" else None

        if not title:
            return None

        media_gaps: list[HomeMediaGap] = []
        poster_url: str | None = None
        backdrop_url: str | None = None
        profile_url: str | None = None

        if media_type == "person":
            profile_path = self._text(raw.get("profile_path"))
            if profile_path:
                profile_url = self._image_url(
                    images.secure_base_url,
                    images.profile_size,
                    profile_path,
                )
            else:
                media_gaps.append(
                    self._media_gap(
                        entity_type="person",
                        provider_id=provider_id,
                        entity_name=title,
                        asset_kind="profile",
                    )
                )
        else:
            poster_path = self._text(raw.get("poster_path"))
            backdrop_path = self._text(raw.get("backdrop_path"))
            if poster_path:
                poster_url = self._image_url(
                    images.secure_base_url,
                    images.poster_size,
                    poster_path,
                )
            else:
                media_gaps.append(
                    self._media_gap(
                        entity_type=media_type,
                        provider_id=provider_id,
                        entity_name=title,
                        asset_kind="poster",
                    )
                )
            if backdrop_path:
                backdrop_url = self._image_url(
                    images.secure_base_url,
                    images.backdrop_size,
                    backdrop_path,
                )
            else:
                media_gaps.append(
                    self._media_gap(
                        entity_type=media_type,
                        provider_id=provider_id,
                        entity_name=title,
                        asset_kind="backdrop",
                    )
                )

        rating = self._rating(raw) if media_type in {"movie", "tv"} else None

        return HomeItem(
            provider_id=provider_id,
            media_type=media_type,
            title=title,
            overview=self._text(raw.get("overview")),
            date=date,
            popularity=self._number(raw.get("popularity")),
            rating=rating,
            poster_url=poster_url,
            backdrop_url=backdrop_url,
            profile_url=profile_url,
            known_for_department=(
                self._text(raw.get("known_for_department"))
                if media_type == "person"
                else None
            ),
            media_gaps=media_gaps,
        )

    @staticmethod
    def _rating(raw: dict[str, object]) -> HomeRating | None:
        value = HomepageAggregator._number(raw.get("vote_average"))
        count_raw = raw.get("vote_count")
        if value is None:
            return None
        if isinstance(count_raw, bool) or not isinstance(count_raw, int):
            count = 0
        else:
            count = max(0, count_raw)
        return HomeRating(
            value=max(0.0, min(10.0, value)),
            count=count,
        )

    @staticmethod
    def _media_gap(
        *,
        entity_type: str,
        provider_id: int,
        entity_name: str,
        asset_kind: str,
    ) -> HomeMediaGap:
        record = MediaGap(
            provider="tmdb",
            entity_type=entity_type,  # type: ignore[arg-type]
            provider_id=provider_id,
            entity_name=entity_name,
            asset_kind=asset_kind,  # type: ignore[arg-type]
        ).as_record()
        return HomeMediaGap.model_validate(record)

    @staticmethod
    def _image_configuration(payload: dict[str, object]) -> _ImageConfiguration:
        raw_images = payload.get("images")
        if not isinstance(raw_images, dict):
            raise ProviderResponseError(
                provider="tmdb",
                code="TMDB_IMAGE_CONFIGURATION_INVALID",
                message="TMDb image configuration is unavailable.",
            )

        secure_base_url = HomepageAggregator._text(
            raw_images.get("secure_base_url")
        )
        if not secure_base_url:
            raise ProviderResponseError(
                provider="tmdb",
                code="TMDB_IMAGE_CONFIGURATION_INVALID",
                message="TMDb image configuration is unavailable.",
            )

        return _ImageConfiguration(
            secure_base_url=secure_base_url,
            poster_size=HomepageAggregator._choose_size(
                raw_images.get("poster_sizes"),
                preferred="w500",
            ),
            backdrop_size=HomepageAggregator._choose_size(
                raw_images.get("backdrop_sizes"),
                preferred="w1280",
            ),
            profile_size=HomepageAggregator._choose_size(
                raw_images.get("profile_sizes"),
                preferred="w185",
            ),
        )

    @staticmethod
    def _choose_size(value: object, *, preferred: str) -> str:
        if not isinstance(value, list):
            return "original"
        sizes = [item for item in value if isinstance(item, str) and item]
        if preferred in sizes:
            return preferred
        if "original" in sizes:
            return "original"
        return sizes[-1] if sizes else "original"

    @staticmethod
    def _image_url(base: str, size: str, path: str) -> str:
        return f"{base.rstrip('/')}/{size}/{path.lstrip('/')}"

    @staticmethod
    def _text(value: object) -> str | None:
        if not isinstance(value, str):
            return None
        stripped = value.strip()
        return stripped or None

    @staticmethod
    def _number(value: object) -> float | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        return None
