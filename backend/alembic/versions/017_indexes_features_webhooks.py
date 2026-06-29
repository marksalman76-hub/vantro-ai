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


def _table_exists(conn, table_name: str) -> bool:
    return bool(conn.execute(
        sa.text("SELECT to_regclass(:table_name)"),
        {"table_name": table_name},
    ).scalar())


def _column_exists(conn, table_name: str, column_name: str) -> bool:
    return bool(conn.execute(
        sa.text("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = :table_name AND column_name = :column_name
            )
        """),
        {"table_name": table_name, "column_name": column_name},
    ).scalar())


def upgrade() -> None:
    conn = op.get_bind()

    for table_name, column_name, stmt in [
        ("agent_jobs", "workspace_id", "CREATE INDEX IF NOT EXISTS idx_agent_jobs_workspace_id ON agent_jobs(workspace_id)"),
        ("agent_jobs", "status", "CREATE INDEX IF NOT EXISTS idx_agent_jobs_status ON agent_jobs(status)"),
        ("agent_jobs", "created_at", "CREATE INDEX IF NOT EXISTS idx_agent_jobs_created_at ON agent_jobs(created_at DESC)"),
        ("users", "organization_id", "CREATE INDEX IF NOT EXISTS idx_users_organization_id ON users(organization_id)"),
    ]:
        if _column_exists(conn, table_name, column_name):
            conn.execute(sa.text(stmt))

    if _table_exists(conn, "credit_ledger") and _column_exists(conn, "credit_ledger", "workspace_id"):
        conn.execute(sa.text(
            "CREATE INDEX IF NOT EXISTS idx_credit_ledger_workspace ON credit_ledger(workspace_id)"
        ))

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

    if _column_exists(conn, "webhooks_log", "workspace_id"):
        conn.execute(sa.text(
            "CREATE INDEX IF NOT EXISTS idx_webhooks_log_workspace ON webhooks_log(workspace_id)"
        ))


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
