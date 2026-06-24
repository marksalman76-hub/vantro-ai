"""Add announcements, agent_changelogs, system_status tables

Revision ID: 020
Revises: 019
Create Date: 2026-06-24
"""

import sqlalchemy as sa
from alembic import op

revision = "020"
down_revision = "019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "announcements",
        sa.Column("id",          sa.String(36),  primary_key=True),
        sa.Column("title",       sa.String(200), nullable=False),
        sa.Column("body",        sa.Text,        nullable=False),
        sa.Column("affects",     sa.Text,        nullable=True),
        sa.Column("type",        sa.String(30),  nullable=False, server_default="info"),
        sa.Column("target_tier", sa.String(30),  nullable=False, server_default="all"),
        sa.Column("active",      sa.Boolean,     nullable=False, server_default=sa.true()),
        sa.Column("show_as",     sa.String(20),  nullable=False, server_default="banner"),
        sa.Column("created_at",  sa.DateTime,    nullable=False),
        sa.Column("expires_at",  sa.DateTime,    nullable=True),
        sa.Column("created_by",  sa.String(200), nullable=True),
    )
    op.create_index("idx_announcements_active_tier", "announcements", ["active", "target_tier", "created_at"])

    op.create_table(
        "agent_changelogs",
        sa.Column("id",           sa.String(36),  primary_key=True),
        sa.Column("agent_id",     sa.String(100), nullable=False),
        sa.Column("agent_name",   sa.String(200), nullable=False),
        sa.Column("version",      sa.String(30),  nullable=False),
        sa.Column("summary",      sa.String(300), nullable=False),
        sa.Column("changes",      sa.JSON,        nullable=True),
        sa.Column("affects",      sa.Text,        nullable=True),
        sa.Column("release_date", sa.DateTime,    nullable=False),
        sa.Column("created_by",   sa.String(200), nullable=True),
    )
    op.create_index("idx_agent_changelog_agent_date", "agent_changelogs", ["agent_id", "release_date"])

    op.create_table(
        "system_status",
        sa.Column("id",         sa.Integer,     primary_key=True),
        sa.Column("overall",    sa.String(30),  nullable=False, server_default="operational"),
        sa.Column("message",    sa.Text,        nullable=True),
        sa.Column("components", sa.JSON,        nullable=True),
        sa.Column("updated_at", sa.DateTime,    nullable=False),
        sa.Column("updated_by", sa.String(200), nullable=True),
    )

    # Seed default system status row
    op.execute(
        "INSERT INTO system_status (id, overall, message, components, updated_at) "
        "VALUES (1, 'operational', NULL, '[]', NOW())"
    )


def downgrade() -> None:
    op.drop_table("system_status")
    op.drop_index("idx_agent_changelog_agent_date", "agent_changelogs")
    op.drop_table("agent_changelogs")
    op.drop_index("idx_announcements_active_tier", "announcements")
    op.drop_table("announcements")
