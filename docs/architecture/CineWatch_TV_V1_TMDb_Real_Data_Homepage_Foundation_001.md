# CineWatch TV V1 TMDb Real-Data Homepage Foundation

**Milestone:** CWTV.V1.3.3.2.1
**Status:** Implementation candidate
**Primary upstream:** TMDb
**Public surface:** `GET /api/v1/home`

## Purpose

This milestone creates the first CineWatch TV product-data contract. The web application must consume a CineWatch-owned response rather than raw TMDb payloads. TMDb remains the primary entertainment-data provider, while later enrichment providers may participate only behind explicit CineWatch rules.

## Authority chain

```text
TMDb
  -> server-only TmdbClient
  -> HomepageAggregator
  -> CineWatch Pydantic contract
  -> FastAPI /api/v1/home
  -> canonical OpenAPI
  -> generated @cinewatch/contracts types
  -> future CineWatch web homepage
```

No browser code receives provider credentials. No public route contains `tmdb` or `omdb` in its path.

## Homepage response

The V1 response owns five presentation-ready surfaces:

- one hero selected from trending movie or TV data, preferring an item with a backdrop;
- trending entertainment;
- popular movies;
- popular TV;
- trending people.

Each rail is bounded to twelve normalized items in this foundation. The response is not a mirror of a TMDb response. It carries CineWatch field names, stable media types, normalized rating metadata, resolved TMDb image URLs, and governed missing-media instructions.

## Rating authority

TMDb `vote_average` and `vote_count` are retained behind the CineWatch `HomeRating` model. The rating scale is explicitly ten. CineWatch does not invent a replacement score in this milestone.

## Image authority

Image URLs are built from TMDb configuration rather than hard-coded image hosts or sizes. Preferred sizes are `w500` for posters, `w1280` for backdrops, and `w185` for profiles when those sizes are available. The provider's `original` size or another advertised size is used as a deterministic fallback.

Missing media reuses `cinewatch_api.media.fallbacks.MediaGap`.

- missing person profile -> `AWAITING_HUMAN_RESEARCH`;
- missing poster -> existing governed remediation rule;
- missing backdrop -> `GENERATION_ALLOWED`.

This milestone reports missing media but does not fabricate a successful asset. The fallback manifest remains a separate governed authority.

## Provider hierarchy

TMDb is the only unconditional upstream for this homepage foundation.

OMDb is deliberately absent from homepage aggregation. A later field may use OMDb only when a specific CineWatch contract establishes a real information gap and defines deterministic enrichment semantics. The mere availability of an OMDb credential is not a reason to call it.

## Persistence boundary

No PostgreSQL table, migration, repository, cache authority, or AWS resource is introduced here. The first homepage proof is live-provider aggregation. Persistence may be added later only when its ownership, refresh policy, and failure behavior are separately qualified.

## Architectural update neutralization

CineWatch uses updates as replacements of obsolete assumptions, not as layers of contradictory behavior.

The old OpenAPI foundation checker treated the entire route set as a closed list. That assumption was valid while the repository intentionally exposed only the skeleton, but it becomes obsolete once product endpoints begin.

This milestone replaces that closed-list rule with a stable invariant:

- `/health`, `/status`, and `/api/v1/status` remain required foundation routes;
- additional product routes may exist without changing the foundation checker;
- every product surface owns a dedicated checker for its own route, contract, dependencies, and guardrails.

This neutralizes the update at the correct boundary. Future Discover, Watch, Explore, account, or other product routes do not need to edit the V1.2.6 foundation merely because they exist.

If a proposed change would force unrelated features to change together or create circular dependency, implementation stops at the shared boundary. The shared boundary is then stabilized and the feature normalizes into its own contract and checker rather than propagating the change.

## Qualification

Qualification requires:

1. deterministic unit proof of TMDb normalization and media-gap handling;
2. endpoint proof for `GET /api/v1/home`;
3. regenerated canonical OpenAPI;
4. regenerated TypeScript declarations;
5. legacy contract-foundation checker passing without exact product-route enumeration;
6. homepage-specific policy checker passing;
7. backend and repository regression;
8. live local runtime proof against the configured TMDb credential;
9. Chronicle evidence and NexVox projection only after source qualification.
