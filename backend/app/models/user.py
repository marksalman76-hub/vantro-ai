import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON
from app.database import Base
from app.services.encrypted_column import EncryptedText

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(EncryptedText, nullable=True)  # PII — encrypted at rest
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=True)
    stripe_customer_id = Column(String, nullable=True)
    subscription_status = Column(String, nullable=True)
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    brand_profile = Column(JSON, nullable=True)
    is_admin = Column(Boolean, default=False)
    # Populated in DB from the real schema; nullable to avoid FK issues on creation
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=True)
    locked_agent_ids = Column(String, nullable=True)  # JSON array — set at payment, never changed after
    stripe_subscription_id = Column(String, nullable=True)
    subscription_period_end = Column(DateTime, nullable=True)
    cookie_consent = Column(Boolean, nullable=True, default=None)
    cookie_consent_at = Column(DateTime, nullable=True)