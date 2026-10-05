"""Exercise library-card navigation through the real title-video API contract."""

from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi.testclient import TestClient

from cinewatch_api.api.v1 import catalog, trailer_library
from cinewatch_api.application import create_app
from cinewatch_api.catalog.service import CatalogService
from cinewatch_api.settings import Settings


class NavigationTmdb:
    def __init__(self, videos, *, media_type="movie", total_pages=501):
        self.videos = videos
        self.media_type = media_type
        self.total_pages = total_pages
        self.calls = []

    async def get_json(self, path, *, params=None):
        params = params or {}
        self.calls.append((path, dict(params)))
        if path == "/configuration":
            return {"images": {"secure_base_url": "https://image.tmdb.org/t/p/"}}
        if path == f"/discover/{self.media_type}":
            return {"total_pages": self.total_pages, "results": [
                {"id": 100, "title": "Example film", "name": "Example series"},
            ]}
        if path == f"/{self.media_type}/100/videos":
            languages = {params.get("language", "en-US").split("-")[0]}
            languages.update(str(params.get("include_video_language", "")).split(","))
            return {"results": [v for v in self.videos if v.get("iso_639_1") in languages]}
        if path == "/tv/100":
            return {"seasons": []}
        raise AssertionError(f"Unexpected upstream request: {path}")


def video(key, kind="Trailer", language="en", site="YouTube"):
    return {"key": key, "name": f"Example {kind}", "type": kind,
            "iso_639_1": language, "site": site, "official": True}


@pytest.fixture
def navigation_client(monkeypatch):
    def make(fake):
        monkeypatch.setattr(trailer_library, "TmdbClient", lambda **kwargs: fake)
        monkeypatch.setattr(catalog, "_service", lambda request: CatalogService(fake))
        settings = Settings(environment="local", log_level="CRITICAL", _env_file=None)
        return TestClient(create_app(settings))
    return make


def follow_card(client, card):
    destination = urlsplit(card["future_path"])
    assert destination.path == f"/title/{card['media_type']}/100/trailers"
    selection = parse_qs(destination.query)
    assert selection["video_key"] == [card["youtube_key"]]
    assert selection["video_language"] == [card["video_language"]]
    assert selection["video_type"] == [card["video_type"]]
    return client.get(f"/api/v1/catalog/title/{card['media_type']}/100/videos", params={
        key: value[0] for key, value in selection.items()
    })


@pytest.mark.parametrize("media_type", ["movie", "tv"])
def test_spanish_only_selected_video_remains_reachable_from_library_card(navigation_client, media_type):
    fake = NavigationTmdb([video("spanish-only", language="es")], media_type=media_type)
    with navigation_client(fake) as client:
        response = client.get("/api/v1/catalog/trailers", params={
            "media_type": media_type, "video_language": "es", "video_type": "Trailer",
        })
        assert response.status_code == 200
        card = response.json()["items"][0]
        selected = follow_card(client, card)
    assert selected.status_code == 200
    assert selected.json()["videos"][0]["youtube_key"] == "spanish-only"
    video_calls = [params for path, params in fake.calls if path.endswith("/videos")]
    assert len(video_calls) == 2
    assert all(params["include_video_language"] == "es" for params in video_calls)


def test_selected_clip_beyond_ordinary_first_twenty_remains_reachable(navigation_client):
    fake = NavigationTmdb([video(f"trailer-{i}") for i in range(20)] + [video("selected-clip", "Clip")])
    with navigation_client(fake) as client:
        ordinary = client.get("/api/v1/catalog/title/movie/100/videos")
        assert len(ordinary.json()["videos"]) == 20
        assert "selected-clip" not in [v["youtube_key"] for v in ordinary.json()["videos"]]
        library = client.get("/api/v1/catalog/trailers", params={"media_type": "movie", "video_type": "Clip"})
        selected = follow_card(client, library.json()["items"][0])
    assert selected.status_code == 200
    assert len(selected.json()["videos"]) == 20
    assert selected.json()["videos"][0]["youtube_key"] == "selected-clip"
    assert selected.json()["videos"][0]["video_type"] == "Clip"


@pytest.mark.parametrize(("page", "expected"), [(499, True), (500, False)])
def test_trailer_next_page_stops_at_cinewatch_bound(navigation_client, page, expected):
    with navigation_client(NavigationTmdb([video("trailer")], total_pages=1001)) as client:
        response = client.get("/api/v1/catalog/trailers", params={"media_type": "movie", "page": page})
    assert response.status_code == 200
    assert response.json()["page"] == page
    assert response.json()["has_more"] is expected


@pytest.mark.parametrize("selection", [
    {"video_key": "not-on-title"},
    {"video_key": "verified", "video_language": "es"},
    {"video_key": "verified", "video_type": "Clip"},
    {"video_key": "non-youtube"},
])
def test_selected_video_must_be_verified_for_title_and_metadata(navigation_client, selection):
    fake = NavigationTmdb([video("verified"), video("non-youtube", site="Vimeo")])
    with navigation_client(fake) as client:
        response = client.get("/api/v1/catalog/title/movie/100/videos", params=selection)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "CATALOG_VIDEO_NOT_FOUND"


def test_page_501_is_rejected_before_upstream_request(navigation_client):
    fake = NavigationTmdb([])
    with navigation_client(fake) as client:
        response = client.get("/api/v1/catalog/trailers", params={"page": 501})
    assert response.status_code == 422
    assert fake.calls == []


def test_selected_record_without_video_name_uses_library_type_fallback(navigation_client):
    record = video("unnamed-clip", "Clip")
    record.pop("name")
    with navigation_client(NavigationTmdb([record])) as client:
        library = client.get("/api/v1/catalog/trailers", params={"media_type": "movie", "video_type": "Clip"})
        selected = follow_card(client, library.json()["items"][0])
    assert selected.status_code == 200
    assert selected.json()["videos"][0]["youtube_key"] == "unnamed-clip"
    assert selected.json()["videos"][0]["name"] == "Clip"
