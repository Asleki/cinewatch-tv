# CineWatch Failures, Corrections and Lessons

**Source commit:** `20e851e5eb0577831b0b05bc3cb6c92ee6319e43`

Failures are preserved rather than rewritten away. A correction without a recorded FAILED ledger event remains explicitly marked as such.

## CWTV-FC-00001 - CWTV.V1.2.3

State: `CORRECTED`

Failure: Native Termux installation fell back to building pydantic-core and failed on the Android Rust target boundary.

Correction: Ubuntu 26.04 ARM64 PRoot with external Python virtualenv established as the phone backend runtime.

## CWTV-FC-00002 - CWTV.V1.2.4

State: `CORRECTED`

Failure: ESLint 10.10.0 failed while loading react/display-name because the React plugin called a removed context filename API.

Correction: R1 pinned ESLint 9.39.5 and corrected EOF whitespace defects.

## CWTV-FC-00003 - CWTV.V1.2.4

State: `CORRECTED`

Failure: A stale workspace-local ESLint 10.10.0 lock resolution remained after the source package pin and made npm report ELSPROBLEMS.

Correction: npm workspace lock was explicitly reconciled to ESLint 9.39.5 and a clean npm ci removed the invalid local resolution.

## CWTV-FC-00004 - CWTV.V1.2.5

State: `CORRECTED`

Failure: Offline migration qualification exported DATABASE_URL into the later settings test and violated the optional-database configuration contract.

Correction: R1 isolated the placeholder database URL to the Alembic command and added regression checks for environment isolation.

## CWTV-FC-00005 - CWTV.V1.2.5.1

State: `CORRECTED`

Failure: Chronicle static qualification failed.

Correction: R1 synchronized generated Chronicle projections after STARTED events before self-recorded commands execute.

## CWTV-FC-00006 - CWTV.V1.2.5.1

State: `CORRECTED`

Failure: Repository regression after chronicle foundation failed.

Correction: R1 synchronized generated Chronicle projections after STARTED events before self-recorded commands execute.

## CWTV-FC-00007 - CWTV.V1.2.5.1

State: `CORRECTED`

Failure: Rendered dashboard was structurally accurate but failed responsive visual qualification.

Correction: R2 removed fixed-width overflow patterns and introduced responsive semantic color, adaptive chart rendering and motion.

## CWTV-FC-00008 - CWTV.V1.2.6

State: `CORRECTED`

Failure: Contract runtime qualification failed because the checker assumed openapi-typescript was hoisted into repository-root node_modules.

Correction: R1 replaced root-node_modules assumptions with npm workspace resolution for openapi-typescript runtime qualification.

## CWTV-FC-00009 - CWTV.V1.2.7

State: `RESOLVED_BY_PASS`

Failure: CWTV.V1.2.7 native runtime qualification initially failed because the Termux zip packaging utility was unavailable

Correction: No paired correction recorded.

## CWTV-FC-00010 - CWTV.V1.2.7

State: `RESOLVED_BY_PASS`

Failure: CWTV.V1.2.7 native runtime qualification initially failed because the Termux zip packaging utility was unavailable

Correction: No paired correction recorded.

## CWTV-FC-00011 - CWTV.V1.2.7

State: `CORRECTED`

Failure: Final staged diff qualification detected trailing whitespace in the CWTV.V1.2.7 architecture document and ADR

Correction: Removed trailing whitespace from the CWTV.V1.2.7 architecture document and ADR and restaged both files

## CWTV-FC-00012 - CWTV.V1.2.8

State: `CORRECTED`

Failure: V1.2.8 security runtime qualification detected a high-severity js-yaml advisory in the OpenAPI contract-generation dependency path.

Correction: Applied a root-scoped @redocly/openapi-core -> js-yaml 4.3.2 override without changing openapi-typescript 7.13.0.

## CWTV-FC-00013 - CWTV.V1.2.8

State: `CORRECTED`

Failure: R1 dependency-resolution qualification failed because npm 12.0.2 recognized the Redocly-scoped js-yaml override but retained js-yaml 4.3.1 in the installed Redocly subtree.

Correction: Replaced the ineffective parent-scoped Redocly override with a root-global js-yaml 4.3.2 override.

## CWTV-FC-00014 - CWTV.V1.3.1

State: `CORRECTED`

Failure: Detected a NexVox source/projection boundary violation in commit 3f9f175: a commit marked NexVox-Projection true also contains the CineWatch Brand and Streaming Signature Authority and Chronicle source changes. The already-pushed commit is preserved as historical evidence and will not be rewritten.

Correction: Applied append-only recovery for malformed projection 3f9f175 by preserving the pushed commit, establishing a new ordinary source boundary from the corrective engineering record, and requiring the next NexVox projection to target that new source commit.

## CWTV-FC-00015 - CWTV.V1.2.8

State: `CORRECTION_WITHOUT_LEDGER_FAILURE`

Failure: No FAILED ledger event recorded.

Correction: Removed the R1/R2 js-yaml override experiments and restored CineWatch package and lockfile authority to the qualified pre-experiment state.

## CWTV-FC-00016 - CWTV.V1.2.8

State: `CORRECTION_WITHOUT_LEDGER_FAILURE`

Failure: No FAILED ledger event recorded.

Correction: Locked the final V1.2.8 audit boundary: runtime/production vulnerabilities block; development/tooling advisories remain visible and are handled by dependency maintenance.

## CWTV-FC-00017 - CWTV.V1.3.1

State: `CORRECTION_WITHOUT_LEDGER_FAILURE`

Failure: No FAILED ledger event recorded.

Correction: Normalized trailing whitespace in the competitive design intelligence candidate after the staged diff whitespace gate identified Markdown hard-break spacing.

## CWTV-FC-00018 - CWTV.V1.3.1

State: `CORRECTION_WITHOUT_LEDGER_FAILURE`

Failure: No FAILED ledger event recorded.

Correction: Normalized trailing whitespace in the design system and asset foundation candidate after the staged diff whitespace gate identified Markdown hard-break spacing.

## CWTV-FC-00019 - CWTV.V1.3.1

State: `CORRECTION_WITHOUT_LEDGER_FAILURE`

Failure: No FAILED ledger event recorded.

Correction: Corrected scripts/README.md so the local-only NexVox PDF lifecycle matches the approved mandatory regeneration rule for every ordinary non-projection source commit.

## CWTV-FC-00020 - CWTV.V1.3.1

State: `CORRECTION_WITHOUT_LEDGER_FAILURE`

Failure: No FAILED ledger event recorded.

Correction: Added regression protection for the source/projection boundary defect exposed by malformed commit 3f9f175. Future commits marked NexVox-Projection true must fail validation if they contain ordinary source, architecture, workflow, or Chronicle paths.
