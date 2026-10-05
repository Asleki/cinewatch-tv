from __future__ import annotations

import asyncio

from cinewatch_api.home.experience import HomepageExperienceService


class FakeTmdb:
    def __init__(self, payloads: dict[str, dict[str, object]]) -> None:
        self.payloads = payloads
        self.calls: list[tuple[str, dict[str, object]]] = []

    async def get_json(self, path: str, *, params=None):
        self.calls.append((path, dict(params or {})))
        return self.payloads[path]


class FakeOmdb:
    async def lookup_imdb(self, imdb_id: str):
        assert imdb_id == "tt1234567"
        return {
            "Ratings": [
                {"Source": "Internet Movie Database", "Value": "8.2/10"},
                {"Source": "Rotten Tomatoes", "Value": "94%"},
            ]
        }


def configuration():
    return {
        "images": {
            "secure_base_url": "https://image.tmdb.example/t/p/",
            "poster_sizes": ["w500"],
            "backdrop_sizes": ["w1280"],
            "profile_sizes": ["w185"],
        }
    }


def test_tv_hero_prefers_latest_season_trailer_and_enriches_ratings():
    tmdb = FakeTmdb(
        {
            "/tv/42": {
                "id": 42,
                "created_by": [{"name": "Ada Writer"}],
                "seasons": [
                    {"season_number": 1, "air_date": "2024-01-01"},
                    {"season_number": 5, "air_date": "2026-08-01"},
                ],
                "external_ids": {"imdb_id": "tt1234567"},
                "credits": {"crew": []},
                "videos": {
                    "results": [
                        {
                            "site": "YouTube",
                            "type": "Trailer",
                            "key": "season-one",
                            "name": "Official Season 1 Trailer",
                            "official": True,
                            "published_at": "2024-01-01T00:00:00Z",
                        }
                    ]
                },
            },
            "/tv/42/season/5/videos": {
                "results": [
                    {
                        "site": "YouTube",
                        "type": "Trailer",
                        "key": "season-five",
                        "name": "Season 5 Official Trailer",
                        "official": True,
                        "published_at": "2026-07-20T00:00:00Z",
                    }
                ]
            },
        }
    )
    result = asyncio.run(HomepageExperienceService(tmdb, FakeOmdb()).hero("tv", 42))
    assert result.trailer is not None
    assert result.trailer.youtube_key == "season-five"
    assert result.trailer.season_number == 5
    assert result.writers == ["Ada Writer"]
    assert [(rating.source, rating.display_value) for rating in result.ratings] == [
        ("imdb", "8.2/10"),
        ("rotten_tomatoes", "94%"),
    ]


def test_genres_merge_movie_and_tv_authority():
    tmdb = FakeTmdb(
        {
            "/genre/movie/list": {"genres": [{"id": 18, "name": "Drama"}, {"id": 28, "name": "Action"}]},
            "/genre/tv/list": {"genres": [{"id": 18, "name": "Drama"}, {"id": 10765, "name": "Sci-Fi & Fantasy"}]},
        }
    )
    result = asyncio.run(HomepageExperienceService(tmdb).genres())
    drama = next(item for item in result.genres if item.slug == "drama")
    assert drama.movie_provider_id == 18
    assert drama.tv_provider_id == 18
    assert drama.future_path == "/genre/drama"


def test_genre_art_is_taken_from_a_matching_title_not_the_genre_name():
    tmdb = FakeTmdb({
        "/genre/movie/list": {"genres": [{"id": 18, "name": "Drama"}]},
        "/genre/tv/list": {"genres": []},
        "/configuration": configuration(),
        "/discover/movie": {"results": [{"id": 14, "poster_path": "/drama.jpg", "genre_ids": [18]}]},
        "/discover/tv": {"results": []},
    })
    result = asyncio.run(HomepageExperienceService(tmdb).genres())
    assert result.genres[0].poster_url == "https://image.tmdb.example/t/p/w500/drama.jpg"


def test_search_carries_future_route_without_navigating():
    tmdb = FakeTmdb(
        {
            "/configuration": configuration(),
            "/search/multi": {
                "results": [
                    {
                        "id": 7,
                        "media_type": "movie",
                        "title": "Seven",
                        "poster_path": "/seven.jpg",
                        "backdrop_path": "/seven-bg.jpg",
                        "genre_ids": [18, 80],
                    },
                    {
                        "id": 9,
                        "media_type": "person",
                        "name": "Actor Example",
                        "profile_path": "/actor.jpg",
                        "known_for_department": "Acting",
                    },
                ]
            },
        }
    )
    result = asyncio.run(HomepageExperienceService(tmdb).search("sev"))
    assert result.suggestions[0].future_path == "/title/movie/7"
    assert result.suggestions[1].future_path == "/person/9"


def test_kenyan_rail_combines_and_deduplicates_sources():
    payload_movie = {
        "results": [
            {
                "id": 1,
                "title": "Nairobi Story",
                "poster_path": "/n.jpg",
                "backdrop_path": "/n-bg.jpg",
                "popularity": 20,
            }
        ]
    }
    payload_tv = {
        "results": [
            {
                "id": 2,
                "name": "Swahili Show",
                "poster_path": "/s.jpg",
                "backdrop_path": "/s-bg.jpg",
                "popularity": 30,
            }
        ]
    }
    tmdb = FakeTmdb(
        {
            "/configuration": configuration(),
            "/discover/movie": payload_movie,
            "/discover/tv": payload_tv,
        }
    )
    result = asyncio.run(HomepageExperienceService(tmdb).rail("kenyan-stories"))
    assert result.title == "Kenyan Stories"
    assert [item.provider_id for item in result.items] == [2, 1]
    assert result.items[0].future_path == "/title/tv/2"


def test_tv_hero_series_fallback_rejects_wrong_season_and_stale_video():
    tmdb = FakeTmdb(
        {
            "/tv/77": {
                "id": 77,
                "created_by": [],
                "seasons": [
                    {"season_number": 4, "air_date": "2025-01-01"},
                    {"season_number": 5, "air_date": "2026-08-01"},
                ],
                "external_ids": {},
                "credits": {"crew": []},
                "videos": {
                    "results": [
                        {
                            "site": "YouTube",
                            "type": "Trailer",
                            "key": "wrong-season",
                            "name": "Season 1 Official Trailer",
                            "official": True,
                            "published_at": "2024-01-01T00:00:00Z",
                        },
                        {
                            "site": "YouTube",
                            "type": "Trailer",
                            "key": "stale-general",
                            "name": "Official Trailer",
                            "official": True,
                            "published_at": "2024-01-01T00:00:00Z",
                        },
                        {
                            "site": "YouTube",
                            "type": "Trailer",
                            "key": "current-general",
                            "name": "Official Trailer",
                            "official": True,
                            "published_at": "2026-07-25T00:00:00Z",
                        },
                    ]
                },
            },
            "/tv/77/season/5/videos": {"results": []},
        }
    )

    result = asyncio.run(HomepageExperienceService(tmdb).hero("tv", 77))

    assert result.trailer is not None
    assert result.trailer.youtube_key == "current-general"
