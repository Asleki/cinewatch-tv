# CWTV ADR 0005 — OpenAPI Canonical Contract and Type Generation

**Status:** Accepted for CWTV.V1.2.6

## Decision

FastAPI/Pydantic declarations are the API schema authority. CineWatch checks in one deterministic OpenAPI 3.1 JSON projection and generates TypeScript declarations from that document with pinned `openapi-typescript`.

Every route receives an explicit operation ID before it becomes part of the governed contract. Frontend code imports generated response types through `@cinewatch/contracts`; it must not independently duplicate backend response interfaces.

## Why

This preserves one schema authority while still giving Git review, drift detection and compile-time TypeScript safety. A checked-in canonical OpenAPI document also allows contract review without requiring a running API server.

## Rejected alternatives

- Hand-maintaining parallel Python and TypeScript interfaces: rejected because they can silently diverge.
- Making generated TypeScript the backend authority: rejected because backend route/Pydantic contracts are the service truth.
- Runtime fetching of `/openapi.json` during frontend builds: rejected because builds must not depend on a running backend.
- Introducing a large generated runtime SDK at this stage: rejected as premature for three skeleton endpoints.

## Consequences

Schema-producing dependencies are pinned, OpenAPI changes become reviewable repository diffs, and generated declarations must be regenerated whenever backend contract authority changes.
