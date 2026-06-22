import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class AgentJob(Base):
    __tablename__ = "agent_jobs"
    id           = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    agent_id     = Column(String, nullable=False)
    agent_name   = Column(String, nullable=True)
    status       = Column(String, nullable=False, default="pending")
    hitl_level   = Column(String, nullable=True)
    input_data   = Column(Text, nullable=True)
    output_data  = Column(Text, nullable=True)
    credits_used = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)
    created_at   = Column(DateTime, nullable=True)
    updated_at   = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    workspace = relationship("Workspace", backref="agent_jobs")


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
