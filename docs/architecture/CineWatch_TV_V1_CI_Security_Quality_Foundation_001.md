# CineWatch TV V1 — CI / Security / Quality Foundation

**Milestone:** CWTV.V1.2.8
**Document:** CWTV-V1-ENG-CI-001
**Status:** Candidate for qualification
**Baseline:** `50a453e1efccba0d963d2990b7c6a528fc35ffcf`

## 1. Purpose

CWTV.V1.2.8 makes Linux continuous integration an authoritative quality gate
for CineWatch changes while preserving the local Termux/Linux workflow from
CWTV.V1.2.7.

The milestone adds no product functionality and provisions no cloud resource.

## 2. Inspected baseline

The live repository inspection established:

- clean `main` synchronized with `origin/main` at `50a453e1efccba0d963d2990b7c6a528fc35ffcf`;
- no pre-existing `.github` workflow files;
- seven repository regression tests before this milestone;
- existing repository, backend, frontend, database, contract, Chronicle and
  Termux/Linux policy gates;
- existing backend, frontend, contract and database runtime qualification
  scripts;
- no existing npm-audit, pip-audit, CodeQL, Trivy, Bandit, Gitleaks or
  Dependabot authority;
- `.gitignore` already excludes environment files, keys, secret directories,
  AWS local state, Python caches, Node build state and generated artifacts.

The qualified local Linux parity runtime is Python 3.14.4, Node 24.18.0,
npm 12.0.2, pytest 9.1.1 and Alembic 1.19.2.

## 3. CI topology

```text
push(main) / pull_request(main) / manual dispatch
                     |
                     v
             GitHub-hosted Linux
                     |
          +----------+-----------+
          |                      |
          v                      v
     quality job           security job
          |                      |
repository policies       tracked secret scan
repository tests          pip check
OpenAPI drift             pip-audit
contract runtime          npm audit
backend runtime
frontend runtime
offline migrations
tracked-file drift
```

The workflow uses `ubuntu-24.04`.

## 4. Runtime versions

CI uses:

- Python `3.14`;
- Node `24.18.0`;
- npm from the governed Node distribution.

Patch-level Python identity remains locally proven as Python 3.14.4. CI uses
the governed Python 3.14 line so GitHub-hosted setup remains portable.

## 5. GitHub Actions supply-chain policy

External actions are pinned to full-length commit SHAs.

Pinned authorities in this milestone:

- `actions/checkout` v7.0.1:
  `3d3c42e5aac5ba805825da76410c181273ba90b1`
- `actions/setup-node` v7.0.0:
  `820762786026740c76f36085b0efc47a31fe5020`
- `actions/setup-python` v7.0.0:
  `5fda3b95a4ea91299a34e894583c3862153e4b97`

The workflow does not rely on floating major tags.

Dependabot monitors GitHub Actions weekly so action updates arrive as explicit
reviewable pull requests.

## 6. Least privilege

Top-level workflow permission is:

```yaml
permissions:
  contents: read
```

The workflow does not request:

- `contents: write`;
- `pull-requests: write`;
- `security-events: write`;
- `id-token: write`;
- deployment/environment write authority.

`actions/checkout` uses `persist-credentials: false`.

CI does not use `pull_request_target`.

## 7. Secret boundary

The workflow contains no `${{ secrets.* }}` references and no application
credential environment variables.

Pull-request jobs therefore do not require:

- PostgreSQL credentials;
- AWS credentials;
- Azure credentials;
- provider API secrets;
- GitHub personal access tokens.

The normal ephemeral `GITHUB_TOKEN` exists as part of GitHub Actions, but the
workflow limits its repository permission to `contents: read` and checkout
does not persist it into Git configuration.

## 8. Quality authority

The Linux quality job runs:

