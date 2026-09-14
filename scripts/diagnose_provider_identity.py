#!/usr/bin/env python
"""Sanitized live identity diagnostics for STANDS4 Lyrics and Apify screenplay.

Prints only safe identity metadata. Never prints credentials, raw screenplay text,
or full provider payloads.
"""

from __future__ import annotations

import asyncio
from collections import Counter

from cinewatch_api.providers.apify import ApifyScreenplayClient
from cinewatch_api.providers.stands4 import Stands4LyricsClient
from cinewatch_api.settings import Settings


def _text(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


async def main() -> int:
    settings = Settings()

    lyrics = Stands4LyricsClient(
        user_id=settings.stands4_lyrics_user_id,
        token=settings.stands4_lyrics_token,
    )
    screenplay = ApifyScreenplayClient(token=settings.apify_api_token)

    print("=== STANDS4 LYRICS SAFE IDENTITY DIAGNOSTIC ===")
    payload = await lyrics.search("Forever Young", "Alphaville")
    raw = payload.get("result")
    if isinstance(raw, dict):
        rows = [raw]
    elif isinstance(raw, list):
        rows = [row for row in raw if isinstance(row, dict)]
    else:
        alt = payload.get("results")
        rows = [row for row in alt if isinstance(row, dict)] if isinstance(alt, list) else []

    print(f"candidate_rows={len(rows)}")
    for index, row in enumerate(rows[:20], start=1):
        song = _text(row.get("song")) or _text(row.get("title")) or _text(row.get("term"))
        artist = _text(row.get("artist")) or _text(row.get("artist_name"))
        album = _text(row.get("album"))
        print(f"{index:02d}. song={song!r} artist={artist!r} album={album!r}")

    print()
    print("=== APIFY SCREENPLAY SAFE IDENTITY DIAGNOSTIC ===")
    rows = await screenplay.search_title("The Matrix")
    counts = Counter(_text(row.get("type")) or "<missing>" for row in rows)
    print("row_types=" + ", ".join(f"{key}:{value}" for key, value in sorted(counts.items())))

    metadata = [row for row in rows if _text(row.get("type")) == "script_metadata"]
    print(f"metadata_rows={len(metadata)}")
    for index, row in enumerate(metadata[:20], start=1):
        print(
            f"{index:02d}. "
            f"title={_text(row.get('title'))!r} "
            f"year={row.get('year')!r} "
            f"source={_text(row.get('source'))!r} "
            f"script_id={_text(row.get('scriptId'))!r} "
            f"has_script_text={row.get('hasScriptText')!r} "
            f"word_count={row.get('wordCount')!r}"
        )

    errors = [row for row in rows if _text(row.get("type")) == "error"]
    print(f"error_rows={len(errors)}")
    for index, row in enumerate(errors[:10], start=1):
        print(
            f"{index:02d}. "
            f"error_type={_text(row.get('errorType'))!r} "
            f"status={_text(row.get('status'))!r} "
            f"retryable={row.get('retryable')!r} "
            f"message={_text(row.get('errorMessage'))!r}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
