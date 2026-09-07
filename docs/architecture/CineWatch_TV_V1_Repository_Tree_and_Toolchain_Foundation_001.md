# CineWatch TV V1 Repository Tree and Toolchain Foundation 001

**Document ID:** `CWTV-V1-REPO-TOOLCHAIN-001`
**Milestone:** `CWTV.V1.2.2`
**Revision:** `001`
**Status:** ACTIVE FOUNDATION
**Baseline commit:** `fd6e885`
**Product:** CineWatch TV
**Date:** 2026-09-07

## 1. Purpose

This milestone establishes the first real CineWatch TV engineering repository structure and deterministic toolchain declarations without implementing CineWatch product features.

It creates boundaries capable of later carrying Discover, Watch, Explore, My CineWatch, CineWatch-native persistence, rights and availability authority, provider integrations, cinematic knowledge, cinema foundations, and future NexVox interfaces while keeping those capabilities out of scope for this milestone.

## 2. Scope lock

`CWTV.V1.2.2` establishes:

- root npm workspace authority;
- one root `package-lock.json`;
- Node and npm runtime policy;
- Python runtime policy and backend project metadata;
- governed web, API-service, contract-package, script, and test boundaries;
- formatting/whitespace policy;
- reusable runtime and repository-tree qualification scripts;
- environment-file conventions already established by `.env.example`;
- Termux-compatible validation;
- Linux-CI-compatible repository metadata;
- repository-tree tests;
- documentation of directory ownership.

This milestone does not implement Discover, Watch, Explore, My CineWatch, authentication, database schemas, migrations, playback, provider adapters, rights receipts, OpenAPI generation, or production deployment.

## 3. Repository authority

The initial repository topology is:

```text
cinewatch-tv/
├── apps/
│   └── web/
├── services/
│   └── api/
├── packages/
│   └── contracts/
├── scripts/
├── tests/
│   └── repository/
├── docs/
│   ├── architecture/
│   │   └── decisions/
│   ├── blueprints/
│   └── governance/
├── .editorconfig
├── .env.example
├── .gitattributes
├── .gitignore
├── .npmrc
├── .nvmrc
├── .python-version
├── package.json
└── package-lock.json
```

The backend path refinement from the R1 architecture illustration is recorded by `CWTV-ADR-0001`.

## 4. JavaScript workspace authority

The root `package.json` is private and owns npm workspace discovery.

Initial workspaces:

```text
apps/web
packages/contracts
```

The Python backend is not an npm workspace.

The repository uses:

- Node.js `24.18.0` as the initial exact toolchain declaration;
- Node 24 as the governed major line;
- npm `12.0.2` as the package-manager authority recorded in `packageManager`;
- npm 12 as the governed major line;
- one root `package-lock.json` using lockfile version 3;
- no pnpm workspace or lockfile.

The exact patch versions are versioned engineering baselines and may be advanced by a later governed toolchain update without changing the Node 24/npm 12 major-line decision.

## 5. Python authority

The initial Python engineering declaration is `3.14.6`, with Python 3.14 as the governed V1 line.

`services/api/pyproject.toml` establishes:

- project identity `cinewatch-api`;
- `>=3.14,<3.15` compatibility policy;
- empty runtime dependencies at this milestone;
- initial Ruff policy;
- initial pytest discovery policy.

FastAPI, Pydantic, SQLAlchemy, psycopg, Alembic, pytest, and other backend runtime/development dependencies are introduced deliberately in subsequent backend/database milestones rather than smuggled into the repository-tree milestone.

## 6. Boundary ownership

### 6.1 `apps/web`

Reserved for the CineWatch TV Next.js web application. The boundary exists now; the frontend skeleton begins in `CWTV.V1.2.4`.

### 6.2 `services/api`

Reserved for the FastAPI backend service authority. The boundary exists now; backend implementation begins in `CWTV.V1.2.3`.

### 6.3 `packages/contracts`

Reserved for generated or governed TypeScript API-contract artifacts. FastAPI OpenAPI remains canonical. Contract generation begins in `CWTV.V1.2.6`.

### 6.4 `scripts`

Contains deterministic repository engineering and qualification scripts. Scripts must remain Termux-usable when their required runtimes exist.

### 6.5 `tests`

Contains cross-cutting repository qualification. Product and service tests remain colocated or governed by their later milestone architecture.

## 7. Environment and secrets convention

The root `.env.example` remains a names-only public template.

Rules:

- `.env` and secret variants remain Git-ignored;
- no credentials are added to package metadata, source, scripts, tests, or documentation;
- application-specific environment variables are added only when the owning milestone introduces the corresponding runtime capability;
- cloud secret stores inject normalized configuration later;
- local Termux configuration must not become repository authority.

## 8. Termux and Linux CI

The repository can be edited, inspected, and qualified from the observed Android/Termux environment.

The runtime check requires:

- Python 3.14;
- Node 24;
- npm 12;
- Git.

PostgreSQL client and GitHub CLI are reported when present but are not generic Linux prerequisites for this milestone.

Linux CI remains authoritative for production build steps that later depend on native tooling unavailable on Android.

## 9. Formatting baseline

`.editorconfig` is tightened so Markdown trailing whitespace is removed like other text files. This prevents the trailing-whitespace failure observed during the initial governance commit.

JSON and web-oriented files use two-space indentation. General text/Python remain four-space by default unless a language-specific formatter later governs the file.

## 10. Qualification

The repository foundation must pass:

1. runtime policy check;
2. repository-tree deterministic check;
3. repository unittest qualification;
4. npm workspace metadata validation;
5. `git diff --check`;
6. secret-pattern review before commit;
7. clean post-commit worktree.

No product-feature test is expected because no product feature is introduced.

## 11. Forward boundary

After this milestone is committed, the next implementation milestone is:

`CWTV.V1.2.3 — Backend Service Skeleton`

That milestone may introduce the first FastAPI runtime, health/status contract, backend dependency lock strategy, and service tests. It must not silently absorb database schema work reserved for `CWTV.V1.2.5`.
