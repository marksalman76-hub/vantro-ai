"""add quality/language/versioning/scheduling/api_keys

Revision ID: 016
Revises: 015
Create Date: 2026-06-24
"""
from alembic import op
import sqlalchemy as sa

revision = "016"
down_revision = "015"
branch_labels = None
depends_on = None


def upgrade():
    # AgentJob quality + tracking fields
    op.add_column("agent_jobs", sa.Column("output_language", sa.String(), nullable=True))
    op.add_column("agent_jobs", sa.Column("agent_version",   sa.String(), nullable=True))
    op.add_column("agent_jobs", sa.Column("prompt_snapshot", sa.Text(),   nullable=True))
    op.add_column("agent_jobs", sa.Column("steps",           sa.Text(),   nullable=True))
    op.add_column("agent_jobs", sa.Column("rating",          sa.Integer(),nullable=True))
    op.add_column("agent_jobs", sa.Column("rating_comment",  sa.Text(),   nullable=True))
    op.add_column("agent_jobs", sa.Column("revision_of",     sa.String(), nullable=True))
    op.add_column("agent_jobs", sa.Column("revision_prompt", sa.Text(),   nullable=True))

    # ScheduledRun table
    op.create_table(
        "scheduled_runs",
        sa.Column("id",          sa.String(), primary_key=True),
        sa.Column("workspace_id",sa.String(), sa.ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id",    sa.String(), nullable=False),
        sa.Column("name",        sa.String(), nullable=True),
        sa.Column("cron_expr",   sa.String(), nullable=False),
        sa.Column("prompt",      sa.Text(),   nullable=False),
        sa.Column("context",     sa.Text(),   nullable=True),
        sa.Column("is_active",   sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_run_at", sa.DateTime(), nullable=True),
        sa.Column("next_run_at", sa.DateTime(), nullable=True),
        sa.Column("created_at",  sa.DateTime(), nullable=True),
    )
    op.create_index("ix_scheduled_runs_workspace", "scheduled_runs", ["workspace_id"])

    # APIKey table
    op.create_table(
        "api_keys",
        sa.Column("id",          sa.String(), primary_key=True),
        sa.Column("workspace_id",sa.String(), sa.ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id",     sa.String(), sa.ForeignKey("users.id",       ondelete="CASCADE"), nullable=False),
        sa.Column("key_hash",    sa.String(), nullable=False, unique=True),
        sa.Column("key_prefix",  sa.String(), nullable=False),
        sa.Column("name",        sa.String(), nullable=True),
        sa.Column("is_active",   sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_used_at",sa.DateTime(), nullable=True),
        sa.Column("created_at",  sa.DateTime(), nullable=True),
        sa.Column("expires_at",  sa.DateTime(), nullable=True),
    )
    op.create_index("ix_api_keys_key_hash", "api_keys", ["key_hash"])


def downgrade():
    op.drop_table("api_keys")
    op.drop_table("scheduled_runs")
    for col in ["revision_prompt", "revision_of", "rating_comment", "rating",
                "steps", "prompt_snapshot", "agent_version", "output_language"]:
        op.drop_column("agent_jobs", col)
