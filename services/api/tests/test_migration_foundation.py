from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

API_ROOT = Path(__file__).resolve().parents[1]


def test_migration_lineage_has_single_governed_head() -> None:
    config = Config(str(API_ROOT / "alembic.ini"))
    script = ScriptDirectory.from_config(config)

    assert script.get_heads() == ["0002_missing_media_authority"]

    head = script.get_revision("0002_missing_media_authority")
    assert head is not None
    assert head.down_revision == "0001_postgresql_foundation"

    foundation = script.get_revision("0001_postgresql_foundation")
    assert foundation is not None
    assert foundation.down_revision is None


def test_foundation_revision_contains_no_domain_operations() -> None:
    migration = (
        API_ROOT
        / "migrations"
        / "versions"
        / "0001_postgresql_migration_foundation.py"
    ).read_text(encoding="utf-8")

    assert "op.create_table" not in migration
    assert "op.add_column" not in migration
    assert "op.execute" not in migration
