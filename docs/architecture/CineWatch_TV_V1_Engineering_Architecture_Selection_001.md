# CineWatch TV V1 Engineering Architecture Selection 001

**Document ID:** `CWTV-V1-ENG-ARCH-001`
**Milestone:** `CWTV.V1.2.1`
**Revision:** `R1`
**Status:** APPROVED
**Baseline commit:** `56c4ffd711615d94a50d213387a74ce5acd36d09`
**Product:** CineWatch TV
**Date:** 2026-09-07

## 1. Purpose

This document selects the CineWatch TV V1 engineering direction without copying the Nexa Provider Platform (NPP) runtime architecture. NPP/AWS material is evidence of existing skills, infrastructure experience, and operational lessons only.

The selection must satisfy four constraints simultaneously:

1. CineWatch is an independent product and application authority.
2. NPP may later act as a governed provider to CineWatch and other Nexa systems, but NPP is not CineWatch storage authority.
3. the current AWS student development period ends on 2027-01-29, so CineWatch V1 crosses a planned AWS-to-Azure transition;
4. Android/Termux is a supported engineering client, while Linux CI remains authoritative for platform-specific production builds.

## 2. Evidence and observed development environment

### 2.1 Existing-capability evidence

The supplied NPP/AWS evidence demonstrates prior work with IAM/MFA, budgets/credits, VPC/security groups, RDS PostgreSQL, EC2, Systems Manager, CloudWatch, Git/GitHub, and Python/server deployment.

These capabilities are inputs to CineWatch architecture selection. They are not implementation templates.

### 2.2 Termux runtime qualification — 2026-09-07

Observed on the primary Android engineering device:

- Android: 16
- architecture: `aarch64`
- Git: `2.55.0`
- GitHub CLI: `2.100.0`
- Python: `3.14.6`
- pip: `26.2.1`
- Node.js: `24.18.0`
- npm: `12.0.2`
- Corepack: `0.35.0` installed globally but not required by CineWatch
- PostgreSQL client: `18.2`
- pnpm: unavailable because its installer reported no prebuilt binary for `android-arm64`
- uv: not installed and not required on Termux
- Termux prefix footprint: approximately `903M`
- CineWatch worktree footprint at qualification: approximately `891K`
- device free storage at qualification: approximately `12G`

The failed pnpm installation is treated as architecture evidence, not a local setup defect.

## 3. Authority locks

### ENG-LOCK-001 — Independent CineWatch database authority

CineWatch TV SHALL maintain a PostgreSQL database authority separate from NPP.

`npp_dev` SHALL NOT contain CineWatch-native application state.

The CineWatch development database identity SHALL be `cinewatch_dev` unless a later governed migration changes the environment naming convention.

At minimum CineWatch SHALL have its own:

- database identity;
- owner/application roles;
- credentials;
- migrations;
- backup and restore evidence;
- access policy;
- application connection configuration.

Whether `cinewatch_dev` initially receives a physically dedicated managed PostgreSQL server or is hosted as an independently owned database on shared PostgreSQL infrastructure is a cost/isolation decision. Logical authority separation is mandatory either way.

### ENG-LOCK-002 — NPP provider boundary

NPP may later provide qualified data or services to CineWatch, NexVox, NexiLabs, or other Nexa products.

CineWatch SHALL consume such NPP capabilities through governed service/data contracts. CineWatch application code SHALL NOT use direct ownership of NPP tables as its runtime model.

### ENG-LOCK-003 — CineWatch infrastructure namespace

CineWatch-specific infrastructure SHALL use a CineWatch-owned namespace. NPP-specific resource names SHALL NOT be reused merely because both products currently occupy the same AWS student account.

Initial resource naming direction:

`cinewatch-v1-<environment>-<resource>`

The exact shortened naming rules may be refined in the infrastructure milestone, but the CineWatch/NPP namespace boundary is locked.

### ENG-LOCK-004 — Cloud portability

The AWS-to-Azure transition is a V1 engineering event, not an afterthought.

CineWatch domain/application code SHALL depend on normalized PostgreSQL, configuration, storage, identity, logging, and service boundaries rather than embedding AWS-only semantics into domain logic.

### ENG-LOCK-005 — Provider-neutral identity crosswalk

CineWatch SHALL own its application profile identity and SHALL crosswalk any external identity provider using provider plus external subject identifiers.

Authentication passwords SHALL NOT be CineWatch application data.

### ENG-LOCK-006 — Termux-supported engineering

