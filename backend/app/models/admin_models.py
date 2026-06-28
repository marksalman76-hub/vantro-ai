from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, Index
from app.database import Base


class Announcement(Base):
    __tablename__ = "announcements"

    id          = Column(String(36), primary_key=True)
    title       = Column(String(200), nullable=False)
    body        = Column(Text, nullable=False)
    affects     = Column(Text)
    type        = Column(String(30), nullable=False, default="info")
    target_tier = Column(String(30), nullable=False, default="all")
    active      = Column(Boolean, default=True, nullable=False)
    show_as     = Column(String(20), nullable=False, default="banner")
    created_at  = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at  = Column(DateTime, nullable=True)
    created_by  = Column(String(200))


class AgentChangelog(Base):
    __tablename__ = "agent_changelogs"

    id           = Column(String(36), primary_key=True)
    agent_id     = Column(String(100), nullable=False, index=True)
    agent_name   = Column(String(200), nullable=False)
    version      = Column(String(30), nullable=False)
    summary      = Column(String(300), nullable=False)
    changes      = Column(JSON, default=list)
    affects      = Column(Text)
    release_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by   = Column(String(200))

    __table_args__ = (
        Index('idx_agent_changelog_agent_date', 'agent_id', 'release_date'),
    )


class SystemStatus(Base):
    __tablename__ = "system_status"

    id         = Column(Integer, primary_key=True, default=1)
    overall    = Column(String(30), nullable=False, default="operational")
    message    = Column(Text)
    components = Column(JSON, default=list)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_by = Column(String(200))
