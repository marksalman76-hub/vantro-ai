"""Add Composio as a supported workspace integration provider.

Revision ID: 010
Revises: 009_workspace_business_context
Create Date: 2026-06-24

No schema changes are required.  The workspace_integrations table already
contains all necessary columns (workspace_id, integration_key, integration_name,
encrypted_value, is_active, last_tested_at, last_test_status, created_at,
updated_at).

Composio credentials are stored as two rows per workspace:
  integration_key = "COMPOSIO_API_KEY"    — Fernet-encrypted API key
  integration_key = "COMPOSIO_ENTITY_ID"  — Fernet-encrypted entity identifier

This migration adds an index on (workspace_id, integration_key) to speed up
the per-workspace credential lookups performed by composio_service.py.
If the index already exists (idempotent), the migration succeeds silently.
"""
from alembic import op
import sqlalchemy as sa

revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Create workspace_integrations if it doesn't exist yet
    if "workspace_integrations" not in inspector.get_table_names():
        op.create_table(
            "workspace_integrations",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("workspace_id", sa.String(), sa.ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False),
            sa.Column("integration_key", sa.String(), nullable=False),
            sa.Column("integration_name", sa.String(), nullable=True),
            sa.Column("encrypted_value", sa.Text(), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
            sa.Column("last_tested_at", sa.DateTime(), nullable=True),
            sa.Column("last_test_status", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )

    # Add composite index if absent
    existing_indexes = {
        idx["name"]
        for idx in inspector.get_indexes("workspace_integrations")
    }
    if "ix_workspace_integrations_ws_key" not in existing_indexes:
        op.create_index(
            "ix_workspace_integrations_ws_key",
            "workspace_integrations",
            ["workspace_id", "integration_key"],
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_indexes = {
        idx["name"]
        for idx in inspector.get_indexes("workspace_integrations")
    }
    if "ix_workspace_integrations_ws_key" in existing_indexes:
        op.drop_index("ix_workspace_integrations_ws_key", table_name="workspace_integrations")
