from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from app.database import Base


class OTPToken(Base):
    __tablename__ = "otp_tokens"

    id = Column(String(36), primary_key=True)
    email = Column(String(255), nullable=False, index=True)
    token_hash = Column(String(64), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
