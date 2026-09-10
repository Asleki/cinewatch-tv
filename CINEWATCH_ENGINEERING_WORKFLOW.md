# CineWatch TV Engineering Workflow Lock

**Document ID:** `CWTV-ENGINEERING-WORKFLOW-LOCK-001`
**Product:** CineWatch TV
**Repository:** `Asleki/cinewatch-tv`
**Status:** `LOCKED`
**Revision:** `003`
**Effective date:** `2026-09-10`

---

## 1. Purpose

This document is the persistent operating contract for CineWatch TV engineering work.

Its purpose is to preserve the exact workflow, terminal/window discipline, qualification order, milestone recording method, CI handling, Version Control rules, security practices, and repeatable techniques used by the project.

Future human or AI-assisted work should read this file before performing a CineWatch engineering activity.

This file is **not model retraining**. It is durable repository context intended to prevent future sessions from guessing or reconstructing the working method from memory.

If this file conflicts with a stronger approved CineWatch governance or architecture authority, the stronger authority wins and the conflict must be resolved explicitly.

---

# 2. First rule: inspect, do not assume

Before assigning work to a terminal window, inspect the real tmux layout.

Use:

```bash
tmux list-windows
```

or:

```bash
tmux lsw
```

For a compact authoritative listing:

```bash
tmux list-windows -F '#{window_index}:#{window_name} active=#{window_active} panes=#{window_panes}'
```

For all panes, commands, and working directories:

```bash
tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} window=#{window_name} active=#{pane_active} cmd=#{pane_current_command} path=#{pane_current_path}'
```

Never invent a window name or role when the actual session can be inspected.

---

# 3. Locked CineWatch tmux window map

The CineWatch TV session currently uses **nine windows**:

```text
0: api
1: web
2: postgres
3: tests
4: contracts
5: extract
6: git
7: aws
8: chronicle
```

These names are authoritative unless the user explicitly changes the session design.

## `0:api`

Use for CineWatch backend/API runtime work.

Typical responsibilities:

- start/stop the API;
- inspect API runtime behavior;
- backend service execution;
- live endpoint checks when the API must remain running;
- runtime logs related to the API.

Do not use this window for Version Control.

## `1:web`

Use for CineWatch frontend/web runtime work.

Typical responsibilities:

- start/stop the frontend;
- browser-facing runtime;
- local web server;
- frontend runtime diagnostics.

Do not use this window for Version Control.

## `2:postgres`

Use for PostgreSQL/database work.

Typical responsibilities:

- PostgreSQL sessions;
- schema/database inspection;
- migration investigation;
- database qualification where an interactive database session is required.

Keep database credentials private. Prefer interactive credential entry where applicable.

Do not use this window for Version Control.

## `3:tests`

Use for **tests, qualification, and CI inspection**.

Typical responsibilities:

- focused tests;
- repository regression;
- contract qualification;
- backend/frontend qualification;
- migration qualification;
- security/quality checks;
- dashboard/chronicle verification;
- `gh run list`;
- `gh run watch`;
- `gh run view`;
- CI log inspection;
- `git diff --check` as an integrity check.

Examples:

```bash
python scripts/check_ci_security_quality.py
bash scripts/check_backend_runtime.sh
bash scripts/check_frontend_runtime.sh
bash scripts/check_database_migrations.sh
python scripts/build_progress_dashboard.py --check
python scripts/check_engineering_chronicle.py
gh run list ...
gh run watch ...
gh run view ...
```

Do not use this window for commits or pushes.

## `4:contracts`

Use for **contracts and contract-related source changes**.

Typical responsibilities:

- OpenAPI contract work;
- shared contract package work;
- generated contract authority;
- contract runtime scripts;
- contract-related corrections.

The exact window name is:

```text
4:contracts
```

Never rename it in instructions as `4:code`.

Do not use this window for Version Control.

## `5:extract`

Use for extraction/import/data-processing work.

Typical responsibilities:

- extraction jobs;
- controlled transformation/import tasks;
- temporary extraction outputs;
- data preparation associated with repository work.

Do not use this window for Version Control.