The repository SHALL remain editable and operable from Termux. Tooling that lacks reliable Android support SHALL NOT be a mandatory local prerequisite.

Linux CI and/or a Linux development host SHALL be authoritative for build steps that depend on native tooling unavailable on Android.

### ENG-LOCK-007 — Containers are deployment artifacts

CineWatch web/API services SHALL be containerizable for cloud portability, but Docker SHALL NOT be required for the primary Termux workflow.

### ENG-LOCK-008 — FastAPI owns backend application authority

Next.js SHALL NOT become a second business-logic backend. Rights enforcement, persistence, provider policy, canonical application APIs, and CineWatch domain rules SHALL remain behind the FastAPI service boundary.

### ENG-LOCK-009 — OpenAPI contract authority

FastAPI-generated OpenAPI SHALL be the canonical runtime API schema. TypeScript types/clients SHALL be generated or checked against it to prevent drift.

### ENG-LOCK-010 — Migration-owned schema

All CineWatch PostgreSQL schema changes SHALL be represented by ordered migrations. Ad hoc production schema mutation is prohibited.

### ENG-LOCK-011 — Secrets outside source

Cloud secret systems may inject runtime values, but application code SHALL consume normalized configuration keys and SHALL NOT contain provider credentials.

## 4. Selected application stack

### 4.1 Web

Selected direction:

- Next.js App Router;
- React;
- TypeScript;
- Server Components by default;
- Client Components only where interaction requires them;
- semantic design tokens and shared CineWatch components;
- no private provider secrets in browser bundles.

Linux CI is the authoritative web production-build environment. A successful local Next.js native build on Android SHALL NOT be a release gate.

### 4.2 Backend

Selected direction:

- Python 3.14 foundation;
- FastAPI;
- Pydantic v2;
- SQLAlchemy 2.x;
- psycopg 3;
- Alembic;
- pytest;
- Ruff;
- static type checking to be selected and qualified during repository/toolchain implementation.

The repository SHALL use standard `pyproject.toml` metadata. Termux local setup SHALL work through Python `venv` plus pip. `uv` may be used by Linux CI later if beneficial, but it SHALL NOT be the only supported dependency path.

### 4.3 PostgreSQL

CineWatch server target: PostgreSQL 17.

Termux client observed: PostgreSQL 18.2.

The client/server major-version difference is intentional. Installing the current Termux client does not change the CineWatch server target.

Initial development database identity: `cinewatch_dev`.

The final AWS physical topology SHALL be selected after cost/isolation qualification against remaining AWS student credits and the existing NPP burn rate.

### 4.4 JavaScript package management

Selected direction after Termux qualification:

- npm workspaces;
- root `package.json`;
- one root `package-lock.json`;
- Node.js 24 LTS line;
- npm 12 line, with the initial qualified toolchain at `12.0.2`;
- no pnpm requirement;
- no `pnpm-workspace.yaml`;
- no Turborepo requirement in the initial foundation;
- Corepack presence is tolerated but CineWatch does not depend on it.

This R1 decision supersedes the proposal's pnpm-workspace direction because pnpm installation failed on the primary `android-arm64` Termux device.

### 4.5 API contract

- FastAPI OpenAPI output is canonical runtime schema;
- TypeScript API types are generated from or checked against OpenAPI;
- CineWatch web uses a typed API adapter rather than arbitrary raw external-provider calls;
- checked-in OpenAPI artifacts require deterministic generation plus drift qualification.

## 5. Repository topology

Selected initial topology:

```text
cinewatch-tv/
├── .github/
│   └── workflows/
├── apps/
│   ├── api/
│   │   ├── src/cinewatch_api/
│   │   │   ├── api/v1/
│   │   │   ├── application/
│   │   │   ├── core/
│   │   │   ├── domain/
│   │   │   ├── integrations/
│   │   │   ├── repositories/
│   │   │   └── main.py
│   │   ├── migrations/
│   │   ├── tests/
│   │   └── pyproject.toml
│   └── web/
│       ├── public/
│       ├── src/
│       │   ├── app/
│       │   ├── components/
│       │   ├── features/
│       │   ├── lib/
│       │   └── styles/
│       └── package.json
├── packages/
│   ├── api-contract/
│   └── design-tokens/
├── infrastructure/
│   ├── aws/
│   ├── azure/
│   └── containers/
├── scripts/
├── docs/
│   ├── architecture/
│   │   └── decisions/
│   ├── blueprints/
│   └── governance/
├── .editorconfig
├── .env.example
├── .gitattributes
├── .gitignore
├── package.json
├── package-lock.json
└── README.md
```

