import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=True)
    stripe_customer_id = Column(String, nullable=True)
    subscription_status = Column(String, nullable=True)
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    # Populated in DB from the real schema; nullable to avoid FK issues on creation
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=True)