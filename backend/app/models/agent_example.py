from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class AgentExample(Base):
    __tablename__ = "agent_examples"

    id = Column(Integer, primary_key=True)
    agent_id = Column(String(100), nullable=False, index=True)
    task_description = Column(Text, nullable=False)
    exemplary_output = Column(Text, nullable=False)
    quality_note = Column(String(500), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    source_job_id = Column(String(100), nullable=True)   # AgentJob.id is a UUID string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(100), nullable=True)       # User.id is a UUID string
