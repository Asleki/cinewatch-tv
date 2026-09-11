# CineWatch TV V1.3.3.1 R1 — NexVox CI Projection History Checkout Correction

**Milestone:** CWTV.V1.3.3.1-R1
**Status:** Correction candidate
**Date:** 2026-09-11
**Remote baseline:** `c6d5c298de22d88b818c854240b29b1cee2cc4e1`

## Problem

The provider-runtime source commit and its NexVox projection both qualified locally and were pushed successfully. The subsequent GitHub-hosted Linux quality job failed inside `check_nexvox_engineering_corpus.py` while validating the exact source commit recorded by the projection.

The checkout used the default shallow history. The projection checker intentionally verifies that the source commit named in `sync-state.yaml` exists and that a projection commit binds to its exact source parent. The shallow checkout therefore removed evidence that the checker is required to inspect.

## Correction

The Linux quality job now sets:

```yaml
fetch-depth: 0
```

for its `actions/checkout` step.

This provides complete commit history to the quality job without changing repository permissions, persisting credentials, or exposing application secrets.

The dependency/security job remains shallow because it does not require commit-lineage validation.

## Regression guard

A focused repository test verifies that:

- the quality job retains `persist-credentials: false`;
- the quality job uses `fetch-depth: 0`;
- the security job retains `persist-credentials: false`;
- the security job does not fetch full history;
- the security job does not consume repository/application secrets.

## Scope

This correction does not modify:

- TMDb or OMDb provider behavior;
- provider credentials or local secret files;
- FastAPI runtime behavior;
- PostgreSQL or migration authority;
- NexVox projection validation rules;
- GitHub workflow permissions;
- AWS or deployment architecture.

The correction changes only the Git history made available to the Linux quality job and adds deterministic regression coverage for that requirement.
