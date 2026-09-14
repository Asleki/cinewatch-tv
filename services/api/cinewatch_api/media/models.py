"""PostgreSQL models for CineWatch missing-media discovery and approved overrides."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from cinewatch_api.database.base import Base


class MissingMediaRecord(Base):
    __tablename__ = "cinewatch_missing_media"
    __table_args__ = (
        UniqueConstraint(
            "provider", "entity_type", "provider_id", "asset_kind",
            name="uq_cinewatch_missing_media_identity",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(40), nullable=False)
    provider_id: Mapped[int] = mapped_column(Integer, nullable=False)
    canonical_name: Mapped[str] = mapped_column(String(300), nullable=False)
    asset_kind: Mapped[str] = mapped_column(String(40), nullable=False)
    suggested_filename: Mapped[str] = mapped_column(String(360), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="MISSING")
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class MediaOverrideRecord(Base):
    __tablename__ = "cinewatch_media_override"
    __table_args__ = (
        UniqueConstraint(
            "provider", "entity_type", "provider_id", "asset_kind",
            name="uq_cinewatch_media_override_identity",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    missing_media_id: Mapped[int | None] = mapped_column(
        ForeignKey("cinewatch_missing_media.id", ondelete="SET NULL"), nullable=True
    )
    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(40), nullable=False)
    provider_id: Mapped[int] = mapped_column(Integer, nullable=False)
    asset_kind: Mapped[str] = mapped_column(String(40), nullable=False)
    file_name: Mapped[str] = mapped_column(String(360), nullable=False)
    public_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    provenance_url: Mapped[str | None] = mapped_column(String(1500), nullable=True)
    usage_authority: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(220), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
