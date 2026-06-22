"""Add agent_jobs and package_downloads tables

Revision ID: 003_add_agent_system
Revises: 002_add_heygen_and_password_reset
Create Date: 2026-06-22 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "003_add_agent_system"
down_revision = "002_add_heygen_and_password_reset"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Agent execution jobs — one row per agent run
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

    # Package download OTC — one row per granted download code
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

    op.execute("CREATE INDEX IF NOT EXISTS ix_agent_jobs_workspace_id ON agent_jobs (workspace_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_agent_jobs_agent_id     ON agent_jobs (agent_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_agent_jobs_status       ON agent_jobs (status)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_pkg_downloads_workspace  ON package_downloads (workspace_id)")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_pkg_otc_code     ON package_downloads (otc_code)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS package_downloads")
    op.execute("DROP TABLE IF EXISTS agent_jobs")
