# CWTV ADR 0007 — Linux CI, Least Privilege and Supply-Chain Gates

**Milestone:** CWTV.V1.2.8
**Status:** Accepted
**Decision date:** 2026-09-09

## Context

CineWatch already has deterministic local policy and runtime checks, but no
GitHub workflow authority. A private V1 repository still needs repeatable
Linux verification, dependency monitoring, secret exclusion and least-
privilege pull-request execution.

## Decision

1. GitHub-hosted Ubuntu is the remote CI authority.
2. CI runs on pushes to `main`, pull requests targeting `main`, and explicit
   manual dispatch.
3. Workflow repository permission is `contents: read`.
4. `pull_request_target` is prohibited for the V1 quality workflow.
5. Checkout credentials are not persisted.
6. External GitHub Actions are pinned to full-length commit SHAs.
7. The quality job runs existing CineWatch static, repository and Linux-
   portable runtime qualifications.
8. The Termux-only runtime checker remains local and is not executed on
   GitHub-hosted Linux.
9. The security job blocks tracked secret material and known dependency
   vulnerabilities at the configured policy level.
10. Dependabot monitors npm, pip and GitHub Actions.
11. CI receives no CineWatch database, provider, AWS, Azure or GitHub PAT
    secrets.
12. Cloud deployment, CodeQL, container scanning and production security
    operations are deferred until their architecture exists.

## Consequences

Every proposed change gains a reproducible Linux quality result independent
of the Android host.

Dependency and action updates become visible pull requests instead of silent
drift.

Security checks can fail a change without granting CI write access to the
repository or cloud infrastructure.

## Rejected alternatives

- relying only on manual local checks;
- giving CI write-all permissions;
- using `pull_request_target` for untrusted contribution validation;
- passing database or cloud credentials into general pull-request jobs;
- floating third-party action tags as the security baseline;
- running the Termux-specific runtime checker on generic Ubuntu;
- introducing container/cloud scanners before those systems exist.

## Acceptance

Accepted as the CI/security/quality authority for **CWTV.V1.2.8**.
