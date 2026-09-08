# CineWatch TV V1 PostgreSQL & Migration Foundation

**Document ID:** CWTV-V1-DB-MIG-001
**Milestone:** CWTV.V1.2.5
**Revision:** 001-R1
**Status:** IMPLEMENTATION CANDIDATE
**Baseline:** `7b6a8392d90fb08be9f522e9a182c723f2719cdd`

## 1. Purpose

CWTV.V1.2.5 turns PostgreSQL from an approved architectural target into a concrete CineWatch application persistence boundary. It establishes configuration, SQLAlchemy metadata, engine/session factories, Alembic migration lineage, dependency authority, and deterministic qualification without creating CineWatch product-domain tables.

This milestone does **not** provision AWS infrastructure, Azure infrastructure, or a PostgreSQL server. Hosting remains separate from the application/database contract.

## 2. Authority boundary

CineWatch TV owns its native PostgreSQL authority. The development database identity is `cinewatch_dev`.

`cinewatch_dev` and NPP's `npp_dev` are separate database authorities. CineWatch must not read or write native application state through NPP tables. Any future NPP relationship must use governed provider/service contracts.

## 3. PostgreSQL server target

The approved CineWatch server target remains PostgreSQL 17. A newer local `psql` client or a later cloud host does not redefine that application authority.

CWTV.V1.2.5 does not require a server to be running. Offline Alembic SQL generation proves the migration lineage and PostgreSQL dialect contract. Real server provisioning/connectivity is qualified by the infrastructure-owning milestone.

## 4. Python database stack

The V1.2.5 candidate pins stable production lines:

- SQLAlchemy `2.0.52`;
- Alembic `1.19.2`;
- Psycopg `3.3.5` with the binary extra for the qualified Linux development/runtime path.

SQLAlchemy 2.1 is not adopted while it remains a release candidate.

## 5. Database configuration

`DATABASE_URL` is consumed as a secret setting and is optional at service startup. The FastAPI skeleton therefore remains runnable before a database is provisioned.

Database operations require an explicit URL using exactly:

```text
postgresql+psycopg://
```

SQLite and other persistence fallbacks are prohibited. Credentials must never be committed or logged. Diagnostic rendering hides passwords.

## 6. SQLAlchemy model authority

`cinewatch_api.database.Base` is the sole declarative base for future CineWatch-owned models. A stable naming convention is established now so later constraints and indexes receive deterministic names suitable for Alembic migration review.

CWTV.V1.2.5 introduces no Movie, Series, Person, User, Rights, Playback, Cinema, Explore, or other product-domain model.

## 7. Migration authority

Alembic configuration lives under `services/api/` and obtains its URL only from application settings/environment configuration. No credential is stored in `alembic.ini`.

The root revision is:

```text
0001_postgresql_foundation
```

It intentionally performs no product schema mutation. Its purpose is to establish a single deterministic lineage from an empty CineWatch database. Future database milestones extend this lineage rather than creating independent migration histories.

## 8. Qualification

Native Termux qualifies repository/static policy. The qualified ARM64 Linux userland installs the database dependencies and proves:

- exact database-library versions;
- a single Alembic head;
- PostgreSQL offline SQL generation;
- database settings/URL behavior;
- migration lineage tests.

No network connection to AWS, Azure, NPP, or a PostgreSQL server is required for CWTV.V1.2.5 qualification.

### 8.1 R1 offline-environment isolation correction

The offline Alembic placeholder `DATABASE_URL` is command-scoped only to SQL generation and must not be exported as persistent qualification-process state. Database settings tests explicitly remove any inherited `DATABASE_URL` before proving that application startup remains valid without database configuration. This preserves the V1.2.5 contract that database configuration is optional until a database operation is requested.

## 9. Cloud portability

AWS and Azure are infrastructure hosts, not database semantics. The application remains based on standard PostgreSQL + SQLAlchemy + Psycopg + Alembic so the same CineWatch migration lineage can later be applied to the independently hosted `cinewatch_dev` authority during AWS-to-Azure migration.

## 10. Explicit exclusions

CWTV.V1.2.5 does not introduce:

- AWS RDS;
- Azure Database for PostgreSQL;
- credentials or secrets;
- NPP database access;
- authentication tables;
- catalogue/content tables;
- rights or playback tables;
- user/library/community tables;
- provider schemas;
- seed data;
- runtime database health dependency;
- SQLite fallback.
