"""Bounded TMDb title discovery followed by playable YouTube video verification."""
from __future__ import annotations
import asyncio
from urllib.parse import urlencode
from cinewatch_api.contracts.trailer_library import TrailerLibraryCard, TrailerLibraryResponse
from cinewatch_api.home.aggregation import HomepageAggregator
from cinewatch_api.providers.errors import ProviderError

TYPES = {"Trailer", "Teaser", "Clip", "Featurette", "Behind the Scenes"}
MAX_TRAILER_PAGE = 500

class TrailerLibraryService:
    def __init__(self, tmdb) -> None:
        self._tmdb = tmdb
        self._images = HomepageAggregator(tmdb)

    async def browse(self, *, page: int = 1, media_type: str = "all", genre: str | None = None, year: int | None = None, video_language: str | None = None, video_type: str | None = None) -> TrailerLibraryResponse:
        if page < 1 or page > MAX_TRAILER_PAGE or media_type not in {"all", "movie", "tv"} or video_type not in {None, *TYPES}:
            raise ValueError("Invalid trailer filter")
        configuration = await self._tmdb.get_json("/configuration")
        images = self._images._image_configuration(configuration)
        genre_ids: dict[str, int] = {}
        if genre:
            import re
            lists = await asyncio.gather(*(self._tmdb.get_json(f"/genre/{kind}/list", params={"language": "en-US"}) for kind in ("movie", "tv")))
            for kind, payload in zip(("movie", "tv"), lists, strict=True):
                for item in payload.get("genres", []):
                    if isinstance(item, dict) and re.sub(r"[^a-z0-9]+", "-", str(item.get("name", "")).casefold()).strip("-") == genre:
                        genre_ids[kind] = item["id"]
        requests = []
        for kind in ("movie", "tv"):
            if media_type != "all" and media_type != kind:
                continue
            if genre and kind not in genre_ids:
                continue
            params = {"page": page, "sort_by": "popularity.desc", "include_adult": False}
            if genre: params["with_genres"] = genre_ids[kind]
            if year: params["primary_release_year" if kind == "movie" else "first_air_date_year"] = year
            requests.append((kind, self._tmdb.get_json(f"/discover/{kind}", params=params)))
        found = await asyncio.gather(*(request for _, request in requests))
        candidates = []
        has_more = False
        for (kind, _), payload in zip(requests, found, strict=True):
            has_more |= page < min(MAX_TRAILER_PAGE, int(payload.get("total_pages") or 0))
            for row in payload.get("results", [])[:16]:
                if isinstance(row, dict) and isinstance(row.get("id"), int) and row["id"] > 0:
                    candidates.append((kind, row))
        semaphore = asyncio.Semaphore(6)
        async def video_for(kind, row):
            async with semaphore:
                try:
                    params = {"language": "en-US", "include_video_language": video_language} if video_language else None
                    payload = await self._tmdb.get_json(f"/{kind}/{row['id']}/videos", params=params)
                except ProviderError:
                    return None
            raw = payload.get("results")
            if not isinstance(raw, list): return None
            options = [v for v in raw if isinstance(v, dict) and v.get("site") == "YouTube" and v.get("type") in TYPES and isinstance(v.get("key"), str) and v["key"] and (not video_type or v["type"] == video_type) and (not video_language or v.get("iso_639_1") == video_language)]
            if not options: return None
            options.sort(key=lambda v: (v.get("type") != "Trailer", not v.get("official"), v.get("published_at") or ""))
            video = options[0]
            selection = {"video_key": video["key"], "video_type": video["type"]}
            if isinstance(video.get("iso_639_1"), str) and video["iso_639_1"]:
                selection["video_language"] = video["iso_639_1"]
            title = row.get("title") or row.get("name")
            if not isinstance(title, str) or not title.strip(): return None
            release = row.get("release_date") or row.get("first_air_date")
            release_year = int(release[:4]) if isinstance(release, str) and len(release) >= 4 and release[:4].isdigit() else None
            poster = row.get("poster_path")
            return TrailerLibraryCard(provider_id=row["id"], media_type=kind, title=title, release_year=release_year,
                genre_ids=[g for g in row.get("genre_ids", []) if isinstance(g, int)],
                poster_url=self._images._image_url(images.secure_base_url, images.poster_size, poster) if isinstance(poster, str) else None,
                youtube_key=video["key"], video_name=str(video.get("name") or video["type"]), video_type=video["type"],
                video_language=video.get("iso_639_1") if isinstance(video.get("iso_639_1"), str) else None,
                official=bool(video.get("official")), future_path=f"/title/{kind}/{row['id']}/trailers?{urlencode(selection)}")
        resolved = await asyncio.gather(*(video_for(kind, row) for kind, row in candidates))
        return TrailerLibraryResponse(page=page, has_more=has_more, items=[item for item in resolved if item][:24])
