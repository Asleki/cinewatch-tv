# CWTV ADR 0002 — Backend System Endpoints and Request Identity

**Status:** ACCEPTED BY CWTV.V1.2.3 CANDIDATE

## Context

CineWatch needs operational probes and request correlation before product APIs exist. These concerns must not be confused with product availability, database readiness, or external-provider health.

## Decision

1. `/health` is an unversioned liveness endpoint.
2. `/status` is an unversioned operational service-status endpoint.
3. `/api/v1/status` proves the versioned API namespace without adding a product feature.
4. Every HTTP response receives `X-Request-ID`.
5. Safe caller request IDs may propagate; missing or invalid IDs are replaced.
6. System status reports only service-skeleton readiness at this milestone.

## Consequences

Infrastructure can probe the backend without depending on a product API version, while clients and contract tooling can prove that `/api/v1` exists.

Later database/provider readiness must use explicit component semantics rather than silently changing the meaning of liveness.
