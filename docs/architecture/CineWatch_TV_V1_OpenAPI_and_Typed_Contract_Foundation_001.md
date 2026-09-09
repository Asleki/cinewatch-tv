# CineWatch TV V1 OpenAPI & Typed Contract Foundation 001

**Milestone:** `CWTV.V1.2.6`
**Document:** `CWTV-V1-OPENAPI-CONTRACT-001`
**Status:** implementation candidate
**Baseline:** `74856ca2738afaa33d33ed7cb1983967fc0355bd`

## Purpose

CWTV.V1.2.6 establishes a deterministic, reviewable API-contract bridge between the FastAPI backend and TypeScript consumers without introducing product APIs.

The backend remains the contract authority. The browser does not become a second schema authority.

## Authority chain

```text
FastAPI route declarations
+ Pydantic response models
+ explicit operation IDs
        ↓
canonical OpenAPI 3.1 JSON
        ↓
openapi-typescript 7.13.0
        ↓
@cinewatch/contracts
        ↓
Next.js type-only consumption
```

## Canonical OpenAPI

The checked-in canonical document is:

`packages/contracts/openapi/cinewatch-v1.openapi.json`

It is produced by `scripts/export_openapi_contract.py` directly from `create_app()` and serialized deterministically with sorted JSON keys. `--check` fails if live FastAPI authority no longer matches the checked-in document.

OpenAPI is explicitly locked to 3.1.0. Existing operations receive explicit stable identifiers:

- `system_health`
- `system_status`
- `v1_system_status`

These names are API-contract identity and must not silently change because a Python function or module is renamed.

## Schema-producing dependency determinism

FastAPI and Pydantic participate directly in emitted OpenAPI. CWTV.V1.2.6 therefore makes their qualified versions exact:

- FastAPI 0.141.1
- Pydantic 2.13.5
- pydantic-settings 2.15.0

A deliberate upgrade is allowed later, but any OpenAPI difference must be reviewed as contract drift rather than appearing from an unconstrained reinstall.

## TypeScript projection

`openapi-typescript` 7.13.0 is pinned in `@cinewatch/contracts`. It generates:

`packages/contracts/src/generated/openapi.d.ts`

Application code imports governed aliases from:

`packages/contracts/src/index.d.ts`

The generated file and canonical JSON are never edited by hand.

## Frontend boundary

`apps/web/src/lib/api/system-client.ts` continues to own browser-side HTTP behavior, but its `HealthResponse` and `StatusResponse` types come from `@cinewatch/contracts`. This removes the duplicate frontend response interfaces introduced only as a temporary V1.2.4 skeleton bridge.

This milestone does not introduce a generated runtime HTTP client. Runtime fetch behavior remains small and explicit until later product API requirements justify further abstraction.

## Workspace runtime resolution

`openapi-typescript` is owned by the `@cinewatch/contracts` npm workspace. Runtime qualification must therefore resolve and execute the tool through npm workspace authority rather than assuming npm hoists the package into the repository-root `node_modules`. npm 12 may legitimately install a workspace-owned dependency under `packages/contracts/node_modules`. Both layouts are valid as long as `npm exec --workspace @cinewatch/contracts -- ...` resolves the pinned `7.13.0` tool.

This rule keeps the qualification gate aligned with the same workspace boundary used by `npm run generate -w @cinewatch/contracts` and avoids treating npm's physical installation layout as API-contract authority.

## Drift gates

Qualification proves:

1. canonical OpenAPI equals live FastAPI authority;
2. explicit operation IDs remain stable;
3. the generated TypeScript declaration equals a fresh generation from the canonical JSON;
4. frontend TypeScript compiles while consuming `@cinewatch/contracts`;
5. repository tests reject hand-maintained duplicate system response types;
6. only `/health`, `/status`, and `/api/v1/status` exist in this foundation.

## Scope exclusions

CWTV.V1.2.6 does not implement authentication, users, canonical media entities, providers, rights, Discover, Watch, Explore, My CineWatch, cinema, NexVox, AWS deployment or PostgreSQL product tables.

## Portability

Generation is repository-local and requires no running backend server, AWS service, Azure service, PostgreSQL server or external provider. FastAPI is imported locally, OpenAPI is emitted locally, and TypeScript declarations are generated from a local JSON file.
