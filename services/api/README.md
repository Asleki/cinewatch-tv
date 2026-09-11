# CineWatch TV API Service

This directory is the governed CineWatch TV FastAPI backend service boundary.

`CWTV.V1.2.3` established the backend service skeleton. `CWTV.V1.2.5` adds the PostgreSQL application boundary: secret database configuration, SQLAlchemy metadata/engine/session factories, Psycopg 3, and the single Alembic migration lineage.

CWTV.V1.3.3.1 introduces the first server-only provider adapters and local secret boundary without adding product-domain API routes. Authentication, rights enforcement, playback, Discover, Watch, Explore, My CineWatch, cinema, NexVox product features, and product-domain database tables remain out of scope.

## Linux development setup

The production-style Python dependency path is the qualified ARM64 Linux userland rather than native Android Python.

From the repository root inside that Linux environment:

```bash
. /root/.venvs/cinewatch-api/bin/activate
python -m pip install -e 'services/api[test]'
```

## Tests

```bash
python -m pytest services/api/tests -q
```

## Database migration foundation

The development database identity is `cinewatch_dev`, but CWTV.V1.2.5 does not provision a server.

`DATABASE_URL` is required only when database or migration operations are explicitly invoked. It must use the `postgresql+psycopg` driver. No real credentials belong in Git.

Offline migration qualification requires no running PostgreSQL server:

```bash
CWTV_API_PYTHON=/root/.venvs/cinewatch-api/bin/python \
  bash scripts/check_database_migrations.sh
```

A future infrastructure-owning milestone will qualify a real PostgreSQL server and cloud connectivity.

## Run the API locally

```bash
python -m uvicorn cinewatch_api.main:app \
  --app-dir services/api \
  --host 127.0.0.1 \
  --port 8000
```

Then inspect `/health`, `/status`, `/api/v1/status`, and `/docs` on the local server.

## OpenAPI contract authority

CWTV.V1.2.6 makes the FastAPI OpenAPI 3.1 projection a governed, checked-in contract. Existing system routes use explicit stable operation IDs. Run `python scripts/export_openapi_contract.py --check` from the repository root to detect schema drift. TypeScript declarations are generated downstream in `packages/contracts`; the API service remains authoritative.


## Local provider runtime

Create a root `.env.local` for real local credentials; never commit it. The initial keys are `TMDB_API_KEY` and `OMDB_API_KEY`. TMDb is primary and OMDb is enrichment-only.

After installing the API dependencies, explicit live probes are:

```bash
python scripts/probe_provider_runtime.py tmdb
python scripts/probe_provider_runtime.py omdb --imdb-id tt0111161
```

CI does not use live provider credentials. Provider adapter tests use deterministic mocked HTTP responses.

Fallback media is reconciled with:

```bash
python scripts/reconcile_provider_fallbacks.py
python scripts/reconcile_provider_fallbacks.py --check
```
