"""indexes, feature_flags, webhooks_log

Revision ID: 017
Revises: 016
Create Date: 2026-06-24
"""

from alembic import op
import sqlalchemy as sa

revision = "017"
down_revision = "016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # ── Indexes ──────────────────────────────────────────────────────────────
    for stmt in [
        "CREATE INDEX IF NOT EXISTS idx_agent_jobs_workspace_id ON agent_jobs(workspace_id)",
        "CREATE INDEX IF NOT EXISTS idx_agent_jobs_status ON agent_jobs(status)",
        "CREATE INDEX IF NOT EXISTS idx_agent_jobs_created_at ON agent_jobs(created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_users_organization_id ON users(organization_id)",
    ]:
        try:
            conn.execute(sa.text(stmt))
        except Exception:
            pass

    # credit_ledger index — only if table exists
    try:
        result = conn.execute(
            sa.text("SELECT to_regclass('credit_ledger')")
        ).scalar()
        if result:
            try:
                conn.execute(sa.text(
                    "CREATE INDEX IF NOT EXISTS idx_credit_ledger_workspace ON credit_ledger(workspace_id)"
                ))
            except Exception:
                pass
    except Exception:
        pass

    # ── feature_flags ────────────────────────────────────────────────────────
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS feature_flags (
            id VARCHAR PRIMARY KEY,
            key VARCHAR UNIQUE NOT NULL,
            is_enabled BOOLEAN NOT NULL DEFAULT false,
            description TEXT,
            target_workspace_ids JSONB,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
        )
    """))

    # ── webhooks_log ─────────────────────────────────────────────────────────
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS webhooks_log (
            id VARCHAR PRIMARY KEY,
            workspace_id VARCHAR REFERENCES workspaces(id) ON DELETE SET NULL,
            event_type VARCHAR NOT NULL,
            payload TEXT,
            status VARCHAR NOT NULL DEFAULT 'pending',
            attempts INTEGER NOT NULL DEFAULT 0,
            last_attempted_at TIMESTAMP WITHOUT TIME ZONE,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
        )
    """))

    try:
        conn.execute(sa.text(
            "CREATE INDEX IF NOT EXISTS idx_webhooks_log_workspace ON webhooks_log(workspace_id)"
        ))
    except Exception:
        pass


def downgrade() -> None:
    conn = op.get_bind()
    for stmt in [
        "DROP TABLE IF EXISTS webhooks_log",
        "DROP TABLE IF EXISTS feature_flags",
        "DROP INDEX IF EXISTS idx_credit_ledger_workspace",
        "DROP INDEX IF EXISTS idx_users_organization_id",
        "DROP INDEX IF EXISTS idx_agent_jobs_created_at",
        "DROP INDEX IF EXISTS idx_agent_jobs_status",
        "DROP INDEX IF EXISTS idx_agent_jobs_workspace_id",
    ]:
        try:
            conn.execute(sa.text(stmt))
        except Exception:
            pass
