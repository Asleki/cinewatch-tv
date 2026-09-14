"""Create CineWatch missing-media and approved override authority.

Revision ID: 0002_missing_media_authority
Revises: 0001_postgresql_foundation
Create Date: 2026-09-13
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0002_missing_media_authority"
down_revision: str | Sequence[str] | None = "0001_postgresql_foundation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cinewatch_missing_media",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("provider", sa.String(length=40), nullable=False),
        sa.Column("entity_type", sa.String(length=40), nullable=False),
        sa.Column("provider_id", sa.Integer(), nullable=False),
        sa.Column("canonical_name", sa.String(length=300), nullable=False),
        sa.Column("asset_kind", sa.String(length=40), nullable=False),
        sa.Column("suggested_filename", sa.String(length=360), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="MISSING"),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cinewatch_missing_media")),
        sa.UniqueConstraint("provider", "entity_type", "provider_id", "asset_kind", name="uq_cinewatch_missing_media_identity"),
    )
    op.create_table(
        "cinewatch_media_override",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("missing_media_id", sa.Integer(), nullable=True),
        sa.Column("provider", sa.String(length=40), nullable=False),
        sa.Column("entity_type", sa.String(length=40), nullable=False),
        sa.Column("provider_id", sa.Integer(), nullable=False),
        sa.Column("asset_kind", sa.String(length=40), nullable=False),
        sa.Column("file_name", sa.String(length=360), nullable=False),
        sa.Column("public_url", sa.String(length=1000), nullable=False),
        sa.Column("provenance_url", sa.String(length=1500), nullable=True),
        sa.Column("usage_authority", sa.Text(), nullable=True),
        sa.Column("approved_by", sa.String(length=220), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["missing_media_id"], ["cinewatch_missing_media.id"], name=op.f("fk_cinewatch_media_override_missing_media_id_cinewatch_missing_media"), ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cinewatch_media_override")),
        sa.UniqueConstraint("provider", "entity_type", "provider_id", "asset_kind", name="uq_cinewatch_media_override_identity"),
    )


def downgrade() -> None:
    op.drop_table("cinewatch_media_override")
    op.drop_table("cinewatch_missing_media")
