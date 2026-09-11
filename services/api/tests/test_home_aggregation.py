from __future__ import annotations

import asyncio

import pytest

from cinewatch_api.home.aggregation import HomepageAggregator
from cinewatch_api.providers.errors import ProviderResponseError


class FakeTmdb:
    def __init__(self, payloads: dict[str, dict[str, object]]) -> None:
        self.payloads = payloads
        self.calls: list[str] = []

    async def get_json(
        self,
        path: str,
        *,
        params: dict[str, str | int | float | bool] | None = None,
    ) -> dict[str, object]:
        del params
        self.calls.append(path)
        return self.payloads[path]


def _configuration() -> dict[str, object]:
    return {
        "images": {
            "secure_base_url": "https://image.tmdb.example/t/p/",
            "poster_sizes": ["w342", "w500", "original"],
            "backdrop_sizes": ["w780", "w1280", "original"],
            "profile_sizes": ["w185", "original"],
        }
    }


def test_homepage_aggregation_normalizes_sections_and_media_gaps() -> None:
    tmdb = FakeTmdb(
        {
            "/configuration": _configuration(),
            "/trending/all/day": {
                "results": [
                    {
                        "id": 1,
                        "media_type": "movie",
                        "title": "Alpha",
                        "overview": "First.",
                        "release_date": "2026-01-01",
                        "vote_average": 8.2,
                        "vote_count": 100,
                        "popularity": 90.0,
                        "poster_path": "/alpha.jpg",
                        "backdrop_path": None,
                    },
                    {
                        "id": 2,
                        "media_type": "tv",
                        "name": "Beta",
                        "overview": "Second.",
                        "first_air_date": "2026-02-01",
                        "vote_average": 7.5,
                        "vote_count": 55,
                        "popularity": 80.0,
                        "poster_path": None,
                        "backdrop_path": "/beta-bg.jpg",
                    },
                    {
                        "id": 3,
                        "media_type": "person",
                        "name": "Filtered Person",
                    },
                ]
            },
            "/movie/popular": {
                "results": [
                    {
                        "id": 10,
                        "title": "Missing Art Movie",
                        "overview": "",
                        "release_date": "2025-12-01",
                        "vote_average": 9.0,
                        "vote_count": 8,
                        "poster_path": None,
                        "backdrop_path": None,
                    }
                ]
            },
            "/tv/popular": {
                "results": [
                    {
                        "id": 20,
                        "name": "Gamma TV",
                        "first_air_date": "2026-03-01",
                        "vote_average": 6.8,
                        "vote_count": 12,
                        "poster_path": "/gamma-poster.jpg",
                        "backdrop_path": "/gamma-bg.jpg",
                    }
                ]
            },
            "/trending/person/day": {
                "results": [
                    {
                        "id": 30,
                        "name": "Ada Example",
                        "known_for_department": "Acting",
                        "profile_path": None,
                        "popularity": 50.0,
                    }
                ]
            },
        }
    )

    result = asyncio.run(HomepageAggregator(tmdb).build())

    assert result.primary_provider == "tmdb"
    assert result.hero is not None
    assert result.hero.provider_id == 2
    assert result.hero.backdrop_url == (
        "https://image.tmdb.example/t/p/w1280/beta-bg.jpg"
    )

    assert [item.provider_id for item in result.sections.trending] == [1, 2]
    alpha = result.sections.trending[0]
    assert alpha.poster_url == "https://image.tmdb.example/t/p/w500/alpha.jpg"
    assert alpha.rating is not None
    assert alpha.rating.value == 8.2
    assert alpha.rating.count == 100

    missing_movie = result.sections.popular_movies[0]
    assert {gap.asset_kind for gap in missing_movie.media_gaps} == {
        "poster",
        "backdrop",
    }
    remediation = {
        gap.asset_kind: gap.remediation for gap in missing_movie.media_gaps
    }
    assert remediation["poster"] == "AWAITING_HUMAN_RESEARCH"
    assert remediation["backdrop"] == "GENERATION_ALLOWED"

    person = result.sections.trending_people[0]
    assert person.profile_url is None
    assert len(person.media_gaps) == 1
    assert person.media_gaps[0].asset_kind == "profile"
    assert person.media_gaps[0].remediation == "AWAITING_HUMAN_RESEARCH"
    assert person.media_gaps[0].suggested_filename == (
        "tmdb-person-30-ada-example.webp"
    )

    assert tmdb.calls == [
        "/configuration",
        "/trending/all/day",
        "/movie/popular",
        "/tv/popular",
        "/trending/person/day",
    ]


def test_homepage_aggregation_rejects_missing_tmdb_image_configuration() -> None:
    tmdb = FakeTmdb(
        {
            "/configuration": {"images": {}},
            "/trending/all/day": {"results": []},
            "/movie/popular": {"results": []},
            "/tv/popular": {"results": []},
            "/trending/person/day": {"results": []},
        }
    )

    with pytest.raises(ProviderResponseError) as captured:
        asyncio.run(HomepageAggregator(tmdb).build())

    assert captured.value.code == "TMDB_IMAGE_CONFIGURATION_INVALID"
