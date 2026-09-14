"""Persistence helpers for CineWatch media gaps and approved replacements."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from cinewatch_api.media.fallbacks import MediaGap
from cinewatch_api.media.models import MediaOverrideRecord, MissingMediaRecord


class MediaAuthorityRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_override(self, gap: MediaGap) -> str | None:
        row = self._session.scalar(
            select(MediaOverrideRecord).where(
                MediaOverrideRecord.provider == gap.provider,
                MediaOverrideRecord.entity_type == gap.entity_type,
                MediaOverrideRecord.provider_id == gap.provider_id,
                MediaOverrideRecord.asset_kind == gap.asset_kind,
                MediaOverrideRecord.active.is_(True),
            )
        )
        if row is None or not row.public_url.strip():
            return None
        return row.public_url.strip()

    def record_gap(self, gap: MediaGap) -> MissingMediaRecord:
        row = self._session.scalar(
            select(MissingMediaRecord).where(
                MissingMediaRecord.provider == gap.provider,
                MissingMediaRecord.entity_type == gap.entity_type,
                MissingMediaRecord.provider_id == gap.provider_id,
                MissingMediaRecord.asset_kind == gap.asset_kind,
            )
        )
        now = datetime.now(timezone.utc)
        if row is None:
            row = MissingMediaRecord(
                provider=gap.provider,
                entity_type=gap.entity_type,
                provider_id=gap.provider_id,
                canonical_name=gap.entity_name,
                asset_kind=gap.asset_kind,
                suggested_filename=gap.suggested_filename,
                status="MISSING",
                first_seen_at=now,
                last_seen_at=now,
            )
            self._session.add(row)
        else:
            row.canonical_name = gap.entity_name
            row.suggested_filename = gap.suggested_filename
            row.last_seen_at = now
            if row.status == "RESOLVED" and self.find_override(gap) is None:
                row.status = "MISSING"
        self._session.flush()
        return row
