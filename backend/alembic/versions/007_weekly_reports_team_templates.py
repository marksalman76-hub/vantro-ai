"""Add weekly_reports, team_templates, workspace_report_settings, report_feedback

Revision ID: 007_weekly_reports_team_templates
Revises: 006_workspace_invites
Create Date: 2026-06-23
"""
from alembic import op

revision = "007_weekly_reports_team_templates"
down_revision = "006_workspace_invites"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Workspace-level report preferences
    op.execute("""
        CREATE TABLE IF NOT EXISTS workspace_report_settings (
            id                      TEXT        PRIMARY KEY,
            workspace_id            TEXT        NOT NULL UNIQUE REFERENCES workspaces(id) ON DELETE CASCADE,
            enabled                 BOOLEAN     NOT NULL DEFAULT true,
            schedule_day            TEXT        NOT NULL DEFAULT 'monday',
            schedule_hour           INTEGER     NOT NULL DEFAULT 9,
            timezone                TEXT        NOT NULL DEFAULT 'UTC',
            consolidated            BOOLEAN     NOT NULL DEFAULT true,
            include_credit_summary  BOOLEAN     NOT NULL DEFAULT true,
            include_recommendations BOOLEAN     NOT NULL DEFAULT true,
            include_failures        BOOLEAN     NOT NULL DEFAULT true,
            include_output_links    BOOLEAN     NOT NULL DEFAULT true,
            recipients              JSONB       NOT NULL DEFAULT '[]',
            created_at              TIMESTAMP   NOT NULL DEFAULT NOW(),
            updated_at              TIMESTAMP
        )
    """)

    # Generated weekly reports
    op.execute("""
        CREATE TABLE IF NOT EXISTS weekly_reports (
            id                      TEXT        PRIMARY KEY,
            workspace_id            TEXT        NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
            reporting_period_start  TIMESTAMP   NOT NULL,
            reporting_period_end    TIMESTAMP   NOT NULL,
            sections                JSONB       NOT NULL DEFAULT '[]',
            team_sections           JSONB       NOT NULL DEFAULT '[]',
            executive_summary       TEXT,
            status                  TEXT        NOT NULL DEFAULT 'generated',
            email_sent_at           TIMESTAMP,
            email_recipients        JSONB       NOT NULL DEFAULT '[]',
            delivery_status         TEXT        NOT NULL DEFAULT 'pending',
            delivery_error          TEXT,
            disabled_by_admin       BOOLEAN     NOT NULL DEFAULT false,
            created_at              TIMESTAMP   NOT NULL DEFAULT NOW(),
            updated_at              TIMESTAMP
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_weekly_reports_workspace_id ON weekly_reports (workspace_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_weekly_reports_created_at ON weekly_reports (created_at DESC)")

    # Client/admin report feedback
    op.execute("""
        CREATE TABLE IF NOT EXISTS report_feedback (
            id              TEXT        PRIMARY KEY,
            report_id       TEXT        NOT NULL REFERENCES weekly_reports(id) ON DELETE CASCADE,
            workspace_id    TEXT        NOT NULL,
            rating          TEXT        NOT NULL,
            comment         TEXT,
            created_at      TIMESTAMP   NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_report_feedback_report_id ON report_feedback (report_id)")

    # Saved team templates (platform + user-created)
    op.execute("""
        CREATE TABLE IF NOT EXISTS team_templates (
            id              TEXT        PRIMARY KEY,
            workspace_id    TEXT        REFERENCES workspaces(id) ON DELETE CASCADE,
            name            TEXT        NOT NULL,
            description     TEXT,
            agent_ids       JSONB       NOT NULL DEFAULT '[]',
            lead_agent_id   TEXT,
            is_platform     BOOLEAN     NOT NULL DEFAULT false,
            min_package     TEXT,
            created_by      TEXT,
            created_at      TIMESTAMP   NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMP
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_team_templates_workspace_id ON team_templates (workspace_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS team_templates")
    op.execute("DROP TABLE IF EXISTS report_feedback")
    op.execute("DROP TABLE IF EXISTS weekly_reports")
    op.execute("DROP TABLE IF EXISTS workspace_report_settings")
