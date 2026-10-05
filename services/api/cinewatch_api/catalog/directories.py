"""Small TMDb-backed person and organization directories."""
from __future__ import annotations

import asyncio
import time
from datetime import date
from urllib.parse import urlparse

from cinewatch_api.contracts.directories import (
    OrganizationDetailResponse, OrganizationDirectoryResponse, OrganizationItem,
    PeopleDirectoryResponse, PersonDirectoryItem,
)
from cinewatch_api.home.aggregation import HomepageAggregator
from cinewatch_api.providers.errors import ProviderError
from cinewatch_api.providers.tmdb import TmdbClient

_ORG_CACHE: dict[int, tuple[float, OrganizationDirectoryResponse]] = {}


class DirectoryService:
    def __init__(self, tmdb) -> None:
        self._tmdb = tmdb
        self._images = HomepageAggregator(tmdb)

    @staticmethod
    def _text(value: object) -> str | None:
        return value.strip() or None if isinstance(value, str) else None

    @staticmethod
    def _homepage(value: object) -> str | None:
        if not isinstance(value, str):
            return None
        parsed = urlparse(value.strip())
        return value.strip() if parsed.scheme == "https" and parsed.netloc and not parsed.username else None

    def _image(self, images, size: str, path: object) -> str | None:
        return self._images._image_url(images.secure_base_url, size, path) if isinstance(path, str) and path.startswith("/") else None

    async def people(self, page: int = 1, department: str | None = None) -> PeopleDirectoryResponse:
        if page < 1 or page > 500:
            raise ValueError("Invalid people page")
        if department not in {None, "Acting", "Writing", "Directing", "Production"}:
            raise ValueError("Invalid department")
        config, payload = await asyncio.gather(
            self._tmdb.get_json("/configuration"),
            self._tmdb.get_json("/person/popular", params={"language": "en-US", "page": page}),
        )
        images = self._images._image_configuration(config)
        items: list[PersonDirectoryItem] = []
        for row in payload.get("results", []):
            if not isinstance(row, dict):
                continue
            identity, name = row.get("id"), self._text(row.get("name"))
            known_for = self._text(row.get("known_for_department"))
            if not isinstance(identity, int) or identity <= 0 or not name or (department and known_for != department):
                continue
            items.append(PersonDirectoryItem(
                provider_id=identity, name=name, known_for_department=known_for,
                profile_url=self._image(images, images.profile_size, row.get("profile_path")),
                future_path=f"/person/{identity}",
            ))
        return PeopleDirectoryResponse(
            page=page, total_pages=min(500, max(0, int(payload.get("total_pages") or 0))),
            department=department, items=items[:20],
        )

    def _organization(self, row: dict, kind: str, images) -> OrganizationItem | None:
        identity, name = row.get("id"), self._text(row.get("name"))
        if not isinstance(identity, int) or identity <= 0 or not name:
            return None
        return OrganizationItem(
            provider_id=identity, kind=kind, name=name,  # type: ignore[arg-type]
            logo_url=self._image(images, images.profile_size, row.get("logo_path")),
            origin_country=self._text(row.get("origin_country")),
            headquarters=self._text(row.get("headquarters")),
            homepage_url=self._homepage(row.get("homepage")),
            future_path=f"/{kind}/{identity}",
        )

    async def organizations(self, page: int = 1) -> OrganizationDirectoryResponse:
        """Discover a bounded directory from real popular title associations."""
        if page < 1 or page > 100:
            raise ValueError("Invalid organization page")
        if isinstance(self._tmdb, TmdbClient) and page in _ORG_CACHE and _ORG_CACHE[page][0] > time.monotonic():
            return _ORG_CACHE[page][1].model_copy(deep=True)
        config, tv_list, movie_list = await asyncio.gather(
            self._tmdb.get_json("/configuration"),
            self._tmdb.get_json("/tv/popular", params={"page": page, "language": "en-US"}),
            self._tmdb.get_json("/movie/popular", params={"page": page, "language": "en-US"}),
        )
        images = self._images._image_configuration(config)
        requests = []
        for kind, payload in (("tv", tv_list), ("movie", movie_list)):
            for row in payload.get("results", [])[:6]:
                if isinstance(row, dict) and isinstance(row.get("id"), int):
                    requests.append(self._tmdb.get_json(f"/{kind}/{row['id']}", params={"language": "en-US"}))
        details = await asyncio.gather(*requests, return_exceptions=True)
        identities: dict[tuple[str, int], OrganizationItem] = {}
        for row in details:
            if isinstance(row, BaseException) or not isinstance(row, dict):
                continue
            for field, kind in (("networks", "network"), ("production_companies", "company")):
                for raw in row.get(field, []):
                    if isinstance(raw, dict):
                        item = self._organization(raw, kind, images)
                        if item:
                            identities[(kind, item.provider_id)] = item
        selected = list(identities.values())[:24]
        semaphore = asyncio.Semaphore(6)
        async def enrich(item: OrganizationItem) -> OrganizationItem:
            async with semaphore:
                try:
                    raw = await self._tmdb.get_json(f"/{item.kind}/{item.provider_id}")
                    return self._organization(raw, item.kind, images) or item
                except ProviderError:
                    return item
        result = OrganizationDirectoryResponse(page=page, has_more=page < 100 and (page < int(tv_list.get("total_pages") or 0) or page < int(movie_list.get("total_pages") or 0)), items=list(await asyncio.gather(*(enrich(item) for item in selected))))
        if isinstance(self._tmdb, TmdbClient):
            _ORG_CACHE[page] = (time.monotonic() + 900, result.model_copy(deep=True))
        return result

    async def organization(self, kind: str, provider_id: int) -> OrganizationDetailResponse:
        if kind not in {"network", "company"} or provider_id <= 0:
            raise ValueError("Invalid organization identity")
        config, raw = await asyncio.gather(
            self._tmdb.get_json("/configuration"),
            self._tmdb.get_json(f"/{kind}/{provider_id}"),
        )
        images = self._images._image_configuration(config)
        org = self._organization(raw, kind, images)
        if not org:
            raise ValueError("Unknown organization")
        requests = []
        if kind == "company":
            requests.append(("movie", self._tmdb.get_json("/discover/movie", params={"with_companies": provider_id, "sort_by": "primary_release_date.desc", "primary_release_date.lte": date.today().isoformat(), "page": 1})))
        requests.append(("tv", self._tmdb.get_json("/discover/tv", params={"with_networks" if kind == "network" else "with_companies": provider_id, "sort_by": "first_air_date.desc", "first_air_date.lte": date.today().isoformat(), "page": 1})))
        found = await asyncio.gather(*(request for _, request in requests), return_exceptions=True)
        movie_count = series_count = None
        candidate: tuple[str, int, str | None, str] | None = None
        for (media_type, _), payload in zip(requests, found, strict=True):
            if isinstance(payload, BaseException) or not isinstance(payload, dict):
                continue
            count = max(0, int(payload.get("total_results") or 0))
            if media_type == "movie": movie_count = count
            else: series_count = count
            for title in payload.get("results", []):
                if isinstance(title, dict) and isinstance(title.get("id"), int):
                    name = self._text(title.get("title")) or self._text(title.get("name")) or org.name
                    candidate = candidate or (media_type, title["id"], self._text(title.get("backdrop_path")), name)
                    if candidate[2] is None and isinstance(title.get("backdrop_path"), str):
                        candidate = (media_type, title["id"], title["backdrop_path"], name)
                    break
        return OrganizationDetailResponse(
            organization=org, description=self._text(raw.get("description")),
            backdrop_url=self._image(images, images.backdrop_size, candidate[2]) if candidate and candidate[2] else None,
            backdrop_media_type=candidate[0] if candidate else None,
            backdrop_title_id=candidate[1] if candidate else None,
            backdrop_title_name=candidate[3] if candidate else None,
            movie_count=movie_count, series_count=series_count,
        )
