# CineWatch TV V1 Backend Service Skeleton 001

**Document ID:** `CWTV-V1-BACKEND-SKELETON-001`

**Milestone:** `CWTV.V1.2.3`

**Status:** IMPLEMENTATION CANDIDATE

**Baseline commit:** `d050344387a963e0c3336a010fcef1ab7644eadd`

## 1. Purpose

This milestone creates the first runnable CineWatch TV backend service while preserving the approved separation between engineering foundation and product features.

The service proves that CineWatch can boot a typed FastAPI application, expose operational endpoints, load normalized configuration, assign request identities, emit structured logs, return stable error envelopes, and qualify itself through automated tests.

It does not implement CineWatch product domains.

## 2. Runtime boundary

The backend remains owned by `services/api`.

The Python package is `cinewatch_api` and the ASGI entry point is `cinewatch_api.main:app`.

Repository-root development launch:

`python -m uvicorn cinewatch_api.main:app --app-dir services/api --host 127.0.0.1 --port 8000`

## 3. System endpoints

- `GET /health` — unversioned liveness probe;
- `GET /status` — unversioned operational service status;
- `GET /api/v1/status` — proof of the governed V1 API namespace.

`ready` in this milestone means the backend process and skeleton are serving requests. It does not claim database, provider, authentication, rights, or playback readiness.

## 4. Request identity

Every HTTP request receives an `X-Request-ID` response header. A caller-supplied request ID is retained only when it matches the bounded safe identifier grammar. Invalid or missing values are replaced with a locally generated UUID-derived identifier.

## 5. Error envelope

Expected and unexpected errors have a stable envelope foundation:

```json
{
  "error": {
    "code": "SOME_CODE",
    "message": "Public-safe message.",
    "request_id": "..."
  }
}
```

No product-domain error codes are introduced yet.

## 6. Settings

The backend recognizes `CINEWATCH_ENV`, `CINEWATCH_APP_NAME`, `CINEWATCH_SERVICE_NAME`, and `CINEWATCH_LOG_LEVEL`.

The root `.env` file is a local-development convenience only. Production environments inject normalized environment values through deployment infrastructure.

No database URL is consumed by application code in this milestone even though the root template reserves that future variable.

## 7. Logging

The backend configures a JSON-lines logging bootstrap using Python standard-library logging. A later observability milestone may route records to cloud-specific collection without making AWS or Azure a domain dependency.

## 8. Dependency policy

Runtime dependencies are limited to FastAPI, Pydantic Settings, and Uvicorn. Test dependencies are isolated in the `test` optional dependency group.

Linux-only quality tooling is isolated in the `quality` optional dependency group because Ruff does not provide the Android/Termux runtime path required for the primary phone environment.

Database, migration, authentication, provider, media, and cloud SDK dependencies remain prohibited at this milestone.

## 9. Test boundary

Service tests are colocated in `services/api/tests` and cover health/status, V1 namespace, request IDs, error envelopes, OpenAPI exposure, settings, and live Uvicorn smoke verification.

## 10. Explicit exclusions

`CWTV.V1.2.3` does not implement Discover, Watch, Explore, My CineWatch, authentication, PostgreSQL connectivity or schemas, Alembic migrations, providers, content identity, rights, playback, cinema, NexVox, or cloud provisioning.

## 11. Forward boundary

After qualification, `CWTV.V1.2.4 — Frontend Application Skeleton` may create the first Next.js runtime boundary. Database work remains reserved for `CWTV.V1.2.5`.
