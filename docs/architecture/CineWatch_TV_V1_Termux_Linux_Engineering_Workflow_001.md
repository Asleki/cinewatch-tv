# CineWatch TV V1 — Termux / Linux Engineering Workflow Foundation

**Milestone:** CWTV.V1.2.7
**Document:** CWTV-V1-ENG-WORKFLOW-001
**Status:** Candidate for qualification
**Baseline:** `e15752642ed22d30b99caadf546214eea15b730f`

## 1. Purpose

CWTV.V1.2.7 turns the already-proven Android engineering environment into a
repeatable, named, recoverable workflow. Termux is the host and workspace
authority. Ubuntu PRoot (`cwtv-linux`) is the authoritative Linux application
runtime. The repository remains one Git worktree.

This milestone does not add CineWatch product functionality.

## 2. Locked runtime topology

```text
Android
└── Termux
    ├── Git / GitHub / downloads / native psql
    ├── tmux session: cinewatch-tv
    │   ├── 0 api        -> Ubuntu PRoot + API venv
    │   ├── 1 web        -> Ubuntu PRoot + governed Node/npm
    │   ├── 2 postgres   -> native Termux psql
    │   ├── 3 tests      -> Ubuntu PRoot + API venv + Node/npm
    │   ├── 4 contracts  -> Ubuntu PRoot + API venv + Node/npm
    │   ├── 5 extract    -> native Termux downloads/checksum/ZIP work
    │   ├── 6 git        -> native Termux Git/GitHub work
    │   ├── 7 aws        -> native Termux AWS named-profile work
    │   └── 8 chronicle  -> native Termux engineering ledger/dashboard work
    └── Ubuntu PRoot: cwtv-linux
        └── bind: ~/projects/cinewatch-tv -> /workspace/cinewatch-tv
```

The Linux authority remains:

- Python `3.14.4`
- API venv `/root/.venvs/cinewatch-api`
- Node `v24.18.0`
- npm `12.0.2`
- Node root `/opt/node-v24.18.0-linux-arm64`

The native Termux PostgreSQL client observed during manual qualification is
PostgreSQL client `18.2`.

## 3. Named session contract

The session name is `cinewatch-tv`.

The locked window order is:

1. `api`
2. `web`
3. `postgres`
4. `tests`
5. `contracts`
6. `extract`
7. `git`
8. `aws`
9. `chronicle`

The repository-owned command:

```bash
cwtv-session
```

creates the session when it does not exist and reuses it when the exact
governed nine-window layout already exists.

For non-interactive validation:

```bash
cwtv-session --no-attach
```

Readiness is inspected with:

```bash
cwtv-session-status
```

No servers are auto-started by the launcher. The launcher establishes a ready
engineering shell only.

## 4. Development port ownership

The session exports these non-secret development port identities:

- API: `CWTV_API_PORT=8000`
- web: `CWTV_WEB_PORT=3000`
- Chronicle dashboard: `CWTV_CHRONICLE_PORT=8785`

Starting a server remains an explicit developer action.

## 5. PostgreSQL session policy

The `postgres` window stays native Termux.

Before CineWatch cloud PostgreSQL exists, the window is intentionally
`RESERVED`; no host, user or password is invented.

After `cinewatch_dev` is provisioned, non-secret connection settings may be
placed in:

```text
~/.config/cinewatch/postgres.env
```

Allowed keys only:

- `PGHOST`
- `PGPORT`
- `PGDATABASE`
- `PGUSER`
- `PGSSLMODE`
- `PGCONNECT_TIMEOUT`

The password must not be stored there.

PostgreSQL password persistence, when eventually required, uses:

```text
~/.pgpass
```

with permission mode `600`.

The repository template is:

```text
scripts/termux/config/postgres.env.example
```

## 6. GitHub authentication policy

The `git` window stays native Termux.

GitHub credentials are not stored in the CineWatch repository and are not
embedded in the session launcher. Persistent GitHub CLI authentication uses
`gh auth login` / `gh auth status` or Git SSH authentication.

The launcher deliberately removes inherited token environment variables from
its governed shells.

## 7. AWS profile policy

The `aws` window stays native Termux.

AWS credentials are not embedded in the repository or launcher. When AWS CLI
work is required, CineWatch uses a named AWS profile, normally
`cinewatch-dev`.

A non-secret environment selector may be stored in:

```text
~/.config/cinewatch/aws.env
```

The repository template is:

```text
scripts/termux/config/aws.env.example
```

AWS access keys, secret keys and session tokens remain under the AWS
credential/profile mechanism, not this file.

The AWS CLI itself is not a V1.2.7 blocking dependency before cloud
provisioning requires it.

## 8. Secret-environment isolation

Every governed window removes inherited values for database passwords,
GitHub token variables and raw AWS credential variables before opening the
interactive shell.

The final interactive shells are started without user profile re-import. This
prevents an uncontrolled shell profile from silently re-exporting credentials
that the workflow intentionally removed.

## 9. CineWatch / NPP isolation

CineWatch and NPP are separate engineering authorities.

CineWatch uses:

- repository `cinewatch-tv`
- tmux session `cinewatch-tv`
- database identity `cinewatch_dev`
- API venv `/root/.venvs/cinewatch-api`
- AWS profile `cinewatch-dev`

NPP runtime values, database identities, hosts, users, tmux sessions and
credentials must never be copied into the CineWatch workflow.

## 10. Recovery contract

After Termux or the phone is restarted:

```bash
cd ~/projects/cinewatch-tv
cwtv-session
```

is the intended recovery path.

If a governed session is already alive, it is reused.

If the session exists but its window layout is inconsistent, the launcher
fails rather than silently mutating an unknown session.

No destructive session reset occurs automatically.

## 11. Manual proof preserved by this milestone

Before this delivery was generated, the developer manually established and
verified all nine windows.

Observed green gates included:

- clean `main` at `e15752642ed22d30b99caadf546214eea15b730f`
- tmux `3.7c`
- `api`: Linux bind + Python venv + Node/npm
- `web`: Linux bind + Node/npm + Next.js `16.3.4`, no Python venv
- `postgres`: native Termux psql `18.2`, no CineWatch cloud credentials yet
- `tests`: pytest `9.1.1`, Alembic `1.19.2`, no exported database password
- `contracts`: openapi-typescript `7.13.0`, OpenAPI drift and policy gates green
- `chronicle`: append-only ledger/dashboard checks green
- exact nine-window tmux structure present

## 12. Out of scope

CWTV.V1.2.7 does not:

- provision AWS or Azure resources;
- create the CineWatch PostgreSQL server;
- start application servers automatically;
- implement external providers;
- add product functionality;
- create or store database passwords, GitHub tokens or AWS credential values;
- alter NPP.

## 13. Qualification

Static policy:

```bash
python scripts/check_termux_linux_workflow.py
```

Repository regression:

```bash
python -m unittest discover -s tests/repository -p 'test_*.py'
```

Native Termux runtime:

```bash
bash scripts/check_termux_linux_runtime.sh
```

The milestone is qualified only after the launcher, session status, static
policy, repository regression and recreated-session proof are green.
