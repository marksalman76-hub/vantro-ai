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
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. users: add columns the app models expect ───────────────────────────
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS name                VARCHAR")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_status  VARCHAR")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS stripe_customer_id   VARCHAR")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token           VARCHAR")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token_expires   TIMESTAMP")

    # Back-fill name from first_name + last_name if present
    op.execute("""
        UPDATE users
        SET name = TRIM(COALESCE(first_name,'') || ' ' || COALESCE(last_name,''))
        WHERE name IS NULL AND (first_name IS NOT NULL OR last_name IS NOT NULL)
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

    # Seed credits_accounts from workspaces.total_credits / used_credits if they exist
    op.execute("""
        INSERT INTO credits_accounts (id, workspace_id, total_credits, used_credits, created_at, updated_at)
        SELECT
            gen_random_uuid()::text,
            w.id,
            COALESCE(w.total_credits, 0),
            COALESCE(w.used_credits, 0),
            NOW(),
            NOW()
        FROM workspaces w
        WHERE NOT EXISTS (
            SELECT 1 FROM credits_accounts ca WHERE ca.workspace_id = w.id
        )
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
