"""Identity-safe composition for external CineWatch test-repo data sources."""

from __future__ import annotations

import re
import unicodedata
from typing import Protocol
from urllib.parse import urlparse

from cinewatch_api.contracts.external import (
    ExternalAvailabilityResponse,
    ExternalAvailabilitySource,
    ExternalTrailer,
    ExternalTrailerLibraryResponse,
    LyricsLookupResponse,
    LyricsMatch,
    ScriptLookupResponse,
    ScriptMatch,
)
from cinewatch_api.providers.errors import ProviderResponseError


class WatchmodeGateway(Protocol):
    async def get_json(self, path: str, *, params=None) -> dict[str, object] | list[object]: ...


class KinoCheckGateway(Protocol):
    async def get_json(self, path: str, *, params=None) -> dict[str, object] | list[object]: ...


class LyricsGateway(Protocol):
    async def search(self, term: str, artist: str) -> dict[str, object]: ...


class ScreenplayGateway(Protocol):
    async def search_title(self, title: str) -> list[dict[str, object]]: ...


class ExternalDataService:
    def __init__(
        self,
        *,
        watchmode: WatchmodeGateway | None = None,
        kinocheck: KinoCheckGateway | None = None,
        lyrics: LyricsGateway | None = None,
        screenplay: ScreenplayGateway | None = None,
    ) -> None:
        self._watchmode = watchmode
        self._kinocheck = kinocheck
        self._lyrics = lyrics
        self._screenplay = screenplay

    async def where_to_watch(
        self, media_type: str, tmdb_id: int, *, region: str = "US"
    ) -> ExternalAvailabilityResponse:
        if media_type not in {"movie", "tv"}:
            raise ValueError("media_type must be movie or tv")
        if tmdb_id <= 0:
            raise ValueError("tmdb_id must be positive")
        if self._watchmode is None:
            raise RuntimeError("Watchmode gateway is unavailable")
        identity = f"{media_type}-{tmdb_id}"
        payload = await self._watchmode.get_json(
            f"/title/{identity}/sources/", params={"regions": region.upper()}
        )
        if not isinstance(payload, list):
            raise ProviderResponseError(
                provider="watchmode",
                code="WATCHMODE_SOURCES_INVALID",
                message="Watchmode returned an invalid sources payload.",
            )
        sources: list[ExternalAvailabilitySource] = []
        seen: set[tuple[object, ...]] = set()
        for raw in payload:
            if not isinstance(raw, dict):
                continue
            name = self._text(raw.get("name"))
            if not name:
                continue
            source_id = self._positive_int(raw.get("source_id"))
            source_type = self._text(raw.get("type")) or self._text(raw.get("source_type"))
            source_region = self._text(raw.get("region")) or region.upper()
            web_url = self._safe_https_url(raw.get("web_url")) or self._safe_https_url(raw.get("url"))
            fmt = self._text(raw.get("format"))
            price = self._number(raw.get("price"))
            key = (source_id, name.casefold(), source_type, source_region, web_url, fmt, price)
            if key in seen:
                continue
            seen.add(key)
            sources.append(
                ExternalAvailabilitySource(
                    source_id=source_id,
                    name=name,
                    source_type=source_type,
                    region=source_region,
                    web_url=web_url,
                    format=fmt,
                    price=price,
                )
            )
        return ExternalAvailabilityResponse(
            media_type=media_type,  # type: ignore[arg-type]
            tmdb_id=tmdb_id,
            region=region.upper(),
            sources=sources,
        )

    async def trailer_library(self, *, page: int = 1, latest: bool = True) -> ExternalTrailerLibraryResponse:
        if self._kinocheck is None:
            raise RuntimeError("KinoCheck gateway is unavailable")
        page = max(1, page)
        path = "/trailers/latest" if latest else "/trailers/trending"
        payload = await self._kinocheck.get_json(path, params={"language": "en", "page": page, "limit": 24})
        metadata: dict[str, object] = {}
        raw_items: object = payload
        if isinstance(payload, dict):
            metadata = payload.get("_metadata") if isinstance(payload.get("_metadata"), dict) else {}
            raw_items = payload.get("trailers") or payload.get("results") or payload.get("items") or []
        rows = raw_items if isinstance(raw_items, list) else []
        trailers: list[ExternalTrailer] = []
        seen: set[str] = set()
        for raw in rows:
            if not isinstance(raw, dict):
                continue
            video_id = self._text(raw.get("youtube_video_id"))
            title = self._text(raw.get("title"))
            provider_id = self._text(raw.get("id"))
            if not video_id or not title or not provider_id or video_id in seen:
                continue
            seen.add(video_id)
            resource = raw.get("resource") if isinstance(raw.get("resource"), dict) else {}
            resource_type = self._text(resource.get("type"))
            media_type = "tv" if resource_type == "show" else "movie" if resource_type == "movie" else None
            categories = raw.get("categories") if isinstance(raw.get("categories"), list) else []
            trailers.append(
                ExternalTrailer(
                    provider_id=provider_id,
                    youtube_video_id=video_id,
                    title=title,
                    thumbnail_url=self._safe_https_url(raw.get("youtube_thumbnail")) or self._safe_https_url(raw.get("thumbnail")),
                    language=self._text(raw.get("language")),
                    categories=[text for value in categories if (text := self._text(value))][:10],
                    published_at=self._text(raw.get("published")),
                    media_type=media_type,  # type: ignore[arg-type]
                    tmdb_id=self._positive_int(resource.get("tmdb_id")),
                    resource_title=self._text(resource.get("title")),
                )
            )
        total_pages = self._nonnegative_int(metadata.get("total_pages")) or (1 if trailers else 0)
        total_results = self._nonnegative_int(metadata.get("total_count")) or len(trailers)
        return ExternalTrailerLibraryResponse(
            page=page,
            total_pages=total_pages,
            total_results=total_results,
            trailers=trailers,
        )

    async def lyrics_lookup(
        self,
        term: str,
        artist: str,
        *,
        album: str | None = None,
        reference_url: str | None = None,
    ) -> LyricsLookupResponse:
        """Resolve a lyrics identity without guessing between provider records."""
        if self._lyrics is None:
            raise RuntimeError("Lyrics gateway is unavailable")
        clean_term = self._require_text(term, "song title")
        clean_artist = self._require_text(artist, "artist")
        clean_album = self._require_text(album, "album") if album is not None and album.strip() else None
        clean_reference = self._safe_https_url(reference_url) if reference_url else None
        if reference_url and clean_reference is None:
            raise ValueError("reference_url must be an HTTPS provider song URL")

        payload = await self._lyrics.search(clean_term, clean_artist)
        raw = payload.get("result")
        if isinstance(raw, dict):
            provider_rows = [raw]
        elif isinstance(raw, list):
            provider_rows = [item for item in raw if isinstance(item, dict)]
        else:
            raw = payload.get("results")
            provider_rows = [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []

        exact: list[LyricsMatch] = []
        for item in provider_rows:
            song = self._text(item.get("song")) or self._text(item.get("title")) or self._text(item.get("term"))
            result_artist = self._text(item.get("artist")) or self._text(item.get("artist_name"))
            if not song or not result_artist:
                continue
            if self._identity(song) != self._identity(clean_term):
                continue
            if self._identity(result_artist) != self._identity(clean_artist):
                continue
            candidate = LyricsMatch(
                song=song,
                artist=result_artist,
                album=self._text(item.get("album")),
                song_url=self._safe_https_url(item.get("song-link")) or self._safe_https_url(item.get("song_link")) or self._safe_https_url(item.get("url")),
                artist_url=self._safe_https_url(item.get("artist-link")) or self._safe_https_url(item.get("artist_link")),
                album_url=self._safe_https_url(item.get("album-link")) or self._safe_https_url(item.get("album_link")),
            )
            if clean_album is not None:
                if not candidate.album or self._identity(candidate.album) != self._identity(clean_album):
                    continue
            exact.append(candidate)

        deduped: list[LyricsMatch] = []
        seen_urls: set[str] = set()
        seen_fallback: set[tuple[str, str, str, str, str]] = set()
        for candidate in exact:
            if candidate.song_url:
                if candidate.song_url in seen_urls:
                    continue
                seen_urls.add(candidate.song_url)
            else:
                fallback_key = (
                    self._identity(candidate.song),
                    self._identity(candidate.artist),
                    self._identity(candidate.album or ""),
                    candidate.artist_url or "",
                    candidate.album_url or "",
                )
                if fallback_key in seen_fallback:
                    continue
                seen_fallback.add(fallback_key)
            deduped.append(candidate)

        deduped.sort(key=lambda item: (self._identity(item.album or ""), item.album_url or "", item.song_url or ""))

        if clean_reference is not None:
            selected = [candidate for candidate in deduped if candidate.song_url == clean_reference]
            if len(selected) == 1:
                return LyricsLookupResponse(term=clean_term, artist=clean_artist, album=clean_album, resolved=True, match=selected[0], candidate_count=1)
            return LyricsLookupResponse(term=clean_term, artist=clean_artist, album=clean_album, resolved=False, ambiguous=len(deduped) > 1, candidates=deduped, candidate_count=len(deduped))

        if len(deduped) != 1:
            return LyricsLookupResponse(term=clean_term, artist=clean_artist, album=clean_album, resolved=False, ambiguous=len(deduped) > 1, candidates=deduped, candidate_count=len(deduped))

        return LyricsLookupResponse(term=clean_term, artist=clean_artist, album=clean_album, resolved=True, candidate_count=1, match=deduped[0])

    async def script_lookup(self, title: str, *, year: int | None = None) -> ScriptLookupResponse:
        if self._screenplay is None:
            raise RuntimeError("Screenplay gateway is unavailable")
        requested = self._require_text(title, "movie title")
        rows = await self._screenplay.search_title(requested)
        metadata_rows = [row for row in rows if self._text(row.get("type")) == "script_metadata"]
        exact = [row for row in metadata_rows if self._identity(self._text(row.get("title")) or "") == self._identity(requested)]
        if year is not None and exact:
            exact_year = [row for row in exact if self._positive_int(row.get("year")) == year]
            if exact_year:
                exact = exact_year
            else:
                # The screenplay actor documents year as optional. A provider-supplied
                # conflicting year is a hard rejection. If every exact-title candidate
                # omits year, one unique exact-title result may remain eligible without
                # inventing a year; multiple same-title rows remain ambiguous.
                provider_years = [self._positive_int(row.get("year")) for row in exact]
                if any(value is not None for value in provider_years):
                    exact = []
        if len(exact) != 1:
            return ScriptLookupResponse(
                requested_title=requested,
                resolved=False,
                ambiguous=len(exact) > 1,
                candidate_count=len(exact),
            )
        metadata = exact[0]
        script_id = self._text(metadata.get("scriptId"))
        chunks = [
            row for row in rows
            if self._text(row.get("type")) == "script_chunk"
            and (not script_id or self._text(row.get("scriptId")) == script_id)
            and self._identity(self._text(row.get("title")) or "") == self._identity(requested)
        ]
        chunks.sort(key=lambda row: self._nonnegative_int(row.get("chunkIndex")) or 0)
        excerpt = self._text(chunks[0].get("chunkText"))[:700] if chunks and self._text(chunks[0].get("chunkText")) else None
        writers = metadata.get("writers") if isinstance(metadata.get("writers"), list) else []
        genres = metadata.get("genres") if isinstance(metadata.get("genres"), list) else []
        return ScriptLookupResponse(
            requested_title=requested,
            resolved=True,
            candidate_count=1,
            match=ScriptMatch(
                title=self._text(metadata.get("title")) or requested,
                year=self._positive_int(metadata.get("year")),
                source=self._text(metadata.get("source")),
                script_url=self._safe_https_url(metadata.get("scriptUrl")),
                download_url=self._safe_https_url(metadata.get("downloadUrl")),
                writers=[text for value in writers if (text := self._text(value))][:20],
                genres=[text for value in genres if (text := self._text(value))][:20],
                script_format=self._text(metadata.get("scriptFormat")),
                has_script_text=metadata.get("hasScriptText") is True,
                word_count=self._nonnegative_int(metadata.get("wordCount")),
                scene_count=self._nonnegative_int(metadata.get("sceneCount")),
                excerpt=excerpt,
            ),
        )

    @staticmethod
    def _identity(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        ascii_text = "".join(ch for ch in normalized if not unicodedata.combining(ch))
        return re.sub(r"[^a-z0-9]+", " ", ascii_text.casefold()).strip()

    @staticmethod
    def _require_text(value: str, label: str) -> str:
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError(f"{label} is required")
        return cleaned[:300]

    @staticmethod
    def _text(value: object) -> str | None:
        if not isinstance(value, str):
            return None
        value = value.strip()
        return value or None

    @staticmethod
    def _positive_int(value: object) -> int | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, int) and value > 0:
            return value
        if isinstance(value, str) and value.isdigit() and int(value) > 0:
            return int(value)
        return None

    @staticmethod
    def _nonnegative_int(value: object) -> int | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, int) and value >= 0:
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return None

    @staticmethod
    def _number(value: object) -> float | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return None
        return None

    @staticmethod
    def _safe_https_url(value: object) -> str | None:
        text = ExternalDataService._text(value)
        if not text:
            return None
        parsed = urlparse(text)
        if parsed.scheme != "https" or not parsed.netloc:
            return None
        return text
