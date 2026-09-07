# CWTV ADR 0001 — Repository Service Boundary Naming

**Decision ID:** `CWTV-ADR-0001`
**Milestone:** `CWTV.V1.2.2`
**Status:** ACCEPTED
**Date:** 2026-09-07
**Baseline:** `fd6e885`

## Context

`CWTV-V1-ENG-ARCH-001` Revision R1 established the architectural boundaries but illustrated the backend and shared-contract paths as `apps/api` and `packages/api-contract`.

The explicitly confirmed `CWTV.V1.2.2` repository direction uses:

- `apps/web` for the user-facing web application;
- `services/api` for the independent FastAPI backend service;
- `packages/contracts` for shared/generated API-contract artifacts.

The path refinement changes repository naming only. It does not change backend authority, OpenAPI authority, database authority, provider boundaries, cloud portability, or any other approved engineering lock.

## Decision

The initial V1 repository tree SHALL use:

```text
apps/web
services/api
packages/contracts
```

`services/api` emphasizes that the FastAPI backend is an independent service authority rather than a frontend application package.

`packages/contracts` remains implementation-neutral while FastAPI-generated OpenAPI stays the canonical runtime API schema.

## Superseded path illustrations

For repository placement only, this ADR supersedes the following path illustrations in Section 5 of `CWTV-V1-ENG-ARCH-001` Revision R1:

```text
apps/api            -> services/api
packages/api-contract -> packages/contracts
```

No other section or engineering lock is superseded.
