# Repository Scripts

Repository-level deterministic engineering and qualification scripts live here.

Scripts must remain usable from Termux where the required runtime exists. Platform-specific production runtime checks execute in the qualified Linux userland when Android native dependencies are unsuitable.

Current backend checks:

- `python scripts/check_backend_skeleton.py` validates the V1.2.3 source/dependency boundary without importing FastAPI;
- `bash scripts/check_backend_runtime.sh` runs compile, service tests, a temporary local Uvicorn server, and live health/status/request-ID probes using the selected backend Python.

CWTV.V1.2.4 adds:

- `check_frontend_skeleton.py` — static frontend architecture and policy qualification;
- `check_frontend_runtime.sh` — Linux Node 24/npm 12 lint, typecheck, production-build, and live-route smoke qualification.

CWTV.V1.2.5 adds:

- `check_database_foundation.py` — static PostgreSQL, dependency, secret-configuration, NPP-separation, and migration-root qualification;
- `check_database_migrations.sh` — Linux Python qualification of SQLAlchemy/Alembic/Psycopg versions, the single Alembic head, PostgreSQL offline migration SQL, and database-foundation tests without requiring a server.
