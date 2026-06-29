"""Reconcile diverged schema + add agent_jobs and package_downloads

This migration is idempotent (all statements use IF NOT EXISTS / IF EXISTS guards).
It closes the gap between the existing local DB schema and what the application
models expect, then adds the agent system tables.

Revision ID: 004_reconcile_and_agent_tables
Revises: 001_initial_schema
Create Date: 2026-06-22
"""
from alembic import op
import sqlalchemy as sa

revision = "004_reconcile_and_agent_tables"
down_revision = "003_add_agent_system"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. users: add columns the app models expect ───────────────────────────
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS name                VARCHAR")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_status  VARCHAR")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS stripe_customer_id   VARCHAR")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token           VARCHAR")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token_expires   TIMESTAMP")

    # Back-fill name from first_name + last_name only on legacy schemas that have them.
    op.execute("""
        DO $$
        DECLARE
            first_expr TEXT := quote_literal('');
            last_expr TEXT := quote_literal('');
            first_predicate TEXT := 'false';
            last_predicate TEXT := 'false';
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'first_name'
            ) THEN
                first_expr := 'COALESCE(first_name, '''')';
                first_predicate := 'first_name IS NOT NULL';
            END IF;

            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'last_name'
            ) THEN
                last_expr := 'COALESCE(last_name, '''')';
                last_predicate := 'last_name IS NOT NULL';
            END IF;

            IF first_predicate <> 'false' OR last_predicate <> 'false' THEN
                EXECUTE format(
                    'UPDATE users
                     SET name = TRIM(%s || '' '' || %s)
                     WHERE name IS NULL AND (%s OR %s)',
                    first_expr,
                    last_expr,
                    first_predicate,
                    last_predicate
                );
            END IF;
        END $$;
    """)

    # ── 2. organizations: add owner_id if missing ─────────────────────────────
    op.execute("ALTER TABLE organizations ADD COLUMN IF NOT EXISTS owner_id VARCHAR REFERENCES users(id)")

    # ── 3. credits_accounts table ─────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS credits_accounts (
            id           VARCHAR PRIMARY KEY,
            workspace_id VARCHAR NOT NULL UNIQUE REFERENCES workspaces(id) ON DELETE CASCADE,
            total_credits INTEGER DEFAULT 0,
            used_credits  INTEGER DEFAULT 0,
            created_at    TIMESTAMP,
            updated_at    TIMESTAMP
        )
    """)

    # Seed credits_accounts from legacy workspace credit columns when present.
    op.execute("""
        DO $$
        DECLARE
            total_expr TEXT := '0';
            used_expr TEXT := '0';
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'workspaces' AND column_name = 'total_credits'
            ) THEN
                total_expr := 'COALESCE(w.total_credits, 0)';
            END IF;

            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'workspaces' AND column_name = 'used_credits'
            ) THEN
                used_expr := 'COALESCE(w.used_credits, 0)';
            END IF;

            EXECUTE format(
                'INSERT INTO credits_accounts (id, workspace_id, total_credits, used_credits, created_at, updated_at)
                 SELECT gen_random_uuid()::text, w.id, %s, %s, NOW(), NOW()
                 FROM workspaces w
                 WHERE NOT EXISTS (
                     SELECT 1 FROM credits_accounts ca WHERE ca.workspace_id = w.id
                 )',
                total_expr,
                used_expr
            );
        END $$;
    """)

    # ── 4. media_jobs table ───────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS media_jobs (
            id                  VARCHAR PRIMARY KEY,
            workspace_id        VARCHAR NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
            avatar_id           VARCHAR NOT NULL DEFAULT '',
            voice_id            VARCHAR NOT NULL DEFAULT '',
            language            VARCHAR,
            tone                VARCHAR,
            script              TEXT NOT NULL DEFAULT '',
            facial_expressions  VARCHAR,
            eye_movement        VARCHAR,
            blinking            VARCHAR,
            head_movement       VARCHAR,
            external_job_id     VARCHAR,
            status              VARCHAR DEFAULT 'pending',
            video_url           VARCHAR,
            error_message       TEXT,
            created_at          TIMESTAMP,
            updated_at          TIMESTAMP,
            completed_at        TIMESTAMP
        )
    """)

    # ── 5. agent_jobs table ───────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS agent_jobs (
            id               VARCHAR      PRIMARY KEY,
            workspace_id     VARCHAR      NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
            agent_id         VARCHAR      NOT NULL,
            agent_name       VARCHAR,
            status           VARCHAR      NOT NULL DEFAULT 'pending',
            hitl_level       VARCHAR,
            input_data       TEXT,
            output_data      TEXT,
            credits_used     INTEGER      NOT NULL DEFAULT 0,
            error_message    TEXT,
            created_at       TIMESTAMP,
            updated_at       TIMESTAMP,
            completed_at     TIMESTAMP
        )
    """)

    # ── 6. package_downloads table ────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS package_downloads (
            id               VARCHAR      PRIMARY KEY,
            workspace_id     VARCHAR      NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
            package_name     VARCHAR      NOT NULL,
            otc_code         VARCHAR      NOT NULL UNIQUE,
            is_used          BOOLEAN      NOT NULL DEFAULT FALSE,
            used_at          TIMESTAMP,
            expires_at       TIMESTAMP,
            ip_address       VARCHAR,
            created_at       TIMESTAMP,
            updated_at       TIMESTAMP
        )
    """)

    # ── 7. Indexes ────────────────────────────────────────────────────────────
    op.execute("CREATE INDEX IF NOT EXISTS ix_agent_jobs_workspace_id   ON agent_jobs (workspace_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_agent_jobs_agent_id       ON agent_jobs (agent_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_agent_jobs_status         ON agent_jobs (status)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_pkg_downloads_workspace   ON package_downloads (workspace_id)")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_pkg_otc_code       ON package_downloads (otc_code)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_media_jobs_workspace_id   ON media_jobs (workspace_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_media_jobs_status         ON media_jobs (status)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS package_downloads")
    op.execute("DROP TABLE IF EXISTS agent_jobs")
    op.execute("DROP TABLE IF EXISTS media_jobs")
    op.execute("DROP TABLE IF EXISTS credits_accounts")
