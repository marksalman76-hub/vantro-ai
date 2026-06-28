"""Add team_runs table and team_run_id to agent_jobs

Revision ID: 021
Revises: 020
Create Date: 2026-06-28
"""

import sqlalchemy as sa
from alembic import op

revision = "021"
down_revision = "020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "team_runs",
        sa.Column("id",                     sa.String(36),  primary_key=True),
        sa.Column("workspace_id",           sa.String(36),  nullable=False),
        sa.Column("lead_agent_id",          sa.String(100), nullable=False),
        sa.Column("agent_ids",              sa.Text,        nullable=False),
        sa.Column("objective",              sa.Text,        nullable=False),
        sa.Column("status",                 sa.String(30),  nullable=False, server_default="pending"),
        sa.Column("output",                 sa.Text,        nullable=True),
        sa.Column("credits_used",           sa.Integer,     nullable=False, server_default="0"),
        sa.Column("requires_hitl3_approval", sa.Boolean,   nullable=False, server_default=sa.false()),
        sa.Column("created_at",             sa.DateTime,    nullable=True),
        sa.Column("completed_at",           sa.DateTime,    nullable=True),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
    )

    op.add_column(
        "agent_jobs",
        sa.Column("team_run_id", sa.String(36), nullable=True),
    )
    op.create_foreign_key(
        "fk_agent_jobs_team_run_id",
        "agent_jobs", "team_runs",
        ["team_run_id"], ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_agent_jobs_team_run_id", "agent_jobs", ["team_run_id"])


def downgrade() -> None:
    op.drop_index("ix_agent_jobs_team_run_id", "agent_jobs")
    op.drop_constraint("fk_agent_jobs_team_run_id", "agent_jobs", type_="foreignkey")
    op.drop_column("agent_jobs", "team_run_id")
    op.drop_table("team_runs")
