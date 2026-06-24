"""Add workspace_invites table

Revision ID: 006_workspace_invites
Revises: 005_stripe_idempotency_brand_support
Create Date: 2026-06-23
"""
from alembic import op

revision = "006_workspace_invites"
down_revision = "005_stripe_idempotency_brand_support"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS workspace_invites (
            id            TEXT        PRIMARY KEY,
            workspace_id  TEXT        NOT NULL,
            invited_email TEXT        NOT NULL,
            role          TEXT        DEFAULT 'member',
            token_hash    TEXT        NOT NULL UNIQUE,
            invited_by    TEXT        NOT NULL,
            expires_at    TIMESTAMP   NOT NULL,
            accepted_at   TIMESTAMP,
            created_at    TIMESTAMP
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_workspace_invites_token_hash ON workspace_invites (token_hash)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_workspace_invites_workspace_id ON workspace_invites (workspace_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS workspace_invites")
