# CWTV ADR 0008 — Provider Runtime and Media Fallback Authority

**Status:** Accepted for `CWTV.V1.3.3.1` implementation candidate.

## Context

CineWatch TV now needs real provider data for V1 browser qualification. The frontend architecture already prohibits direct external-provider calls, and local development must support private credentials before AWS secret infrastructure is introduced. Provider responses may also omit posters, person images, logos or backdrops.

## Decision

FastAPI remains the exclusive provider-policy boundary. TMDb is the primary entertainment-data upstream; OMDb begins as a capability-specific enrichment provider. Next.js consumes CineWatch-owned API contracts only.

Real local credentials are stored only in ignored `.env.local` or process environment values and are represented by backend `SecretStr` settings. CI uses mocks and never receives provider secrets. Live provider qualification is explicit and local-only.

Missing provider media is represented as a deterministic media gap. Fallback assets use stable provider/entity identities in WebP filenames and a generated manifest. Real-person profiles require human research and authentic-source selection; synthetic person likenesses are prohibited. Neutral generated fallback media is allowed for logos and backdrops, provided it does not masquerade as official rightsholder artwork. Posters remain human-research remediation until explicitly changed.

## Consequences

The upcoming homepage can use real data without leaking provider keys into the browser, and missing media can be surfaced as exact remediation work rather than discovered ad hoc. AWS Secrets Manager, PostgreSQL persistence and production caching can replace local mechanisms later without changing the web/provider boundary.
