# CWTV ADR 0009 - Homepage Data Contract and TMDb Aggregation Authority

**Status:** Proposed for qualification
**Milestone:** CWTV.V1.3.3.2.1
**Decision date:** 2026-09-11

## Context

CineWatch TV now has a qualified provider-runtime and media-fallback foundation. The next product step requires real homepage data without binding the frontend directly to TMDb response shapes or credentials.

The existing OpenAPI foundation checker also encoded a now-obsolete development assumption: the complete canonical path set had to equal the three system endpoints. Simply adding `/api/v1/home` to that closed list would make every future product route require another edit to the old foundation checker.

That is an architectural update cascade.

## Decision

CineWatch adopts `GET /api/v1/home` as the first V1 product-data endpoint.

TMDb is the primary upstream. The CineWatch API owns aggregation, normalization, rating representation, image URL construction, missing-media detection, and the public response contract. The frontend will consume the generated CineWatch contract and will not call TMDb directly.

OMDb is not an unconditional dependency of this endpoint.

The V1.2.6 contract checker is updated once at its actual obsolete assumption: system routes become required subset invariants rather than an exact enumeration of every route in the product. Homepage-specific expectations move into `scripts/check_homepage_data_foundation.py`.

## Update rule

For CineWatch engineering, an update replaces the obsolete assumption it targets.

Before changing a shared authority, its repository dependents must be considered. If the change can be fully neutralized at the shared boundary while preserving tests and safety, update the boundary. If the change would force multiple unrelated features to move together or introduce circular dependency, do not propagate the change. Lock the shared authority to a stable interface and let the consuming feature normalize into its own guardrails.

For this decision:

- the shared contract foundation is neutralized by subset invariants;
- the homepage owns its own checker;
- system endpoints remain unchanged;
- provider runtime remains unchanged;
- media fallback authority remains unchanged;
- database and cloud architecture remain unchanged;
- future product routes do not need to modify the foundation checker solely to exist.

## Consequences

The canonical OpenAPI surface can grow without weakening the original system-route guarantees.

Every new product contract must bring its own explicit policy gate rather than silently inheriting homepage assumptions.

Raw TMDb field names remain an internal provider concern. Public clients receive CineWatch models.

Generated OpenAPI and TypeScript files remain generator-owned. They are regenerated in the real repository after source placement and are not hand-authored in the delivery package.

## Rejected alternatives

**Keep exact route enumeration and append `/api/v1/home`.**
Rejected because the same old checker would need edits for every new product endpoint.

**Expose `/api/v1/tmdb/...` to the frontend.**
Rejected because it leaks upstream identity into the public contract and encourages provider coupling.

**Call TMDb and OMDb on every homepage request.**
Rejected because it creates unnecessary latency, additional failure modes, and provider coupling before a concrete enrichment gap exists.

**Introduce PostgreSQL caching immediately.**
Rejected for this slice because persistence ownership and refresh semantics have not yet been qualified.
