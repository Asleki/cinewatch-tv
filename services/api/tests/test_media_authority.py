from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from cinewatch_api.contracts.catalog import CatalogBrowseResponse, CatalogMediaSummary
from cinewatch_api.database.base import Base
from cinewatch_api.media.authority import MediaAuthority
from cinewatch_api.media.models import MediaOverrideRecord, MissingMediaRecord


def _payload(*, poster_url: str | None = None) -> CatalogBrowseResponse:
    return CatalogBrowseResponse(
        kind="collection",
        slug="trending",
        title="Trending Now",
        page=1,
        total_pages=1,
        total_results=1,
        media_type="movie",
        sort="popularity.desc",
        items=[
            CatalogMediaSummary(
                provider_id=42,
                media_type="movie",
                title="Missing Poster Film",
                year=2026,
                poster_url=poster_url,
                backdrop_url=None,
                rating=7.4,
                future_path="/title/movie/42",
            )
        ],
    )


def test_missing_media_is_logged_without_disqualifying_entity() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        result = MediaAuthority(session).apply_browse(_payload())
        assert len(result.items) == 1
        assert result.items[0].title == "Missing Poster Film"
        assert result.items[0].poster_url is None
        rows = session.scalars(select(MissingMediaRecord)).all()
        assert {(row.asset_kind, row.suggested_filename) for row in rows} == {
            ("poster", "Missing_Poster_Film_poster.webp"),
            ("backdrop", "Missing_Poster_Film_backdrop.webp"),
        }


def test_approved_override_precedes_missing_provider_media() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(
            MediaOverrideRecord(
                missing_media_id=None,
                provider="tmdb",
                entity_type="movie",
                provider_id=42,
                asset_kind="poster",
                file_name="Missing_Poster_Film_poster.webp",
                public_url="/cinewatch-media/Missing_Poster_Film_poster.webp",
                provenance_url="https://example.test/provenance",
                usage_authority="Approved for CineWatch test use",
                approved_by="test-authority",
                approved_at=datetime.now(timezone.utc),
                active=True,
            )
        )
        session.commit()
        result = MediaAuthority(session).apply_browse(_payload())
        assert result.items[0].poster_url == "/cinewatch-media/Missing_Poster_Film_poster.webp"
        # Backdrop remains missing, but the title itself is still present.
        assert len(result.items) == 1