Provider-specific infrastructure remains outside application/domain code.

## 6. Cloud execution model

### 6.1 AWS development phase

AWS remains the current development cloud until the student-plan transition.

CineWatch receives its own PostgreSQL authority. Compute topology is selected by cost, isolation, portability, and private-beta requirements rather than copied from NPP.

No CineWatch resource SHALL require an Elastic IP merely because NPP used one.

### 6.2 Planned Azure phase

CineWatch and NPP remain independent authorities during and after migration.

Conceptual target:

```text
AWS
├── NPP PostgreSQL authority
└── CineWatch PostgreSQL authority

        ↓ governed migration

Azure
├── NPP PostgreSQL authority
└── CineWatch PostgreSQL authority
```

Migration tooling SHALL be selected according to database size, downtime tolerance, and the Azure service available at cutover. Standard PostgreSQL export/restore remains the portability baseline.

### 6.3 Credit discipline

Student credits are an engineering constraint. CineWatch SHALL NOT duplicate always-on infrastructure merely for naming symmetry when equivalent authority/isolation can be obtained more economically.

Cost optimization SHALL NOT weaken the independent CineWatch data-authority boundary.

## 7. Authentication direction

V1.2 establishes an identity-provider abstraction only.

The concrete provider is selected in `CWTV.V1.5 — Identity & Private Membership`.

CineWatch profile continuity SHALL survive a provider migration through governed identity crosswalks.

## 8. Observability and configuration

Initial requirements:

- structured logs in deployed environments;
- request/correlation IDs;
- OpenTelemetry-compatible instrumentation boundary;
- normalized environment configuration;
- secrets outside Git;
- no requirement that domain logic import AWS- or Azure-specific SDKs.

## 9. Deliberately excluded from V1.2 foundation

The following are not selected without later evidence:

- Redis;
- Elasticsearch/OpenSearch;
- Kafka;
- Celery;
- Kubernetes;
- GraphQL;
- proprietary vector databases;
- PostgreSQL vector extensions;
- custom DRM;
- CineWatch-owned video CDN.

## 10. Initial CI and qualification direction

GitHub Actions on Linux SHALL be the authoritative automated qualification environment.

Expected early gates:

- repository and trailing-whitespace checks;
- Python dependency reproducibility;
- backend lint/format check;
- backend static type check;
- backend tests;
- npm clean/frozen install behavior using the committed lockfile;
- frontend lint;
- frontend type check;
- frontend tests;
- frontend production build;
- OpenAPI contract drift check;
- security/dependency checks.

## 11. V1.2 mini-milestone sequence

1. `CWTV.V1.2.1` — Existing Capability Inventory & Engineering Architecture Selection
2. `CWTV.V1.2.2` — Repository Tree & Toolchain Foundation
3. `CWTV.V1.2.3` — Backend Service Skeleton
4. `CWTV.V1.2.4` — Frontend Application Skeleton
5. `CWTV.V1.2.5` — PostgreSQL & Migration Foundation
6. `CWTV.V1.2.6` — OpenAPI & Typed Contract Foundation
7. `CWTV.V1.2.7` — Termux/Linux Development Workflow
8. `CWTV.V1.2.8` — CI, Security & Quality Gates
9. `CWTV.V1.2.9` — Container & Cloud-Portability Foundation
10. `CWTV.V1.2.10` — Repository Engineering Regression & V1.2 Freeze

## 12. Approval

**Document ID:** `CWTV-V1-ENG-ARCH-001`

**Revision:** `R1`

**Milestone:** `CWTV.V1.2.1`

**Status:** APPROVED

**Approved by:** Alex Malunda

**Approval statement:** I approve CWTV-V1-ENG-ARCH-001 Revision R1.

**Approval recorded:** 2026-09-07 20:10:58 CAT (UTC+02:00)

**Approval mode:** Explicit user approval recorded in the CineWatch TV engineering session.

**Baseline commit:** `56c4ffd711615d94a50d213387a74ce5acd36d09`

**Approved candidate package SHA-256:** `bbc83113a3b68a89f1952d277498eaf2ce95ef88a26bf71782b8f731d6c6a3d6`

This approved R1 architecture document is repository-ready at:

`docs/architecture/CineWatch_TV_V1_Engineering_Architecture_Selection_001.md`

No application code is introduced by this architecture-selection milestone.