## `6:git`

Use for **Version Control only. Period.**

Allowed responsibilities:

- inspect worktree/staged state;
- inspect diffs;
- stage explicit paths;
- check staged integrity;
- commit;
- push;
- inspect commit history;
- inspect local HEAD.

Examples:

```bash
git status --short
git diff --check
git diff --cached --check
git diff --cached --stat
git diff --cached -- <paths>
git add <explicit-paths>
git commit -m "..."
git push
git --no-pager log -5 --oneline --decorate
git rev-parse HEAD
```

Do **not** use `6:git` for:

- GitHub Actions log inspection;
- application tests;
- CI tests;
- API runtime;
- frontend runtime;
- PostgreSQL;
- AWS;
- contract editing;
- extraction;
- chronicle/dashboard generation.

When Version Control work is complete, leave this window.

## `7:aws`

Use for AWS/cloud-specific work.

Typical responsibilities:

- AWS infrastructure;
- AWS connectivity;
- cloud services;
- deployment/infrastructure qualification;
- AWS environment operations.

Never commit cloud credentials.

Do not use this window for unrelated code or Version Control.

## `8:chronicle`

Use for the **engineering chronicle, milestone activity records, progress dashboard governance, and project-history recording**.

Typical responsibilities:

- `record_engineering_activity.py`;
- milestone qualification/closure records;
- engineering chronicle inspection;
- progress dashboard generation;
- dashboard governance records;
- milestone evidence preservation;
- NexVox engineering-corpus generation after a non-projection source commit;
- mandatory local-only NexVox PDF regeneration after every ordinary non-projection source commit.

This is the preferred window for creating or updating durable engineering-workflow governance documents such as this file, followed by qualification in `3:tests` and Version Control in `6:git`.

---

# 4. Working-directory discipline

Different windows/environments may expose the repository at different paths, including:

```text
/workspace/cinewatch-tv
~/projects/cinewatch-tv
```

Never assume environment variables, GitHub CLI authentication, virtual environments, or shell state are shared merely because repository changes appear in both environments.

Before consequential work, confirm:

```bash
pwd
git status --short
```

If the current environment is ambiguous, inspect it before continuing.

---

# 5. Standard engineering sequence

The default sequence for a change is:

```text
inspect
  ↓
identify authority and scope
  ↓
make the smallest justified change
  ↓
run focused validation
  ↓
run relevant component/runtime validation
  ↓
run repository/policy validation
  ↓
run diff integrity checks
  ↓
6:git — create the normal engineering source commit
  ↓
8:chronicle — build NexVox engineering corpus for that exact commit
  ↓
3:tests — verify NexVox corpus determinism/integrity
  ↓
6:git — create one NexVox projection commit
  ↓
push source + projection commits
  ↓
3:tests — GitHub CI verification
  ↓
remote qualification proof
  ↓
8:chronicle — milestone/activity recording when applicable
  ↓
dashboard rebuild + verification
  ↓
6:git — persist closure/progress source commit
  ↓
8:chronicle + 3:tests + 6:git — sync its NexVox projection
  ↓
push closure + projection commits
  ↓
formal milestone lock
```

Do not reverse this order without a specific reason.

---

# 6. Inspect before changing

Before editing:

1. inspect the relevant file;
2. inspect the relevant test or policy;
3. inspect the first actual failure;
4. identify the source of truth;
5. determine whether the defect belongs to:
   - application code;
   - contract;
   - generated artifact;
   - test harness;
   - CI environment;
   - dependency/runtime;
   - database/migration;
   - policy;
6. make the smallest correction that preserves the architecture.

Do not change multiple unrelated areas merely because they are nearby.

Do not weaken a test just to obtain a PASS.

---

# 7. Fail-fast CI discipline

GitHub Actions may stop a job at the first blocking failure.

Always distinguish:

```text
PASS
FAIL
REACHED BUT BOOTSTRAP-FAILED
SKIPPED / NOT REACHED
ADVISORY / NON-BLOCKING
```

A step that starts and fails before its substantive tests is **not** proof that those substantive tests were exercised.

