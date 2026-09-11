#!/usr/bin/env python3
"""Run an explicit local-only live probe against a configured provider."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICE_ROOT = ROOT / "services/api"
sys.path.insert(0, str(SERVICE_ROOT))

from cinewatch_api.providers.errors import ProviderError  # noqa: E402
from cinewatch_api.providers.omdb import OmdbClient  # noqa: E402
from cinewatch_api.providers.tmdb import TmdbClient  # noqa: E402
from cinewatch_api.settings import Settings  # noqa: E402


async def probe_tmdb(settings: Settings) -> None:
    payload = await TmdbClient(api_key=settings.tmdb_api_key).configuration()
    images = payload.get("images")
    if not isinstance(images, dict):
        raise RuntimeError("TMDb configuration probe returned no image configuration.")
    print("PASS  TMDb authenticated provider probe")
    print("PASS  TMDb image configuration available")


async def probe_omdb(settings: Settings, imdb_id: str) -> None:
    payload = await OmdbClient(api_key=settings.omdb_api_key).lookup_imdb(imdb_id)
    if payload.get("imdbID") != imdb_id:
        raise RuntimeError("OMDb probe returned an unexpected IMDb identity.")
    print("PASS  OMDb authenticated provider probe")
    print(f"PASS  OMDb identity lookup {imdb_id}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("provider", choices=("tmdb", "omdb"))
    parser.add_argument("--imdb-id", default="tt0111161")
    args = parser.parse_args()

    settings = Settings()
    try:
        if args.provider == "tmdb":
            asyncio.run(probe_tmdb(settings))
        else:
            asyncio.run(probe_omdb(settings, args.imdb_id))
    except (ProviderError, RuntimeError, ValueError) as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
