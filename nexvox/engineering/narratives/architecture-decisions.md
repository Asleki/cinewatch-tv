# CineWatch Architecture and Decisions

**Source commit:** `20e851e5eb0577831b0b05bc3cb6c92ee6319e43`

This projection summarizes ADRs and architecture evidence; source documents remain authoritative.

## CWTV-ADR-0001 - CWTV ADR 0001 — Repository Service Boundary Naming

Source: `docs/architecture/decisions/CWTV_ADR_0001_Repository_Service_Boundary_Naming.md`

The initial V1 repository tree SHALL use: ```text apps/web services/api packages/contracts ``` `services/api` emphasizes that the FastAPI backend is an independent service authority rather than a frontend application package. `packages/contracts` remains implementation-neutral while FastAPI-generated OpenAPI stays the canonical runtime API schema.

## CWTV-ADR-0002 - CWTV ADR 0002 — Backend System Endpoints and Request Identity

Source: `docs/architecture/decisions/CWTV_ADR_0002_Backend_System_Endpoints_and_Request_Identity.md`

1. `/health` is an unversioned liveness endpoint. 2. `/status` is an unversioned operational service-status endpoint. 3. `/api/v1/status` proves the versioned API namespace without adding a product feature. 4. Every HTTP response receives `X-Request-ID`. 5. Safe caller request IDs may propagate; missing or invalid IDs are replaced. 6. System status reports only service-skeleton readiness at this milestone.

## CWTV-ADR-0003 - CWTV ADR 0003 — Frontend Runtime and Build Portability

Source: `docs/architecture/decisions/CWTV_ADR_0003_Frontend_Runtime_and_Build_Portability.md`

CineWatch TV V1 uses Next.js 16.3.4 App Router with React 19.2.8 and TypeScript 6.0.3 under the existing Node 24/npm 12 toolchain authority. `next dev --webpack` and `next build --webpack` are the initial governed web commands. Native Android/Termux is not a production-build gate. Full Next.js runtime qualification runs in Linux userland and later Linux CI.

## CWTV-ADR-0004 - ADR 0004 — PostgreSQL Authority & Migration Boundary

Source: `docs/architecture/decisions/CWTV_ADR_0004_PostgreSQL_Authority_and_Migration_Boundary.md`

CineWatch native application state will use an independent PostgreSQL database authority, development identity `cinewatch_dev`, accessed by the FastAPI service through SQLAlchemy 2.x and Psycopg 3. Alembic is the only schema-migration authority. The migration lineage begins with `0001_postgresql_foundation`, an intentionally empty root migration. Product-domain schemas are deferred to their owning milestones. `DATABASE_URL` is secret configuration. Only `postgresql+psycopg` URLs are accepted. SQLite fallback is prohibited.

## CWTV-ADR-0005 - CWTV ADR 0005 — OpenAPI Canonical Contract and Type Generation

Source: `docs/architecture/decisions/CWTV_ADR_0005_OpenAPI_Canonical_Contract_and_Type_Generation.md`

FastAPI/Pydantic declarations are the API schema authority. CineWatch checks in one deterministic OpenAPI 3.1 JSON projection and generates TypeScript declarations from that document with pinned `openapi-typescript`. Every route receives an explicit operation ID before it becomes part of the governed contract. Frontend code imports generated response types through `@cinewatch/contracts`; it must not independently duplicate backend response interfaces.

## CWTV-ADR-0006 - CWTV ADR 0006 — Termux Host, Linux Runtime and Named Engineering Sessions

Source: `docs/architecture/decisions/CWTV_ADR_0006_Termux_Host_Linux_Runtime_and_Named_Sessions.md`

1. Termux is the host and repository workspace authority. 2. Ubuntu PRoot `cwtv-linux` is the authoritative Linux runtime for the FastAPI/Next.js/contract/test toolchain. 3. A single named tmux session, `cinewatch-tv`, owns nine named task windows: `api`, `web`, `postgres`, `tests`, `contracts`, `extract`, `git`, `aws`, and `chronicle`. 4. `api`, `web`, `tests` and `contracts` execute through `cwtv-linux`. 5. `postgres`, `extract`, `git`, `aws` and `chronicle` remain native Termux. 6. No database password, GitHub token or raw AWS credential is embedded in repository files or launcher commands. 7. Future PostgreSQL password persistence uses `.pgpass` with mode `600`. 8. Future AWS work uses a named AWS profile. 9. GitHub persistence uses GitHub CLI/SSH authentication rather than exported token literals. 10. CineWatch and NPP remain separate repositories, sessions, database identities, Python environments and cloud profiles. 11. The launcher prepares shells but does not auto-start servers or mutate cloud/database resources.

## CWTV-ADR-0007 - CWTV ADR 0007 — Linux CI, Least Privilege and Supply-Chain Gates

Source: `docs/architecture/decisions/CWTV_ADR_0007_Linux_CI_Least_Privilege_and_Supply_Chain_Gates.md`

1. GitHub-hosted Ubuntu is the remote CI authority. 2. CI runs on pushes to `main`, pull requests targeting `main`, and explicit manual dispatch. 3. Workflow repository permission is `contents: read`. 4. `pull_request_target` is prohibited for the V1 quality workflow. 5. Checkout credentials are not persisted. 6. External GitHub Actions are pinned to full-length commit SHAs. 7. The quality job runs existing CineWatch static, repository and Linux- portable runtime qualifications. 8. The Termux-only runtime checker remains local and is not executed on GitHub-hosted Linux. 9. The security job blocks tracked secret material and known dependency vulnerabilities at the configured policy level. 10. Dependabot monitors npm, pip and GitHub Actions. 11. CI receives no CineWatch database, provider, AWS, Azure or GitHub PAT secrets. 12. Cloud deployment, CodeQL, container scanning and production security operations are deferred until their architecture exists.
