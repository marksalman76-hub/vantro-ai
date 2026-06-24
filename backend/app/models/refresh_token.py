import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from app.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String, unique=True, nullable=False)  # SHA-256 of the opaque token
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
