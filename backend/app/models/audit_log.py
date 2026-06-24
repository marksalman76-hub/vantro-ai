import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String, nullable=False)          # e.g. "login", "agent_run", "approve_job"
    resource_type = Column(String, nullable=True)    # e.g. "agent_job", "user"
    resource_id = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    extra = Column(JSON, nullable=True)              # free-form context
    created_at = Column(DateTime, default=datetime.utcnow)