When a CI run fails:

1. bind the run to the exact commit SHA;
2. inspect the exact first blocking failure;
3. do not diagnose an older run;
4. do not assume skipped downstream gates passed;
5. reproduce the failing environment locally where practical.

Useful commands from `3:tests`:

```bash
gh run list \
  --repo Asleki/cinewatch-tv \
  --workflow ci.yml \
  --limit 3
```

```bash
gh run view "$RUN_ID" \
  --repo Asleki/cinewatch-tv
```

```bash
gh run view "$RUN_ID" \
  --repo Asleki/cinewatch-tv \
  --log-failed
```

```bash
gh run watch "$RUN_ID" \
  --repo Asleki/cinewatch-tv \
  --exit-status
```

---

# 8. Do not repeat one root cause one push at a time

When fail-fast CI exposes the **same class of defect** in multiple files, stop fixing one occurrence per push.

Instead:

1. identify the recurring pattern;
2. search the repository for all relevant consumers;
3. inspect each occurrence;
4. correct every genuine occurrence in scope;
5. run the full remaining local chain;
6. push once.

Example precedent from `CWTV.V1.2.8`:

```text
CWTV_API_PYTHON=python
```

was valid CI input, but scripts that used:

```bash
[ -x "$CWTV_API_PYTHON" ]
```

treated `python` as a literal filesystem path rather than a command available through `PATH`.

The correct pattern for a command-name override is to resolve it first:

```bash
if [[ "$python_bin" != */* ]]; then
  resolved_python="$(command -v -- "$python_bin" || true)"
  if [[ -n "$resolved_python" ]]; then
    python_bin="$resolved_python"
  fi
fi
```

Do not create redundant CI environments merely to satisfy an incorrect checker.

---

# 9. Node/npm runtime governance

CineWatch controls its required Node/npm runtime.

Do not rely silently on whichever npm happens to ship in the current GitHub runner image.

When repository policy defines a governed npm range/version, CI must establish that runtime deliberately before dependency installation.

Do not perform dependency surgery simply because CI's default package-manager version differs from repository policy.

---

# 10. Generated OpenAPI contract governance

The governed generated TypeScript OpenAPI contract is:

```text
packages/contracts/src/generated/openapi.d.ts
```

When repository policy requires it as a tracked contract authority:

- it must exist in clean Git checkouts;
- broad ignore rules must not accidentally hide it;
- it must be generated from the canonical OpenAPI authority;
- it must be compared for drift;
- it must not be hand-edited.

The intended chain is:

```text
backend API authority
  ↓
canonical OpenAPI document
  ↓
generated TypeScript declaration
  ↓
shared contracts package
  ↓
frontend typed consumption
```

A generated artifact may be tracked when it is explicitly part of repository governance.

Do not assume all `generated/` content is disposable.

---

# 11. Generated-file rule

Before changing any generated file, determine:

1. its canonical source;
2. its generator;
3. whether it is tracked;
4. whether CI checks it for drift;
5. whether the generated file itself is an authority or only an output.

Prefer correcting the authority or generator and rebuilding.

Never hand-patch a generated contract artifact merely to silence CI.

---

# 12. Local qualification before Version Control

Before entering `6:git`, run the relevant local checks.

Use a focused-to-broad progression:

```text
focused check
  ↓
component/runtime check
  ↓
repository/policy check
  ↓
relevant regression
  ↓
diff integrity
```

Typical integrity command:

```bash
git diff --check
```

Do not use GitHub CI as the primary debugger when the same failure can be reproduced locally.

---

# 13. Version Control discipline

## 13.1 Explicit staging

Prefer:

```bash
git add path/to/file1 path/to/file2
```

Avoid:

```bash
git add .
```

unless the complete worktree has deliberately been reviewed and every changed file belongs to the same intended candidate.

## 13.2 Required pre-commit inspection

In `6:git`:

```bash
git status --short
```

Then stage explicit paths.

Then:

```bash
git diff --cached --check
```

```bash
git diff --cached --stat
```

```bash
git diff --cached -- <relevant-paths>
```

