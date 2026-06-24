"""008 — refresh_tokens, audit_logs, is_admin column

Revision ID: 008_refresh_tokens_audit_admin
Revises: 007_weekly_reports_team_templates
Create Date: 2026-06-23
"""
from alembic import op
import sqlalchemy as sa

revision = "008_refresh_tokens_audit_admin"
down_revision = "007_weekly_reports_team_templates"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── refresh_tokens ────────────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS refresh_tokens (
            id            VARCHAR PRIMARY KEY,
            user_id       VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            token_hash    VARCHAR UNIQUE NOT NULL,
            expires_at    TIMESTAMP NOT NULL,
            created_at    TIMESTAMP DEFAULT NOW(),
            revoked_at    TIMESTAMP,
            user_agent    VARCHAR(255),
            ip_address    VARCHAR(45)
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_refresh_tokens_user_id ON refresh_tokens(user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_refresh_tokens_expires_at ON refresh_tokens(expires_at)")

    # ── audit_logs ────────────────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id            VARCHAR PRIMARY KEY,
            user_id       VARCHAR REFERENCES users(id) ON DELETE SET NULL,
            action        VARCHAR(100) NOT NULL,
            resource_type VARCHAR(50),
            resource_id   VARCHAR,
            ip_address    VARCHAR(45),
            user_agent    VARCHAR(255),
            extra         JSONB,
            created_at    TIMESTAMP DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_user_id    ON audit_logs(user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_action      ON audit_logs(action)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_created_at  ON audit_logs(created_at)")

    # ── users: add is_admin column ────────────────────────────────────────────
    op.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS is_admin BOOLEAN NOT NULL DEFAULT FALSE
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS is_admin")
    op.execute("DROP TABLE IF EXISTS audit_logs")
    op.execute("DROP TABLE IF EXISTS refresh_tokens")
