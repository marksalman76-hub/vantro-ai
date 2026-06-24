"""Add activation_tokens table for first-payment one-time links

Revision ID: 013
Revises: 012
Create Date: 2026-06-24
"""
from alembic import op
import sqlalchemy as sa

revision = "013"
down_revision = "012"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "activation_tokens",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("workspace_id", sa.String(36), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("plan", sa.String(50), nullable=False),
        sa.Column("agent_ids", sa.Text(), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(100), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_activation_tokens_workspace", "activation_tokens", ["workspace_id"])
    op.create_index("ix_activation_tokens_hash", "activation_tokens", ["token_hash"])


def downgrade():
    op.drop_index("ix_activation_tokens_hash", table_name="activation_tokens")
    op.drop_index("ix_activation_tokens_workspace", table_name="activation_tokens")
    op.drop_table("activation_tokens")