The staged scope must match the intended correction or milestone exactly.

## 13.3 Commit messages

Use concise, descriptive commit messages.

Examples already used successfully:

```text
fix: align CineWatch CI npm runtime
fix: track governed OpenAPI contract
fix: resolve backend CI Python runtime
fix: resolve migration CI Python runtime
```

## 13.4 Push

Push only after local qualification is green **and the required NexVox projection commit has been created for the preceding non-projection engineering commit**.

```bash
git push
```

A `NexVox-Projection: true` commit is exempt from creating another projection.

Then leave `6:git` and verify GitHub Actions from `3:tests`.

---

# 14. Security and secrets

Never commit or paste into repository files:

- GitHub tokens;
- AWS keys;
- database passwords;
- API secrets;
- private certificates;
- private environment files;
- access tokens;
- production credentials.

Do not print a secret merely to prove that it exists.

Prefer interactive credential prompts where possible.

GitHub CLI authentication belongs in the environment/user configuration, not inside the repository.

AWS and database credentials remain outside Git.

Use least privilege.

---

# 15. Mobile / Termux / Alpine discipline

The CineWatch workflow is designed to work from a mobile Linux environment.

Therefore:

- prefer short commands;
- avoid unnecessary pager output;
- use `git --no-pager` when useful;
- use `PAGER=cat` / `PSQL_PAGER=cat` where appropriate;
- do not delete `node_modules` as a generic troubleshooting step;
- do not repeatedly redownload large dependency sets without cause;
- preserve working virtualenvs;
- avoid giant log dumps when `grep`, `sed`, `tail`, or focused diff output is enough;
- use explicit, copy-safe commands;
- preserve recoverable state before destructive operations.

---

# 16. Progress dashboard and engineering chronicle

The CineWatch milestone dashboard is a projection of recorded engineering activity.

Do **not** manually fake a milestone's browser status.

Do **not** hand-edit dashboard output merely to make a milestone appear qualified.

The repository's chronicle/dashboard tooling is the authority for recording and projection.

## 16.1 Record engineering activity

Use:

```bash
python scripts/record_engineering_activity.py \
  --milestone <MILESTONE> \
  --event-type <EVENT_TYPE> \
  --component <COMPONENT> \
  --summary "<SUMMARY>" \
  --result <RESULT>
```

Before recording a final qualification/closure event, inspect existing milestone records to avoid duplicates.

## 16.2 Build the dashboard

After recording:

```bash
python scripts/build_progress_dashboard.py
```

## 16.3 Verify the engineering chronicle

```bash
python scripts/check_engineering_chronicle.py
```

## 16.4 Verify deterministic dashboard generation

```bash
python scripts/build_progress_dashboard.py --check
```

When relevant:

```bash
bash scripts/check_progress_dashboard_runtime.sh
```

## 16.5 Browser verification

After rebuild, verify the milestone in the browser.

A milestone may display fields such as:

```text
Status
Completion
Difficulty
Failures
Corrections
Elapsed
Command runtime
```

`Command runtime not preserved` is not automatically a qualification failure. It means sufficient command timing evidence was not preserved for that metric.

Do not invent timing evidence retroactively.

---

# 17. Milestone closure protocol

A milestone is **not** formally locked only because local tests pass.

A milestone is **not** formally locked only because GitHub CI is green.

The full closure path is:

```text
local qualification PASS
  ↓
candidate committed
  ↓
candidate pushed to main
  ↓
GitHub CI remote qualification PASS
  ↓
exact remote proof captured
  ↓
engineering activity / qualification record written
  ↓
dashboard rebuilt
  ↓
chronicle verified
  ↓
dashboard deterministic check PASS
  ↓
browser projection verified
  ↓
closure/progress files staged in 6:git
  ↓
closure source commit
  ↓
NexVox corpus sync for exact closure source commit
  ↓
NexVox projection commit
  ↓
closure + projection push to main
  ↓
MILESTONE LOCKED
```

Remote proof should include, when available:

```text
milestone ID
commit SHA
GitHub Actions run ID
workflow conclusion
job conclusions
open blockers
```

