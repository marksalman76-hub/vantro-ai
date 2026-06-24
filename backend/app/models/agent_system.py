import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class WorkspaceIntegration(Base):
    """Encrypted third-party credentials per workspace. Raw values never logged or returned."""
    __tablename__ = "workspace_integrations"
    id                = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id      = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    integration_key   = Column(String, nullable=False)   # e.g. "OPENAI_API_KEY"
    integration_name  = Column(String, nullable=True)    # e.g. "OpenAI"
    encrypted_value   = Column(Text,   nullable=False)   # Fernet-encrypted
    is_active         = Column(Boolean, nullable=False, default=True)
    last_tested_at    = Column(DateTime, nullable=True)
    last_test_status  = Column(String, nullable=True)    # "ok" | "failed" | None
    created_at        = Column(DateTime, nullable=True, default=datetime.utcnow)
    updated_at        = Column(DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)

    workspace = relationship("Workspace", backref="integrations")


class AgentJob(Base):
    __tablename__ = "agent_jobs"
    id              = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id    = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    agent_id        = Column(String, nullable=False)
    agent_name      = Column(String, nullable=True)
    status          = Column(String, nullable=False, default="pending")
    hitl_level      = Column(String, nullable=True)
    input_data      = Column(Text, nullable=True)
    output_data     = Column(Text, nullable=True)
    credits_used    = Column(Integer, nullable=False, default=0)
    error_message   = Column(Text, nullable=True)
    created_at      = Column(DateTime, nullable=True)
    updated_at      = Column(DateTime, nullable=True)
    completed_at    = Column(DateTime, nullable=True)
    # Quality + language
    output_language = Column(String, nullable=True)    # "English", "Spanish", etc.
    agent_version   = Column(String, nullable=True)    # model+prompt hash for reproducibility
    prompt_snapshot = Column(Text,   nullable=True)    # system prompt used at execution time
    steps           = Column(Text,   nullable=True)    # JSON [{step, status, ts}] progress timeline
    # Client feedback
    rating          = Column(Integer, nullable=True)   # 1-5 stars
    rating_comment  = Column(Text,    nullable=True)
    # Revision chain
    revision_of     = Column(String,  ForeignKey("agent_jobs.id"), nullable=True)
    revision_prompt = Column(Text,    nullable=True)

    workspace = relationship("Workspace", backref="agent_jobs")


class ScheduledRun(Base):
    """Workspace-level scheduled agent runs (cron-based automation)."""
    __tablename__ = "scheduled_runs"
    id           = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    agent_id     = Column(String, nullable=False)
    name         = Column(String, nullable=True)         # "Weekly SEO Report"
    cron_expr    = Column(String, nullable=False)        # "0 9 * * 1" = Mon 9am UTC
    prompt       = Column(Text,   nullable=False)
    context      = Column(Text,   nullable=True)         # JSON extra context
    is_active    = Column(Boolean, nullable=False, default=True)
    last_run_at  = Column(DateTime, nullable=True)
    next_run_at  = Column(DateTime, nullable=True)
    created_at   = Column(DateTime, nullable=True, default=datetime.utcnow)

    workspace = relationship("Workspace", backref="scheduled_runs")


class APIKey(Base):
    """Workspace API keys for programmatic agent access (API tier)."""
    __tablename__ = "api_keys"
    id           = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id      = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    key_hash     = Column(String, unique=True, nullable=False)  # SHA-256 of raw key
    key_prefix   = Column(String, nullable=False)               # "vtro_" + first 8 chars
    name         = Column(String, nullable=True)
    is_active    = Column(Boolean, nullable=False, default=True)
    last_used_at = Column(DateTime, nullable=True)
    created_at   = Column(DateTime, nullable=True, default=datetime.utcnow)
    expires_at   = Column(DateTime, nullable=True)

    workspace = relationship("Workspace", backref="api_keys")


class PackageDownload(Base):
    __tablename__ = "package_downloads"
    id           = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    package_name = Column(String, nullable=False)
    otc_code     = Column(String, nullable=False, unique=True)
    is_used      = Column(Boolean, nullable=False, default=False)
    used_at      = Column(DateTime, nullable=True)
    expires_at   = Column(DateTime, nullable=True)
    ip_address   = Column(String, nullable=True)
    created_at   = Column(DateTime, nullable=True)
    updated_at   = Column(DateTime, nullable=True)

    workspace = relationship("Workspace", backref="package_downloads")
