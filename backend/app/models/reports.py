import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON
from app.database import Base


def _json_col(**kwargs):
    """Use JSONB on Postgres, fall back to JSON on SQLite (testing)."""
    try:
        return Column(JSONB, **kwargs)
    except Exception:
        return Column(JSON, **kwargs)


class WorkspaceReportSettings(Base):
    __tablename__ = "workspace_report_settings"
    id                      = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id            = Column(String, nullable=False, unique=True)
    enabled                 = Column(Boolean, nullable=False, default=True)
    schedule_day            = Column(String, nullable=False, default="monday")
    schedule_hour           = Column(Integer, nullable=False, default=9)
    timezone                = Column(String, nullable=False, default="UTC")
    consolidated            = Column(Boolean, nullable=False, default=True)
    include_credit_summary  = Column(Boolean, nullable=False, default=True)
    include_recommendations = Column(Boolean, nullable=False, default=True)
    include_failures        = Column(Boolean, nullable=False, default=True)
    include_output_links    = Column(Boolean, nullable=False, default=True)
    recipients              = Column(JSON, nullable=False, default=list)
    created_at              = Column(DateTime, nullable=True)
    updated_at              = Column(DateTime, nullable=True)


class WeeklyReport(Base):
    __tablename__ = "weekly_reports"
    id                      = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id            = Column(String, nullable=False)
    reporting_period_start  = Column(DateTime, nullable=False)
    reporting_period_end    = Column(DateTime, nullable=False)
    sections                = Column(JSON, nullable=False, default=list)   # list of per-agent dicts
    team_sections           = Column(JSON, nullable=False, default=list)   # list of per-team dicts
    executive_summary       = Column(Text, nullable=True)
    status                  = Column(String, nullable=False, default="generated")
    email_sent_at           = Column(DateTime, nullable=True)
    email_recipients        = Column(JSON, nullable=False, default=list)
    delivery_status         = Column(String, nullable=False, default="pending")
    delivery_error          = Column(Text, nullable=True)
    disabled_by_admin       = Column(Boolean, nullable=False, default=False)
    created_at              = Column(DateTime, nullable=True)
    updated_at              = Column(DateTime, nullable=True)


class ReportFeedback(Base):
    __tablename__ = "report_feedback"
    id           = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id    = Column(String, nullable=False)
    workspace_id = Column(String, nullable=False)
    rating       = Column(String, nullable=False)  # 'useful' | 'not_useful' | etc.
    comment      = Column(Text, nullable=True)
    created_at   = Column(DateTime, nullable=True)


class TeamTemplate(Base):
    __tablename__ = "team_templates"
    id           = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, nullable=True)   # None = platform template
    name         = Column(String, nullable=False)
    description  = Column(Text, nullable=True)
    agent_ids    = Column(JSON, nullable=False, default=list)
    lead_agent_id = Column(String, nullable=True)
    is_platform  = Column(Boolean, nullable=False, default=False)
    min_package  = Column(String, nullable=True)
    created_by   = Column(String, nullable=True)   # None = platform
    created_at   = Column(DateTime, nullable=True)
    updated_at   = Column(DateTime, nullable=True)