Never declare a milestone formally closed before its closure record is persisted on repository authority.

---

# 18. Dashboard precedent: CWTV.V1.2.8

`CWTV.V1.2.8 — CI / Security / Quality Foundation` reached:

```text
QUALIFIED
100%
Difficulty: 4.4/5
Failures: 2
Corrections: 4
Elapsed: 6h 49m 22s
Command runtime: not preserved
```

Remote green-CI proof:

```text
GitHub Actions run: 34429017377
Conclusion: SUCCESS
Linux quality gate: PASS
Dependency and secret gate: PASS
```

The sequence established an important distinction:

```text
local PASS
≠ remote CI PASS
≠ recorded dashboard qualification
≠ formal repository lock
```

Each stage must be proven separately.

---

# 19. Advisory findings

A GitHub annotation is not automatically equivalent to workflow failure.

Interpret evidence in this order:

```text
workflow conclusion
  ↓
job conclusion
  ↓
blocking step result
  ↓
advisory annotation
```

If a workflow concludes `success` and all required jobs are green, an informational/advisory annotation should not be turned into unrelated milestone scope unless policy says it is blocking.

---

# 20. Do not hallucinate repository state

Neither a human nor an AI assistant should claim that something was:

- created;
- edited;
- staged;
- committed;
- pushed;
- recorded;
- qualified;
- locked;

unless there is direct evidence that the action actually occurred.

If a tool or environment cannot perform an action, state that plainly.

Never substitute an intended action for a completed action.

---

# 21. Locked DOs

- **DO** inspect tmux windows instead of guessing.
- **DO** use the exact window names.
- **DO** keep `6:git` strictly for Version Control.
- **DO** use `3:tests` for qualification and GitHub CI inspection.
- **DO** use `8:chronicle` for chronicle/dashboard governance.
- **DO** use `4:contracts` for contract work.
- **DO** confirm `pwd` and worktree state when environments differ.
- **DO** inspect before changing.
- **DO** fix root causes, not symptoms.
- **DO** preserve milestone scope.
- **DO** stage explicit paths.
- **DO** run staged diff checks before commit.
- **DO** bind CI evidence to an exact commit and run ID.
- **DO** distinguish fail-fast skipped gates from genuine passes.
- **DO** use canonical generators for generated artifacts.
- **DO** keep secrets outside Git.
- **DO** record milestone status through the engineering chronicle.
- **DO** rebuild and verify the dashboard.
- **DO** verify the browser projection.
- **DO** persist closure records to `main` before applying a formal lock.
- **DO** stop and inspect when reality differs from expected output.

---

# 22. Locked DON'Ts

- **DON'T** invent tmux window names or purposes.
- **DON'T** call `4:contracts` `4:code`.
- **DON'T** use `6:git` for CI inspection.
- **DON'T** use `6:git` for tests.
- **DON'T** stage blindly with `git add .`.
- **DON'T** push an unqualified change just to discover the next predictable failure.
- **DON'T** weaken CI simply to make it green.
- **DON'T** treat skipped tests as passed tests.
- **DON'T** create redundant environments to satisfy a broken checker.
- **DON'T** hand-edit governed generated OpenAPI output.
- **DON'T** manually fake dashboard status.
- **DON'T** duplicate milestone qualification events.
- **DON'T** expose secrets in chat, logs, Git, or screenshots.
- **DON'T** perform unrelated dependency surgery inside a focused milestone.
- **DON'T** delete large dependency trees or caches without a real reason.
- **DON'T** invent command-runtime evidence.
- **DON'T** call a milestone locked until the repository record proves closure.
- **DON'T** claim an action was executed when it was merely proposed.

---

# 23. AI-assisted engineering bootstrap

At the beginning of a future CineWatch engineering activity, the assistant should:

