#!/usr/bin/env python
"""Sanitized STANDS4 Lyrics identity diagnostic.

Purpose:
- show only candidates that exactly match:
    song   = Forever Young
    artist = Alphaville
    album  = Forever Young
- expose safe provider object links/IDs needed to determine whether the
  remaining ambiguity is duplicate provider rows or genuinely distinct objects.

Never prints credentials or lyrics text.
"""

from __future__ import annotations

import asyncio
import re
import unicodedata
from collections import Counter
from urllib.parse import urlparse

from cinewatch_api.providers.stands4 import Stands4LyricsClient
from cinewatch_api.settings import Settings


TARGET_SONG = "Forever Young"
TARGET_ARTIST = "Alphaville"
TARGET_ALBUM = "Forever Young"


def identity(value: object) -> str:
    text = value.strip() if isinstance(value, str) else ""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", ascii_text.casefold()).strip()


def text(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def safe_https(value: object) -> str:
    raw = text(value)
    if not raw:
        return ""
    parsed = urlparse(raw)
    if parsed.scheme != "https" or not parsed.netloc:
        return ""
    return raw


def object_key(url: str) -> str:
    if not url:
        return "<missing>"
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    tail = path.rsplit("/", 1)[-1] if path else ""
    return tail or path or url


async def main() -> int:
    settings = Settings()
    client = Stands4LyricsClient(
        user_id=settings.stands4_lyrics_user_id,
        token=settings.stands4_lyrics_token,
    )

    payload = await client.search(TARGET_SONG, TARGET_ARTIST)
    raw = payload.get("result")
    if isinstance(raw, dict):
        rows = [raw]
    elif isinstance(raw, list):
        rows = [row for row in raw if isinstance(row, dict)]
    else:
        alt = payload.get("results")
        rows = [row for row in alt if isinstance(row, dict)] if isinstance(alt, list) else []

    exact = []
    for row in rows:
        song = text(row.get("song")) or text(row.get("title")) or text(row.get("term"))
        artist = text(row.get("artist")) or text(row.get("artist_name"))
        album = text(row.get("album"))
        if identity(song) != identity(TARGET_SONG):
            continue
        if identity(artist) != identity(TARGET_ARTIST):
            continue
        if identity(album) != identity(TARGET_ALBUM):
            continue

        song_url = (
            safe_https(row.get("song-link"))
            or safe_https(row.get("song_link"))
            or safe_https(row.get("url"))
        )
        artist_url = safe_https(row.get("artist-link")) or safe_https(row.get("artist_link"))
        album_url = safe_https(row.get("album-link")) or safe_https(row.get("album_link"))

        exact.append(
            {
                "song": song,
                "artist": artist,
                "album": album,
                "song_url": song_url,
                "song_object": object_key(song_url),
                "artist_url": artist_url,
                "album_url": album_url,
            }
        )

    print("=== STANDS4 FINAL EXACT CANDIDATES ===")
    print(f"total_provider_rows={len(rows)}")
    print(f"exact_song_artist_album_rows={len(exact)}")
    print()

    for idx, row in enumerate(exact, start=1):
        print(f"{idx:02d}. song={row['song']!r}")
        print(f"    artist={row['artist']!r}")
        print(f"    album={row['album']!r}")
        print(f"    song_object={row['song_object']!r}")
        print(f"    song_url={row['song_url']!r}")
        print(f"    artist_url={row['artist_url']!r}")
        print(f"    album_url={row['album_url']!r}")

    print()
    song_urls = [row["song_url"] for row in exact if row["song_url"]]
    object_keys = [row["song_object"] for row in exact if row["song_object"] != "<missing>"]

    print("=== DEDUPLICATION SUMMARY ===")
    print(f"rows_with_song_url={len(song_urls)}")
    print(f"unique_song_urls={len(set(song_urls))}")
    print(f"unique_song_objects={len(set(object_keys))}")

    if song_urls:
        print("song_url_counts:")
        for url, count in Counter(song_urls).most_common():
            print(f"  {count}x  {url}")

    if not exact:
        print("DECISION_HINT=no exact song+artist+album candidate exists")
    elif len(set(song_urls)) == 1 and len(song_urls) == len(exact):
        print("DECISION_HINT=all exact rows point to one canonical song URL; deterministic collapse is safe")
    elif len(set(object_keys)) == 1 and len(object_keys) == len(exact):
        print("DECISION_HINT=all exact rows share one provider song object; normalize URL variants before collapse")
    else:
        print("DECISION_HINT=multiple provider song objects remain; do not auto-select")

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
