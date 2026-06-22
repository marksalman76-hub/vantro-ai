import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Workspace(Base):
    __tablename__ = "workspaces"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    workspace_type = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    credits_account = relationship("CreditsAccount", back_populates="workspace", uselist=False)
    media_jobs = relationship("MediaJob", back_populates="workspace")


class CreditsAccount(Base):
    __tablename__ = "credits_accounts"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False, unique=True)
    total_credits = Column(Integer, default=0)
    used_credits = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    workspace = relationship("Workspace", back_populates="credits_account")


class MediaJob(Base):
    __tablename__ = "media_jobs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    avatar_id = Column(String, nullable=False)
    voice_id = Column(String, nullable=False)
    language = Column(String, nullable=True)
    tone = Column(String, nullable=True)
    script = Column(Text, nullable=False)
    facial_expressions = Column(String, nullable=True)
    eye_movement = Column(String, nullable=True)
    blinking = Column(String, nullable=True)
    head_movement = Column(String, nullable=True)
    external_job_id = Column(String, nullable=True)
    status = Column(String, default="pending")
    video_url = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    workspace = relationship("Workspace", back_populates="media_jobs")