1. read this file;
2. inspect the actual tmux windows;
3. identify the active milestone;
4. inspect the current dashboard/chronicle state if the task is milestone-related;
5. inspect the relevant approved architecture/governance authority;
6. inspect current repository status;
7. identify the correct window for the task;
8. preserve locked decisions;
9. use live repository evidence rather than reconstructed memory when available;
10. avoid duplicate engineering-activity records;
11. qualify before Version Control;
12. verify remote CI after push;
13. record milestone progress only through the repository's governance flow;
14. never state that a step is complete without evidence.

This file should be used as persistent operational context for CineWatch work.

---

# 24. Change control for this workflow lock

This workflow file may be revised only when:

- the user explicitly changes the working method;
- a window role is explicitly changed;
- repository governance tooling changes;
- a repeated engineering lesson becomes a durable rule;
- a security requirement must be strengthened;
- the current workflow is proven inaccurate.

When changing this file:

1. inspect the current revision;
2. state the proposed rule change;
3. preserve unaffected locks;
4. update the revision;
5. validate Markdown/repository policy;
6. inspect the diff;
7. stage it explicitly in `6:git`;
8. commit;
9. push to `main`;
10. use the new revision as the baseline thereafter.

---

# 25. NexVox engineering knowledge synchronization

The governed engineering-knowledge corpus lives under:

```text
nexvox/engineering/
```

Its purpose is to teach NexVox how CineWatch TV was engineered while preserving exact source provenance, training eligibility, failures, corrections, decisions, and Git history. It is separate from future CineWatch user/search/recommendation training datasets.

## 25.1 Source and projection commits

A Git commit cannot contain its own final SHA inside its tree. Therefore CineWatch uses a two-commit synchronization model.

For every ordinary non-projection engineering commit:

1. create the normal engineering source commit in `6:git`;
2. leave `6:git`;
3. in `8:chronicle`, run `python scripts/build_nexvox_engineering_corpus.py --source-commit <SOURCE_SHA>`;
4. regenerate the local preservation copy with `python scripts/build_nexvox_engineering_pdf.py`; the PDF remains outside Git and is mandatory for every ordinary non-projection source commit;
5. in `3:tests`, run `python scripts/check_nexvox_engineering_corpus.py` plus relevant regression/integrity checks;
6. return to `6:git`;
7. stage the generated NexVox corpus explicitly;
8. create one projection commit with exact trailers;
9. push the source and projection commits together.

Required projection commit trailers:

```text
NexVox-Source-Commit: <40-character source SHA>
NexVox-Projection: true
```

A projection commit SHALL NOT trigger another projection.

A projection commit may change **only generator-owned NexVox projection paths**. Architecture documents, Chronicle/event sources, application code, tests, workflow files, static NexVox authority/policy/schema files, or any other non-generated path must remain in an ordinary source commit. `scripts/check_nexvox_engineering_corpus.py` must fail the projection gate when a commit carrying `NexVox-Projection: true` changes any non-generator-owned path.

## 25.2 Authority and training eligibility

Git remains canonical for commit/file history. `docs/progress/activity/engineering-events.jsonl` remains canonical for recorded engineering activity. NexVox files are projections, indexes, reconciliations, and curated knowledge records.

Every source/record must remain one of:

```text
TRAINING_ELIGIBLE
TRAINING_REVIEW_REQUIRED
REFERENCE_ONLY
TRAINING_PROHIBITED
```

Inspection does not imply training permission. Unknown training permission is not permission. Generated projections must not be recursively duplicated into training records.

## 25.3 Failure preservation

The corpus must preserve failures and corrections. When conversation/terminal evidence proves a failure that was not recorded as a FAILED engineering-ledger event, the discrepancy must be represented through provenance/reconciliation rather than by rewriting the append-only ledger.

## 25.4 Local-only PDF

The NexVox engineering PDF is a human-readable preservation projection only. It must be generated outside the Git worktree and must never become repository authority.

## 25.5 CI expectation

The repository NexVox checker must validate corpus layout, source-commit binding, **projection-path purity**, checksums, JSONL content hashes, training-eligibility boundaries, conversation provenance, secret-value exclusion, and deterministic regeneration.

---

## Final lock

This document defines the default CineWatch TV engineering workflow until explicitly superseded by a later approved revision.

**LOCK STATE: `LOCKED`**
