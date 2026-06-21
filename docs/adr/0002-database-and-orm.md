# ADR 0002: Database and ORM Selection

**Date:** 2026-06-21  
**Status:** Accepted

## Context

The platform needs a relational database for user accounts, organizations, credits, and media jobs.

## Decision

Use **PostgreSQL 17** on AWS RDS with **SQLAlchemy 2.0** as the ORM and **Alembic** for migrations.

- Production: PostgreSQL 17.10 on RDS (Multi-AZ capable)
- Tests: SQLite in-memory with `StaticPool` (no external dependency)
- ORM: SQLAlchemy 2.0 with classic `sessionmaker` pattern
- Migrations: Alembic with `--autogenerate`

## Consequences

**Positive:**
- PostgreSQL is battle-tested for SaaS workloads
- SQLAlchemy abstracts the dialect — tests use SQLite with no mocking needed
- Alembic gives a full audit trail of schema changes

**Negative:**
- SQLite doesn't support all PostgreSQL features (e.g., JSONB, arrays) — tests may miss dialect-specific bugs
- RDS adds operational overhead vs. managed Supabase

## Alternatives considered

- **Supabase**: Considered for managed PostgreSQL + auth, deferred — current RDS setup already works
- **MongoDB**: Rejected — relational model fits our entity relationships better
