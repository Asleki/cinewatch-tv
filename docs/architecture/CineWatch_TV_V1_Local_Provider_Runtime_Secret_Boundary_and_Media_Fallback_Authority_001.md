# CineWatch TV V1 Local Provider Runtime, Secret Boundary & Media Fallback Authority 001

**Document ID:** `CWTV-V1-PROVIDER-RUNTIME-001`
**Milestone:** `CWTV.V1.3.3.1`
**Status:** IMPLEMENTATION CANDIDATE

## 1. Purpose

This milestone establishes the first real external-provider runtime without creating product pages, PostgreSQL dependencies, cloud dependencies, or a second application backend. It prepares CineWatch TV for the real-data homepage in `CWTV.V1.3.3.2`.

TMDb is the primary entertainment-data upstream. OMDb is the first governed enrichment upstream. CineWatch owns its canonical application model and may call secondary providers only for a defined missing or enrichment capability.

## 2. Locked service boundary

`services/api` remains the only CineWatch application API and provider-policy authority. Next.js SHALL NOT call TMDb, OMDb, or another provider directly and SHALL NOT create `src/app/api` product/provider routes.

Provider credentials SHALL be consumed only by FastAPI-side Python code. Browser-visible `NEXT_PUBLIC_*` variables remain limited to CineWatch-owned public URLs and configuration.

## 3. Local secret boundary

Private V1 development may use real provider credentials before AWS secret infrastructure exists. Real values belong in root `.env.local` or process environment variables. `.env.local` is ignored by Git and any tracked `.env*` secret file other than `.env.example` is prohibited by repository policy.

Committed `.env.example` contains variable names only. Provider values SHALL never be copied into source, tests, screenshots intended for source control, generated OpenAPI, or NexVox.

The backend loads `.env` followed by `.env.local`; the latter is the preferred private developer override. Provider keys are represented with Pydantic `SecretStr`.

## 4. Provider runtime V1

The initial runtime adapters are:

- **TMDb** — primary movie, television, person, artwork, discovery, recommendation, review, video and external-identity upstream where its contract permits;
- **OMDb** — secondary enrichment by IMDb identity where TMDb does not supply a required external rating or enrichment field.

`httpx==0.28.1` is the qualified provider HTTP client. Adapters normalize configuration, transport, authentication, rate-limit, upstream-server and invalid-payload failures without exposing provider secrets.

No provider product endpoint is added in this mini-milestone. Live credentials are qualified explicitly with `scripts/probe_provider_runtime.py`; CI remains deterministic and credential-free.

## 5. Live versus deterministic qualification

Repository and CI tests use mocked provider responses. They SHALL NOT depend on provider uptime or real credentials.

A developer may explicitly run:

```bash
python scripts/probe_provider_runtime.py tmdb
python scripts/probe_provider_runtime.py omdb --imdb-id tt0111161
```

These probes read private local configuration, perform real HTTPS requests, and print only pass/fail evidence and non-secret identities.

## 6. Media completeness and fallback authority

A missing upstream image is an engineering state, not an unstructured browser defect. CineWatch represents a missing asset as a deterministic media gap with provider, entity type, provider identity, canonical display name, asset kind, remediation policy, suggested filename and public fallback path.

The initial deterministic naming form is:

```text
<provider>-<entity-type>-<provider-id>-<slug>.webp
```

Examples:

```text
tmdb-person-123456-jane-example.webp
tmdb-network-213-example-network.webp
tmdb-movie-550-example-title.webp
```

Directory authority determines the asset role:

```text
apps/web/public/provider-fallbacks/
├── people/
├── networks/
├── posters/
├── backdrops/
└── manifest.json
```

`python scripts/reconcile_provider_fallbacks.py` validates WebP containers, deterministic names, entity/directory compatibility, hashes and sizes, then regenerates the manifest. `--check` is deterministic and suitable for CI.

## 7. Human and generated media policy

The following rule is locked for V1:

| Missing asset | Remediation |
|---|---|
| real-person profile | `AWAITING_HUMAN_RESEARCH` |
| network logo | `GENERATION_ALLOWED` |
| title/network backdrop | `GENERATION_ALLOWED` |
| movie/TV poster | `AWAITING_HUMAN_RESEARCH` until a later explicit rule changes it |

A missing real-person profile SHALL NOT be replaced with a generated likeness. The human workflow is: research several authentic candidates from credible sources; compare identity confidence, quality, crop suitability, watermarking, source credibility and rights suitability; select the best candidate; normalize and convert it to WebP; rename it to the architecture-suggested filename; place it in `provider-fallbacks/people`; reconcile the manifest.

Generated logos/backdrops SHALL be neutral CineWatch fallback media and SHALL NOT pretend to be an official provider/rightsholder asset.

## 8. Fallback precedence

For a required image the future canonical service SHALL apply:

```text
provider asset
  -> governed authentic local fallback
  -> generation-eligible neutral CineWatch fallback where policy permits
  -> safe generic presentation state
```

The real-data homepage milestone will connect completeness detection to a machine-readable media-gap report so missing assets become immediate remediation tasks.

## 9. Explicitly out of scope

This mini-milestone does not add the real homepage, Discover/Watch/Explore routes, PostgreSQL persistence, AWS deployment, caching, background ingestion, public indexing, user accounts, hosted playback, or commercial provider rights. Provider use remains subject to the CineWatch API/content-rights qualification register and provider-specific terms.

## 10. Qualification

The milestone is qualified only when the provider checker, backend tests, repository regression, fallback reconciliation, existing security gate and whitespace gate pass, followed by explicit local TMDb/OMDb probes when the developer supplies private credentials.
