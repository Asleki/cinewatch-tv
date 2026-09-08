# ADR 0004 — PostgreSQL Authority & Migration Boundary

**Status:** Accepted for CWTV.V1.2.5 candidate
**Baseline:** `7b6a8392d90fb08be9f522e9a182c723f2719cdd`

## Decision

CineWatch native application state will use an independent PostgreSQL database authority, development identity `cinewatch_dev`, accessed by the FastAPI service through SQLAlchemy 2.x and Psycopg 3. Alembic is the only schema-migration authority.

The migration lineage begins with `0001_postgresql_foundation`, an intentionally empty root migration. Product-domain schemas are deferred to their owning milestones.

`DATABASE_URL` is secret configuration. Only `postgresql+psycopg` URLs are accepted. SQLite fallback is prohibited.

## Separation

NPP's `npp_dev` is not a CineWatch database, migration target, fallback, or shared schema. Future NPP integration must cross an explicit service/provider boundary.

## Infrastructure

This ADR does not provision AWS or Azure. The database contract is provider-neutral so the same lineage can later operate on qualified PostgreSQL hosting in either cloud.

## Consequences

- CineWatch database configuration exists before cloud provisioning.
- The backend can still start while `DATABASE_URL` is absent because no product feature depends on PostgreSQL yet.
- Migration generation and lineage can be qualified offline.
- Later schemas must extend this single Alembic history.
- Credentials are never stored in repository configuration or emitted in diagnostics.
