"""Establish the CineWatch PostgreSQL migration root.

Revision ID: 0001_postgresql_foundation
Revises: None
Create Date: 2026-09-08
"""

from collections.abc import Sequence

revision: str = "0001_postgresql_foundation"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create no product schema; this revision establishes migration lineage only."""

    pass


def downgrade() -> None:
    """Return to the empty migration base."""

    pass
