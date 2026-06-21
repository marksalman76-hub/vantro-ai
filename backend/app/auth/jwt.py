from datetime import datetime, timedelta
from typing import Optional
import os
import jwt

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = {"sub": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except:
        return None
