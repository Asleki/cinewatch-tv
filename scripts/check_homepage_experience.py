#!/usr/bin/env python3
"""Static R3 interaction-policy gate. Browser qualification remains a separate authority."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = (
    "apps/web/src/components/home/HomepageExperience.tsx",
    "apps/web/src/components/site/SiteFrame.tsx",
    "apps/web/src/components/site/UnderDevelopmentPanel.tsx",
    "apps/web/src/components/site/LiveDataFailure.tsx",
    "apps/web/src/app/under-development/[feature]/page.tsx",
    "apps/web/src/app/news/page.tsx",
    "apps/web/src/app/contact/page.tsx",
    "apps/web/src/app/voice-lab/page.tsx",
    "apps/web/src/components/voice/VoiceLab.tsx",
    "services/api/cinewatch_api/api/v1/search.py",
    "services/api/cinewatch_api/api/v1/news.py",
    "services/api/cinewatch_api/api/v1/voice.py",
)


def fail(message: str) -> None:
    print(f"FAIL  {message}", file=sys.stderr)
    raise SystemExit(1)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    if missing:
        fail("missing R3 interaction paths: " + ", ".join(missing))
    print("PASS  R3 interaction source paths")

    frame = read("apps/web/src/components/site/SiteFrame.tsx")
    for token in (
        'href: "/"',
        'href: "/under-development/stream-now"',
        'href: "/discover/trending"',
        'href: "/genres"',
        'href: "/cinema-guide"',
        'router.push("/voice-lab")',
        '/api/cinewatch/search?q=',
        '.slice(0, 5)',
        'cinewatch-startup-ready-v1',
        'window.sessionStorage.setItem(startupKey, "1")',
        '}, 3000);',
        '["News", "/news"]',
        '["Contact", "/contact"]',
    ):
        if token not in frame:
            fail(f"site frame missing R3 authority token: {token}")
    for forbidden in ("SpeechRecognition", "webkitSpeechRecognition", 'href="#stream-now"', 'href="#discover"', 'aria-disabled="true"'):
        if forbidden in frame:
            fail(f"obsolete/dead global interaction remains: {forbidden}")
    print("PASS  route-aware navigation, five-result search, readiness and NexVox routing")

    homepage = read("apps/web/src/components/home/HomepageExperience.tsx")
    for token in (
        'title="Stream Now"',
        '/under-development/stream-now',
        'title="Trending Now"',
        'title="Popular Movies"',
        'title="Popular TV Shows"',
        '<LazyRail slug="k-drama" />',
        '<LazyRail slug="kenyan-stories" />',
        '<LazyRail slug="tyler-perry" />',
        'href={`/title/${item.media_type}/${item.provider_id}/trailers`}',
        'Stream Now is under development',
        'state === "empty"',
        'Open CineWatch News',
    ):
        if token not in homepage:
            fail(f"homepage missing R3 behavior token: {token}")
    for forbidden in ("stream-placeholder-", "Coming to Stream Now", "Rights-cleared playback will appear here.", "aria-disabled=", "youtube-nocookie.com/embed"):
        if forbidden in homepage:
            fail(f"obsolete homepage behavior remains: {forbidden}")
    print("PASS  no fake Stream cards, governed trailer routes, explicit error/empty behavior")

    voice = read("apps/web/src/components/voice/VoiceLab.tsx")
    for token in ("getUserMedia", "encodeWav", "audio/wav", "Accept recording", "consentVersion", "/api/cinewatch/voice-lab/samples"):
        if token not in voice:
            fail(f"NexVox Voice Lab missing governed capture token: {token}")
    if voice.find("getUserMedia") < voice.find("if (!consented)"):
        fail("microphone capture appears before explicit consent guard")
    print("PASS  NexVox consent/WAV/local-preview/staging boundary")

    browser_source = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "apps/web/src").rglob("*.tsx"))
    for forbidden in ("api.themoviedb.org", "www.omdbapi.com", "newsapi.org", "TMDB_API_KEY", "OMDB_API_KEY", "NEWS_API_KEY"):
        if forbidden in browser_source:
            fail(f"provider authority or credential leaked into browser source: {forbidden}")
    print("PASS  browser remains provider-secret neutral")

    schema = json.loads((ROOT / "packages/contracts/openapi/cinewatch-v1.openapi.json").read_text(encoding="utf-8"))
    for path in ("/api/v1/search", "/api/v1/news", "/api/v1/voice-lab/samples"):
        if path not in schema.get("paths", {}):
            fail(f"canonical OpenAPI missing R3 path: {path}")
    print("PASS  R3 search/news/voice paths present in canonical OpenAPI")

    print("PASS  R3 static interaction policy (does not claim browser qualification)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
