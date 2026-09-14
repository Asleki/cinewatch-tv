from __future__ import annotations

import asyncio

from cinewatch_api.external.service import ExternalDataService


class FakeWatchmode:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    async def get_json(self, path: str, *, params=None):
        self.calls.append((path, dict(params or {})))
        return self.payload


class FakeKinoCheck:
    def __init__(self, payload):
        self.payload = payload

    async def get_json(self, path: str, *, params=None):
        assert path in {"/trailers/latest", "/trailers/trending"}
        return self.payload


class FakeLyrics:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    async def search(self, term: str, artist: str):
        self.calls.append((term, artist))
        return self.payload


class FakeScreenplay:
    def __init__(self, rows):
        self.rows = rows
        self.calls = []

    async def search_title(self, title: str):
        self.calls.append(title)
        return self.rows


def test_watchmode_uses_exact_tmdb_identity_and_region() -> None:
    gateway = FakeWatchmode([
        {"source_id": 203, "name": "Example Stream", "type": "sub", "region": "KE", "web_url": "https://example.test/watch"}
    ])
    result = asyncio.run(ExternalDataService(watchmode=gateway).where_to_watch("movie", 278, region="ke"))
    assert gateway.calls == [("/title/movie-278/sources/", {"regions": "KE"})]
    assert result.tmdb_id == 278
    assert result.media_type == "movie"
    assert [item.name for item in result.sources] == ["Example Stream"]


def test_watchmode_rejects_non_https_handoffs() -> None:
    gateway = FakeWatchmode([
        {"source_id": 1, "name": "Unsafe", "type": "free", "region": "US", "web_url": "http://example.test/watch"}
    ])
    result = asyncio.run(ExternalDataService(watchmode=gateway).where_to_watch("tv", 1396))
    assert result.sources[0].web_url is None


def test_kinocheck_preserves_connected_tmdb_identity() -> None:
    payload = {
        "trailers": [
            {
                "id": "4ghv",
                "youtube_video_id": "EJJedP2_7_k",
                "youtube_thumbnail": "https://img.youtube.com/example.jpg",
                "title": "Official Trailer",
                "language": "en",
                "categories": ["Trailer"],
                "resource": {"type": "movie", "tmdb_id": 299534, "title": "Avengers: Endgame"},
            }
        ],
        "_metadata": {"page": 1, "total_pages": 3, "total_count": 51},
    }
    result = asyncio.run(ExternalDataService(kinocheck=FakeKinoCheck(payload)).trailer_library())
    assert result.total_pages == 3
    assert result.total_results == 51
    assert result.trailers[0].tmdb_id == 299534
    assert result.trailers[0].media_type == "movie"


def test_lyrics_requires_exact_song_and_artist() -> None:
    gateway = FakeLyrics({
        "result": [
            {"song": "Moonlight", "artist": "Correct Artist", "song-link": "https://lyrics.example/correct"},
            {"song": "Moonlight", "artist": "Different Artist", "song-link": "https://lyrics.example/wrong"},
        ]
    })
    result = asyncio.run(ExternalDataService(lyrics=gateway).lyrics_lookup("Moonlight", "Correct Artist"))
    assert result.resolved is True
    assert result.match is not None
    assert result.match.artist == "Correct Artist"
    assert result.match.song_url == "https://lyrics.example/correct"


def test_lyrics_same_name_without_artist_identity_is_unresolved() -> None:
    gateway = FakeLyrics({
        "result": [
            {"song": "Moonlight", "artist": "Artist One"},
            {"song": "Moonlight", "artist": "Artist Two"},
        ]
    })
    result = asyncio.run(ExternalDataService(lyrics=gateway).lyrics_lookup("Moonlight", "Unknown Artist"))
    assert result.resolved is False
    assert result.ambiguous is False
    assert result.candidate_count == 0


def test_lyrics_duplicate_exact_identities_are_ambiguous_not_guessed() -> None:
    gateway = FakeLyrics({
        "result": [
            {"song": "Moonlight", "artist": "Same Artist", "album": "Album One"},
            {"song": "Moonlight", "artist": "Same Artist", "album": "Album Two"},
        ]
    })
    result = asyncio.run(ExternalDataService(lyrics=gateway).lyrics_lookup("Moonlight", "Same Artist"))
    assert result.resolved is False
    assert result.ambiguous is True
    assert result.candidate_count == 2


def test_screenplay_requires_exact_title() -> None:
    rows = [
        {"type": "script_metadata", "scriptId": "a", "title": "The Matrix", "year": 1999, "scriptUrl": "https://scripts.example/matrix"},
        {"type": "script_metadata", "scriptId": "b", "title": "Matrix Reloaded", "year": 2003},
        {"type": "script_chunk", "scriptId": "a", "title": "The Matrix", "chunkIndex": 0, "chunkText": "FADE IN..."},
    ]
    result = asyncio.run(ExternalDataService(screenplay=FakeScreenplay(rows)).script_lookup("The Matrix", year=1999))
    assert result.resolved is True
    assert result.match is not None
    assert result.match.title == "The Matrix"
    assert result.match.excerpt == "FADE IN..."


