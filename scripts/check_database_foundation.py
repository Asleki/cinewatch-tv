#!/usr/bin/env python3
"""Static policy qualification for CWTV.V1.2.5."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = (
    "services/api/alembic.ini",
    "services/api/cinewatch_api/database/__init__.py",
    "services/api/cinewatch_api/database/base.py",
    "services/api/cinewatch_api/database/engine.py",
    "services/api/cinewatch_api/database/session.py",
    "services/api/cinewatch_api/database/url.py",
    "services/api/migrations/env.py",
    "services/api/migrations/script.py.mako",
    "services/api/migrations/versions/0001_postgresql_migration_foundation.py",
    "docs/architecture/CineWatch_TV_V1_PostgreSQL_and_Migration_Foundation_001.md",
    "docs/architecture/decisions/CWTV_ADR_0004_PostgreSQL_Authority_and_Migration_Boundary.md",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL  {message}")


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    for path in REQUIRED_PATHS:
        require((ROOT / path).is_file(), f"missing required path: {path}")
    print("PASS  PostgreSQL and migration foundation paths")

    pyproject = read("services/api/pyproject.toml")
    for dependency in (
        '"SQLAlchemy==2.0.52"',
        '"alembic==1.19.2"',
        '"psycopg[binary]==3.3.5"',
    ):
        require(dependency in pyproject, f"missing database dependency authority: {dependency}")
    print("PASS  SQLAlchemy/Alembic/Psycopg dependency authority")

    settings = read("services/api/cinewatch_api/settings.py")
    require("SecretStr" in settings, "database URL must use secret settings type")
    require('validation_alias="DATABASE_URL"' in settings, "DATABASE_URL settings alias missing")

    url_module = read("services/api/cinewatch_api/database/url.py")
    require('POSTGRESQL_DRIVER = "postgresql+psycopg"' in url_module, "psycopg driver lock missing")
    require("hide_password=True" in url_module, "database URL redaction missing")
    print("PASS  secret database configuration and redaction policy")

    production_database_files = [
        "services/api/cinewatch_api/database/base.py",
        "services/api/cinewatch_api/database/engine.py",
        "services/api/cinewatch_api/database/session.py",
        "services/api/cinewatch_api/database/url.py",
        "services/api/migrations/env.py",
    ]
    for path in production_database_files:
        require("sqlite" not in read(path).lower(), f"SQLite fallback forbidden in {path}")
    print("PASS  PostgreSQL-only persistence policy")

    migration = read(
        "services/api/migrations/versions/0001_postgresql_migration_foundation.py"
    )
    require('revision: str = "0001_postgresql_foundation"' in migration, "root revision ID mismatch")
    require("down_revision: str | Sequence[str] | None = None" in migration, "root revision must have no parent")
    require("Create no product schema" in migration, "foundation migration scope statement missing")
    print("PASS  single empty migration root contract")

    env_example = read(".env.example")
    require("DATABASE_URL=" in env_example, "DATABASE_URL example variable missing")
    require("cinewatch_dev" in env_example, "cinewatch_dev authority guidance missing")
    print("PASS  environment contract reserves independent cinewatch_dev authority")

    architecture = read(
        "docs/architecture/CineWatch_TV_V1_PostgreSQL_and_Migration_Foundation_001.md"
    )
    require("npp_dev" in architecture, "NPP separation statement missing")
    require("AWS" in architecture and "Azure" in architecture, "cloud-portability statement missing")
    print("PASS  NPP separation and cloud-portability policy")

    migration_check = read("scripts/check_database_migrations.sh")
    require("export DATABASE_URL" not in migration_check, "offline migration URL must not be globally exported")
    require('DATABASE_URL="$OFFLINE_DATABASE_URL"' in migration_check, "offline Alembic URL must be command-scoped")
    require("env -u DATABASE_URL" in migration_check, "database tests must run without inherited DATABASE_URL")

    database_tests = read("services/api/tests/test_database_foundation.py")
    require(
        'monkeypatch.delenv("DATABASE_URL", raising=False)' in database_tests,
        "optional database URL test must isolate caller environment",
    )
    print("PASS  offline migration environment isolation policy")

    print("PASS  CWTV.V1.2.5 PostgreSQL and migration foundation policy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
