"""009 — workspace business_context column

Revision ID: 009
Revises: 008_refresh_tokens_audit_admin
Create Date: 2026-06-24
"""
from alembic import op
import sqlalchemy as sa

revision = "009"
down_revision = "008_refresh_tokens_audit_admin"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('workspaces', sa.Column('business_context', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('workspaces', 'business_context')
