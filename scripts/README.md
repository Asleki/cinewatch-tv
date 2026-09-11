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

## CWTV.V1.2.6 OpenAPI and typed contracts

```text
python scripts/check_contract_foundation.py
python scripts/export_openapi_contract.py --check
npm run contracts:update
npm run contracts:check
```

`contracts:update` regenerates the canonical OpenAPI JSON from FastAPI and then regenerates the TypeScript declaration package. `contracts:check` is the non-mutating Linux qualification gate.

## NexVox engineering knowledge

```text
python scripts/build_nexvox_engineering_corpus.py --source-commit <SHA>
python scripts/check_nexvox_engineering_corpus.py
python scripts/build_nexvox_engineering_pdf.py
```

The corpus generator projects an exact Git source commit into the governed `nexvox/engineering` knowledge layer. The checker validates source binding, checksums, record hashes, eligibility boundaries, conversation provenance, secret exclusion, and deterministic regeneration. The PDF is local-only, does not participate in CI authority, and must be regenerated after every ordinary non-projection source commit once the corpus is rebuilt for that exact source commit.


## Provider runtime and media fallback

`check_provider_runtime.py` qualifies the CWTV.V1.3.3.1 provider/secret/media policy. `probe_provider_runtime.py` is an explicit local-only live credential probe for TMDb or OMDb. `reconcile_provider_fallbacks.py` validates deterministic WebP fallback names and regenerates the public fallback manifest.
