# CineWatch NexVox Engineering Knowledge Authority 001

**Document ID:** `CWTV-NEXVOX-ENGINEERING-KNOWLEDGE-AUTHORITY-001`
**Product:** CineWatch TV / NexVox
**Repository:** `Asleki/cinewatch-tv`
**Status:** `CANDIDATE`
**Revision:** `001`
**Effective date:** `2026-09-10`

---

## 1. Purpose

This document governs the engineering-knowledge corpus that allows NexVox to learn how CineWatch TV was built.

The corpus preserves architecture, code evolution, engineering decisions, tests, failures, corrections, qualifications, tooling, workflow rules, and human-validated engineering context. It is not a substitute for Git, the CineWatch engineering ledger, or product governance.

## 2. Scope

The corpus MAY represent:

- every reachable Git commit and parent relationship;
- every tracked repository path and historical file version;
- source code, tests, scripts, migrations, contracts, architecture, governance, and workflow documents;
- engineering-event records;
- failure/correction chains;
- qualification evidence;
- architecture decisions;
- dependency relationships;
- curated conversation-derived engineering facts;
- source conflicts and their governed resolution.

The corpus SHALL NOT silently ingest secrets, credentials, private provider data, personal data unrelated to engineering, or third-party material whose training rights are unknown.

## 3. Separation from future product AI data

`nexvox/engineering` is an engineering-history and engineering-knowledge corpus. It is separate from future CineWatch product AI datasets, including user behavior, search history, recommendations, profile data, private activity, content-provider payloads, or other user-facing NexVox data.

No eligibility decision in this corpus authorizes future product/user data for AI training.

## 4. Canonical sources

Authority is domain-specific.

### Git history

Git is canonical for commit existence, parentage, file trees, blobs, file changes, and commit timestamps/messages.

### Engineering activity

`docs/progress/activity/engineering-events.jsonl` is canonical for recorded engineering activities. Generated Chronicle and dashboard files are projections.

### Product and architecture

Approved blueprints, accepted architecture authorities, ADRs, governance documents, qualified implementation, and source code each retain authority within their defined domains.

### Generated contracts

Generated OpenAPI and TypeScript artifacts are downstream projections of canonical API authority. They are preserved for provenance but SHALL NOT be weighted as independent duplicated training authority.

## 5. Training eligibility

Every source and every derived knowledge record SHALL carry one of:

- `TRAINING_ELIGIBLE`;
- `TRAINING_REVIEW_REQUIRED`;
- `REFERENCE_ONLY`;
- `TRAINING_PROHIBITED`.

Inspection of a source does not imply training permission. Unknown permission does not become permission by inference.

## 6. Conversation evidence

Conversation-derived knowledge MUST state whether it is verbatim or transformed. Memory summaries and normalized engineering facts SHALL NOT be represented as verbatim transcripts.

Conversation records require human validation before they may be promoted from `TRAINING_REVIEW_REQUIRED` to `TRAINING_ELIGIBLE`.

## 7. Historical integrity

Failures and corrections SHALL be preserved rather than rewritten away.

If a failure is known from terminal/conversation evidence but absent from the append-only engineering ledger, the corpus SHALL record the discrepancy instead of manufacturing a historical ledger event.

## 8. Generated-output recursion

NexVox-generated datasets, narratives, manifests, and checksums SHALL NOT be recursively re-ingested as primary training source.

The generator may index its governing authority, policy, schema, scripts, and tests after those files exist in a source commit, but generated corpus projections are reference-only.

## 9. Per-commit synchronization

Every ordinary CineWatch engineering commit SHOULD be followed before push by one NexVox projection commit.

The projection commit SHALL identify the exact preceding source commit with:

```text
NexVox-Source-Commit: <40-char SHA>
NexVox-Projection: true
```

A commit with `NexVox-Projection: true` SHALL NOT trigger another projection.

This two-commit design avoids impossible Git self-reference: a commit cannot contain its own final SHA inside one of its files.

## 10. Determinism

Generated corpus content SHALL depend on the declared source commit and governed static inputs, not wall-clock time. Source commit timestamps may be used because they are part of Git authority.

Repeated generation for the same source commit and same governed inputs SHOULD produce byte-identical outputs.

## 11. Local-only PDF

The PDF engineering knowledge book is a local preservation projection. It SHALL remain outside Git and SHALL NOT become source authority. It SHALL be regenerated after every ordinary non-projection source commit, after the tracked corpus has been rebuilt for that exact source commit. A NexVox projection commit SHALL NOT recursively trigger another PDF regeneration.

## 12. Secret exclusion

Corpus generation and checking SHALL fail closed on obvious credential patterns or prohibited private files. Secrets SHALL NOT be copied merely so NexVox can learn that a secret once existed.

## 13. Portability

The corpus uses Markdown, YAML, CSV, and JSONL to remain human-readable and portable across future NexVox training/search infrastructure on AWS, Azure, Google Cloud/Vertex AI, Alibaba Cloud, or other approved platforms.

## 14. Change control

This authority may change only through governed repository revision, validation, explicit staging, commit, push, and engineering-history recording.

---

**Candidate lock:** This document becomes authoritative only after repository qualification and commit.
