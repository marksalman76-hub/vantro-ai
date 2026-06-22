import uuid
import secrets
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.auth import hash_password, verify_password, create_access_token, verify_token
from app.models import User
from app.database import SessionLocal
from app.services import email_service
from sqlalchemy.orm import Session
from app.limiter import limiter

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    subscription_status: str | None = None
    stripe_customer_id: str | None = None

@router.post("/register", response_model=AuthResponse, status_code=201)
@limiter.limit("5/minute")
async def register(request: Request, body: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_id = str(uuid.uuid4())
    user = User(
        id=new_id,
        email=body.email,
        password_hash=hash_password(body.password),
        name=body.name,
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    token = create_access_token(new_id, expires_delta=timedelta(hours=24))
    email_service.send_welcome(body.email, body.name or body.email.split("@")[0])
    return {"access_token": token, "user_id": new_id}

@router.post("/login", response_model=AuthResponse)
@limiter.limit("10/minute")
async def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.id, expires_delta=timedelta(hours=24))
    return {"access_token": token, "user_id": user.id}

@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@router.post("/forgot-password")
@limiter.limit("5/minute")
async def forgot_password(request: Request, body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    # Always return 200 to avoid email enumeration
    if user:
        tok = secrets.token_urlsafe(32)
        user.reset_token = tok
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()
        email_service.send_password_reset(user.email, tok)
    return {"message": "If that email exists you will receive a reset link shortly."}


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    if len(request.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    user = (
        db.query(User)
        .filter(User.reset_token == request.token)
        .first()
    )
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Reset link is invalid or has expired")
    user.password_hash = hash_password(request.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    return {"message": "Password updated. You can now log in."}


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
