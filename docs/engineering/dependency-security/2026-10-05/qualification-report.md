# CineWatch dependency security correction — GHSA-vcvr-r3jv-pc5j

Starting Main was independently verified as `854ba0772232a1b8096426697334d5fe80f8fcce`. The GitHub advisory and Next.js repository advisory both identify versions `>=16.2.0,<16.3.6` as affected, with `16.3.6` the first patched version. The Node.js next/og ImageResponse exploit conditions are source-reported; this correction does not claim the CineWatch site was exploited.

## Narrow correction

Source `195005ee12c14be6401280319853aa2fa2ba33ff` changes only `apps/web/package.json`, `package-lock.json` and the existing exact Next.js authority in `scripts/check_frontend_skeleton.py`. Next.js is exact-pinned at 16.3.6. Eleven lock entries changed: workspace manifest, Next.js, @next/env and eight patch-matched SWC platform packages. No unrelated package/version/metadata or top-level lock churn was accepted. React/React DOM, Node 24.18.0, npm 12.0.2, TypeScript and eslint-config-next 16.3.4 are unchanged. Existing lint, types and production runtime passed without ESLint patch alignment. npm audit fix --force was not used.

## Qualification and publication

Local checks passed: 20 repository tests, 83 API tests, 3 contract subset tests and 6 migration subset tests; repository, policy and secret checks; OpenAPI and generated TypeScript parity; contracts/backend/frontend runtime; lint/typecheck/production build; offline PostgreSQL migration; pip check/strict pip-audit; production npm audit; whitespace and post-commit tracked-file drift checks. Subset counts overlap the full API suite. The initial strict Python audit failed before auditing because its cache was read-only; a writable cache retry passed with no known vulnerabilities. That bootstrap failure is preserved. A local PDF retry used existing reportlab outside the API qualification venv.

Production npm audit changed from one critical finding to zero vulnerabilities. Full npm audit retains eight high-severity development findings; the existing CI workflow treats that full report as advisory. These findings are reported, not silently fixed or described as absent.

The initial requested ordering could not satisfy canonical CI because every ordinary source commit requires its immediate NexVox projection. The owner’s later concurrent-authority clarification permitted the CineWatch-local source → projection pair specifically required by CI. Chronicle/evidence closure and Praxis ingestion waited for fully green source CI. No NexVox AI repository writes occurred.

Candidate projection `31e2b4da9e8d8a40cf50f52d5347b30d723ea35e` binds exactly to source 195005ee. Branch dispatch CI 37329234294 passed both required jobs. PR 14 CI 37329456030 failed its synthetic merge checkout freshness gate, not the dependency correction; its checkout SHA differed from the recorded projection HEAD. Existing workflow_dispatch ran the exact candidate without workflow changes. After refreshing unchanged Main, a non-force update promoted the exact qualified pair. Main push CI 37329625428 passed both jobs. No squash or unrelated merge commit replaced source/projection identities.

## Authority and stop boundary

CineWatch-local engineering projection remains in CineWatch. A later filtered Praxis successor is permitted only after this qualification and final projection, from freshly inspected Praxis Main. The separate NexVox AI task owns the NexVox AI repository; this task neither writes it nor declares routing synchronized without that task’s final report.

The next unused Chronicle identifier `CWTV.V1.3.3.2.4` is reserved for this dependency-security correction, separate from discovery release CWTV.V1.3.3.2.3. Historical events and failures remain append-only. External-advisory interpretation and Codex synthesis are review-required for training, even when machine evidence proves byte integrity.

002 remains immutable and unapplied. Its 53 paths currently have zero collisions with the inspected starting-Main/security delta, but the required old-base check remains 304bc33e. The companion reconciliation plan requires reconstructing 002 on that exact old base, then three-way reconciliation onto qualified new Main and separately versioned 003. No AWS call, EC2 change, deployment, DB mutation or service restart was performed.