def test_screenplay_year_is_hard_identity_constraint() -> None:
    rows = [
        {"type": "script_metadata", "scriptId": "a", "title": "Example", "year": 1999},
    ]
    result = asyncio.run(ExternalDataService(screenplay=FakeScreenplay(rows)).script_lookup("Example", year=2026))
    assert result.resolved is False
    assert result.candidate_count == 0


def test_screenplay_multiple_exact_matches_are_ambiguous() -> None:
    rows = [
        {"type": "script_metadata", "scriptId": "a", "title": "Example", "year": 2026},
        {"type": "script_metadata", "scriptId": "b", "title": "Example", "year": 2026},
    ]
    result = asyncio.run(ExternalDataService(screenplay=FakeScreenplay(rows)).script_lookup("Example", year=2026))
    assert result.resolved is False
    assert result.ambiguous is True
    assert result.candidate_count == 2


def test_lyrics_album_disambiguates_duplicate_song_artist_releases() -> None:
    gateway = FakeLyrics({
        "result": [
            {"song": "Forever Young", "artist": "Alphaville", "album": "Forever Young", "song-link": "https://lyrics.example/original"},
            {"song": "Forever Young", "artist": "Alphaville", "album": "Best Of", "song-link": "https://lyrics.example/best-of"},
        ]
    })
    result = asyncio.run(
        ExternalDataService(lyrics=gateway).lyrics_lookup(
            "Forever Young", "Alphaville", album="Forever Young"
        )
    )
    assert result.resolved is True
    assert result.match is not None
    assert result.match.album == "Forever Young"


def test_lyrics_duplicate_rows_with_same_provider_song_url_collapse_safely() -> None:
    gateway = FakeLyrics({
        "result": [
            {"song": "Moonlight", "artist": "Same Artist", "album": "Album One", "song-link": "https://lyrics.example/moonlight"},
            {"song": "Moonlight", "artist": "Same Artist", "album": "Compilation", "song-link": "https://lyrics.example/moonlight"},
        ]
    })
    result = asyncio.run(ExternalDataService(lyrics=gateway).lyrics_lookup("Moonlight", "Same Artist"))
    assert result.resolved is True
    assert result.match is not None
    assert result.match.song_url == "https://lyrics.example/moonlight"


def test_screenplay_unique_exact_title_may_resolve_when_provider_omits_optional_year() -> None:
    rows = [
        {"type": "script_metadata", "scriptId": "a", "title": "The Matrix", "year": None},
        {"type": "script_chunk", "scriptId": "a", "title": "The Matrix", "chunkIndex": 1, "chunkText": "FADE IN..."},
    ]
    result = asyncio.run(ExternalDataService(screenplay=FakeScreenplay(rows)).script_lookup("The Matrix", year=1999))
    assert result.resolved is True
    assert result.match is not None
    assert result.match.title == "The Matrix"
    assert result.match.year is None


def test_screenplay_provider_year_conflict_still_rejects_exact_title() -> None:
    rows = [
        {"type": "script_metadata", "scriptId": "a", "title": "Example", "year": 1999},
    ]
    result = asyncio.run(ExternalDataService(screenplay=FakeScreenplay(rows)).script_lookup("Example", year=2026))
    assert result.resolved is False
    assert result.candidate_count == 0


def test_lyrics_distinct_provider_song_urls_remain_candidates_not_guessed() -> None:
    gateway = FakeLyrics({"result": [
        {"song": "Forever Young", "artist": "Alphaville", "album": "Forever Young", "song-link": "https://www.lyrics.com/lyric/30312258/Alphaville/Forever+Young"},
        {"song": "Forever Young", "artist": "Alphaville", "album": "Forever Young", "song-link": "https://www.lyrics.com/lyric/28827950/Alphaville/Forever+Young"},
    ]})
    result = asyncio.run(ExternalDataService(lyrics=gateway).lyrics_lookup("Forever Young", "Alphaville", album="Forever Young"))
    assert result.resolved is False
    assert result.ambiguous is True
    assert result.candidate_count == 2
    assert len(result.candidates) == 2


def test_lyrics_explicit_provider_reference_resolves_one_ambiguous_candidate() -> None:
    selected_url = "https://www.lyrics.com/lyric/28827950/Alphaville/Forever+Young"
    gateway = FakeLyrics({"result": [
        {"song": "Forever Young", "artist": "Alphaville", "album": "Forever Young", "song-link": "https://www.lyrics.com/lyric/30312258/Alphaville/Forever+Young"},
        {"song": "Forever Young", "artist": "Alphaville", "album": "Forever Young", "song-link": selected_url},
    ]})
    result = asyncio.run(ExternalDataService(lyrics=gateway).lyrics_lookup("Forever Young", "Alphaville", album="Forever Young", reference_url=selected_url))
    assert result.resolved is True
    assert result.match is not None
    assert result.match.song_url == selected_url


def test_lyrics_invalid_reference_url_is_rejected() -> None:
    gateway = FakeLyrics({"result": []})
    try:
        asyncio.run(ExternalDataService(lyrics=gateway).lyrics_lookup("Forever Young", "Alphaville", reference_url="http://example.test/not-https"))
    except ValueError as exc:
        assert "HTTPS" in str(exc)
    else:
        raise AssertionError("non-HTTPS lyrics reference should be rejected")
