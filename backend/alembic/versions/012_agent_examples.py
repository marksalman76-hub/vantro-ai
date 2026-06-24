"""Add agent_examples table for few-shot quality examples

Revision ID: 012
Revises: 011
Create Date: 2026-06-24
"""
from alembic import op
import sqlalchemy as sa

revision = "012"
down_revision = "011"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "agent_examples",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("agent_id", sa.String(100), nullable=False, index=True),
        sa.Column("task_description", sa.Text(), nullable=False),
        sa.Column("exemplary_output", sa.Text(), nullable=False),
        sa.Column("quality_note", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True, server_default="true"),
        sa.Column("source_job_id", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_by", sa.String(100), nullable=True),
    )
    op.create_index("ix_agent_examples_agent_active", "agent_examples", ["agent_id", "is_active"])


def downgrade():
    op.drop_index("ix_agent_examples_agent_active", table_name="agent_examples")
    op.drop_table("agent_examples")
