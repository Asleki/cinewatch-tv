#!/usr/bin/env python3
"""Verify built Next.js library links against a real API with deterministic TMDb fixtures.

Run after the production build. No provider credentials or external services are used.
The build must use the repository's default local API URL (127.0.0.1:8000).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlsplit
from urllib.request import urlopen

import uvicorn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services/api/tests"))
from test_trailer_navigation import NavigationTmdb, video  # noqa: E402
from cinewatch_api.api.v1 import catalog, trailer_library  # noqa: E402
from cinewatch_api.application import create_app  # noqa: E402
from cinewatch_api.catalog.service import CatalogService  # noqa: E402
from cinewatch_api.contracts.catalog import CatalogTitleResponse  # noqa: E402
from cinewatch_api.settings import Settings  # noqa: E402


class FixtureTmdb:
    def __init__(self):
        self.spanish = NavigationTmdb([video("spanish-only", language="es")], total_pages=1001)
        self.clips = NavigationTmdb(
            [video(f"trailer-{i}") for i in range(20)] + [video("selected-clip", "Clip")],
        )

    async def get_json(self, path, *, params=None):
        if path == "/discover/movie":
            return {"total_pages": 1001, "results": [
                {"id": 100, "title": "Spanish-only film"},
                {"id": 101, "title": "Film with twenty trailers and a clip"},
            ]}
        if path == "/movie/101/videos":
            return await self.clips.get_json("/movie/100/videos", params=params)
        return await self.spanish.get_json(path, params=params)


class FixtureCatalog(CatalogService):
    async def title(self, media_type, provider_id, **kwargs):
        return CatalogTitleResponse(provider_id=provider_id, media_type=media_type, title="Fixture title")


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links = []
        self.frames = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag == "iframe" and attrs.get("src"):
            self.frames.append(attrs["src"])


def read(url):
    with urlopen(url, timeout=20) as response:
        assert response.status == 200
        return response.read().decode()


def wait_ready(url, process=None):
    for _ in range(100):
        if process is not None and process.poll() is not None:
            raise RuntimeError("Next.js exited before readiness")
        try:
            read(url)
            return
        except (OSError, TimeoutError):
            time.sleep(0.1)
    raise RuntimeError(f"Runtime did not become ready: {url}")


def main():
    api_port, web_port = 8000, 3111
    for port in (api_port, web_port):
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", port))
    assert (ROOT / "apps/web/.next/BUILD_ID").is_file(), "Run the production build first"
    fake = FixtureTmdb()
    catalog._service = lambda request: FixtureCatalog(fake)
    trailer_library.TmdbClient = lambda **kwargs: fake
    app = create_app(Settings(environment="local", log_level="CRITICAL", _env_file=None))
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=api_port, log_level="critical"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    process = None
    try:
        wait_ready(f"http://127.0.0.1:{api_port}/health")
        with tempfile.TemporaryDirectory(prefix="cwtv-trailer-navigation-") as directory:
            log_path = Path(directory) / "next.log"
            with log_path.open("w") as log:
                process = subprocess.Popen(
                    [os.environ.get("CWTV_WEB_NPM", "npm"), "run", "start", "-w", "@cinewatch/web",
                     "--", "--hostname", "127.0.0.1", "--port", str(web_port)],
                    cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
                )
                web = f"http://127.0.0.1:{web_port}"
                try:
                    wait_ready(web + "/robots.txt", process)
                    for filters, key, title_id in (
                        ("video_language=es&video_type=Trailer", "spanish-only", 100),
                        ("video_type=Clip", "selected-clip", 101),
                    ):
                        page = Page(read(web + "/trailers?media_type=movie&" + filters))
                        route = next(link for link in page.links if
                                     urlsplit(link).path == f"/title/movie/{title_id}/trailers")
                        query = parse_qs(urlsplit(route).query)
                        assert query.get("video_key") == [key], route
                        destination = Page(read(web + route))
                        assert any(urlsplit(src).path == f"/embed/{key}" for src in destination.frames), (
                            f"Card {route} did not render the selected YouTube iframe: {destination.frames}"
                        )
                        print(f"PASS  real Next.js card → title route → verified API → selected iframe: {key}")
                    ordinary = json.loads(read(f"http://127.0.0.1:{api_port}/api/v1/catalog/title/movie/101/videos"))
                    assert len(ordinary["videos"]) == 20
                    assert all(item["youtube_key"] != "selected-clip" for item in ordinary["videos"])
                    for current, allowed in ((499, "500"), (500, None)):
                        page = Page(read(web + f"/trailers?media_type=movie&page={current}"))
                        next_pages = [parse_qs(urlsplit(link).query).get("page", [None])[0]
                                      for link in page.links if urlsplit(link).path == "/trailers"]
                        if allowed:
                            assert allowed in next_pages
                        assert "501" not in next_pages
                        print(f"PASS  real Next.js trailer page {current}: next-page bound")
                except Exception:
                    log.flush()
                    print(log_path.read_text()[-4000:], file=sys.stderr)
                    raise
                finally:
                    if process.poll() is None:
                        os.killpg(process.pid, signal.SIGTERM)
                        process.wait(timeout=10)
    finally:
        server.should_exit = True
        thread.join(timeout=10)
    print("PASS  trailer navigation web/API regression smoke (fixture data; no live-provider claim)")


if __name__ == "__main__":
    main()
