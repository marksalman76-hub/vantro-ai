import hashlib
import os
import re
import secrets
import uuid
from datetime import datetime, timedelta

import jwt as _jwt
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import hash_password, verify_password, create_access_token, verify_token
from app.auth.jwt import SECRET_KEY, REFRESH_TOKEN_EXPIRE_DAYS
from app.database import SessionLocal
from app.limiter import limiter
from app.models import User
from app.models.refresh_token import RefreshToken
from app.models.otp_token import OTPToken
from app.models.audit_log import AuditLog
from app.services import email_service

_IS_PROD = os.getenv("ENVIRONMENT", "development") == "production"

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)

# Minimum password: 8 chars, at least one letter and one digit
_PASSWORD_RE = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{8,}$")


def _validate_password(pw: str) -> None:
    if not _PASSWORD_RE.match(pw):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters and contain at least one letter and one number",
        )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _set_auth_cookie(response: JSONResponse, token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=_IS_PROD,
        samesite="lax",
        max_age=86400,  # matches 24-hour access token
        path="/",
    )


def _set_refresh_cookie(response: JSONResponse, token: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        secure=_IS_PROD,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/api/auth",  # scoped to auth endpoints (covers /refresh and /logout)
    )


def _create_refresh_token(user_id: str, request: Request, db: Session) -> str:
    opaque = secrets.token_urlsafe(48)
    token_hash = hashlib.sha256(opaque.encode()).hexdigest()
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    rt = RefreshToken(
        id=str(uuid.uuid4()),
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        user_agent=request.headers.get("user-agent", "")[:255],
        ip_address=request.client.host if request.client else None,
    )
    db.add(rt)
    db.commit()
    return opaque


def _audit(db: Session, request: Request, action: str, user_id: str | None = None,
           resource_type: str | None = None, resource_id: str | None = None, extra: dict | None = None) -> None:
    try:
        log = AuditLog(
            id=str(uuid.uuid4()),
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent", "")[:255],
            extra=extra,
        )
        db.add(log)
        db.commit()
    except Exception:
        pass  # never block the main path for audit failure


# ── Pydantic models ────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str | None
    is_active: bool
    is_admin: bool = False
    subscription_status: str | None = None
    stripe_customer_id: str | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/register", status_code=201)
@limiter.limit("5/minute")
async def register(request: Request, body: RegisterRequest, db: Session = Depends(get_db)):
    _validate_password(body.password)
    existing = db.query(User).filter(User.email == body.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_id = str(uuid.uuid4())
    user = User(
        id=new_id,
        email=body.email.lower(),
        password_hash=hash_password(body.password),
        name=body.name,
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()

    access_token = create_access_token(new_id, expires_delta=timedelta(hours=24))
    refresh_opaque = _create_refresh_token(new_id, request, db)
    _audit(db, request, "register", user_id=new_id, resource_type="user")
    email_service.send_welcome(body.email, body.name or body.email.split("@")[0])

    resp = JSONResponse(
        content={"access_token": access_token, "token_type": "bearer", "user_id": new_id},
        status_code=201,
    )
    _set_auth_cookie(resp, access_token)
    _set_refresh_cookie(resp, refresh_opaque)
    return resp


@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    import logging as _logging
    _log = _logging.getLogger(__name__)

    try:
        user = db.query(User).filter(User.email == body.email.lower()).first()
        if not user or not verify_password(body.password, user.password_hash) or not user.is_active:
            _audit(db, request, "login_failed", resource_type="auth", extra={"email": body.email})
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = create_access_token(user.id, expires_delta=timedelta(hours=24))
        try:
            refresh_opaque = _create_refresh_token(user.id, request, db)
        except Exception as rt_err:
            _log.error("Refresh token creation failed: %s", rt_err)
            refresh_opaque = None

        _audit(db, request, "login", user_id=user.id, resource_type="auth")

        resp = JSONResponse(content={"access_token": access_token, "token_type": "bearer", "user_id": user.id})
        _set_auth_cookie(resp, access_token)
        if refresh_opaque:
            _set_refresh_cookie(resp, refresh_opaque)
        return resp
    except HTTPException:
        raise
    except Exception as e:
        _log.error("Login error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Authentication error")


@router.post("/refresh")
@limiter.limit("30/minute")
async def refresh_token(request: Request, db: Session = Depends(get_db)):
    """Issue a new access token using a valid refresh token (rotation — old token revoked)."""
    opaque = request.cookies.get("refresh_token")
    if not opaque:
        raise HTTPException(status_code=401, detail="No refresh token")

    token_hash = hashlib.sha256(opaque.encode()).hexdigest()
    rt = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
        RefreshToken.revoked_at.is_(None),
    ).first()

    if not rt or rt.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh token expired or invalid")

    # Rotate: revoke the old refresh token and issue a new one
    rt.revoked_at = datetime.utcnow()
    db.commit()

    new_access = create_access_token(rt.user_id, expires_delta=timedelta(hours=24))
    new_refresh = _create_refresh_token(rt.user_id, request, db)
    _audit(db, request, "token_refresh", user_id=rt.user_id)

    resp = JSONResponse(content={"access_token": new_access, "token_type": "bearer"})
    _set_auth_cookie(resp, new_access)
    _set_refresh_cookie(resp, new_refresh)
    return resp


@router.post("/logout")
async def logout(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    # Revoke access token JTI in Redis blocklist
    raw_token = credentials.credentials if credentials else request.cookies.get("access_token")
    if raw_token:
        try:
            payload = _jwt.decode(raw_token, SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False})
            jti = payload.get("jti")
            exp = payload.get("exp")
            if jti and exp:
                remaining = max(1, int(exp - datetime.utcnow().timestamp()))
                from app.services.cache_service import revoke_jti
                revoke_jti(jti, remaining)
        except Exception:
            pass

    # Revoke refresh token in DB
    opaque = request.cookies.get("refresh_token")
    if opaque:
        token_hash = hashlib.sha256(opaque.encode()).hexdigest()
        rt = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
        ).first()
        if rt:
            rt.revoked_at = datetime.utcnow()
            db.commit()

    user_id = None
    if raw_token:
        try:
            pl = _jwt.decode(raw_token, SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False})
            user_id = pl.get("sub")
        except Exception:
            pass
    _audit(db, request, "logout", user_id=user_id)

    resp = JSONResponse(content={"message": "Logged out successfully"})
    resp.delete_cookie(key="access_token", path="/")
    resp.delete_cookie(key="refresh_token", path="/api/auth")
    return resp


