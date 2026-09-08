from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_database_foundation_paths_exist() -> None:
    required = (
        "services/api/alembic.ini",
        "services/api/cinewatch_api/database/base.py",
        "services/api/cinewatch_api/database/engine.py",
        "services/api/cinewatch_api/database/session.py",
        "services/api/cinewatch_api/database/url.py",
        "services/api/migrations/env.py",
        "services/api/migrations/versions/0001_postgresql_migration_foundation.py",
        "scripts/check_database_foundation.py",
        "scripts/check_database_migrations.sh",
    )

    for path in required:
        assert (ROOT / path).is_file(), path


def test_database_dependencies_are_governed() -> None:
    pyproject = (ROOT / "services/api/pyproject.toml").read_text(encoding="utf-8")

    assert '"SQLAlchemy==2.0.52"' in pyproject
    assert '"alembic==1.19.2"' in pyproject
    assert '"psycopg[binary]==3.3.5"' in pyproject
