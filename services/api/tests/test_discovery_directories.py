"""The new directories keep provider identities, scopes, and playable videos exact."""
import asyncio
from cinewatch_api.catalog.directories import DirectoryService
from cinewatch_api.catalog.trailer_library import TrailerLibraryService

CONFIG = {"images": {"secure_base_url": "https://image.tmdb.org/t/p/", "poster_sizes": ["w342"], "backdrop_sizes": ["w780"], "profile_sizes": ["w185"]}}

class FakeTmdb:
    def __init__(self, payloads):
        self.payloads = payloads
        self.calls = []
    async def get_json(self, path, *, params=None):
        self.calls.append((path, params or {}))
        return self.payloads[path]

def test_people_keep_search_identity_and_do_not_infer_country():
    fake = FakeTmdb({"/configuration": CONFIG, "/person/popular": {"total_pages": 3, "results": [
        {"id": 31, "name": "Example Performer", "known_for_department": "Acting", "profile_path": None},
        {"id": 42, "name": "Example Writer", "known_for_department": "Writing", "profile_path": "/writer.jpg"},
    ]}})
    payload = asyncio.run(DirectoryService(fake).people(department="Writing"))
    assert [item.future_path for item in payload.items] == ["/person/42"]
    assert payload.items[0].profile_url
    assert payload.total_pages == 3

def test_network_is_series_only_and_company_uses_both_discover_scopes():
    fake = FakeTmdb({"/configuration": CONFIG, "/network/9": {"id": 9, "name": "Network Nine", "logo_path": None},
        "/discover/tv": {"total_results": 12, "results": [{"id": 72, "name": "Series", "backdrop_path": None}]}})
    result = asyncio.run(DirectoryService(fake).organization("network", 9))
    assert result.movie_count is None and result.series_count == 12
    assert result.backdrop_title_id == 72 and result.backdrop_url is None
    assert [path for path, _ in fake.calls if path.startswith("/discover/")] == ["/discover/tv"]
    assert fake.calls[-1][1]["with_networks"] == 9

def test_trailer_cards_require_youtube_and_title_link_and_filter_video_language():
    fake = FakeTmdb({"/configuration": CONFIG,
        "/discover/movie": {"total_pages": 2, "results": [{"id": 100, "title": "The Film", "release_date": "2025-01-01", "poster_path": None, "genre_ids": [80]}]},
        "/movie/100/videos": {"results": [
            {"site": "YouTube", "key": "es123", "type": "Trailer", "iso_639_1": "es", "name": "Spanish trailer"},
            {"site": "Vimeo", "key": "en123", "type": "Trailer", "iso_639_1": "en"},
        ]}})
    result = asyncio.run(TrailerLibraryService(fake).browse(media_type="movie", video_language="es"))
    assert result.has_more and len(result.items) == 1
    from urllib.parse import parse_qs, urlsplit
    route = urlsplit(result.items[0].future_path)
    assert route.path == "/title/movie/100/trailers"
    assert parse_qs(route.query) == {"video_key": ["es123"], "video_language": ["es"], "video_type": ["Trailer"]}
    assert result.items[0].video_language == "es"
