# CineWatch TV V1.3.3.2.1 R1 OpenAPI Foundation Test Neutralization Correction

**Milestone:** CWTV.V1.3.3.2.1
**Correction:** R1
**Status:** Correction candidate
**Date:** 2026-09-11

## Trigger

The full backend regression exposed a stale foundation-era test in
`services/api/tests/test_openapi.py`.

The test required the complete OpenAPI path set to equal only the original
three system routes. After the governed `/api/v1/home` product route was added,
the test failed even though the canonical OpenAPI document, generated
TypeScript authority, homepage contract checker, and focused homepage tests
were already valid.

## Architectural diagnosis

The obsolete invariant was not the existence of `/api/v1/home`. The obsolete
invariant was that a foundation test owned the complete future public route set.

The updated `scripts/check_contract_foundation.py` already neutralizes this
coupling by requiring the original system routes as foundation invariants rather
than enumerating every product route. The stale backend test had not been
updated to the same architecture.

## Correction

Replace the old exact-path-set test with a foundation-preservation test:

- the OpenAPI version remains 3.1.0;
- `/health`, `/status`, and `/api/v1/status` remain required;
- their operation IDs remain explicit and stable;
- product routes are free to evolve under their own feature-specific guardrails.

The homepage-specific authority remains owned by
`scripts/check_homepage_data_foundation.py`.

## Why this is an update rather than an additive workaround

No parallel test is added and no exception for `/api/v1/home` is appended to the
old skeleton rule. The obsolete complete-path ownership assumption is removed
from the existing test itself.

This prevents the same foundation test from failing every time a legitimate
future CineWatch product route is introduced.

## Update-impact scan

The correction was evaluated against:

- the canonical OpenAPI exporter;
- generated TypeScript contracts;
- the V1 router;
- the three system routes;
- `/api/v1/home`;
- `scripts/check_contract_foundation.py`;
- `scripts/check_homepage_data_foundation.py`;
- contract snapshot tests;
- backend regression;
- repository regression;
- CI contract gates.

No production route, response model, provider runtime, credential boundary,
database authority, frontend page, generated contract, or NexVox corpus file
needs modification for this correction.

## Acceptance

R1 is qualified only when:

1. `services/api/tests/test_openapi.py` passes;
2. the complete `services/api/tests` suite passes;
3. the contract foundation checker passes;
4. the homepage data foundation checker passes;
5. repository regression passes;
6. `git diff --check` is clean;
7. Markdown LF, trailing-whitespace, and final-newline gates pass.

No Git commit or NexVox regeneration should occur before those gates are green.
