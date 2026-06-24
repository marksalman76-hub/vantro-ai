"""add locked_agent_ids to users

Revision ID: 014
Revises: 013
Create Date: 2026-06-24
"""
from alembic import op
import sqlalchemy as sa

revision = "014"
down_revision = "013"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("locked_agent_ids", sa.Text(), nullable=True),
    )


def downgrade():
    op.drop_column("users", "locked_agent_ids")
