# CWTV ADR 0006 — Termux Host, Linux Runtime and Named Engineering Sessions

**Milestone:** CWTV.V1.2.7
**Status:** Accepted
**Decision date:** 2026-09-09

## Context

CineWatch TV is developed primarily from Android. Native Termux is reliable
for Git, GitHub, downloads, native PostgreSQL client work and general shell
operations. The application stack also needs a normal Linux runtime because
native Android Python package compatibility is not a production architecture
constraint.

The developer also needs multiple simultaneous responsibilities without
reconstructing environment state in anonymous terminal tabs.

## Decision

1. Termux is the host and repository workspace authority.
2. Ubuntu PRoot `cwtv-linux` is the authoritative Linux runtime for the
   FastAPI/Next.js/contract/test toolchain.
3. A single named tmux session, `cinewatch-tv`, owns nine named task windows:
   `api`, `web`, `postgres`, `tests`, `contracts`, `extract`, `git`, `aws`,
   and `chronicle`.
4. `api`, `web`, `tests` and `contracts` execute through `cwtv-linux`.
5. `postgres`, `extract`, `git`, `aws` and `chronicle` remain native Termux.
6. No database password, GitHub token or raw AWS credential is embedded in
   repository files or launcher commands.
7. Future PostgreSQL password persistence uses `.pgpass` with mode `600`.
8. Future AWS work uses a named AWS profile.
9. GitHub persistence uses GitHub CLI/SSH authentication rather than exported
   token literals.
10. CineWatch and NPP remain separate repositories, sessions, database
    identities, Python environments and cloud profiles.
11. The launcher prepares shells but does not auto-start servers or mutate
    cloud/database resources.

## Consequences

The engineering environment becomes recoverable with a short command while
retaining Linux production parity and explicit secret boundaries.

A phone or Termux restart no longer requires the developer to remember the
nine role-specific initialization sequences.

Cloud/database provisioning remains deferred to its own milestone.

## Rejected alternatives

- Native Android Python as application runtime authority.
- Anonymous Termux tabs with manually repeated setup.
- Storing database passwords in shell profiles or repository `.env` files.
- Exporting GitHub tokens or raw AWS credentials from the launcher.
- Sharing NPP database/session/cloud identities with CineWatch.
- Automatically starting servers on session creation.

## Acceptance

Accepted for **CWTV.V1.2.7** as the governed CineWatch V1 mobile/Linux
engineering-session architecture.
