from datetime import datetime, timedelta
from typing import Optional
import os
import uuid
import jwt

from app.config import get_config

_secret = get_config("SECRET_KEY") or get_config("JWT_SECRET")
if not _secret or _secret == "dev-secret-key-change-in-production":
    _env = os.getenv("ENVIRONMENT", "development")
    if _env == "production":
        raise ValueError(
            "SECRET_KEY / JWT_SECRET is not set or still uses the dev default. "
            "Set it via environment variable or AWS Secrets Manager before starting in production."
        )
    _secret = "dev-secret-key-change-in-production"

SECRET_KEY: str = _secret
ACCESS_TOKEN_EXPIRE_MINUTES = 60   # 1 hour; refresh tokens keep sessions alive longer
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    jti = str(uuid.uuid4())
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"sub": user_id, "jti": jti, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        jti = payload.get("jti")
        if jti:
            try:
                from app.services.cache_service import is_token_revoked
                if is_token_revoked(jti):
                    return None
            except Exception:
                pass  # Redis unavailable — fail open; prefer availability
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
