# CWTV ADR 0010 — Homepage Interaction and Lazy Discovery Authority

**Status:** Proposed for qualification
**Milestone:** `CWTV.V1.3.3.2.2`
**Decision date:** 2026-09-12

## Context

`CWTV.V1.3.3.2.1` proved a bounded provider-neutral homepage contract, but the real Next.js homepage is still the original application skeleton. CineWatch now needs live visual presentation, search, trailer playback, dynamic genres, and editorial discovery without turning the homepage into a details-page preload or exposing provider credentials to browser code.

The historical `CineWatchStream` project proved useful interaction patterns, including TMDb search, dynamic genres, cultural/editorial collections, trailer discovery, and in-page YouTube embedding. That repository is evidence of product intent only; its browser-side provider-key architecture is not inherited.

## Decision

CineWatch adopts a layered homepage interaction model:

1. `GET /api/v1/home` remains the bounded first-viewport authority.
2. High-cost or below-the-fold surfaces load lazily from dedicated CineWatch homepage endpoints.
3. Only the hero receives writers, optional secondary ratings, and trailer enrichment.
4. Search returns lightweight identity suggestions rather than full details payloads.
5. Homepage cards preserve future route identity while remaining inert until destination pages exist.
6. Dynamic genres are merged from movie and television genre authorities.
7. CineWatch editorial rails are explicit CineWatch taxonomy and may use deterministic provider-query heuristics.
8. Stream Now is reserved exclusively for content CineWatch is authorized to play inside CineWatch.
9. The trailer button is absent when no qualifying trailer exists.
10. No quote is fabricated and no CineWatch rating is displayed before CineWatch owns the corresponding data.

## Trailer decision

Television trailers are season-aware. CineWatch resolves the latest regular aired season before selecting a trailer. Explicitly mismatched older-season trailers are rejected when a later season is the active context.

This replaces the historical “first YouTube trailer” behavior with a deterministic relevance rule.

## Browser transport decision

FastAPI remains the application API authority. Next.js may expose a configuration-only rewrite from `/api/cinewatch/*` to the configured FastAPI `/api/v1/*` origin so browser interactions can remain same-origin during local development.

This rewrite is transport plumbing, not an application endpoint. No `apps/web/src/app/api` route is added, no provider key enters browser source, and no provider-specific route becomes public CineWatch product language.

## Stream Now decision

Nationality, language, popularity, TMDb presence, or placement in a CineWatch discovery category never establishes Stream Now eligibility.

Until an explicit CineWatch rights authority exists, the homepage renders five inert Stream Now placeholders. This prevents provider metadata from being mistaken for a CineWatch playback grant.

## Performance decision

Homepage work is bounded by presentation need:

- initial rails remain capped;
- lazy rails are fetched only near the viewport;
- trailer candidates are capped at six and the rendered trailer rail at four;
- external ratings are hero-only;
- card selection does not trigger details fetches;
- people are not rendered as a homepage rail.

A later cache/refresh milestone may reduce repeated provider configuration calls after measurement. This milestone does not introduce persistence or a cache authority solely to hide unmeasured latency.

## Consequences

The homepage can look and behave like a real CineWatch product while future details, genre, country, network, archive, review, and playback pages remain unimplemented.

The public API grows under feature-specific contracts without modifying the original provider-runtime or contract-foundation meaning.

The web layer remains provider-credential neutral.

## Rejected alternatives

**Direct TMDb/OMDb calls from React.** Rejected because provider credentials and provider response shapes would leak into the client boundary.

**Next.js application API routes as a proxy.** Rejected because the qualified frontend architecture assigns application API ownership to FastAPI. A configuration-only rewrite is sufficient.

**Load every future detail for every homepage card.** Rejected because it creates unnecessary N+1 provider load and couples Home to future pages.

**Show any Kenyan or TMDb item under Stream Now.** Rejected because discovery identity is not playback authorization.

**Always show a disabled Trailer button.** Rejected because absence communicates unavailable capability more accurately than a dead action.

**Fabricate a quote for visual completeness.** Rejected because the homepage must not present invented dialogue as source material.
