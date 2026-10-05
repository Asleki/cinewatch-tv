from __future__ import annotations

import asyncio

from cinewatch_api.catalog.service import CatalogService


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
                {"Source": "Internet Movie Database", "Value": "8.1/10"},
                {"Source": "Rotten Tomatoes", "Value": "92%"},
            ],
            "Awards": "Won 2 awards.",
            "BoxOffice": "$10,000,000",
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


def test_movie_title_composes_ratings_cast_provider_and_recommendations():
    tmdb = FakeTmdb(
        {
            "/configuration": configuration(),
            "/movie/42": {
                "id": 42,
                "title": "Example Film",
                "release_date": "2026-08-01",
                "runtime": 119,
                "overview": "A test story.",
                "poster_path": "/poster.jpg",
                "backdrop_path": "/backdrop.jpg",
                "vote_average": 7.7,
                "genres": [{"id": 18, "name": "Drama"}],
                "external_ids": {"imdb_id": "tt1234567"},
                "credits": {
                    "cast": [{"id": 7, "name": "Actor Example", "character": "Lead", "profile_path": "/actor.jpg"}],
                    "crew": [{"id": 8, "name": "Writer Example", "department": "Writing", "job": "Writer"}],
                },
                "videos": {"results": [{"site": "YouTube", "type": "Trailer", "key": "trailer-key", "name": "Official Trailer", "official": True, "published_at": "2026-07-01T00:00:00Z"}]},
                "reviews": {"total_results": 1, "results": [{"id": "r1", "author": "Reviewer", "content": "Strong film.", "author_details": {"rating": 8.0}}]},
                "recommendations": {"results": [{"id": 99, "media_type": "movie", "title": "Next Film", "release_date": "2025-01-01", "poster_path": "/next.jpg", "vote_average": 7.2}]},
                "production_companies": [{"id": 3, "name": "Studio", "logo_path": "/studio.png"}],
                "budget": 5000000,
                "revenue": 12000000,
            },
            "/movie/42/watch/providers": {"results": {"KE": {"link": "https://watch.example", "flatrate": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/netflix.png"}]}}},
        }
    )

    result = asyncio.run(CatalogService(tmdb, FakeOmdb()).title("movie", 42, watch_region="KE"))

    assert result.title == "Example Film"
    assert [(rating.source, rating.display_value) for rating in result.ratings] == [
        ("tmdb", "7.7/10"),
        ("imdb", "8.1/10"),
        ("rotten_tomatoes", "92%"),
    ]
    assert result.trailer is not None and result.trailer.youtube_key == "trailer-key"
    assert result.cast[0].future_path == "/person/7"
    assert result.watch_region == "KE"
    assert result.watch_providers[0].name == "Netflix"
    assert result.networks[0].kind == "company"
    assert result.recommendations[0].future_path == "/title/movie/99"
    assert result.awards == "Won 2 awards."


def test_person_uses_popular_credit_backdrop_and_role_identity():
    tmdb = FakeTmdb(
        {
            "/configuration": configuration(),
            "/person/7": {"id": 7, "name": "Actor Example", "biography": "Biography", "known_for_department": "Acting", "profile_path": "/actor.jpg"},
            "/person/7/combined_credits": {"cast": [{"id": 90, "media_type": "tv", "name": "Popular Show", "first_air_date": "2026-01-01", "character": "Hero", "popularity": 80, "poster_path": "/show.jpg", "backdrop_path": "/show-bg.jpg"}]},
        }
    )
    result = asyncio.run(CatalogService(tmdb).person(7))
    assert result.name == "Actor Example"
    assert result.hero_backdrop_url is not None and result.hero_backdrop_url.endswith("/w1280/show-bg.jpg")
    assert result.credits[0].role == "Hero"
    assert result.credits[0].future_path == "/title/tv/90"


def test_kenyan_browse_uses_country_and_swahili_signals():
    tmdb = FakeTmdb({"/configuration": configuration(), "/discover/movie": {"page": 1, "total_pages": 1, "total_results": 1, "results": []}, "/discover/tv": {"page": 1, "total_pages": 1, "total_results": 1, "results": []}})
    asyncio.run(CatalogService(tmdb).browse("collection", "kenyan-stories"))
    calls = [params for path, params in tmdb.calls if path.startswith("/discover/")]
    assert any(params.get("with_origin_country") == "KE" for params in calls)
    assert any(params.get("with_original_language") == "sw" for params in calls)


def test_unknown_genre_is_rejected_instead_of_rendering_fake_empty_collection():
    tmdb = FakeTmdb({
        "/configuration": configuration(),
        "/genre/movie/list": {"genres": [{"id": 18, "name": "Drama"}]},
        "/genre/tv/list": {"genres": [{"id": 18, "name": "Drama"}]},
    })
    try:
        asyncio.run(CatalogService(tmdb).browse("genre", "not-a-real-genre"))
    except ValueError as exc:
        assert "genre" in str(exc).lower()
    else:
        raise AssertionError("unknown genre should be rejected")



def test_unknown_country_is_rejected_instead_of_rendering_fake_collection():
    tmdb = FakeTmdb({"/configuration": configuration()})
    try:
        asyncio.run(CatalogService(tmdb).browse("country", "ZZ"))
    except ValueError as exc:
        assert "country" in str(exc).lower()
    else:
        raise AssertionError("unknown country should be rejected")


def test_country_genre_filter_is_applied_to_both_media_types():
    tmdb = FakeTmdb({
        "/configuration": configuration(),
        "/genre/movie/list": {"genres": [{"id": 80, "name": "Crime"}]},
        "/genre/tv/list": {"genres": [{"id": 80, "name": "Crime"}]},
        "/discover/movie": {"page": 1, "total_pages": 1, "total_results": 0, "results": []},
        "/discover/tv": {"page": 1, "total_pages": 1, "total_results": 0, "results": []},
    })
    result = asyncio.run(CatalogService(tmdb).browse("country", "KE", genre="crime"))
    assert result.genre == "crime"
    discover = [params for path, params in tmdb.calls if path.startswith("/discover/")]
    assert len(discover) == 2
    assert all(params["with_genres"] == 80 and params["with_origin_country"] == "KE" for params in discover)

def test_tv_title_prefers_latest_regular_season_trailer_and_exposes_seasons():
    tmdb = FakeTmdb({
        "/configuration": configuration(),
        "/tv/55": {
            "id": 55,
            "name": "Example Series",
            "first_air_date": "2024-01-01",
            "vote_average": 8.0,
            "genres": [{"id": 18, "name": "Drama"}],
            "external_ids": {},
            "credits": {"cast": [], "crew": []},
            "videos": {"results": [{"site": "YouTube", "type": "Trailer", "key": "old-series", "name": "Season 1 Trailer", "official": True, "published_at": "2024-01-01T00:00:00Z"}]},
            "reviews": {"total_results": 0, "results": []},
            "recommendations": {"results": []},
            "seasons": [{"id": 501, "season_number": 1, "name": "Season 1", "episode_count": 8, "air_date": "2024-01-01"}, {"id": 502, "season_number": 2, "name": "Season 2", "episode_count": 10, "air_date": "2026-01-01"}],
            "networks": [],
        },
        "/tv/55/watch/providers": {"results": {}},
        "/tv/55/season/2/videos": {"results": [{"site": "YouTube", "type": "Trailer", "key": "season-two", "name": "Season 2 Official Trailer", "official": True, "published_at": "2025-12-01T00:00:00Z"}]},
    })
    result = asyncio.run(CatalogService(tmdb).title("tv", 55))
    assert [season.season_number for season in result.seasons] == [1, 2]
    assert result.trailer is not None and result.trailer.youtube_key == "season-two"
    assert result.trailer.season_number == 2


def test_unavailable_rating_values_are_omitted_and_watch_provider_cap_is_bounded():
    providers = []
    for index in range(1, 25):
        providers.append({"provider_id": index, "provider_name": f"Provider {index}", "logo_path": None})
    tmdb = FakeTmdb({
        "/configuration": configuration(),
        "/movie/77": {
            "id": 77,
            "title": "Provider Test",
            "release_date": "2026-01-01",
            "vote_average": 0.0,
            "vote_count": 0,
            "genres": [],
            "external_ids": {"imdb_id": "tt1234567"},
            "credits": {"cast": [], "crew": []},
            "videos": {"results": []},
            "reviews": {"total_results": 0, "results": []},
            "recommendations": {"results": []},
            "production_companies": [],
        },
        "/movie/77/watch/providers": {"results": {"KE": {"flatrate": providers[:12], "rent": providers[12:]}}},
    })

    class UnavailableOmdb:
        async def lookup_imdb(self, imdb_id: str):
            assert imdb_id == "tt1234567"
            return {"Ratings": [{"Source": "Internet Movie Database", "Value": "N/A"}]}

    result = asyncio.run(CatalogService(tmdb, UnavailableOmdb()).title("movie", 77, watch_region="KE"))
    assert result.ratings == []
    assert len(result.watch_providers) == 18


def test_collection_media_type_filter_does_not_return_wrong_feed_type():
    tmdb = FakeTmdb({
        "/configuration": configuration(),
        "/trending/tv/week": {"page": 1, "total_pages": 1, "total_results": 1, "results": []},
    })
    asyncio.run(CatalogService(tmdb).browse("collection", "trending", media_type="tv"))
    discover_calls = [path for path, _ in tmdb.calls if path.startswith("/trending/")]
    assert discover_calls == ["/trending/tv/week"]


def test_title_videos_include_supported_youtube_media_and_rank_official_trailer_first():
    tmdb = FakeTmdb({
        "/movie/42/videos": {
            "results": [
                {"site": "YouTube", "type": "Clip", "key": "clip-key", "name": "Scene Clip", "official": True, "published_at": "2026-06-01T00:00:00Z"},
                {"site": "YouTube", "type": "Trailer", "key": "trailer-key", "name": "Official Trailer", "official": True, "published_at": "2026-07-01T00:00:00Z"},
                {"site": "Vimeo", "type": "Trailer", "key": "ignored", "name": "Vimeo Trailer", "official": True},
            ]
        }
    })
    result = asyncio.run(CatalogService(tmdb).videos("movie", 42))
    assert [video.youtube_key for video in result.videos] == ["trailer-key", "clip-key"]
    assert result.videos[1].video_type == "Clip"


def test_review_contract_exposes_tmdb_provenance():
    tmdb = FakeTmdb({
        "/movie/42/reviews": {
            "page": 1,
            "total_pages": 1,
            "total_results": 1,
            "results": [
                {"id": "review-1", "author": "Reviewer", "content": "Useful review.", "author_details": {"rating": 7.0}}
            ],
        }
    })
    result = asyncio.run(CatalogService(tmdb).reviews("movie", 42))
    assert result.reviews[0].source == "tmdb"
    assert result.reviews[0].source_label == "TMDb"


def test_language_filter_ranks_preferred_language_first_and_keeps_year_hard():
    class FilteringTmdb:
        def __init__(self):
            self.calls = []

        async def get_json(self, path: str, *, params=None):
            params = dict(params or {})
            self.calls.append((path, params))
            if path == "/configuration":
                return configuration()
            assert path == "/discover/movie"
            # Both responses obey the hard 2000 year scope. The preferred request
            # supplies a Swahili title; the broad request supplies another eligible
            # movie which may follow but may not outrank the language match.
            if params.get("with_original_language") == "sw":
                return {
                    "page": 1,
                    "total_pages": 1,
                    "total_results": 1,
                    "results": [{"id": 101, "title": "Swahili First", "release_date": "2000-01-01", "original_language": "sw", "vote_average": 7.0}],
                }
            return {
                "page": 1,
                "total_pages": 1,
                "total_results": 2,
                "results": [
                    {"id": 202, "title": "Eligible Later", "release_date": "2000-02-01", "vote_average": 8.0},
                    {"id": 101, "title": "Swahili First", "release_date": "2000-01-01", "original_language": "sw", "vote_average": 7.0},
                ],
            }

    tmdb = FilteringTmdb()
    result = asyncio.run(
        CatalogService(tmdb).browse(
            "collection", "popular-movies", media_type="movie", year=2000, language="sw"
        )
    )
    assert [item.title for item in result.items] == ["Swahili First", "Eligible Later"]
    discover_calls = [params for path, params in tmdb.calls if path == "/discover/movie"]
    assert len(discover_calls) == 2
    assert all(params.get("primary_release_year") == 2000 for params in discover_calls)
    assert discover_calls[0].get("with_original_language") == "sw"
    assert "with_original_language" not in discover_calls[1]


def test_discovery_scope_rechecks_provider_language_and_year_anomalies():
    class AnomalousTmdb:
        async def get_json(self, path: str, *, params=None):
            params = dict(params or {})
            if path == "/configuration":
                return configuration()
            assert path == "/discover/movie"
            if params.get("with_original_language") == "sw":
                return {
                    "page": 1,
                    "total_pages": 1,
                    "total_results": 3,
                    "results": [
                        {"id": 1, "title": "Correct Swahili", "release_date": "2000-01-02", "original_language": "sw", "vote_average": 7.2},
                        {"id": 2, "title": "Wrong Language", "release_date": "2000-01-03", "original_language": "en", "vote_average": 9.9},
                        {"id": 3, "title": "Wrong Year", "release_date": "2001-01-03", "original_language": "sw", "vote_average": 9.8},
                    ],
                }
            return {
                "page": 1,
                "total_pages": 1,
                "total_results": 3,
                "results": [
                    {"id": 4, "title": "Eligible Fallback", "release_date": "2000-02-01", "original_language": "en", "vote_average": 8.0},
                    {"id": 5, "title": "Fallback Wrong Year", "release_date": "2002-02-01", "original_language": "en", "vote_average": 9.5},
                    {"id": 1, "title": "Correct Swahili", "release_date": "2000-01-02", "original_language": "sw", "vote_average": 7.2},
                ],
            }

    result = asyncio.run(
        CatalogService(AnomalousTmdb()).browse(
            "collection", "popular-movies", media_type="movie", year=2000, language="sw"
        )
    )
    assert [item.title for item in result.items] == ["Correct Swahili", "Eligible Fallback"]