- `check_ci_security_quality.py`;
- repository-tree policy;
- backend skeleton policy;
- frontend skeleton policy;
- database foundation policy;
- contract foundation policy;
- Termux/Linux static policy;
- Chronicle integrity policy;
- all repository unit tests;
- canonical OpenAPI drift check;
- contract runtime qualification;
- backend runtime qualification;
- frontend runtime qualification;
- offline database migration qualification;
- Git whitespace and tracked-file drift checks.

`check_termux_linux_runtime.sh` is deliberately NOT executed in GitHub CI.
That script remains the Android/Termux runtime authority.

## 9. Security authority

The security job adds:

- tracked secret-pattern and forbidden-file scanning;
- `python -m pip check`;
- `pip-audit==2.10.1` against `services/api`;
- blocking `npm audit --omit=dev --audit-level=high` for production/runtime dependencies;
- a complete npm advisory report for development/tooling dependencies;
- final whitespace validation.

Production/runtime vulnerability findings at the configured severity are
blocking failures.

Development/tooling advisories are still surfaced by the complete npm audit,
but they do not force dependency-tree surgery inside this foundation
milestone. They are preserved as dependency-maintenance evidence and handled
when the owning dependency milestone is opened.

## 9.1 Scope boundary for dependency advisories

The first live V1.2.8 audit surfaced a high-severity `js-yaml` advisory through
the OpenAPI contract-generation toolchain. Two override experiments were
tested and rejected because they changed package-resolution policy without
reliably changing the installed Redocly subtree under npm 12.0.2.

Those experimental overrides are removed. `package.json` and
`package-lock.json` return to their qualified pre-experiment authority.

The final V1.2.8 rule is:

- runtime/production dependency vulnerabilities block qualification;
- development/tooling advisories remain visible in the full audit report;
- dependency-version or transitive-resolution surgery is a separate
  dependency-maintenance concern, not a CI-foundation concern;
- Dependabot remains the normal mechanism for surfacing reviewable dependency
  updates.

This keeps V1.2.8 focused on CI, security visibility and quality enforcement.

## 9.2 Storage hygiene

V1.2.8 does not add a persistent local vulnerability-scanner environment.
The local Python audit runs in a temporary virtual environment and deletes it
when the gate exits. No extra application package is retained for the scanner.

The R1/R2 extracted correction directories and ZIPs are disposable after R3
qualification. Active repository dependencies such as `node_modules` are not
classified as obsolete while CineWatch development continues.

## 10. Dependabot

`.github/dependabot.yml` monitors weekly:

- npm at repository root;
- Python/pip under `/services/api`;
- GitHub Actions.

Dependency-update pull requests must pass the same CineWatch CI gates.

## 11. Branch protection

This repository file set establishes CI check authority but does not silently
change GitHub repository administration settings.

After the first green `CineWatch CI` run on `main`, repository branch/ruleset
configuration may require the Linux quality and dependency/security checks
before merge. That administrative action is explicit and separately verified.

## 12. Deferred security systems

The following are intentionally not introduced by V1.2.8:

- CodeQL/code scanning that requires additional repository permissions or
  account entitlement;
- Trivy/container scanning before a container authority exists;
- cloud posture scanning before AWS/Azure resources exist;
- deployment signing/provenance before a deployable artifact exists;
- production incident-response operations.

They can be added when their corresponding architecture exists.

## 13. Out of scope

CWTV.V1.2.8 does not:

- provision PostgreSQL;
- connect CI to `cinewatch_dev`;
- provision AWS or Azure;
- inject provider credentials;
- implement TMDb, OMDb or any provider;
- implement Discover, Watch, Explore or authentication;
- replace the local Termux runtime gate.

## 14. Qualification

Static policy:

```bash
python scripts/check_ci_security_quality.py
```

Repository regression:

```bash
python -m unittest discover -s tests/repository -p 'test_*.py'
```

Linux security runtime:

```bash
bash scripts/check_ci_security_quality_runtime.sh
```

After commit/push, the actual GitHub-hosted `CineWatch CI` run is the final
remote proof of this milestone.
