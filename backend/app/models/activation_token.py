import hashlib
import secrets
import uuid
from datetime import datetime, timedelta

from sqlalchemy import Boolean, Column, DateTime, String, Text

from app.database import Base

TOKEN_TTL_DAYS = 7


class ActivationToken(Base):
    __tablename__ = "activation_tokens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), nullable=False, index=True)
    token_hash = Column(String(64), nullable=False, unique=True)
    plan = Column(String(50), nullable=False)
    agent_ids = Column(Text, nullable=True)  # JSON array stored as text
    stripe_subscription_id = Column(String(100), nullable=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def generate() -> tuple[str, str]:
        raw = secrets.token_urlsafe(48)
        hashed = hashlib.sha256(raw.encode()).hexdigest()
        return raw, hashed

    @staticmethod
    def hash(raw: str) -> str:
        return hashlib.sha256(raw.encode()).hexdigest()

    @staticmethod
    def default_expiry() -> datetime:
        return datetime.utcnow() + timedelta(days=TOKEN_TTL_DAYS)
