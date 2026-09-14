from __future__ import annotations

import asyncio

from cinewatch_api.search.service import SearchService


class FakeTmdb:
    async def get_json(self, path: str, *, params=None):
        del params
        if path == "/configuration":
            return {
                "images": {
                    "secure_base_url": "https://image.tmdb.test/",
                    "poster_sizes": ["w500"],
                    "backdrop_sizes": ["w1280"],
                    "profile_sizes": ["w185"],
                }
            }
        if path == "/search/multi":
            return {
                "results": [
                    {"id": 1, "media_type": "movie", "title": "Moonlight", "poster_path": "/m.jpg", "release_date": "2016-10-21"},
                    {"id": 2, "media_type": "person", "name": "Lupita Nyong'o", "profile_path": "/l.jpg", "known_for_department": "Acting"},
                ]
            }
        if path == "/genre/movie/list":
            return {"genres": [{"id": 18, "name": "Drama"}]}
        if path == "/genre/tv/list":
            return {"genres": [{"id": 18, "name": "Drama"}]}
        if path == "/watch/providers/movie":
            return {"results": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/n.jpg"}]}
        if path == "/watch/providers/tv":
            return {"results": []}
        raise AssertionError(path)


def test_typed_search_is_bounded_and_routes_entities() -> None:
    payload = asyncio.run(SearchService(FakeTmdb()).search("Lupita"))
    assert len(payload.suggestions) <= 5
    person = next(item for item in payload.suggestions if item.entity_type == "PERSON")
    assert person.destination == "/person/2"


def test_typed_search_can_return_genre() -> None:
    payload = asyncio.run(SearchService(FakeTmdb()).search("Dram"))
    genre = next(item for item in payload.suggestions if item.entity_type == "GENRE")
    assert genre.destination == "/genre/drama"


def test_typed_search_can_return_network_provider() -> None:
    payload = asyncio.run(SearchService(FakeTmdb()).search("Netflix"))
    provider = next(item for item in payload.suggestions if item.entity_type == "NETWORK_PROVIDER")
    assert provider.provider_id == 8
    assert provider.destination == "/provider/8"