@router.post("/change-password")
@limiter.limit("5/minute")
async def change_password(
    request: Request,
    body: ChangePasswordRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _validate_password(body.new_password)
    token = credentials.credentials if credentials else request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(body.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user.password_hash = hash_password(body.new_password)
    db.commit()
    _audit(db, request, "change_password", user_id=user.id)
    return {"message": "Password updated successfully"}


@router.post("/forgot-password")
@limiter.limit("5/minute")
async def forgot_password(request: Request, body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email.lower()).first()
    # Always return 200 to avoid email enumeration
    if user:
        tok = secrets.token_urlsafe(32)
        user.reset_token = tok
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()
        email_service.send_password_reset(user.email, tok)
    return {"message": "If that email exists you will receive a reset link shortly."}


@router.post("/reset-password")
@limiter.limit("5/minute")
async def reset_password(request: Request, body: ResetPasswordRequest, db: Session = Depends(get_db)):
    _validate_password(body.new_password)
    user = db.query(User).filter(User.reset_token == body.token).first()
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Reset link is invalid or has expired")
    user.password_hash = hash_password(body.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    _audit(db, request, "password_reset", user_id=user.id)
    return {"message": "Password updated. You can now log in."}


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials if credentials else request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ── Two-step verification (OTP) ───────────────────────────────────────────────

class OTPRequestBody(BaseModel):
    email: str
    password: str


class OTPVerifyBody(BaseModel):
    email: str
    code: str


def _clean_expired_otps(email: str, db: Session) -> None:
    db.query(OTPToken).filter(
        OTPToken.email == email.lower(),
        OTPToken.expires_at < datetime.utcnow(),
    ).delete(synchronize_session=False)
    db.commit()


@router.post("/otp/request")
@limiter.limit("5/minute")
async def request_otp(request: Request, body: OTPRequestBody, db: Session = Depends(get_db)):
    """Step 1: validate credentials, send 6-digit OTP to registered email."""
    user = db.query(User).filter(User.email == body.email.lower()).first()
    if not user or not verify_password(body.password, user.password_hash) or not user.is_active:
        # Generic error — don't reveal whether email exists
        raise HTTPException(status_code=401, detail="Invalid credentials")

    code = str(secrets.randbelow(900000) + 100000)  # 100000–999999
    code_hash = hashlib.sha256(code.encode()).hexdigest()
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    _clean_expired_otps(body.email, db)

    otp = OTPToken(
        id=str(uuid.uuid4()),
        email=body.email.lower(),
        token_hash=code_hash,
        expires_at=expires_at,
        used=False,
    )
    db.add(otp)
    db.commit()

    email_service.send_otp(user.email, code, user.name or "")
    _audit(db, request, "otp_requested", user_id=user.id, resource_type="auth")

    return {"ok": True, "message": "Verification code sent to your email"}


@router.post("/otp/verify")
@limiter.limit("10/minute")
async def verify_otp(request: Request, body: OTPVerifyBody, db: Session = Depends(get_db)):
    """Step 2: verify OTP code, return access token on success."""
    code = body.code.strip()
    if not code or len(code) != 6 or not code.isdigit():
        raise HTTPException(status_code=400, detail="Invalid verification code format")

    code_hash = hashlib.sha256(code.encode()).hexdigest()

    otp = db.query(OTPToken).filter(
        OTPToken.email == body.email.lower(),
        OTPToken.token_hash == code_hash,
        OTPToken.used == False,  # noqa: E712
        OTPToken.expires_at > datetime.utcnow(),
    ).first()

    if not otp:
        _audit(db, request, "otp_failed", resource_type="auth")
        raise HTTPException(status_code=401, detail="Invalid or expired verification code")

    otp.used = True
    db.commit()

    user = db.query(User).filter(User.email == body.email.lower()).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Account not found or inactive")

    access_token = create_access_token(user.id, expires_delta=timedelta(hours=24))
    try:
        refresh_opaque = _create_refresh_token(user.id, request, db)
    except Exception:
        refresh_opaque = None

    _audit(db, request, "login_otp", user_id=user.id, resource_type="auth")

    resp = JSONResponse(content={"access_token": access_token, "token_type": "bearer", "user_id": user.id})
    _set_auth_cookie(resp, access_token)
    if refresh_opaque:
        _set_refresh_cookie(resp, refresh_opaque)
    return resp
